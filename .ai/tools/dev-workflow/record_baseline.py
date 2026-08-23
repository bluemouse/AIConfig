#!/usr/bin/env python3
"""Record a baseline at the start of a dev-workflow phase.

Captures:
- The current git HEAD sha
- The set of dirty paths (from git status --porcelain)
- Content hashes for dirty paths and files in the run directory

These are written to `baseline.txt`, `phase-start-dirty-hashes.json`, and
`phase-start-snapshot.txt` in the run directory. Mode enforcement checks read
these to distinguish pre-existing changes from mutations made during the phase.

Usage:
    python .ai/tools/dev-workflow/record_baseline.py --phase research --run-dir .ai/workflow/<slug> [--repo-root <path>]

Exit codes:
    0 — baseline recorded
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


def _file_digest(path: Path) -> str | None:
    """Return a stable digest for a file, or None when it no longer exists."""
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    args = parser.parse_args()

    return record_baseline(args.run_dir.resolve(), args.repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
