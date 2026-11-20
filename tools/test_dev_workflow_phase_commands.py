#!/usr/bin/env python3
"""Tests for the per-phase dev-workflow command bootstrap sources.

Validates that the four per-phase commands (`/research`, `/plan`,
`/implement`, `/review`) exist as bootstrap sources under
`commands/<phase>/COMMAND.md`, have valid frontmatter, and contain no
tool-specific content in the shared body.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_CREATOR_SCRIPTS = REPO_ROOT / "skills" / "command-creator" / "scripts"

# Load quick_validate as a module (it lives outside the tools/ package),
# stashing and restoring sys.modules["quick_validate"] so sibling test suites
# loading skill-creator/agent-creator quick_validate are unaffected.
_QUICK_VALIDATE_MISSING = object()
_prior_quick_validate = sys.modules.get("quick_validate", _QUICK_VALIDATE_MISSING)
_spec = importlib.util.spec_from_file_location(
    "quick_validate", COMMAND_CREATOR_SCRIPTS / "quick_validate.py"
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"Could not load quick_validate from {COMMAND_CREATOR_SCRIPTS}")
quick_validate = importlib.util.module_from_spec(_spec)
sys.modules["quick_validate"] = quick_validate
try:
    _spec.loader.exec_module(quick_validate)
finally:
    if _prior_quick_validate is _QUICK_VALIDATE_MISSING:
        sys.modules.pop("quick_validate", None)
    else:
        sys.modules["quick_validate"] = _prior_quick_validate  # type: ignore[assignment]


PHASE_COMMANDS = (
    "research",
    "plan",
    "implement",
    "review",
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
    """Conformance between the four per-phase commands and the
    dev-workflow-orchestrator skill they mirror (plan §7 pg-003, tests t-001..t-005)."""

    def _command_body(self, name: str) -> str:
        path = _command_md_path(name)
        if not path.is_file():
            self.fail(f"COMMAND.md missing for {name}: {path}")
        return quick_validate.body_after_frontmatter(
            path.read_text(encoding="utf-8")
    )

    def test_command_round_copy_rule_incremental(self) -> None:
        """t-001: the incremental `-r<N>` copy rule (N = round just completed,
        carry all prior paths) lives in the orchestrator's loop procedure; the
        per-phase commands delegate loop mechanics to it and must not
        re-encode a stale copy rule."""
        orch = ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        self.assertIsNone(
            HARDCODED_R1_COPY.search(orch),
            "orchestrator: hard-coded `-r1` copy target found — use the incremental "
            "`-r<N>` rule (copy to `-r<N>` where N is the round just "
            "completed) and carry all prior `-r1`..`-r<N>` paths",
        )
        self.assertRegex(
            orch,
            r"-r<N>\.md` \(N = round just completed",
            "orchestrator: incremental `-r<N>` copy rule missing",
        )
        self.assertRegex(
            orch,
            r"all `-r<N>` paths|all `-r1`[^`\n]*`-r",
            "orchestrator: carry-all-prior-paths instruction missing",
        )
        for name in PHASE_COMMANDS:
            body = self._command_body(name)
            self.assertIsNone(
                HARDCODED_R1_COPY.search(body),
                f"{name}: command re-encodes a stale `-r1` copy rule — loop "
                "mechanics belong to the orchestrator",
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
        """t-003: round caps are stated once in the orchestrator's loop
        procedure; the review command's delta table carries the checker-first
        round-1 ordering."""
        orch = ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        self.assertIn(
            "round caps: research 5, plan 3, implement 3, code review 5",
            orch,
            "orchestrator: per-phase round caps missing",
        )
        review_body = self._command_body("review")
        self.assertIn("Round cap | 5", review_body)
        self.assertIn("Round 1: checker first", review_body)
        for name, cap in (
            ("research", "Round cap | 5"),
            ("plan", "Round cap | 3"),
            ("implement", "Round cap | 3"),
        ):
            body = self._command_body(name)
            self.assertIn(cap, body, f"{name}: delta-table round cap missing")

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
        """t-005: each command's bootstrap manifest rule records a dispatch
        mode selected by host capability detection rather than pinned to
        delegated, and the checker dispatch reads `## Dispatch log`."""
        for name in PHASE_COMMANDS:
            body = self._command_body(name)
            # "Dispatch mode: native" may wrap across lines in the body;
            # assert the wording without the exact wrap point.
            self.assertRegex(
                body,
                r"Dispatch mode:\s*native",
                f"{name}: native dispatch-mode recording missing",
            )
            self.assertRegex(
                body,
                r"default to\s+delegated",
                f"{name}: delegated dispatch-mode fallback recording missing",
            )
            self.assertIsNone(
                re.search(r"unknown at bootstrap time", body),
                f"{name}: outdated pinned-delegated bootstrap rationale found",
            )
        # The checker-pass dispatch-log read lives in the orchestrator's loop
        # procedure, which every phase command loads in step 1.
        orch = ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
        self.assertIn("## Dispatch log", orch,
                      "orchestrator: dispatch-log read missing")

    def test_commands_bootstrap_manifest_sections_explicit(self) -> None:
        """cr-014: all 4 PHASE_COMMANDS explicitly name the required manifest
        headings (`# Run Manifest`, `## Run metadata`, `## Phase status`,
        `## Artifact registry`) in their bootstrap rules."""
        required_headings = (
            "# Run Manifest",
            "## Run metadata",
            "## Phase status",
            "## Artifact registry",
        )
        for name in PHASE_COMMANDS:
            body = self._command_body(name)
            for heading in required_headings:
                self.assertIn(
                    heading,
                    body,
                    f"{name}: bootstrap manifest rule missing required heading {heading!r}",
                )

    def test_review_bootstrap_clean_tree_and_files_changed_sections(self) -> None:
        """cr-014: `/review` bootstrap checks `git status --porcelain` (not
        `if `git diff --stat``) and synthesizes `## Files changed`."""
        review_body = self._command_body("review")
        self.assertIn(
            "git status --porcelain",
            review_body,
            "review: bootstrap must check working tree via `git status --porcelain`",
        )
        self.assertNotIn(
            "if `git diff --stat`",
            review_body,
            "review: stale `if `git diff --stat`` clean-tree check must not appear",
        )
        self.assertIn(
            "## Files changed",
            review_body,
            "review: synthesized 30-implementation-report.md must include `## Files changed`",
        )


if __name__ == "__main__":
    unittest.main()
