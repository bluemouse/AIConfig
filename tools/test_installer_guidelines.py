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
        self.assertTrue(
            (REPO_ROOT / "guidelines" / "coding-behavior-guidelines.md").is_file(),
            "Guideline must live at guidelines/coding-behavior-guidelines.md",
        )
        self.assertFalse(
            (REPO_ROOT / "coding-behavior-guidelines.md").exists(),
            "Guideline must no longer sit at the repo root",
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
                write_source_guideline(root, "not-allowlisted")
                discovered = mod.discover_guidelines()
            finally:
                mod.REPO_ROOT = original_root

            self.assertEqual(discovered, ["coding-behavior-guidelines"])


class AgentsMdIntegrationTests(unittest.TestCase):
    """The consent-gated AGENTS.md citation append/remove machinery."""

    def test_citation_line_format(self) -> None:
        line = mod.build_guideline_citation_line("coding-behavior-guidelines")
        self.assertEqual(
            line,
            "- Follow [.ai/guidelines/coding-behavior-guidelines.md]"
            "(.ai/guidelines/coding-behavior-guidelines.md) "
            "when generating or editing any code in this repo.",
        )

    def test_append_lines_to_existing_agents_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            agents_md = target / "AGENTS.md"
            # No trailing newline: pins the newline-safety mitigation.
            agents_md.write_text("# Project\n\nSome existing guidance.", encoding="utf-8")

            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"]
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            self.assertEqual(already, [])
            text = agents_md.read_text(encoding="utf-8")
            self.assertIn("# Project\n\nSome existing guidance.", text)
            self.assertIn(
                mod.build_guideline_citation_line("coding-behavior-guidelines"),
                text,
            )
            lines = text.splitlines()
            self.assertEqual(
                lines[-1],
                mod.build_guideline_citation_line("coding-behavior-guidelines"),
            )

    def test_append_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "AGENTS.md").write_text("# Project\n", encoding="utf-8")

            mod.agents_md_append_lines(target, ["coding-behavior-guidelines"])
            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"]
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

            appended, already = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"]
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

            appended, already = mod.agents_md_append_lines(
                target, ["first-guideline", "second-guideline"]
            )

            self.assertEqual(appended, ["second-guideline"])
            self.assertEqual(already, ["first-guideline"])
            text = agents_md.read_text(encoding="utf-8")
            self.assertIn(mod.build_guideline_citation_line("second-guideline"), text)
            self.assertNotIn(mod.build_guideline_citation_line("first-guideline"), text)

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
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_text(
                f"# Project\n\n{line}\n", encoding="utf-8"
            )

            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"]
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

            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"]
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

            appended, _ = mod.agents_md_append_lines(
                target, ["coding-behavior-guidelines"]
            )

            self.assertEqual(appended, ["coding-behavior-guidelines"])
            raw = (target / "AGENTS.md").read_bytes()
            # 3 original CRLF line endings + 1 for the appended line.
            self.assertEqual(raw.count(b"\r\n"), 4)
            self.assertNotIn(b"\r\n\r\n\n", raw)
            self.assertIn(
                mod.build_guideline_citation_line("coding-behavior-guidelines").encode("utf-8")
                + b"\r\n",
                raw,
            )

    def test_remove_preserves_crlf_line_endings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            line = mod.build_guideline_citation_line("coding-behavior-guidelines")
            (target / "AGENTS.md").write_bytes(
                f"# Project\r\n\r\n{line}\r\n\r\nTail.\r\n".encode("utf-8")
            )

            removed, kept = mod.agents_md_remove_lines(
                target, ["coding-behavior-guidelines"]
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
            text = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertNotIn("coding-behavior-guidelines", text)


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
