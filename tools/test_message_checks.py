#!/usr/bin/env python3
"""Tests for the commit-message lint: harness gate + skill script twin.

Covers:
- lint_message_text rule behavior (fixtures field-tested against the
  2026-11-09 two-day reword: reworded messages pass, originals fail)
- rule parity between the harness module and the skill script (drift guard)
- check_commit_messages baseline plumbing against a real temp git repo
- the skill script's CLI contract
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = REPO_ROOT / ".ai" / "tools" / "dev-workflow"
SKILL_SCRIPT = REPO_ROOT / "skills" / "commit-message-writer" / "scripts" / "lint_message.py"

sys.path.insert(0, str(HARNESS_DIR))

from checks import message_checks  # noqa: E402


def _load_skill_module():
    spec = importlib.util.spec_from_file_location("lint_message", SKILL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {SKILL_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["lint_message"] = module
    spec.loader.exec_module(module)
    return module


skill_lint = _load_skill_module()

# A real reworded message (passes): self-contained, no ids, no narration.
GOOD_MESSAGE = """\
fix(shaders): correct stale comments and pin bicubic identity warp

Comment and doc corrections where the text drifted from the code, plus a
gpu oracle for the bicubic xform texel-centering fix:

- worleyNoise2D: the F2 sentinel comment claimed the 3D bound (~2*sqrt(3));
  the 2D maximum at jitter 1 is ~2*sqrt(2)

New BicubicXformIdentityWarpMatchesInput gpu test: an identity warp with
equal source and destination sizes must reproduce the input byte-for-byte
(plus-minus 1 tolerance for the sRGB store round-trip).
"""

# A real pre-reword message (fails): ids in body, stage narration, 88-char subject.
BAD_MESSAGE = """\
fix(shaders): pixel-neutral shader fixes, smudge bbox restructure, histogram shared path

Stage 1 of the fresh-review HIGH+MEDIUM fixes (findings M1-M3, M5, M7,
M11, M13, M14, M19-M29; H1/M29 smoke-variant wiring):

- pattern/toonCloud: premultiply before the blendAlpha over-operator (M1)
- noise/worleyNoise: F1/F2 sentinels 1.0 -> 8.0 (M2)
"""

# The B2x id class that a naive single-regex version missed.
B20_MESSAGE = """\
docs(shaders): correct stale comments and unify style

Comment sweep including riding document-only rows (B20/B21/B25, A07, A23).
"""

# Section references like "A.5" must NOT be flagged (false-positive guard).
SECTION_REF_MESSAGE = """\
docs(painter): update the smudge limitation appendix

The per-dab blit note now points at appendix A.5; the fence-wait claim is
gone (a stroke batch is one command buffer with one submit).
"""

COAUTHORED_MESSAGE = """\
fix(app): tighten retry backoff

Retries now cap at 30s.

Co-authored-by: Some Assistant <assistant@example.com>
"""


class LintMessageTextTests(unittest.TestCase):
    def test_good_message_passes(self) -> None:
        self.assertEqual(message_checks.lint_message_text(GOOD_MESSAGE), [])

    def test_bad_message_flags_ids_narration_and_length(self) -> None:
        violations = message_checks.lint_message_text(BAD_MESSAGE)
        joined = "\n".join(violations)
        self.assertIn("stage narration", joined)
        self.assertIn("finding id", joined)
        self.assertIn("severity label", joined)
        self.assertIn("review narration", joined)
        self.assertIn("subject exceeds 72 characters (88)", joined)

    def test_b2x_ids_flagged(self) -> None:
        violations = message_checks.lint_message_text(B20_MESSAGE)
        self.assertTrue(any("finding id" in v for v in violations), violations)

    def test_section_reference_not_flagged(self) -> None:
        self.assertEqual(message_checks.lint_message_text(SECTION_REF_MESSAGE), [])

    def test_coauthored_footer_flagged(self) -> None:
        violations = message_checks.lint_message_text(COAUTHORED_MESSAGE)
        self.assertTrue(any("Co-authored-by" in v for v in violations), violations)

    def test_long_subject_flagged(self) -> None:
        text = "fix(shaders): " + "x" * 70
        violations = message_checks.lint_message_text(text)
        self.assertTrue(any("exceeds 72" in v for v in violations), violations)

    def test_non_conventional_subject_flagged(self) -> None:
        violations = message_checks.lint_message_text("fixed the retry backoff\n\nBody.")
        self.assertTrue(any("not a Conventional Commits line" in v for v in violations), violations)

    def test_trailing_period_flagged(self) -> None:
        violations = message_checks.lint_message_text("fix(app): tighten retry backoff.\n")
        self.assertTrue(any("trailing period" in v for v in violations), violations)

    def test_empty_message_flagged(self) -> None:
        self.assertEqual(message_checks.lint_message_text("  \n"), ["empty message"])


class RuleParityTests(unittest.TestCase):
    """The harness gate and the skill script must flag the same things."""

    FIXTURES = [
        GOOD_MESSAGE,
        BAD_MESSAGE,
        B20_MESSAGE,
        SECTION_REF_MESSAGE,
        COAUTHORED_MESSAGE,
        "fix(app): tighten retry backoff.\n",
        "fixed the retry backoff\n\nBody.",
        "",
    ]

    def test_twin_rule_sets_agree(self) -> None:
        for text in self.FIXTURES:
            with self.subTest(text=text[:40]):
                self.assertEqual(
                    message_checks.lint_message_text(text),
                    skill_lint.lint_message_text(text),
                )


class CheckCommitMessagesTests(unittest.TestCase):
    """Baseline plumbing against a real temp git repository."""

    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="message-checks-"))
        self.repo = self.temp / "repo"
        self.repo.mkdir()
        self._git("init", "--quiet")
        (self.repo / "file.txt").write_text("seed\n", encoding="utf-8")
        self._git("add", "file.txt")
        self._git("commit", "--quiet", "-m", "chore: seed")
        self.run_dir = self.temp / "run"
        self.run_dir.mkdir()
        self._record_baseline()

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

    def _head(self) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self.repo, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    def _record_baseline(self) -> None:
        (self.run_dir / "baseline.txt").write_text(self._head() + "\n", encoding="utf-8")

    def _commit(self, message: str) -> str:
        self._counter = getattr(self, "_counter", 0) + 1
        (self.repo / "file.txt").write_text(f"change {self._counter}\n", encoding="utf-8")
        self._git("add", "file.txt")
        self._git("commit", "--quiet", "-m", message)
        return self._head()

    def test_bad_commit_flagged(self) -> None:
        sha = self._commit(BAD_MESSAGE)
        findings = message_checks.check_commit_messages(self.run_dir, "implement", self.repo)
        errors = [f for f in findings if f.severity == "error"]
        self.assertTrue(errors, findings)
        self.assertTrue(all(f.check == "commit_message" for f in errors))
        self.assertIn(sha[:8], errors[0].message)

    def test_good_commit_clean(self) -> None:
        self._commit(GOOD_MESSAGE)
        findings = message_checks.check_commit_messages(self.run_dir, "implement", self.repo)
        self.assertEqual(findings, [])

    def test_mixed_range_flags_only_bad_commits(self) -> None:
        good_sha = self._commit(GOOD_MESSAGE)
        bad_sha = self._commit(BAD_MESSAGE)
        findings = message_checks.check_commit_messages(self.run_dir, "implement", self.repo)
        errors = [f for f in findings if f.severity == "error"]
        self.assertTrue(errors, findings)
        # Every error belongs to the bad commit; the good one contributes none.
        self.assertTrue(all(f.message.startswith(f"commit {bad_sha[:8]}") for f in errors), errors)
        self.assertFalse(any(good_sha[:8] in f.message for f in errors), errors)

    def test_head_at_baseline_clean(self) -> None:
        findings = message_checks.check_commit_messages(self.run_dir, "implement", self.repo)
        self.assertEqual(findings, [])

    def test_non_lint_phase_ignored(self) -> None:
        self._commit(BAD_MESSAGE)
        self.assertEqual(message_checks.check_commit_messages(self.run_dir, "research", self.repo), [])

    def test_missing_baseline_clean(self) -> None:
        (self.run_dir / "baseline.txt").unlink()
        self._commit(BAD_MESSAGE)
        self.assertEqual(message_checks.check_commit_messages(self.run_dir, "implement", self.repo), [])

    def test_rebaseline_absorbs_dispositioned_commit(self) -> None:
        self._commit(BAD_MESSAGE)
        self.assertTrue(message_checks.check_commit_messages(self.run_dir, "implement", self.repo))
        # The established disposition repair: re-record the baseline mid-phase.
        self._record_baseline()
        self.assertEqual(message_checks.check_commit_messages(self.run_dir, "implement", self.repo), [])

    def test_none_repo_root_clean(self) -> None:
        self._commit(BAD_MESSAGE)
        self.assertEqual(message_checks.check_commit_messages(self.run_dir, "implement", None), [])


class SkillScriptCliTests(unittest.TestCase):
    def _run(self, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SKILL_SCRIPT), *args],
            capture_output=True,
            text=True,
            input=stdin,
        )

    def test_good_message_exit_zero(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
            handle.write(GOOD_MESSAGE)
            path = handle.name
        result = self._run(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASSED", result.stdout)

    def test_bad_message_exit_one(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
            handle.write(BAD_MESSAGE)
            path = handle.name
        result = self._run(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("LINT FAILED", result.stderr)

    def test_stdin_mode(self) -> None:
        result = self._run("-", stdin=GOOD_MESSAGE)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self._run("-", stdin=BAD_MESSAGE)
        self.assertEqual(result.returncode, 1)

    def test_usage_error_exit_two(self) -> None:
        result = self._run()
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
