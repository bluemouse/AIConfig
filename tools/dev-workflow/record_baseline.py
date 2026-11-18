#!/usr/bin/env python3
"""Record a baseline at the start of a dev-workflow phase.

Captures:
- The current git HEAD sha
- The set of dirty paths (from git status --porcelain)
- Content hashes for dirty paths and files in the run directory

These are written to `baseline.txt`, `phase-start-dirty-hashes.json`, and
`phase-start-snapshot.txt` in the run directory. Mode enforcement checks read
these to distinguish pre-existing changes from mutations made during the phase.

With --manifest-only, no new baseline is recorded; instead the run-dir
snapshot's entry for the run manifest (`00-run-manifest.md`) is refreshed to
its current hash. The orchestrator runs this after every manifest write:
`check_no_manifest_edits_by_phase` pins the manifest against the snapshot, so
an orchestrator-owned update must be re-pinned or post-flight flags it. The
feature brief's pin is deliberately left at its phase-start hash — the
orchestrator never legitimately writes the brief mid-phase, so refreshing it
would launder a forbidden doer/checker edit (cr-009). A full re-record here
would defeat the other mode-enforcement checks —
`check_no_forbidden_source_edits` compares dirty paths against
`baseline.txt`'s, and `check_no_commits_in_non_commit_phase` compares HEAD
against the baseline HEAD — so --manifest-only deliberately leaves those
files untouched.

Usage:
    python .agents/tools/dev-workflow/record_baseline.py --phase research --run-dir .agents/workflow/<slug> [--repo-root <path>] [--manifest-only]

Exit codes:
    0 — baseline recorded (or manifest pin refreshed)
    1 — error (not a git repo, run dir missing, etc.)
    2 — usage error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# Orchestrator-owned run-dir files: only the orchestrator writes these, and
# check_no_manifest_edits_by_phase pins them against the run-dir snapshot.
# Keep in lockstep with ORCHESTRATOR_OWNED in checks/mode_checks.py.
ORCHESTRATOR_OWNED = {"00-run-manifest.md", "01-feature-brief.md"}

# The pin refresh is for the manifest only: the orchestrator legitimately
# updates the manifest mid-phase, but never the feature brief — so
# refreshing the brief's snapshot entry would launder a forbidden
# doer/checker edit of the brief into the pin (cr-009). The brief stays
# pinned at its phase-start hash.
MANIFEST_PIN_FILES = {"00-run-manifest.md"}


def _file_digest(path: Path) -> str | None:
    """Return a stable digest for a file, or None when it no longer exists."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def refresh_manifest_pin(run_dir: Path) -> int:
    """Refresh the snapshot's manifest entry; touch nothing else.

    Reads `phase-start-snapshot.txt`, replaces the hash for the run manifest
    (`00-run-manifest.md`) with its current digest, and writes the file back
    with unchanged ordering. `baseline.txt` and
    `phase-start-dirty-hashes.json` — the source-edit and commit pins — and
    the feature brief's snapshot entry are deliberately left as they were:
    the orchestrator never legitimately writes the brief mid-phase, so its
    phase-start pin must keep catching a forbidden edit.
    """
    snapshot_path = run_dir / "phase-start-snapshot.txt"
    if not snapshot_path.is_file():
        print("ERROR: no phase-start snapshot to refresh — record a full baseline first")
        return 1

    lines = snapshot_path.read_text(encoding="utf-8").splitlines()
    updated: list[str] = []
    for line in lines:
        name, _, _ = line.partition("\t")
        if name in MANIFEST_PIN_FILES:
            digest = _file_digest(run_dir / name) or ""
            updated.append(f"{name}\t{digest}")
        else:
            updated.append(line)
    snapshot_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
    print("MANIFEST PIN REFRESHED (manifest entry updated)")
    return 0


def record_baseline(run_dir: Path, repo_root: Path | None) -> int:
    """Record the baseline files in the run directory."""
    if not run_dir.is_dir():
        print(f"ERROR: run directory not found: {run_dir}")
        return 1

    # Find repo root if not specified.
    if repo_root is None:
        current = run_dir
        while current != current.parent:
            if (current / ".git").exists():
                repo_root = current
                break
            current = current.parent

    if repo_root is None or not (repo_root / ".git").exists():
        print("WARNING: not a git repository — recording run-dir snapshot only")
        # Still record the run-dir snapshot.
        snapshot_lines = [
            f"{p.name}\t{_file_digest(p) or ''}"
            for p in run_dir.iterdir()
            if p.is_file()
        ]
        (run_dir / "phase-start-snapshot.txt").write_text(
            "\n".join(sorted(snapshot_lines)) + "\n", encoding="utf-8"
        )
        (run_dir / "phase-start-dirty-hashes.json").write_text(
            "{}\n", encoding="utf-8"
        )
        # Write an empty baseline so checks know it was attempted.
        (run_dir / "baseline.txt").write_text("no-git\n", encoding="utf-8")
        return 0

    # Record git HEAD.
    try:
        head_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print("ERROR: could not run git rev-parse HEAD")
        return 1

    if head_result.returncode != 0:
        print(f"ERROR: git rev-parse HEAD failed: {head_result.stderr.strip()}")
        return 1

    head_sha = head_result.stdout.strip()

    # Record dirty paths.
    try:
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print("ERROR: could not run git status")
        return 1

    if status_result.returncode != 0:
        print(f"ERROR: git status failed: {status_result.stderr.strip()}")
        return 1

    dirty_paths: list[str] = []
    dirty_hashes: dict[str, str | None] = {}
    for line in status_result.stdout.splitlines():
        if not line.strip():
            continue
        filepath = line[3:].strip()
        dirty_paths.append(filepath)
        dirty_hashes[filepath] = _file_digest(repo_root / filepath)

    # Write baseline file.
    baseline_lines = [head_sha] + dirty_paths
    (run_dir / "baseline.txt").write_text(
        "\n".join(baseline_lines) + "\n", encoding="utf-8"
    )
    (run_dir / "phase-start-dirty-hashes.json").write_text(
        json.dumps(dirty_hashes, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Record run-dir snapshot (files that existed at phase start).
    snapshot_lines = [
        f"{p.name}\t{_file_digest(p) or ''}"
        for p in run_dir.iterdir()
        if p.is_file()
    ]
    (run_dir / "phase-start-snapshot.txt").write_text(
        "\n".join(sorted(snapshot_lines)) + "\n", encoding="utf-8"
    )

    print(f"BASELINE RECORDED (HEAD: {head_sha[:8]}, dirty paths: {len(dirty_paths)})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record a baseline at the start of a dev-workflow phase."
    )
    parser.add_argument(
        "--phase",
        required=True,
        choices=["clarify", "research", "plan", "implement", "code-review", "commit"],
        help="The phase about to start.",
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Path to the run directory.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Path to the git repository root. Defaults to the first parent containing .git.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help=(
            "Do not record a new baseline; refresh only the run-dir snapshot's "
            "manifest entry (00-run-manifest.md). Use after orchestrator-owned "
            "manifest writes mid-phase."
        ),
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    if args.manifest_only:
        return refresh_manifest_pin(run_dir)
    return record_baseline(run_dir, args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
