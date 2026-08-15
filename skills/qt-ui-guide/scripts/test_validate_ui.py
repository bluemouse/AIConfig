#!/usr/bin/env python3
"""Fixture tests for validate_ui.py."""

from __future__ import annotations

import unittest
from pathlib import Path

from validate_ui import validate

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ValidateUiTests(unittest.TestCase):
    def test_valid_minimal_passes(self) -> None:
        errors, warnings = validate(FIXTURES / "valid-minimal.ui")
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_missing_top_level_layout_fails(self) -> None:
        errors, _warnings = validate(FIXTURES / "missing-layout.ui")
        self.assertTrue(any("no top-level layout" in message for message in errors))

    def test_duplicate_object_name_fails(self) -> None:
        errors, _warnings = validate(FIXTURES / "duplicate-name.ui")
        self.assertTrue(any("Duplicate object name" in message for message in errors))

    def test_generic_designer_name_warns(self) -> None:
        errors, warnings = validate(FIXTURES / "generic-name.ui")
        self.assertEqual(errors, [])
        self.assertTrue(any("Generic Designer object name" in message for message in warnings))

    def test_bundled_dialog_template_passes(self) -> None:
        template = Path(__file__).resolve().parents[1] / "assets" / "dialog-template.ui"
        errors, warnings = validate(template)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
