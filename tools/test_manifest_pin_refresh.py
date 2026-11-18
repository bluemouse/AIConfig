#!/usr/bin/env python3
"""Tests for the manifest-pin refresh in record_baseline.py (review round fix cr-001).

The orchestrator updates the manifest after every step, but mode enforcement
pins orchestrator-owned run-dir files against the phase-start snapshot. The
original fix guidance said to re-run record_baseline.py (a full re-record)
after each manifest write — which also resets `baseline.txt` (HEAD + dirty
paths) and `phase-start-dirty-hashes.json`, laundering any forbidden source
edit or commit made since phase start past check_no_forbidden_source_edits
and check_no_commits_in_non_commit_phase. The --manifest-only mode refreshes
only the snapshot's orchestrator-owned entries, leaving the source-edit and
commit pins intact.

Run from the repository root: python tools/test_manifest_pin_refresh.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "dev-workflow"))

from checks import mode_checks  # type: ignore[import-not-found]

SCRIPT = REPO_ROOT / "tools" / "dev-workflow" / "record_baseline.py"


class ManifestPinRefreshTests(unittest.TestCase):
    """--manifest-only refreshes the pin without laundering the baseline."""

    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="manifest-pin-"))
        self.repo = self.temp / "repo"
        self.repo.mkdir()
        self._git("init", "--quiet")
        (self.repo / "source.txt").write_text("clean\n", encoding="utf-8")
        self._git("add", "source.txt")
        self._git("commit", "--quiet", "-m", "chore: seed")
        self.run_dir = self.temp / "run"
        self.run_dir.mkdir()
        (self.run_dir / "00-run-manifest.md").write_text(
            "# Run Manifest\nphase-start contents\n", encoding="utf-8"
        )
        (self.run_dir / "01-feature-brief.md").write_text(
            "# Feature Brief\nphase-start contents\n", encoding="utf-8"
        )
        self._run_script()  # full baseline at phase start

    def tearDown(self) -> None:
        subprocess.run(["rm", "-rf", str(self.temp)], check=False)

    def _git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            check=True,
        )

    def _run_script(self, *args: str) -> int:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--phase", "research",
             "--run-dir", str(self.run_dir), "--repo-root", str(self.repo), *args],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.fail(f"record_baseline.py failed: {result.stdout}{result.stderr}")
        return result.returncode

    def _snapshot(self) -> dict[str, str]:
        lines = (self.run_dir / "phase-start-snapshot.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        snapshot: dict[str, str] = {}
        for line in lines:
            name, _, digest = line.partition("\t")
            snapshot[name] = digest
        return snapshot

    def test_feature_brief_edit_not_laundered_by_pin_refresh(self) -> None:
        """cr-009: the pin refresh covers the manifest only. A forbidden
        feature-brief edit (doers/checkers never touch orchestrator-owned
        files) must stay flagged after --manifest-only."""
        (self.run_dir / "01-feature-brief.md").write_text(
            "# Feature Brief\ntampered by the doer pass\n", encoding="utf-8"
        )
        (self.run_dir / "00-run-manifest.md").write_text(
            "# Run Manifest\nupdated by orchestrator\n", encoding="utf-8"
        )
        self._run_script("--manifest-only")

        manifest_findings = mode_checks.check_no_manifest_edits_by_phase(
            self.run_dir, "research"
        )
        brief_flagged = any(
            "01-feature-brief.md" in f.message for f in manifest_findings
        )
        manifest_flagged = any(
            "00-run-manifest.md" in f.message for f in manifest_findings
        )
        self.assertFalse(
            manifest_flagged,
            f"the orchestrator's manifest write must be re-pinned: "
            f"{[f.message for f in manifest_findings]}",
        )
        self.assertTrue(
            brief_flagged,
            f"the forbidden feature-brief edit must NOT be laundered: "
            f"{[f.message for f in manifest_findings]}",
        )

    def test_manifest_only_refreshes_pin_and_preserves_baseline(self) -> None:
        """After an orchestrator manifest write + --manifest-only, the
        manifest check passes but a forbidden source edit made during the
        phase is still flagged (not laundered)."""
        # Simulate the doer pass: an orchestrator manifest write AND a
        # forbidden source edit in a read-only phase.
        (self.repo / "source.txt").write_text("tampered\n", encoding="utf-8")
        (self.run_dir / "00-run-manifest.md").write_text(
            "# Run Manifest\nupdated by orchestrator\n", encoding="utf-8"
        )
        self._run_script("--manifest-only")

        # The manifest pin tracks the orchestrator-owned write.
        manifest_findings = mode_checks.check_no_manifest_edits_by_phase(
            self.run_dir, "research"
        )
        self.assertEqual(
            [f.message for f in manifest_findings],
            [],
            "pin refresh must clear the orchestrator-owned manifest delta",
        )

        # The forbidden source edit is NOT laundered — the dirty-path
        # baseline still catches it.
        source_findings = mode_checks.check_no_forbidden_source_edits(
            self.repo, "research", self.run_dir
        )
        self.assertTrue(
            any("source.txt" in f.message for f in source_findings),
            f"--manifest-only must not launder source edits: "
            f"{[f.message for f in source_findings]}",
        )

    def test_full_rerecord_would_launder_but_manifest_only_does_not(self) -> None:
        """A full re-record (the old guidance) absorbs the forbidden edit;
        --manifest-only does not. Pins the regression the fix exists for."""
        (self.repo / "source.txt").write_text("tampered\n", encoding="utf-8")
        (self.run_dir / "00-run-manifest.md").write_text(
            "# Run Manifest\nupdated\n", encoding="utf-8"
        )

        self._run_script("--manifest-only")
        after_manifest_only = mode_checks.check_no_forbidden_source_edits(
            self.repo, "research", self.run_dir
        )
        self.assertTrue(any("source.txt" in f.message for f in after_manifest_only))

        # Contrast: a full re-record would absorb it (documents why
        # --manifest-only is required).
        self._run_script()
        after_full = mode_checks.check_no_forbidden_source_edits(
            self.repo, "research", self.run_dir
        )
        self.assertFalse(
            any("source.txt" in f.message for f in after_full),
            "sanity: full re-record absorbs the edit (this is the laundering)",
        )

    def test_manifest_only_requires_existing_snapshot(self) -> None:
        """--manifest-only on a run dir with no snapshot fails cleanly."""
        bare = self.temp / "bare-run"
        bare.mkdir()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--phase", "research",
             "--run-dir", str(bare), "--manifest-only"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("no phase-start snapshot", result.stdout)


if __name__ == "__main__":
    unittest.main()
