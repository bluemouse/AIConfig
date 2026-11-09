#!/usr/bin/env python3
"""Tests for the guidelines member kind in installer.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_guidelines", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_guidelines"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()

REPO_ROOT = TOOLS_DIR.parent


class RepoGuidelineLayoutTests(unittest.TestCase):
    """The behavioral guideline lives in guidelines/ at the repo root."""

    def test_repo_guideline_lives_in_guidelines_folder(self) -> None:
        for name in (
            "coding-behavior-guidelines",
            "response-guidelines",
            "code-comment-guidelines",
        ):
            self.assertTrue(
                (REPO_ROOT / "guidelines" / f"{name}.md").is_file(),
                f"Guideline must live at guidelines/{name}.md",
            )
        self.assertFalse(
            (REPO_ROOT / "coding-behavior-guidelines.md").exists(),
            "Guideline must no longer sit at the repo root",
        )

    def test_verdict_first_skill_machinery_removed(self) -> None:
        """fr-2: the converted skill's machinery is fully gone (t-106)."""
        for rel in (
            "skills/verdict-first",
            ".ai/skills/verdict-first",
            ".cursor/skills/verdict-first",
            ".claude/skills/verdict-first",
            ".github/skills/verdict-first",
            ".cursor/rules/verdict-first.mdc",
        ):
            self.assertFalse(
                (REPO_ROOT / rel).exists(),
                f"{rel} must not exist after the guideline conversion",
            )


def write_source_guideline(root: Path, name: str, text: str = "# Guideline\n") -> None:
    """Write a minimal guideline source file under <root>/guidelines/."""
    path = root / "guidelines" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class GuidelineMemberKindTests(unittest.TestCase):
    """The guidelines member kind: discovery, install, and selection."""

    def test_install_guideline_places_file_in_ai_guidelines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_guideline(source, "coding-behavior-guidelines", "# Be careful\n")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["coding-behavior-guidelines"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            installed = target / ".ai" / "guidelines" / "coding-behavior-guidelines.md"
            self.assertTrue(installed.is_file())
            self.assertEqual(installed.read_text(encoding="utf-8"), "# Be careful\n")

    def test_default_selection_excludes_guidelines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                write_source_guideline(root, "coding-behavior-guidelines")
                selection = mod.resolve_cli_selection(
                    bundle_ids=None,
                    skill_names=None,
                    agent_names=None,
                    command_names=None,
                    script_names=None,
                    guideline_names=None,
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(selection.guidelines, [])

    def test_cli_guidelines_flag_installs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_guideline(source, "coding-behavior-guidelines", "# Be careful\n")
            # A discoverable skill in the source: proves --guidelines-only does
            # not leak into the no-selector default (cr-004).
            for rel in (
                ".ai/skills/leak-skill/SKILL.md",
                ".cursor/skills/leak-skill/SKILL.md",
            ):
                path = source / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "---\nname: leak-skill\ndescription: leak probe\n---\n",
                    encoding="utf-8",
                )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli(
                    [str(target), "--guidelines", "coding-behavior-guidelines"]
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            installed = target / ".ai" / "guidelines" / "coding-behavior-guidelines.md"
            self.assertTrue(installed.is_file())
            self.assertFalse(
                (target / ".ai" / "skills" / "leak-skill").exists(),
                "--guidelines-only must not trigger the default skill install",
            )

    def test_discover_guidelines_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            try:
                write_source_guideline(root, "coding-behavior-guidelines")
                write_source_guideline(root, "response-guidelines")
                write_source_guideline(root, "code-comment-guidelines")
                write_source_guideline(root, "not-allowlisted")
                discovered = mod.discover_guidelines()
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(
                discovered,
                [
                    "code-comment-guidelines",
                    "coding-behavior-guidelines",
                    "response-guidelines",
                ],
            )

    def test_install_response_guideline_places_file(self) -> None:
        """fr-3: response-guidelines installs from the real repo (t-105).

        Installs from the REAL REPO_ROOT — the missing source file is the red
        signal (a temp-source fixture would be vacuous: install_items never
        consults the allowlist).
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)

            result = mod.install_items(
                source_root=REPO_ROOT,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["response-guidelines"],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            installed = target / ".ai" / "guidelines" / "response-guidelines.md"
            self.assertTrue(installed.is_file())
            self.assertIn("# Verdict First", installed.read_text(encoding="utf-8"))


class GuidelineCitationDescriptionParsingTests(unittest.TestCase):
    """The frontmatter description parser feeding citation lines (pg-001).

    A guideline's load-trigger description lives in its YAML frontmatter
    (`description:` key); the parser must never raise — every unreadable
    shape degrades to None so the citation falls back to the bare wording.
    """

    def test_parser_returns_description_from_frontmatter(self) -> None:
        """t-101: frontmatter'd source yields the stripped description."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# LLM Coding Behavioral Guidelines\n",
            )

            description = mod.parse_guideline_citation_description(
                source, "coding-behavior-guidelines"
            )

            self.assertEqual(description, "Load before writing or editing code.")

    def test_parser_returns_none_without_frontmatter(self) -> None:
        """t-102: a plain markdown file has no description."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            write_source_guideline(source, "coding-behavior-guidelines")

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_parser_returns_none_on_malformed_yaml(self) -> None:
        """t-103: malformed frontmatter degrades to None, never raises."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: [unclosed\n"
                "---\n"
                "# Guideline\n",
            )

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_parser_returns_none_on_unclosed_frontmatter(self) -> None:
        """pr-005: an opening --- with no closing delimiter yields None."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\ndescription: never closed\n# Guideline\n",
            )

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_parser_returns_none_on_missing_or_empty_description(self) -> None:
        """t-104: a frontmatter block without a usable description yields None."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\nname: something\n---\n# Guideline\n",
            )
            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\ndescription: \"\"\n---\n# Guideline\n",
            )
            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\ndescription:\n  - multi\n  - line\n---\n# Guideline\n",
            )
            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_parser_returns_none_for_missing_file(self) -> None:
        """t-105: a guideline that does not exist yields None."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_parser_returns_none_for_multiline_description(self) -> None:
        """cr-001/cr2-001: a line-break-bearing description (any Unicode line
        break, e.g. \\u2028) would corrupt the citation line (and make it
        unremovable) — degrade to None instead."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: |\n"
                "  first line\n"
                "  second line\n"
                "---\n"
                "# Guideline\n",
            )

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

            # Unicode line separator: splitlines() treats it as a break even
            # though it contains no \n or \r.
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: \"line one\\u2028line two\"\n"
                "---\n"
                "# Guideline\n",
            )

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_parser_returns_none_for_unreadable_file(self) -> None:
        """cr-002: an unreadable or non-UTF-8 file degrades to None, no raise."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            (source / "guidelines").mkdir(parents=True)
            path = source / "guidelines" / "coding-behavior-guidelines.md"
            path.write_bytes(
                b"---\ndescription: \xff\xfe broken utf-8\n---\n# Guideline\n"
            )

            self.assertIsNone(
                mod.parse_guideline_citation_description(
                    source, "coding-behavior-guidelines"
                )
            )

    def test_real_repo_guidelines_carry_descriptions(self) -> None:
        """t-211: every installable guideline ships a frontmatter description."""
        for name in mod.INSTALLABLE_GUIDELINES:
            description = mod.parse_guideline_citation_description(
                REPO_ROOT, name
            )
            self.assertTrue(
                description,
                f"guidelines/{name}.md must carry a non-empty 'description:' "
                "frontmatter value",
            )


class AgentsMdIntegrationTests(unittest.TestCase):
    """The consent-gated AGENTS.md citation insert/remove machinery.

    Citations land under a '## AI guidelines' section — created at the end of
    the file when missing — and uninstall drops the section again once the
    installer-written citations inside it are gone.
    """

    def test_citation_line_format(self) -> None:
        line = mod.build_guideline_citation_line("coding-behavior-guidelines")
        self.assertEqual(
            line,
            "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
            "(.ai/guidelines/coding-behavior-guidelines.md) "
            "in this repo.",
        )

    def test_citation_line_with_description(self) -> None:
        """t-201: a described citation uses the em-dash form (fr-2)."""
        line = mod.build_guideline_citation_line(
            "coding-behavior-guidelines",
            "Load before writing or editing code.",
        )
        self.assertEqual(
            line,
            "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
            "(.ai/guidelines/coding-behavior-guidelines.md) "
            "— Load before writing or editing code.",
        )

    def test_citation_line_empty_description_falls_back_to_bare(self) -> None:
        """t-202: None/empty descriptions keep the bare wording (fr-3)."""
        for description in (None, ""):
            self.assertEqual(
                mod.build_guideline_citation_line(
                    "coding-behavior-guidelines", description
                ),
                mod.build_guideline_citation_line("coding-behavior-guidelines"),
            )

    def test_citation_variants_include_described_form(self) -> None:
        """t-203: removal matches described, bare, and legacy wordings (fr-5)."""
        variants = mod.guideline_citation_variants(
            "coding-behavior-guidelines",
            "Load before writing or editing code.",
        )
        self.assertEqual(
            variants,
            {
                mod.build_guideline_citation_line(
                    "coding-behavior-guidelines",
                    "Load before writing or editing code.",
                ),
                mod.build_guideline_citation_line("coding-behavior-guidelines"),
                mod._legacy_guideline_citation_line("coding-behavior-guidelines"),
            },
        )

    def test_append_writes_described_line_for_frontmatter_source(self) -> None:
        """t-204: append surfaces the frontmatter description (fr-2, fr-4)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            self.assertEqual(already, [])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n"
                "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
                "(.ai/guidelines/coding-behavior-guidelines.md)"
                " — Load before writing or editing code.\n",
            )

    def test_append_bare_line_for_frontmatterless_source(self) -> None:
        """t-205 (described-path twin): no frontmatter → bare wording (fr-3)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(source, "coding-behavior-guidelines")
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n"
                + mod.build_guideline_citation_line("coding-behavior-guidelines")
                + "\n",
            )

    def test_remove_drops_installer_written_described_line(self) -> None:
        """t-206: uninstall removes the described wording (fr-5)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            described = mod.build_guideline_citation_line(
                "coding-behavior-guidelines",
                "Load before writing or editing code.",
            )
            (target / "AGENTS.md").write_text(
                f"# Project\n\n{described}\nTail.\n", encoding="utf-8"
            )

            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(kept, [])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\nTail.\n",
            )

    def test_remove_keeps_user_edited_described_line(self) -> None:
        """t-207: a hand-reworded description is user content, kept (fr-6)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            edited = mod.build_guideline_citation_line(
                "coding-behavior-guidelines",
                "Load before writing or editing code. (edited by user)",
            )
            (target / "AGENTS.md").write_text(
                f"# Project\n\n{edited}\nTail.\n", encoding="utf-8"
            )

            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, [])
            self.assertEqual(kept, ["coding-behavior-guidelines"])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                f"# Project\n\n{edited}\nTail.\n",
            )

    def test_append_described_line_is_idempotent(self) -> None:
        """t-209: a described citation is not duplicated on re-append (fr-7)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, [])
            self.assertEqual(already, ["coding-behavior-guidelines"])
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(text.count("## AI guidelines"), 1)
            self.assertEqual(
                text.count(
                    "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
                ),
                1,
            )

    def test_described_append_remove_round_trip_is_byte_exact(self) -> None:
        """t-210: described citations round-trip byte-exactly (nfr-2)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            original = "# Project\n\nSome existing guidance.\n"
            (target / "AGENTS.md").write_text(original, encoding="utf-8")

            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"), original
            )

    def test_described_crlf_append_remove_round_trip_is_byte_exact(self) -> None:
        """cr-003: the described em-dash line round-trips on CRLF files too."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            original = b"# Project\r\n\r\nSome guidance.\r\n"
            (target / "AGENTS.md").write_bytes(original)

            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            raw = (target / "AGENTS.md").read_bytes()
            # The described line landed with CRLF endings and no stray LF.
            self.assertIn(b" \xe2\x80\x94 Load before writing or editing code.\r\n", raw)
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

            mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            self.assertEqual((target / "AGENTS.md").read_bytes(), original)

    def test_uninstall_removes_frontmatterd_guideline_file(self) -> None:
        """t-212: sha256 provenance holds for frontmatter'd sources (AC-5)."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            target.mkdir(parents=True)
            write_source_guideline(
                source,
                "coding-behavior-guidelines",
                "---\n"
                "description: Load before writing or editing code.\n"
                "---\n"
                "# Be careful\n",
            )
            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["coding-behavior-guidelines"],
            )

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                result = mod.uninstall_items(
                    target_root=target,
                    skills=[],
                    agents=[],
                    commands=[],
                    scripts=[],
                    guidelines=["coding-behavior-guidelines"],
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertTrue(result.ok, result.errors)
            self.assertFalse(
                (target / ".ai" / "guidelines" / "coding-behavior-guidelines.md").exists()
            )

    def test_remove_matches_legacy_citation_wording(self) -> None:
        """fr-5: uninstall also removes citations written with the pre-generalization wording."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            legacy = (
                "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
                "(.ai/guidelines/coding-behavior-guidelines.md) "
                "when generating or editing any code in this repo."
            )
            agents_md.write_text(f"# Project\n{legacy}\nTail.\n", encoding="utf-8")

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(kept, [])
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"), "# Project\nTail.\n"
            )

    def test_remove_matches_legacy_citation_wording_with_crlf(self) -> None:
        """cr-001: legacy-wording removal also works on CRLF files.

        The dual-match set and the CRLF-preserving rewrite are independent
        code paths; this pins their intersection.
        """
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            legacy = (
                "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
                "(.ai/guidelines/coding-behavior-guidelines.md) "
                "when generating or editing any code in this repo."
            )
            (target / "AGENTS.md").write_bytes(
                f"# Project\r\n\r\n{legacy}\r\n\r\nTail.\r\n".encode("utf-8")
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(kept, [])
            raw = (target / "AGENTS.md").read_bytes()
            self.assertEqual(raw, b"# Project\r\n\r\n\r\nTail.\r\n")

    def test_append_lines_to_existing_agents_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            # No trailing newline: pins the newline-safety mitigation.
            agents_md.write_text("# Project\n\nSome existing guidance.", encoding="utf-8")

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            self.assertEqual(already, [])
            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"),
                "# Project\n\nSome existing guidance.\n\n"
                "## AI guidelines\n\n" + citation + "\n",
            )

    def test_append_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, [])
            self.assertEqual(already, ["coding-behavior-guidelines"])
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertEqual(
                text.count(
                    mod.build_guideline_citation_line("coding-behavior-guidelines")
                ),
                1,
            )

    def test_append_recognizes_hand_worded_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            hand_worded = (
                "- See .ai/guidelines/coding-behavior-guidelines.md for coding rules."
            )
            agents_md.write_text(f"# Project\n{hand_worded}\n", encoding="utf-8")
            before = agents_md.read_bytes()

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, [])
            self.assertEqual(already, ["coding-behavior-guidelines"])
            self.assertEqual(agents_md.read_bytes(), before)

    def test_append_offer_reports_already_cited_for_hand_worded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "# Project\n"
                "- See .ai/guidelines/coding-behavior-guidelines.md for rules.\n",
                encoding="utf-8",
            )
            before = agents_md.read_bytes()

            message = mod.run_agents_md_append_offer(
                target, ["coding-behavior-guidelines"], update_flag=True
            )

            self.assertIn("already cited", message)
            self.assertEqual(agents_md.read_bytes(), before)

    def test_append_mixed_hand_worded_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "# Project\n- See .ai/guidelines/first-guideline.md for rules.\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "second-guideline")
            appended, already = mod.agents_md_append_lines(
                target, ["first-guideline", "second-guideline"], source_root=source
            )

            self.assertEqual(appended, ["second-guideline"])
            self.assertEqual(already, ["first-guideline"])
            text = agents_md.read_text(encoding="utf-8")
            self.assertIn(mod.build_guideline_citation_line("second-guideline"), text)
            self.assertNotIn(mod.build_guideline_citation_line("first-guideline"), text)

    def test_append_inserts_under_existing_guidelines_section(self) -> None:
        """Citations join the section's content instead of the file end."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "# Project\n\n## AI guidelines\n\n- Keep it simple.\n\n"
                "## Other\n\nTail.\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            self.assertEqual(already, [])
            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n- Keep it simple.\n"
                + citation
                + "\n\n## Other\n\nTail.\n",
            )

    def test_append_into_empty_guidelines_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "# Project\n\n## AI guidelines\n\n## Other\n\nTail.\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n"
                + citation
                + "\n\n## Other\n\nTail.\n",
            )

    def test_append_creates_section_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "# Project\n\nSome guidance.\n", encoding="utf-8"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"),
                "# Project\n\nSome guidance.\n\n## AI guidelines\n\n"
                + citation
                + "\n",
            )

    def test_append_separates_citations_from_next_heading(self) -> None:
        """Section content glued to the next heading gains a blank line."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "## AI guidelines\n- old\n## Other\n", encoding="utf-8"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"),
                "## AI guidelines\n- old\n" + citation + "\n\n## Other\n",
            )

    def test_append_treats_deeper_headings_as_section_content(self) -> None:
        """h3+ headings live inside the section; citations go after them."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text(
                "## AI guidelines\n### Notes\nnote\n", encoding="utf-8"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                agents_md.read_text(encoding="utf-8"),
                "## AI guidelines\n### Notes\nnote\n" + citation + "\n",
            )

    def test_append_into_section_preserves_crlf_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_bytes(
                b"# Project\r\n## AI guidelines\r\n- old\r\n## Other\r\n"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            appended, _ = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            ).encode("utf-8")
            self.assertEqual(
                (target / "AGENTS.md").read_bytes(),
                b"# Project\r\n## AI guidelines\r\n- old\r\n"
                + citation
                + b"\r\n\r\n## Other\r\n",
            )

    def test_append_ignores_fenced_guidelines_heading(self) -> None:
        """A fenced '## AI guidelines' example is content, not a section."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text(
                "# Project\n\n```\n## AI guidelines\n```\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            appended, _ = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\n```\n## AI guidelines\n```\n\n"
                "## AI guidelines\n\n" + citation + "\n",
            )

    def test_section_scan_ignores_fenced_boundary_heading(self) -> None:
        """A fenced '##' line does not end the section."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text(
                "## AI guidelines\n\n- rule\n\n```\n## Other\n```\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            citation = mod.build_guideline_citation_line(
                "coding-behavior-guidelines"
            )
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "## AI guidelines\n\n- rule\n\n```\n## Other\n```\n"
                + citation
                + "\n",
            )

    def test_no_agents_md_skips_and_instructs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            message = mod.run_agents_md_append_offer(
                target,
                ["coding-behavior-guidelines"],
                update_flag=True,
            )

            self.assertFalse((target / "AGENTS.md").exists())
            self.assertIn("AGENTS.md", message)
            self.assertIn("create", message.lower())

    def test_non_tty_skips_offer(self) -> None:
        self.assertEqual(
            mod.resolve_agents_md_action(
                update_flag=False, no_update_flag=False, is_tty=False
            ),
            "skip",
        )

    def test_update_flag_forces_append(self) -> None:
        self.assertEqual(
            mod.resolve_agents_md_action(
                update_flag=True, no_update_flag=False, is_tty=False
            ),
            "append",
        )

    def test_no_update_flag_forces_skip(self) -> None:
        self.assertEqual(
            mod.resolve_agents_md_action(
                update_flag=False, no_update_flag=True, is_tty=True
            ),
            "skip",
        )

    def test_both_flags_error(self) -> None:
        with self.assertRaises(mod.InstallerError):
            mod.resolve_agents_md_action(
                update_flag=True, no_update_flag=True, is_tty=False
            )

    def test_uninstall_removes_identical_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_guideline(source, "coding-behavior-guidelines", "# Be careful\n")
            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["coding-behavior-guidelines"],
            )

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                result = mod.uninstall_items(
                    target_root=target,
                    skills=[],
                    agents=[],
                    commands=[],
                    scripts=[],
                    guidelines=["coding-behavior-guidelines"],
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertTrue(result.ok, result.errors)
            self.assertFalse(
                (target / ".ai" / "guidelines" / "coding-behavior-guidelines.md").exists()
            )

    def test_uninstall_skips_modified_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_guideline(source, "coding-behavior-guidelines", "# Be careful\n")
            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=[],
                scripts=[],
                guidelines=["coding-behavior-guidelines"],
            )
            installed = target / ".ai" / "guidelines" / "coding-behavior-guidelines.md"
            installed.write_text("# User-customized guideline\n", encoding="utf-8")

            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                result = mod.uninstall_items(
                    target_root=target,
                    skills=[],
                    agents=[],
                    commands=[],
                    scripts=[],
                    guidelines=["coding-behavior-guidelines"],
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertTrue(result.ok, result.errors)
            self.assertTrue(installed.exists())
            self.assertIn(
                ".ai/guidelines/coding-behavior-guidelines.md", result.skipped
            )

    def test_uninstall_removes_identical_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_text(
                f"# Project\n\n{line}\n", encoding="utf-8"
            )

            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(kept, [])
            self.assertNotIn(line, (target / "AGENTS.md").read_text(encoding="utf-8"))

    def test_uninstall_keeps_edited_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            edited = (
                "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
                "(.ai/guidelines/coding-behavior-guidelines.md) "
                "but only on weekdays (user edit)."
            )
            (target / "AGENTS.md").write_text(
                f"# Project\n\n{edited}\n", encoding="utf-8"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, [])
            self.assertEqual(kept, ["coding-behavior-guidelines"])
            self.assertIn(
                edited, (target / "AGENTS.md").read_text(encoding="utf-8")
            )

    def test_append_preserves_crlf_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_bytes(
                b"# Project\r\n\r\nSome guidance.\r\n"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            appended, _ = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            raw = (target / "AGENTS.md").read_bytes()
            # 3 original CRLF line endings + separator blank + section
            # heading + blank + the appended citation line.
            self.assertEqual(raw.count(b"\r\n"), 7)
            self.assertNotIn(b"\r\n\r\n\n", raw)
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
            self.assertIn(
                b"## AI guidelines\r\n\r\n"
                + mod.build_guideline_citation_line(
                    "coding-behavior-guidelines"
                ).encode("utf-8")
                + b"\r\n",
                raw,
            )

    def test_remove_drops_appended_section_at_eof(self) -> None:
        """Uninstall reverses an installer-appended EOF section exactly."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_text(
                f"# Project\n\n## AI guidelines\n\n{line}\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(kept, [])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n",
            )

    def test_remove_drops_appended_section_at_eof_crlf(self) -> None:
        """The EOF drop preserves CRLF endings and the separator blank."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_bytes(
                f"# Project\r\n\r\n## AI guidelines\r\n\r\n{line}\r\n".encode(
                    "utf-8"
                )
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, _ = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(
                (target / "AGENTS.md").read_bytes(), b"# Project\r\n"
            )

    def test_remove_keeps_midfile_emptied_section(self) -> None:
        """A mid-file section is always user-created; its heading stays."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_text(
                f"# Project\n\n## AI guidelines\n\n{line}\n\n## Other\n\nTail.\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n\n## Other\n\nTail.\n",
            )

    def test_append_remove_round_trip_is_byte_exact(self) -> None:
        """Install then uninstall restores the original AGENTS.md exactly."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            original = "# Project\n\nSome guidance.\n"
            (target / "AGENTS.md").write_text(original, encoding="utf-8")

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"), original
            )

    def test_remove_drops_user_created_empty_eof_section(self) -> None:
        """Documented edge: an empty EOF section with a separator blank is
        byte-identical to an installer append and is dropped (no content)."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text(
                "# Project\n\n## AI guidelines\n\n", encoding="utf-8"
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            removed, _ = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n",
            )

    def test_remove_keeps_eof_section_without_separator_blank(self) -> None:
        """No blank before the heading → not the installer's append shape."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            original = "# Project\n## AI guidelines\n\n"
            (target / "AGENTS.md").write_text(original, encoding="utf-8")

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )
            mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"), original
            )

    def test_remove_keeps_guidelines_section_with_user_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_text(
                f"# Project\n\n## AI guidelines\n\n- My own rule.\n{line}\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n- My own rule.\n",
            )

    def test_remove_keeps_user_created_empty_guidelines_section(self) -> None:
        """A section the installer never wrote into is left alone (provenance)."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_text(
                f"# Project\n\n## AI guidelines\n\n## Other\n\n{line}\n",
                encoding="utf-8",
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"),
                "# Project\n\n## AI guidelines\n\n## Other\n\n",
            )

    def test_remove_preserves_crlf_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_bytes(
                f"# Project\r\n\r\n{line}\r\n\r\nTail.\r\n".encode("utf-8")
            )

            source = Path(tmp) / "source"
            write_source_guideline(source, "coding-behavior-guidelines")
            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"], source_root=source
            )

            self.assertEqual(removed, ["coding-behavior-guidelines"])
            self.assertEqual(kept, [])
            raw = (target / "AGENTS.md").read_bytes()
            # Exactly the citation line is removed; surrounding blank lines and
            # CRLF endings are preserved byte-for-byte.
            self.assertEqual(raw, b"# Project\r\n\r\n\r\nTail.\r\n")

    def test_integration_message_content(self) -> None:
        message = mod.format_guidelines_integration_message(
            ["coding-behavior-guidelines"]
        )
        self.assertIn(".ai/guidelines/coding-behavior-guidelines.md", message)
        self.assertIn("AGENTS.md", message)
        self.assertIn("prompt", message.lower())


class RunCliCompositionTests(unittest.TestCase):
    """End-to-end: flags → run_operation → resolver → AGENTS.md mutation."""

    def _prepare(self, tmp: str) -> tuple[Path, Path]:
        source = Path(tmp) / "source"
        target = Path(tmp) / "target"
        write_source_guideline(source, "coding-behavior-guidelines", "# Be careful\n")
        target.mkdir(parents=True, exist_ok=True)
        return source, target

    def test_update_flag_appends_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target = self._prepare(tmp)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli(
                    [
                        str(target),
                        "--guidelines",
                        "coding-behavior-guidelines",
                        "--update-agents-md",
                    ]
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("## AI guidelines", text)
            self.assertIn(
                mod.build_guideline_citation_line("coding-behavior-guidelines"), text
            )

    def test_no_update_flag_skips_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target = self._prepare(tmp)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                code = mod.run_cli(
                    [
                        str(target),
                        "--guidelines",
                        "coding-behavior-guidelines",
                        "--no-update-agents-md",
                    ]
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("coding-behavior-guidelines", text)

    def test_non_tty_default_skips_line(self) -> None:
        import contextlib
        import io

        with tempfile.TemporaryDirectory() as tmp:
            source, target = self._prepare(tmp)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                with mock.patch("sys.stdin") as fake_stdin:
                    fake_stdin.isatty.return_value = False
                    captured = io.StringIO()
                    with contextlib.redirect_stdout(captured):
                        code = mod.run_cli(
                            [str(target), "--guidelines", "coding-behavior-guidelines"]
                        )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("coding-behavior-guidelines", text)
            # The integration instructions must reach the user (cr-004).
            self.assertIn("AGENTS.md", captured.getvalue())
            self.assertIn("inert until loaded", captured.getvalue())

    def test_read_only_agents_md_warns_instead_of_crashing(self) -> None:
        """cr-202 regression: the offer path must not crash on OSError (cr-002)."""
        import contextlib
        import io
        import os
        import sys as sys_module

        with tempfile.TemporaryDirectory() as tmp:
            source, target = self._prepare(tmp)
            agents_md = target / "AGENTS.md"
            agents_md.write_text("# Project\n", encoding="utf-8")
            os.chmod(agents_md, 0o444)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                if os.access(agents_md, os.W_OK):
                    raise unittest.SkipTest("running as root — permission probe ineffective")
                captured_err = io.StringIO()
                with mock.patch("sys.stdin") as fake_stdin:
                    fake_stdin.isatty.return_value = False
                    with contextlib.redirect_stderr(captured_err):
                        code = mod.run_cli(
                            [
                                str(target),
                                "--guidelines",
                                "coding-behavior-guidelines",
                                "--update-agents-md",
                            ]
                        )
            finally:
                os.chmod(agents_md, 0o644)
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            self.assertIn("could not update AGENTS.md", captured_err.getvalue())

    def test_uninstall_with_update_flag_removes_file_and_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source, target = self._prepare(tmp)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            try:
                mod.run_cli(
                    [
                        str(target),
                        "--guidelines",
                        "coding-behavior-guidelines",
                        "--update-agents-md",
                    ]
                )
                code = mod.run_cli(
                    [
                        str(target),
                        "--guidelines",
                        "coding-behavior-guidelines",
                        "--uninstall",
                        "--update-agents-md",
                    ]
                )
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(code, 0)
            self.assertFalse(
                (target / ".ai" / "guidelines" / "coding-behavior-guidelines.md").exists()
            )
            # Byte-exact round trip: install + uninstall restores the file.
            self.assertEqual(
                (target / "AGENTS.md").read_text(encoding="utf-8"), "# Project\n"
            )


def _tk_available() -> bool:
    """Return True when a tkinter display is available (pr-001 scaffolding)."""
    try:
        import tkinter as tk

        root = tk.Tk()
    except Exception:
        return False
    root.destroy()
    return True


@unittest.skipUnless(_tk_available(), "no display available for tkinter")
class GuiGuidelinesPanelTests(unittest.TestCase):
    """The GUI exposes a Guidelines panel wired to the tested offer helpers."""

    def test_gui_panel_construction(self) -> None:
        import tkinter as tk

        with tempfile.TemporaryDirectory() as tmp:
            root_path = Path(tmp)
            write_source_guideline(root_path, "coding-behavior-guidelines")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root_path
            try:
                root = tk.Tk()
                root.withdraw()
                app = mod.InstallerApp(root)
                try:
                    self.assertIn("coding-behavior-guidelines", app.guideline_vars)
                    self.assertEqual(
                        app.guideline_descriptions.get("coding-behavior-guidelines"),
                        "Guideline",
                    )
                finally:
                    root.destroy()
            finally:
                mod.REPO_ROOT = original_root

    def test_gui_run_wires_offer(self) -> None:
        """The GUI _run path routes the offer through the tested helpers (cr-003)."""
        import tkinter as tk

        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_guideline(source, "coding-behavior-guidelines", "# Be careful\n")
            target.mkdir(parents=True, exist_ok=True)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            root = None
            try:
                root = tk.Tk()
                root.withdraw()
                app = mod.InstallerApp(root)
                app.target_var.set(str(target))
                app.guideline_vars["coding-behavior-guidelines"].set(True)
                with (
                    mock.patch.object(
                        mod, "run_operation", return_value=(0, "Installed:")
                    ) as fake_op,
                    mock.patch.object(
                        mod.messagebox, "askyesno", return_value=True
                    ) as fake_ask,
                ):
                    app._run()
                try:
                    self.assertEqual(fake_op.call_count, 1)
                    self.assertIn(
                        "coding-behavior-guidelines",
                        fake_op.call_args.kwargs.get("guidelines", []),
                    )
                    self.assertTrue(fake_ask.called)
                    text = (target / "AGENTS.md").read_text(encoding="utf-8")
                    self.assertIn(
                        mod.build_guideline_citation_line("coding-behavior-guidelines"),
                        text,
                    )
                finally:
                    root.destroy()
            finally:
                mod.REPO_ROOT = original_root
                if root is not None:
                    try:
                        root.destroy()
                    except tk.TclError:
                        pass


if __name__ == "__main__":
    unittest.main()
