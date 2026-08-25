#!/usr/bin/env python3
"""Tests for staged-mode manifest extension (pg-005).

Validates:
- t-005: manifest template has `Run mode` field
- t-005b: manifest template has `## Stage status` section
"""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "skills" / "dev-workflow-orchestrator" / "references" / "manifest-format.md"


class StagedManifestTests(unittest.TestCase):
    """t-005, t-005b: Manifest has Run mode and Stage status."""

    def test_manifest_has_run_mode_field(self) -> None:
        """t-005: manifest template has `Run mode: linear | staged` field."""
        self.assertTrue(MANIFEST_PATH.is_file(), f"Manifest template not found at {MANIFEST_PATH}")
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Run mode",
            text,
            "Manifest template must have a `Run mode` field for staged mode",
        )

    def test_manifest_has_stage_status_section(self) -> None:
        """t-005b: manifest has `## Stage status` section in staged mode."""
        self.assertTrue(MANIFEST_PATH.is_file(), f"Manifest template not found at {MANIFEST_PATH}")
        text = MANIFEST_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Stage status",
            text,
            "Manifest template must have a `## Stage status` section for staged mode",
        )


if __name__ == "__main__":
    unittest.main()
