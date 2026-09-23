#!/usr/bin/env python3
"""Tests for the per-phase dev-workflow command bootstrap sources.

Validates that the four `/dev-workflow-<phase>` commands exist as bootstrap
sources under `commands/dev-workflow-<phase>/COMMAND.md`, have valid
frontmatter, and contain no tool-specific content in the shared body.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_CREATOR_SCRIPTS = REPO_ROOT / "skills" / "command-creator" / "scripts"

# Load quick_validate as a module (it lives outside the tools/ package).
_spec = importlib.util.spec_from_file_location(
    "quick_validate", COMMAND_CREATOR_SCRIPTS / "quick_validate.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load quick_validate from {COMMAND_CREATOR_SCRIPTS}")
quick_validate = importlib.util.module_from_spec(_spec)
sys.modules["quick_validate"] = quick_validate
_spec.loader.exec_module(quick_validate)


PHASE_COMMANDS = (
    "dev-workflow-research",
    "dev-workflow-plan",
    "dev-workflow-implement",
    "dev-workflow-review",
)


def _command_md_path(name: str) -> Path:
    return REPO_ROOT / "commands" / name / "COMMAND.md"


class CommandBootstrapFilesTests(unittest.TestCase):
    def test_command_bootstrap_files_exist(self) -> None:
        """All four per-phase COMMAND.md bootstrap files must exist."""
        for name in PHASE_COMMANDS:
            path = _command_md_path(name)
            self.assertTrue(
                path.is_file(),
                f"Missing bootstrap COMMAND.md for {name}: expected at {path}",
            )

    def test_command_frontmatter_valid(self) -> None:
        """Each COMMAND.md must have valid frontmatter with name and description."""
        for name in PHASE_COMMANDS:
            path = _command_md_path(name)
            if not path.is_file():
                self.fail(f"COMMAND.md missing for {name}: {path}")
            content = path.read_text(encoding="utf-8")
            frontmatter, error = quick_validate.parse_frontmatter(content)
            self.assertIsNone(error, f"Invalid frontmatter in {path}: {error}")
            assert frontmatter is not None  # for type checkers
            self.assertEqual(
                frontmatter.get("name"),
                name,
                f"Frontmatter 'name' in {path} should be '{name}', "
                f"got {frontmatter.get('name')!r}",
            )
            description = str(frontmatter.get("description", "")).strip()
            self.assertTrue(
                description,
                f"Frontmatter 'description' in {path} must be non-empty",
            )

    def test_command_body_tool_neutral(self) -> None:
        """Shared COMMAND.md bodies must not contain tool-specific patterns."""
        for name in PHASE_COMMANDS:
            path = _command_md_path(name)
            if not path.is_file():
                self.fail(f"COMMAND.md missing for {name}: {path}")
            content = path.read_text(encoding="utf-8")
            body = quick_validate.body_after_frontmatter(content)
            for pattern in quick_validate.TOOL_NEUTRALITY_PATTERNS:
                match = pattern.search(body)
                self.assertIsNone(
                    match,
                    f"Tool-specific pattern {pattern.pattern!r} found in {path} body: "
                    f"{match.group(0) if match else ''}",
                )


ORCHESTRATOR_SKILL = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "SKILL.md"
DISPATCH_MODES_REF = (
    REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "dispatch-modes.md"
)

# Hard-coded round-1 copy destinations, per phase. The fixed incremental rule copies to
# `-r<N>` where N is the round just completed, so a literal `-r1` copy target is the
# dw-009-class data-loss defect. Match the copy-destination pattern, not the bare
# `-r1` token — the fixed incremental text legitimately contains `-r1`
# ("round 2 -> `-r1`").
HARDCODED_R1_COPY = re.compile(
    r"to `(?:11-research-review|21-plan-review|31-implementation-audit|"
    r"40-code-review)-r1\.md`"
)


class CommandConformanceTests(unittest.TestCase):
    """Conformance between the four /dev-workflow-<phase> commands and the
    dev-workflow-orchestrator skill they mirror (plan §7 pg-003, tests t-001..t-005)."""

    def _command_body(self, name: str) -> str:
        path = _command_md_path(name)
        if not path.is_file():
            self.fail(f"COMMAND.md missing for {name}: {path}")
        return quick_validate.body_after_frontmatter(
            path.read_text(encoding="utf-8")
    )

    def test_command_round_copy_rule_incremental(self) -> None:
        """t-001: each command's revise-route bullet uses the incremental
        `-r<N>` copy rule (N = round just completed) and carries all prior paths."""
        for name in PHASE_COMMANDS:
            body = self._command_body(name)
            self.assertIsNone(
                HARDCODED_R1_COPY.search(body),
                f"{name}: hard-coded `-r1` copy target found — use the incremental "
                "`-r<N>` rule (copy to `-r<N>` where N is the round just "
                "completed) and carry all prior `-r1`..`-r<N>` paths",
            )
            self.assertRegex(
                body,
                r"-r<N>\.md` where N is the round just completed",
                f"{name}: incremental `-r<N>` copy rule missing",
            )
            self.assertRegex(
                body,
                r"all prior `-r1`[^`\n]*`-r",
                f"{name}: carry-all-prior-paths instruction missing",
            )

    def test_orchestrator_packet_spec_all_prior_paths(self) -> None:
        """t-002: both dispatch-modes.md and the SKILL.md Dispatch-model summary
        express all-prior-paths (no singular `-r1`-only phrasing)."""
        for path in (DISPATCH_MODES_REF, ORCHESTRATOR_SKILL):
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                re.search(r"the `-r1` artifact path", text),
                f"{path}: singular `-r1`-only packet spec found",
            )
            self.assertIsNone(
                re.search(r"`-r1` review path for rounds > 1", text),
                f"{path}: singular `-r1`-only Dispatch-model phrasing found",
            )

    def test_command_conformance_caps_verdicts_ordering(self) -> None:
        """t-003: round caps, verdict sets, and checker-first round-1 ordering
        in the review command match the orchestrator's loop contracts."""
        review_body = self._command_body("dev-workflow-review")
        self.assertIn("Round cap is 5", review_body)
        self.assertRegex(review_body, r"checker runs\s+first")
        for name, cap in (
            ("dev-workflow-research", "Round cap is 5"),
            ("dev-workflow-plan", "Round cap is 3"),
            ("dev-workflow-implement", "Round cap is 3"),
        ):
            body = self._command_body(name)
            self.assertIn(cap, body, f"{name}: round cap missing")

    def test_dispatch_fallback_covers_hung_checker(self) -> None:
        """t-004: the dispatch fallback covers hung/no-verdict checkers,
        not just spawn failure."""
        text = DISPATCH_MODES_REF.read_text(encoding="utf-8")
        self.assertIn("Fallback on spawn failure", text)
        self.assertRegex(
            text,
            r"no verdict within the host's\s+bounded window",
            "dispatch-modes.md: hung/no-verdict checker fallback missing",
        )

    def test_commands_read_dispatch_log(self) -> None:
        """t-005: each command reads `## Dispatch log` before dispatching;
        bootstrap manifests record a dispatch mode."""
        for name in PHASE_COMMANDS:
            body = self._command_body(name)
            self.assertIn("## Dispatch log", body,
                          f"{name}: dispatch-log read missing")
            self.assertIn("Dispatch mode: delegated", body,
                          f"{name}: bootstrap dispatch-mode recording missing")


if __name__ == "__main__":
    unittest.main()
