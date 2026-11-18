#!/usr/bin/env python3
"""Tests for the ar-013 root-cause-phase per-finding validation (review round fix cr-002).

Regression cases for the block-boundary defect: a finding-definition block
previously ended at the next occurrence *of the same finding id*, so a
missing field in an earlier finding was masked by a later finding's field.
Blocks now end at the next finding-id occurrence of any form, and only
heading/list-item ids count as finding definitions — summary-table and
prior-round disposition rows mention ids without defining findings.

Run from the repository root: python tools/test_root_cause_phase_validation.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "dev-workflow"))

from checks import loop_checks  # type: ignore[import-not-found]


def _run_check(text: str, phase: str, checker_file: str) -> list[str]:
    """Run check_root_cause_phase_present on a synthetic checker artifact."""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_dir = Path(tmpdir)
        (run_dir / checker_file).write_text(text, encoding="utf-8")
        return [
            f.message
            for f in loop_checks.check_root_cause_phase_present(run_dir, phase)
        ]


class RootCauseBlockBoundaryTests(unittest.TestCase):
    """cr-002: block ends at the next finding id of any form."""

    def test_missing_field_not_masked_by_later_finding(self) -> None:
        """The original false negative: rr-001 lacks the field, rr-002 has
        it — the old same-id block split let rr-001's block run to EOF and
        inherit rr-002's field."""
        text = (
            "### rr-001: missing field\n"
            "- severity: blocker\n"
            "### rr-002: has field\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertTrue(
            any("rr-001" in m and "no 'root-cause-phase'" in m for m in messages),
            f"rr-001's missing field must be flagged: {messages}",
        )
        self.assertFalse(
            any("rr-002" in m for m in messages),
            f"rr-002 has the field and must not be flagged: {messages}",
        )

    def test_template_conformant_artifact_passes(self) -> None:
        """Summary-table row + detail block, both carrying the field — the
        shapes the checker report templates actually produce."""
        text = (
            "## 3. Top findings\n"
            "| id | severity | affected section | issue | required fix |\n"
            "|----|----------|------------------|-------|--------------|\n"
            "| rr-001 | blocker | §4 | gap | fix |\n"
            "\n"
            "#### rr-001: evidence gap\n"
            "- severity: blocker\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertEqual(messages, [], f"conformant artifact must pass: {messages}")

    def test_midline_cross_reference_does_not_create_finding(self) -> None:
        """A cross-reference inside a block ("duplicates cr-002's gap") is a
        mention, not a definition or a block split."""
        text = (
            "#### rr-001: gap\n"
            "- root-cause-phase: local\n"
            "- duplicates cr-002's guard gap (see also rr-003)\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertEqual(messages, [], f"cross-references must not be flagged: {messages}")

    def test_disposition_table_rows_are_not_findings(self) -> None:
        """Prior-round disposition rows mention ids without re-defining
        findings — they carry no root-cause column and must not be
        presence-checked."""
        text = (
            "## 8. Prior-round dispositions\n"
            "| prior finding | disposition | evidence |\n"
            "|---------------|-------------|----------|\n"
            "| rr-001 | resolved | evidence |\n"
            "\n"
            "## 3. Top findings\n"
            "| rr-002 | blocker | x | y | z |\n"
            "\n"
            "#### rr-002: new\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertEqual(
            messages,
            [],
            f"disposition rows must not be presence-checked: {messages}",
        )

    def test_implement_phase_id_prefix(self) -> None:
        """ia-NNN ids in the implement phase resolve against the implement
        checker artifact."""
        text = (
            "#### ia-001: defect\n"
            "- root-cause-phase: plan\n"
        )
        messages = _run_check(text, "implement", "31-implementation-audit.md")
        self.assertEqual(messages, [], f"valid plan value must pass: {messages}")


class RootCauseValueVocabularyTests(unittest.TestCase):
    """The value check applies to every field occurrence in the artifact."""

    def test_upstream_value_rejected(self) -> None:
        """`upstream` is command-prose routing shorthand, not a field value;
        a checker that emits it must fail validation (vocabulary pin)."""
        text = (
            "#### rr-001: x\n"
            "- root-cause-phase: upstream\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertTrue(
            any("'upstream'" in m and "vocabulary" in m for m in messages),
            f"'upstream' must be rejected as a field value: {messages}",
        )

    def test_clarify_value_accepted_in_research_phase(self) -> None:
        text = (
            "#### rr-001: x\n"
            "- root-cause-phase: clarify\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertEqual(messages, [], f"'clarify' must be accepted: {messages}")

    def test_value_check_covers_table_occurrences(self) -> None:
        """The code-reviewer summary table carries a root-cause-phase column;
        an invalid value there must be flagged even when the detail block is
        valid."""
        text = (
            "## 4. Findings\n"
            "| id | severity | root-cause-phase |\n"
            "|----|----------|------------------|\n"
            "| cr-001 | blocker | plan |\n"
            "\n"
            "#### cr-001: y\n"
            "- root-cause-phase: local\n"
        )
        # 'plan' is valid vocabulary — use an invalid value to prove tables are checked
        text_invalid = text.replace("| cr-001 | blocker | plan |", "| cr-001 | blocker | upstream |")
        messages = _run_check(text_invalid, "code-review", "40-code-review.md")
        self.assertTrue(
            any("'upstream'" in m and "vocabulary" in m for m in messages),
            f"table-cell values must be vocabulary-checked: {messages}",
        )

    def test_full_template_conformant_artifact_is_clean(self) -> None:
        """cr-008 regression: a complete template-conformant code-review
        artifact — summary table with a markdown separator row, detail
        blocks, and a later unrelated table — must produce zero findings.
        The unbounded table scan and the separator-row check previously
        flagged exactly this shape."""
        text = (
            "# Code Review Report\n"
            "\n"
            "## 2. Automated checks (when run)\n"
            "\n"
            "| Command | Purpose | Result | Notes |\n"
            "|---------|---------|--------|-------|\n"
            "| `python -m unittest` | tests | pass | 27 OK |\n"
            "\n"
            "## 4. Findings\n"
            "\n"
            "| id | severity | scope | location | issue | root-cause-phase | recommended route |\n"
            "|----|----------|-------|----------|-------|------------------|-------------------|\n"
            "| cr-001 | blocker | correctness | src/x.py:1 | y | local | direct edit |\n"
            "\n"
            "### Finding details\n"
            "\n"
            "#### cr-001: y\n"
            "- Severity: blocker\n"
            "- root-cause-phase: local\n"
            "\n"
            "## 5. Open questions or assumptions\n"
            "\n"
            "- none\n"
        )
        messages = _run_check(text, "code-review", "40-code-review.md")
        self.assertEqual(
            messages,
            [],
            f"a fully conformant artifact must produce zero findings: {messages}",
        )

    def test_unrelated_table_after_root_cause_table_not_checked(self) -> None:
        """cr-008 regression: the table scan must stop at the root-cause
        table's end — a later, unrelated table (fewer columns, arbitrary
        cell content) must never be validated against the root-cause
        column index."""
        text = (
            "## 4. Findings\n"
            "| id | root-cause-phase |\n"
            "|----|------------------|\n"
            "| cr-001 | local |\n"
            "\n"
            "#### cr-001: y\n"
            "- root-cause-phase: local\n"
            "\n"
            "## 2. Automated checks\n"
            "| Command | Result | Notes |\n"
            "|---------|--------|-------|\n"
            "| `python -m unittest` | pass | 27 OK, all green, everything validated |\n"
        )
        messages = _run_check(text, "code-review", "40-code-review.md")
        self.assertEqual(
            messages,
            [],
            f"unrelated later tables must not be scanned: {messages}",
        )

    def test_template_placeholder_row_renders_clean(self) -> None:
        """cr-015 regression: the code-reviewer template's summary-table
        example row lists the allowed values as a slash-separated
        placeholder. A checker rendering the template verbatim (the verdict
        extractor tolerates exactly this via strip_placeholder_options)
        must not be flagged; a real single-value cell is still checked."""
        text = (
            "## 4. Findings\n"
            "| id | severity | scope | location | issue | root-cause-phase | recommended route |\n"
            "|----|----------|-------|----------|-------|------------------|-------------------|\n"
            "| cr-001 | blocker | design | x:1 | y | local/research/clarify/plan/implement/code-review | direct edit |\n"
            "\n"
            "#### cr-001: y\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text, "code-review", "40-code-review.md")
        self.assertEqual(
            messages,
            [],
            f"a verbatim template placeholder row must be clean: {messages}",
        )
        text_invalid = text.replace(
            "| local/research/clarify/plan/implement/code-review |", "| upstream |"
        )
        messages = _run_check(text_invalid, "code-review", "40-code-review.md")
        self.assertTrue(
            any("'upstream'" in m and "vocabulary" in m for m in messages),
            f"single-value cells must still be vocabulary-checked: {messages}",
        )

    def test_blank_line_gap_ends_table_scan(self) -> None:
        """cr-014 regression: markdown ends a table at a blank line. A
        blank-line-separated table after a root-cause table must never be
        validated against the root-cause column index — including the
        realistic re-review shape of a findings table followed by a
        prior-round disposition table."""
        # Shape 1: unrelated Automated-checks-style table
        text_unrelated = (
            "## 4. Findings\n"
            "| id | root-cause-phase |\n"
            "|----|------------------|\n"
            "| cr-001 | local |\n"
            "\n"
            "| Command | Result | Notes |\n"
            "|---------|--------|-------|\n"
            "| `python -m unittest` | pass | 27 OK |\n"
            "\n"
            "#### cr-001: y\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text_unrelated, "code-review", "40-code-review.md")
        self.assertEqual(
            messages,
            [],
            f"blank-line-separated unrelated tables must not be scanned: {messages}",
        )

        # Shape 2: findings table + prior-round disposition table, adjacent
        text_disposition = (
            "## 3. Top findings\n"
            "| id | severity | root-cause-phase |\n"
            "|----|----------|------------------|\n"
            "| rr-001 | blocker | local |\n"
            "\n"
            "| prior finding | disposition | evidence in updated report |\n"
            "|---------------|-------------|---------------------------|\n"
            "| rr-001 | resolved | §2 rewritten |\n"
            "\n"
            "#### rr-001: gap\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text_disposition, "research", "11-research-review.md")
        self.assertEqual(
            messages,
            [],
            f"adjacent disposition tables must not be scanned: {messages}",
        )

    def test_second_root_cause_table_checked_independently(self) -> None:
        """A disposition table that itself carries a root-cause-phase column
        is still checked — table scanning stops at gaps but each header
        with the column starts a new scan."""
        text = (
            "## 4. Findings\n"
            "| id | root-cause-phase |\n"
            "|----|------------------|\n"
            "| cr-001 | local |\n"
            "\n"
            "#### cr-001: y\n"
            "- root-cause-phase: local\n"
            "\n"
            "## 9. Dispositions\n"
            "| id | root-cause-phase |\n"
            "|----|------------------|\n"
            "| cr-002 | upstream |\n"
        )
        messages = _run_check(text, "code-review", "40-code-review.md")
        self.assertTrue(
            any("'upstream'" in m and "vocabulary" in m for m in messages),
            f"a second table's invalid value must still be flagged: {messages}",
        )

    def test_line_initial_reference_bullet_not_a_definition(self) -> None:
        """cr-013: a line-initial cross-reference bullet ("- Resolve
        rr-001 first") is a mention, not a finding definition — it must not
        demand a root-cause-phase field in its block."""
        text = (
            "## Recommended next actions\n"
            "- Resolve rr-001 first (it blocks the rest)\n"
            "\n"
            "#### rr-001: evidence gap\n"
            "- root-cause-phase: local\n"
        )
        messages = _run_check(text, "research", "11-research-review.md")
        self.assertEqual(
            messages,
            [],
            f"reference bullets must not be presence-checked: {messages}",
        )


if __name__ == "__main__":
    unittest.main()
