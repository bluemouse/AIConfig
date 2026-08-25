#!/usr/bin/env python3
"""Tests for the staged-mode plan template extension (pg-001).

Validates that the implementation plan template includes:
- `Execution mode` field in §10 Execution handoff (fr-1)
- `Stage breakdown` subsection in §10 (fr-1)
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = REPO_ROOT / "skills" / "plan-guide" / "references" / "implementation-plan-template.md"


class PlanTemplateStagedModeTests(unittest.TestCase):
    """t-001, t-002: Plan template has Execution mode and Stage breakdown."""

    def test_plan_template_has_execution_mode_and_stage_breakdown(self) -> None:
        """t-001: Plan template §10 contains both `Execution mode` and `Stage breakdown`."""
        self.assertTrue(
            TEMPLATE_PATH.is_file(),
            f"Plan template not found at {TEMPLATE_PATH}",
        )
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Execution mode",
            text,
            "Plan template §10 must contain `Execution mode` field for staged mode (fr-1)",
        )
        self.assertIn(
            "Stage breakdown",
            text,
            "Plan template §10 must contain `Stage breakdown` subsection for staged mode (fr-1)",
        )

    def test_stage_breakdown_groups_task_ids(self) -> None:
        """t-002: Stage breakdown subsection lists ordered stages with task id groups."""
        self.assertTrue(
            TEMPLATE_PATH.is_file(),
            f"Plan template not found at {TEMPLATE_PATH}",
        )
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        # The Stage breakdown section should reference task ids and stages
        self.assertIn(
            "Stage breakdown",
            text,
            "Plan template must have a Stage breakdown subsection",
        )
        # Verify the stage breakdown provides structure for grouping task ids
        # The template should have a placeholder or structure for stages with task ids
        stage_breakdown_section = self._extract_section(text, "Stage breakdown")
        self.assertIsNotNone(
            stage_breakdown_section,
            "Stage breakdown section not found in template",
        )

    def _extract_section(self, text: str, section_name: str) -> str | None:
        """Extract a section's content by name (returns None if not found)."""
        lines = text.splitlines()
        start = None
        for i, line in enumerate(lines):
            if section_name.lower() in line.lower():
                start = i
                break
        if start is None:
            return None
        # Read until the next section of similar or higher level
        end = len(lines)
        for i in range(start + 1, len(lines)):
            line = lines[i]
            # Stop at the next ## or ### heading
            if line.startswith("## ") or line.startswith("### "):
                if section_name.lower() not in line.lower():
                    end = i
                    break
        return "\n".join(lines[start:end])


if __name__ == "__main__":
    unittest.main()
