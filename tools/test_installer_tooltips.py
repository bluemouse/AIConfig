#!/usr/bin/env python3
"""Tests for description loading used by installer GUI tooltips."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"
REPO_ROOT = TOOLS_DIR.parent


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_tooltips", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_tooltips"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()


def write_markdown(path: Path, *, description: str | None, body: str = "# Title\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if description is None:
        path.write_text(body, encoding="utf-8")
        return
    path.write_text(
        f"---\nname: example\ndescription: {description}\n---\n{body}",
        encoding="utf-8",
    )


class FrontmatterDescriptionTests(unittest.TestCase):
    def test_parse_frontmatter_valid(self) -> None:
        content = "---\nname: demo\ndescription: Demo skill\n---\n# Body\n"
        frontmatter = mod.parse_frontmatter(content)
        self.assertIsNotNone(frontmatter)
        assert frontmatter is not None
        self.assertEqual(frontmatter["name"], "demo")
        self.assertEqual(frontmatter["description"], "Demo skill")

    def test_parse_frontmatter_missing(self) -> None:
        self.assertIsNone(mod.parse_frontmatter("# No frontmatter\n"))

    def test_read_description_from_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            write_markdown(path, description="Install helper skill")
            self.assertEqual(
                mod.read_description_from_markdown(path),
                "Install helper skill",
            )

    def test_read_description_missing_file(self) -> None:
        self.assertIsNone(mod.read_description_from_markdown(Path("/tmp/does-not-exist.md")))

    def test_read_description_without_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent.md"
            write_markdown(path, description=None)
            self.assertIsNone(mod.read_description_from_markdown(path))

    def test_load_skill_descriptions_from_temp_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                write_markdown(
                    root / ".agents/skills/alpha" / "SKILL.md",
                    description="Alpha skill",
                )
                write_markdown(
                    root / ".agents/skills/beta" / "SKILL.md",
                    description="Beta skill",
                )
                descriptions = mod.load_skill_descriptions(["alpha", "beta", "missing"])
            finally:
                mod.REPO_ROOT = original_root

        self.assertEqual(descriptions, {"alpha": "Alpha skill", "beta": "Beta skill"})

    def test_load_agent_descriptions_from_temp_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                write_markdown(
                    root / ".claude/agents/runner.md",
                    description="Runs tasks",
                )
                descriptions = mod.load_agent_descriptions(["runner", "ghost"])
            finally:
                mod.REPO_ROOT = original_root

        self.assertEqual(descriptions, {"runner": "Runs tasks"})

    def test_load_git_guide_description_smoke(self) -> None:
        # Fixture-based (not real-repo): a REPO_ROOT-patched smoke test so it
        # does not depend on this checkout's installed state.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                write_markdown(
                    root / ".agents/skills/git-guide" / "SKILL.md",
                    description="Runs git operations",
                )
                descriptions = mod.load_skill_descriptions(["git-guide"])
            finally:
                mod.REPO_ROOT = original_root

        self.assertIn("git-guide", descriptions)
        self.assertTrue(descriptions["git-guide"])


class SelectionHelpFormatTests(unittest.TestCase):
    def test_format_selection_help_empty(self) -> None:
        text = mod.format_selection_help([], empty_message="No skills selected.")
        self.assertEqual(text, "No skills selected.")

    def test_format_selection_help_entries(self) -> None:
        text = mod.format_selection_help(
            [
                ("alpha", "First description."),
                ("beta", ""),
            ],
            empty_message="No skills selected.",
        )
        self.assertIn("alpha\n=====\nFirst description.", text)
        self.assertIn("beta\n====\n(No description available.)", text)
        self.assertIn("\n\n", text)


class BundleHelpEntriesTests(unittest.TestCase):
    def _bundle(self, bundle_id: str, name: str, skills: frozenset[str]) -> mod.SkillBundle:
        return mod.SkillBundle(
            id=bundle_id,
            name=name,
            description=f"{name} description",
            skills=skills,
        )

    def test_all_members_selected(self) -> None:
        bundles = [self._bundle("core", "Core bundle", frozenset({"a", "b"}))]
        entries = mod.bundle_help_entries(
            bundles,
            present_members=lambda bundle: sorted(bundle.skills),
            is_selected=lambda _name: True,
        )
        self.assertEqual(entries, [("Core bundle", "Core bundle description")])

    def test_partial_selection(self) -> None:
        bundles = [self._bundle("extended", "Extended bundle", frozenset({"a", "b"}))]
        entries = mod.bundle_help_entries(
            bundles,
            present_members=lambda bundle: sorted(bundle.skills),
            is_selected=lambda name: name == "a",
        )
        self.assertEqual(entries, [("Extended bundle (partial)", "Extended bundle description")])

    def test_no_members_selected(self) -> None:
        bundles = [self._bundle("core", "Core bundle", frozenset({"a", "b"}))]
        entries = mod.bundle_help_entries(
            bundles,
            present_members=lambda bundle: sorted(bundle.skills),
            is_selected=lambda _name: False,
        )
        self.assertEqual(entries, [])

    def test_mixed_bundle_states(self) -> None:
        bundles = [
            self._bundle("core", "Core bundle", frozenset({"a", "b"})),
            self._bundle("extended", "Extended bundle", frozenset({"c", "d"})),
        ]
        entries = mod.bundle_help_entries(
            bundles,
            present_members=lambda bundle: sorted(bundle.skills),
            is_selected=lambda name: name in {"a", "b", "c"},
        )
        self.assertEqual(
            entries,
            [
                ("Core bundle", "Core bundle description"),
                ("Extended bundle (partial)", "Extended bundle description"),
            ],
        )


class ParseFrontmatterEmbeddedDelimTests(unittest.TestCase):
    """t-003: an embedded `---` line must not silently truncate frontmatter.

    Sub-case (a) must-not-regress: an indented block-scalar value containing
    an indented `---` line parses correctly today and must keep doing so.
    Sub-case (b) red: a column-0 line beginning with `---` inside the value
    silently truncates the parsed description at HEAD; after the fix the
    equality scan finds the true closing delimiter and yaml.safe_load
    rejects the malformed marker per the None-on-error semantics — the
    correct deterministic outcome is None, not a silently-truncated dict.
    """

    def test_indented_block_scalar_embedded_delim_parses(self) -> None:
        content = (
            "---\n"
            "name: my-skill\n"
            "description: >-\n"
            "  line one\n"
            "  ---\n"
            "  line two\n"
            "---\n"
            "body\n"
        )
        parsed = mod.parse_frontmatter(content)
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed["name"], "my-skill")
        self.assertEqual(parsed["description"], "line one --- line two")

    def test_column_zero_delim_line_yields_none_not_truncation(self) -> None:
        # `--- ` at column 0 ends the YAML block scalar; the value becomes
        # invalid YAML from that point — explicit None beats silent
        # truncation. Same for a `----` line.
        for marker in ("--- ", "----"):
            with self.subTest(marker=marker):
                content = (
                    "---\n"
                    "name: my-skill\n"
                    "description: >-\n"
                    "  line one\n"
                    f"{marker}\n"
                    "  line two\n"
                    "---\n"
                    "body\n"
                )
                self.assertIsNone(mod.parse_frontmatter(content))


if __name__ == "__main__":
    unittest.main()
