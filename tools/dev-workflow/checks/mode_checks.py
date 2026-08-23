"""Category 5: Mode enforcement checks.

Verify that each phase wrote only to its allowed artifacts and did not touch
forbidden files (source code in read-only phases, commits in non-commit phases).

Baseline mechanism: the orchestrator records a baseline at phase start by running
`record_baseline.py`. The baseline file contains the git HEAD sha and the set of
dirty paths at phase start. Mode checks diff the current state against the baseline
to find only NEW changes made during the phase.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from . import Finding

# Allowed artifact filename prefixes per phase.
# These are the only files a phase should create/modify in the run directory.
PHASE_ALLOWED_PREFIXES: dict[str, set[str]] = {
    "clarify": {"02"},
    "research": {"10", "11", "12", "13", "14", "15"},
    "plan": {"20", "21", "22", "23"},
    "implement": {"30", "31", "32", "33"},
    "code-review": {"40", "41", "42", "43"},
    "commit": {"50"},
}

# Orchestrator-owned files that no phase should write.
ORCHESTRATOR_OWNED = {"00-run-manifest.md", "01-feature-brief.md"}

# Phases that are allowed to modify source files.
WRITE_SOURCE_PHASES = {"implement", "code-review"}

# Phases that are allowed to run tests.
RUN_TESTS_PHASES = {"implement", "code-review"}

# Phases that are allowed to commit.
COMMIT_PHASES = {"commit"}

# Read-only phases where source-edit checks are meaningful.
# Clarify is read-only but interactive; source-edit checks are skipped (O1).
SOURCE_EDIT_CHECK_PHASES = {"research", "plan", "commit"}


def _read_baseline(run_dir: Path) -> dict[str, str] | None:
    """Read the baseline file for the current phase.

    The baseline file is `baseline.txt` in the run directory. It contains:
    - Line 1: git HEAD sha at phase start
    - Lines 2+: dirty paths at phase start (one per line)

    Returns None if no baseline exists.
    """
    baseline_path = run_dir / "baseline.txt"
    if not baseline_path.exists():
        return None
    lines = baseline_path.read_text(encoding="utf-8").strip().splitlines()
    if not lines:
        return None
    head = lines[0].strip()
    dirty_paths = {line.strip() for line in lines[1:] if line.strip()}
    return {"head": head, "dirty_paths": dirty_paths}


def _get_current_dirty_paths(repo_root: Path) -> set[str] | None:
    """Get the current set of dirty paths from git status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

    if result.returncode != 0:
        return None

    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        filepath = line[3:].strip()
        paths.add(filepath)
    return paths


def _get_current_head(repo_root: Path) -> str | None:
    """Get the current git HEAD sha."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return None

    if result.returncode != 0:
        return None

    return result.stdout.strip()


def _read_run_dir_snapshot(run_dir: Path) -> dict[str, str]:
    """Read the phase-start snapshot of files in the run directory.

    The snapshot file is `phase-start-snapshot.txt`. It contains one filename
    and SHA-256 digest, separated by a tab, per file at phase start.
    """
    snapshot_path = run_dir / "phase-start-snapshot.txt"
    if not snapshot_path.exists():
        return {}
    snapshot: dict[str, str] = {}
    for line in snapshot_path.read_text(encoding="utf-8").splitlines():
        name, separator, digest = line.partition("\t")
        if name:
            snapshot[name] = digest if separator else ""
    return snapshot


def _file_digest(path: Path) -> str | None:
    """Return a stable digest for a file, or None when it no longer exists."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_dirty_hashes(run_dir: Path) -> dict[str, str | None]:
    """Read content fingerprints for paths that were dirty at phase start."""
    hashes_path = run_dir / "phase-start-dirty-hashes.json"
    if not hashes_path.exists():
        return {}
    try:
        data = json.loads(hashes_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        path: digest
        for path, digest in data.items()
        if isinstance(path, str) and (isinstance(digest, str) or digest is None)
    }


def check_only_allowed_artifacts(run_dir: Path, phase: str) -> list[Finding]:
    """Check that only artifacts with allowed prefixes were created in the run dir.

    Uses the phase-start snapshot to distinguish files written during this phase
    from files written by earlier phases. Only unchanged files from before the
    snapshot are exempt; modified earlier artifacts are checked as phase writes.
    """
    findings: list[Finding] = []
    allowed = PHASE_ALLOWED_PREFIXES.get(phase, set())
    existing_files = _read_run_dir_snapshot(run_dir)

    for path in run_dir.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        if path.name in ORCHESTRATOR_OWNED:
            continue
        if path.name.startswith("back-"):
            continue
        # Skip files that existed at phase start and are unchanged. A changed
        # earlier artifact must still be checked against this phase's ownership.
        if existing_files.get(path.name) == _file_digest(path):
            continue
        # Skip baseline/snapshot files themselves.
        if path.name in (
            "baseline.txt",
            "phase-start-snapshot.txt",
            "phase-start-dirty-hashes.json",
        ):
            continue
        prefix = path.name[:2]
        if prefix not in allowed:
            findings.append(Finding(
                severity="error",
                check="mode_enforcement",
                message=(
                    f"Phase {phase} wrote artifact outside its allowed set: {path.name}"
                ),
            ))

    for filename in existing_files:
        path = run_dir / filename
        if (
            not filename.endswith(".md")
            or filename in ORCHESTRATOR_OWNED
            or filename.startswith("back-")
            or path.exists()
        ):
            continue
        if filename[:2] not in allowed:
            findings.append(Finding(
                severity="error",
                check="mode_enforcement",
                message=(
                    f"Phase {phase} deleted artifact outside its allowed set: {filename}"
                ),
            ))
    return findings


def check_no_manifest_edits_by_phase(run_dir: Path, phase: str) -> list[Finding]:
    """Check that the manifest was not modified by a phase (only orchestrator edits it).

    Uses the phase-start snapshot to ensure that phase-owned work did not modify
    the manifest or feature brief. The orchestrator updates the manifest only
    after post-flight validation succeeds.
    """
    findings: list[Finding] = []
    snapshot = _read_run_dir_snapshot(run_dir)
    for filename in ORCHESTRATOR_OWNED:
        path = run_dir / filename
        before = snapshot.get(filename)
        after = _file_digest(path)
        if before is not None and before != after:
            findings.append(Finding(
                severity="error",
                check="mode_enforcement",
                message=f"Phase {phase} modified orchestrator-owned artifact: {filename}",
            ))
    return findings


def check_no_forbidden_source_edits(repo_root: Path, phase: str, run_dir: Path) -> list[Finding]:
    """Check that read-only phases did not modify source files.

    Uses the baseline to distinguish pre-existing changes from changes made
    during this phase. Only NEW dirty paths (not in the baseline) are flagged.
    """
    findings: list[Finding] = []
    if phase in WRITE_SOURCE_PHASES:
        return []
    if phase not in SOURCE_EDIT_CHECK_PHASES:
        return []  # Skip for clarify and other non-source-check phases (O1)

    current_paths = _get_current_dirty_paths(repo_root)
    if current_paths is None:
        return [Finding(
            severity="warning",
            check="mode_enforcement",
            message="Could not run git status to verify mode enforcement",
        )]

    baseline = _read_baseline(run_dir)
    if baseline is not None:
        baseline_paths = baseline["dirty_paths"]
        dirty_hashes = _read_dirty_hashes(run_dir)
        # Flag paths newly dirtied during the phase and existing dirty paths
        # whose contents changed after the baseline was captured.
        new_paths = current_paths - baseline_paths
        modified_paths = {
            filepath
            for filepath in current_paths & baseline_paths
            if filepath in dirty_hashes
            and _file_digest(repo_root / filepath) != dirty_hashes[filepath]
        }
        new_paths |= modified_paths
    else:
        # No baseline — fall back to flagging all dirty paths (old behavior).
        # This will produce false positives on dirty repos, but it's the
        # best we can do without a baseline.
        new_paths = current_paths

    for filepath in sorted(new_paths):
        if filepath.startswith(".ai/workflow/"):
            continue
        if filepath.startswith(".ai/"):
            continue
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message=(
                f"Phase {phase} (read-only) modified source file: {filepath}"
            ),
        ))
    return findings


def check_no_commits_in_non_commit_phase(repo_root: Path, phase: str, run_dir: Path) -> list[Finding]:
    """Check that no commits were made in non-commit phases.

    Compares the current HEAD against the baseline HEAD. If they differ and
    the phase is not a commit phase, a commit was made during the phase.
    """
    findings: list[Finding] = []
    if phase in COMMIT_PHASES:
        return []

    baseline = _read_baseline(run_dir)
    if baseline is None:
        return []  # No baseline to compare against

    current_head = _get_current_head(repo_root)
    if current_head is None:
        return []

    if current_head != baseline["head"]:
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message=(
                f"Phase {phase} made a commit: HEAD changed from "
                f"{baseline['head'][:8]} to {current_head[:8]}"
            ),
        ))
    return findings


def check_commit_exists(repo_root: Path, run_dir: Path) -> list[Finding]:
    """Check that the commit hash recorded in 50-commit.md exists in git history.

    This verifies the commit phase actually produced a commit.
    """
    findings: list[Finding] = []
    commit_record = run_dir / "50-commit.md"
    if not commit_record.exists():
        return []  # Not at commit phase yet

    text = commit_record.read_text(encoding="utf-8")
    hash_match = re.search(r"Commit hash:\s*([0-9a-f]{7,40})", text, re.IGNORECASE)
    if not hash_match:
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message="Commit record (50-commit.md) missing commit hash",
        ))
        return findings

    commit_hash = hash_match.group(1)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"{commit_hash}^{{commit}}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return [Finding(
            severity="warning",
            check="mode_enforcement",
            message="Could not resolve commit hash to verify commit exists",
        )]

    if result.returncode != 0:
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message=f"Commit hash {commit_hash} not found in git history",
        ))
        return findings

    baseline = _read_baseline(run_dir)
    current_head = _get_current_head(repo_root)
    recorded_head = result.stdout.strip()
    if baseline is None or current_head is None:
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message="Could not compare commit record with the phase baseline",
        ))
    elif current_head == baseline["head"]:
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message="Commit phase did not advance HEAD beyond its baseline",
        ))
    elif recorded_head != current_head:
        findings.append(Finding(
            severity="error",
            check="mode_enforcement",
            message=(
                f"Commit record names {recorded_head[:8]}, but HEAD is "
                f"{current_head[:8]}"
            ),
        ))
    return findings


def run_all(run_dir: Path, phase: str, repo_root: Path | None = None) -> list[Finding]:
    """Run all mode enforcement checks for a phase."""
    findings: list[Finding] = []
    findings.extend(check_only_allowed_artifacts(run_dir, phase))
    findings.extend(check_no_manifest_edits_by_phase(run_dir, phase))
    if repo_root is not None:
        findings.extend(check_no_forbidden_source_edits(repo_root, phase, run_dir))
        findings.extend(check_no_commits_in_non_commit_phase(repo_root, phase, run_dir))
        if phase == "commit":
            findings.extend(check_commit_exists(repo_root, run_dir))
    return findings
