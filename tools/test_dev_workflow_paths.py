#!/usr/bin/env python3
"""Tests for the dev-workflow scripts' `.agents/` path contract (t-014).

Covers the pg-013 single-root redesign changes to the harness:

- Mode-check dirty-path exemption: `.agents/` paths (workflow run state,
  plans, researches) are exempt from the read-only-phase source-edit check
  (user decision: exempt ALL of `.agents/`), while dirty files outside
  `.agents/` are still flagged.
- Staged-mode implement prefix exemption: the implement phase's allowed
  artifact prefixes gain 40/41 in staged mode (the per-stage
  40-stageN-*/41-stageN-* review artifacts the staged iterator prescribes);
  linear-mode implement keeps the {30, 31, 32, 33} set. Mirrored in
  loop_checks (loop-cap round counting uses the same prefix sets).
- test_dry_run.py locates the validation scripts next to itself rather
  than via a cwd-relative `.agents/` path, so the dry-run harness passes from
  any working directory (pre- and post-tree-move).

Scratch-fixture based throughout: nothing asserts the repository's own tree.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "scripts"

sys.path.insert(0, str(HARNESS_DIR))

from checks import loop_checks  # type: ignore[import-not-found]  # noqa: E402
from checks import mode_checks  # type: ignore[import-not-found]  # noqa: E402

STAGED_MANIFEST = "# Run Manifest\n\n## Run metadata\n- Run mode: staged\n"
LINEAR_MANIFEST = "# Run Manifest\n\n## Run metadata\n- Run mode: linear\n"


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )


def _make_git_repo(root: Path) -> Path:
    """Create a scratch git repository with one committed source file."""
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q")
    (root / "src.py").write_text("value = 1\n", encoding="utf-8")
    _git(root, "add", "src.py")
    _git(root, "commit", "-qm", "initial")
    return root


def _write_clean_baseline(run_dir: Path, repo_root: Path) -> None:
    """Write a baseline.txt recording a clean tree at phase start."""
    head = _git(repo_root, "rev-parse", "HEAD").stdout.strip()
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "baseline.txt").write_text(head + "\n", encoding="utf-8")


class ModeCheckAgentsExemptionTests(unittest.TestCase):
    """`.agents/` dirty paths are exempt; everything else is still flagged."""

    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="dw-paths-"))
        # run_dir lives outside the repo so only the fixture files are dirty.
        self.repo = _make_git_repo(self.temp / "repo")
        self.run_dir = self.temp / "run"
        _write_clean_baseline(self.run_dir, self.repo)

    def tearDown(self) -> None:
        subprocess.run(["rm", "-rf", str(self.temp)], check=False)

    def test_agents_paths_not_flagged(self) -> None:
        """`.agents/workflow|plans|researches` dirtied mid-phase -> no findings."""
        for rel in (
            ".agents/workflow/feature-slug/baseline.txt",
            ".agents/plans/old-plan.md",
            ".agents/researches/old-research.md",
        ):
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("run state\n", encoding="utf-8")
        findings = mode_checks.check_no_forbidden_source_edits(
            self.repo, "research", self.run_dir
        )
        self.assertEqual(
            [f.message for f in findings],
            [],
            "`.agents/` run-state paths must be exempt from the "
            "read-only source-edit check",
        )

    def test_dirty_source_outside_agents_flagged(self) -> None:
        """A modified tracked file and a new untracked file are both flagged."""
        (self.repo / "src.py").write_text("value = 2\n", encoding="utf-8")
        (self.repo / "new_module.py").write_text("x = 1\n", encoding="utf-8")
        findings = mode_checks.check_no_forbidden_source_edits(
            self.repo, "research", self.run_dir
        )
        messages = [f.message for f in findings]
        self.assertTrue(any("src.py" in m for m in messages), messages)
        self.assertTrue(any("new_module.py" in m for m in messages), messages)


class StagedImplementPrefixTests(unittest.TestCase):
    """Implement's allowed prefixes gain 40/41 in staged mode only."""

    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="dw-prefixes-"))

    def tearDown(self) -> None:
        subprocess.run(["rm", "-rf", str(self.temp)], check=False)

    def _make_run_dir(self, manifest: str) -> Path:
        run_dir = self.temp / f"run-{self.id()[-12:]}"
        run_dir.mkdir(parents=True)
        (run_dir / "00-run-manifest.md").write_text(manifest, encoding="utf-8")
        return run_dir

    def test_staged_implement_allows_stage_review_artifacts(self) -> None:
        """Staged implement accepts 40-stageN-*/41-stageN-* review artifacts."""
        run_dir = self._make_run_dir(STAGED_MANIFEST)
        for name in (
            "30-stage4-implementation-report.md",
            "40-stage4-code-review.md",
            "41-stage4-fix-report.md",
        ):
            (run_dir / name).write_text("# Report\n", encoding="utf-8")
        findings = mode_checks.check_only_allowed_artifacts(run_dir, "implement")
        self.assertEqual(
            [f.message for f in findings],
            [],
            "Staged implement must allow the per-stage review artifacts "
            "the staged iterator prescribes",
        )

    def test_linear_implement_rejects_review_prefixes(self) -> None:
        """Linear implement keeps the {30, 31, 32, 33} set."""
        run_dir = self._make_run_dir(LINEAR_MANIFEST)
        (run_dir / "40-code-review.md").write_text("# Review\n", encoding="utf-8")
        findings = mode_checks.check_only_allowed_artifacts(run_dir, "implement")
        self.assertEqual(len(findings), 1, [f.message for f in findings])
        self.assertIn("40-code-review.md", findings[0].message)

    def test_staged_loop_cap_counts_stage_review_rounds(self) -> None:
        """Staged implement's loop cap counts 40-stageN-*-rN review rounds."""
        run_dir = self._make_run_dir(STAGED_MANIFEST)
        (run_dir / "40-stage1-code-review-r4.md").write_text(
            "# Review\n", encoding="utf-8"
        )
        findings = loop_checks.check_loop_cap_respected(run_dir, "implement")
        self.assertTrue(
            any("Loop cap exceeded" in f.message for f in findings),
            [f.message for f in findings],
        )

    def test_staged_implement_rejects_out_of_set_prefixes(self) -> None:
        """cr-401: staged implement still REJECTS prefixes outside its set.

        The accept-direction tests above pin that 40/41 are admitted in
        staged mode; this negative guard proves a helper regression that
        broadened the guard (e.g. allowing every prefix in staged mode)
        cannot keep them green.
        """
        run_dir = self._make_run_dir(STAGED_MANIFEST)
        (run_dir / "50-commit.md").write_text("# Commit\n", encoding="utf-8")
        findings = mode_checks.check_only_allowed_artifacts(run_dir, "implement")
        self.assertEqual(
            len(findings),
            1,
            "Staged implement must still reject out-of-set prefixes "
            "(50-commit.md belongs to the commit phase); findings: "
            + str([f.message for f in findings]),
        )
        self.assertIn("50-commit.md", findings[0].message)

    def test_linear_loop_cap_ignores_review_rounds(self) -> None:
        """Linear implement round counting ignores 40-* artifacts."""
        run_dir = self._make_run_dir(LINEAR_MANIFEST)
        (run_dir / "40-code-review-r4.md").write_text("# Review\n", encoding="utf-8")
        self.assertEqual(loop_checks.check_loop_cap_respected(run_dir, "implement"), [])


class DryRunHarnessLocationTests(unittest.TestCase):
    """test_dry_run.py runs from any cwd (script-relative validator paths)."""

    def test_dry_run_suite_passes_from_foreign_cwd(self) -> None:
        """The dry-run harness passes when invoked from an unrelated cwd."""
        script = HARNESS_DIR / "test_dry_run.py"
        with tempfile.TemporaryDirectory(prefix="dw-dryrun-cwd-") as tmpdir:
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=120,
            )
        self.assertEqual(
            result.returncode,
            0,
            "dry-run harness must pass from a foreign cwd; output tail:\n"
            + result.stdout[-400:],
        )


if __name__ == "__main__":
    unittest.main()
