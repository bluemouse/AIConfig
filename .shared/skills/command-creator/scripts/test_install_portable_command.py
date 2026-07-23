#!/usr/bin/env python3
"""Tests for install_portable_command.py and bootstrap validation."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


install_mod = load_module("install_portable_command_test", SCRIPTS_DIR / "install_portable_command.py")
validate_mod = load_module("quick_validate_command_test", SCRIPTS_DIR / "quick_validate.py")
scaffold_mod = load_module("scaffold_command_test", SCRIPTS_DIR / "scaffold_command.py")
create_mod = load_module("create_command_test", SCRIPTS_DIR / "create_command.py")

CommandCreatorError = install_mod.CommandCreatorError
install_portable_command = install_mod.install_portable_command
validate_bootstrap_command = validate_mod.validate_bootstrap_command
validate_portable_command = validate_mod.validate_portable_command
quick_validate_main = validate_mod.main
parse_frontmatter = validate_mod.parse_frontmatter
build_claude_content = scaffold_mod.build_claude_content
create_command = create_mod.create_command
validate_install = create_mod.validate_install

COMMAND_NAME = "test-command"
COMMAND_DESCRIPTION = "Test command for unit tests."


def shared_command_md(
    *,
    name: str = COMMAND_NAME,
    description: str = COMMAND_DESCRIPTION,
    body: str = "# Test Command\n\nShared command body for tests.\n",
) -> str:
    return f"""---
name: {name}
description: {description}
---

{body}
"""


def write_bootstrap(
    source: Path,
    *,
    description: str = COMMAND_DESCRIPTION,
    claude_wrapper: str | None = None,
    github_wrapper: str | None = None,
    cursor_wrapper: str | None = None,
) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "COMMAND.md").write_text(shared_command_md(description=description), encoding="utf-8")

    if cursor_wrapper is not None:
        wrapper_dir = source / "wrappers" / "cursor"
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        (wrapper_dir / "COMMAND.md").write_text(cursor_wrapper, encoding="utf-8")

    if claude_wrapper is not None:
        wrapper_dir = source / "wrappers" / "claude"
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        (wrapper_dir / "COMMAND.md").write_text(claude_wrapper, encoding="utf-8")

    if github_wrapper is not None:
        wrapper_dir = source / "wrappers" / "github"
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        (wrapper_dir / "COMMAND.md").write_text(github_wrapper, encoding="utf-8")


class InstallPortableCommandTests(unittest.TestCase):
    def test_install_all_four_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)

            written = install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            self.assertEqual(len(written), 4)
            shared = root / ".shared" / "commands" / f"{COMMAND_NAME}.md"
            cursor = root / ".cursor" / "commands" / f"{COMMAND_NAME}.md"
            claude = root / ".claude" / "commands" / f"{COMMAND_NAME}.md"
            github = root / ".github" / "prompts" / f"{COMMAND_NAME}.prompt.md"
            self.assertTrue(all(path.is_file() for path in (shared, cursor, claude, github)))

            valid, messages = validate_portable_command(root, COMMAND_NAME)
            self.assertTrue(valid, messages)

    def test_cursor_output_has_no_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            cursor = (root / ".cursor" / "commands" / f"{COMMAND_NAME}.md").read_text(
                encoding="utf-8"
            )
            self.assertFalse(cursor.strip().startswith("---"))

    def test_github_output_uses_prompt_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            github_path = root / ".github" / "prompts" / f"{COMMAND_NAME}.prompt.md"
            self.assertTrue(github_path.is_file())

    def test_custom_wrapper_frontmatter_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            claude_wrapper = """---
allowed-tools: Read, Grep
model: claude-opus-4-8
description: stale description
---

Claude-only appendix.
"""
            github_wrapper = """---
tools: ['search/codebase']
agent: plan
description: stale description
---

Copilot-only appendix.
"""
            write_bootstrap(
                source,
                claude_wrapper=claude_wrapper,
                github_wrapper=github_wrapper,
            )
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            claude = (root / ".claude" / "commands" / f"{COMMAND_NAME}.md").read_text(
                encoding="utf-8"
            )
            claude_fm, _ = parse_frontmatter(claude)
            self.assertIsNotNone(claude_fm)
            assert claude_fm is not None
            self.assertEqual(claude_fm.get("allowed-tools"), "Read, Grep")
            self.assertEqual(claude_fm.get("model"), "claude-opus-4-8")
            self.assertEqual(claude_fm.get("description"), COMMAND_DESCRIPTION)
            self.assertIn("Claude-only appendix.", claude)

            github = (root / ".github" / "prompts" / f"{COMMAND_NAME}.prompt.md").read_text(
                encoding="utf-8"
            )
            github_fm, _ = parse_frontmatter(github)
            self.assertIsNotNone(github_fm)
            assert github_fm is not None
            self.assertEqual(github_fm.get("agent"), "plan")
            self.assertEqual(github_fm.get("tools"), ["search/codebase"])
            self.assertIn("Copilot-only appendix.", github)

    def test_folded_block_description_sync(self) -> None:
        folded_description = (
            "Review staged changes and return a findings-first report "
            "with severity labels and file references."
        )
        folded_yaml = f"""---
name: {COMMAND_NAME}
description: >-
  Review staged changes and return a findings-first report
  with severity labels and file references.
---

# Review

Body text.
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            (source / "COMMAND.md").write_text(folded_yaml, encoding="utf-8")
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            claude = (root / ".claude" / "commands" / f"{COMMAND_NAME}.md").read_text(
                encoding="utf-8"
            )
            claude_fm, _ = parse_frontmatter(claude)
            self.assertIsNotNone(claude_fm)
            assert claude_fm is not None
            self.assertEqual(
                " ".join(str(claude_fm.get("description", "")).split()),
                " ".join(folded_description.split()),
            )

    def test_no_overwrite_refuses_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)

            cursor_path = root / ".cursor" / "commands" / f"{COMMAND_NAME}.md"
            cursor_path.parent.mkdir(parents=True, exist_ok=True)
            cursor_path.write_text("stale cursor command", encoding="utf-8")

            with self.assertRaises(CommandCreatorError) as ctx:
                install_portable_command(root, source, COMMAND_NAME, overwrite=False)

            self.assertIn(str(cursor_path), str(ctx.exception))
            self.assertEqual(cursor_path.read_text(encoding="utf-8"), "stale cursor command")

    def test_cursor_wrapper_rejects_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(
                source,
                cursor_wrapper="---\ndescription: bad\n---\n\nAppendix.",
            )
            with self.assertRaises(CommandCreatorError):
                install_portable_command(root, source, COMMAND_NAME, overwrite=True)

    def test_build_claude_preserves_tool_keys(self) -> None:
        content = build_claude_content(
            COMMAND_NAME,
            COMMAND_DESCRIPTION,
            "Shared body.",
            wrapper_content="",
            wrapper_frontmatter={
                "allowed-tools": "Read",
                "model": "claude-opus-4-8",
            },
        )
        frontmatter, _ = parse_frontmatter(content)
        self.assertIsNotNone(frontmatter)
        assert frontmatter is not None
        self.assertEqual(frontmatter.get("allowed-tools"), "Read")
        self.assertEqual(frontmatter.get("model"), "claude-opus-4-8")


class BootstrapValidationTests(unittest.TestCase):
    def test_validate_bootstrap_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "commands" / COMMAND_NAME
            write_bootstrap(source)
            valid, messages = validate_bootstrap_command(source)
            self.assertTrue(valid, messages)

    def test_quick_validate_accepts_bootstrap_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "commands" / COMMAND_NAME
            write_bootstrap(source)
            exit_code = quick_validate_main([str(source)])
            self.assertEqual(exit_code, 0)


class CreateCommandTests(unittest.TestCase):
    def test_create_command_installs_all_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            body_path = root / "body.md"
            body_path.write_text("# Test Command\n\nDirect scaffold body.\n", encoding="utf-8")

            written = create_command(
                root,
                COMMAND_NAME,
                COMMAND_DESCRIPTION,
                body_path.read_text(encoding="utf-8"),
                overwrite=True,
            )

            self.assertEqual(len(written), 4)
            self.assertTrue((root / ".shared" / "commands" / f"{COMMAND_NAME}.md").is_file())
            self.assertTrue((root / ".cursor" / "commands" / f"{COMMAND_NAME}.md").is_file())
            self.assertTrue((root / ".claude" / "commands" / f"{COMMAND_NAME}.md").is_file())
            self.assertTrue(
                (root / ".github" / "prompts" / f"{COMMAND_NAME}.prompt.md").is_file()
            )

    def test_create_command_validates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = create_command(
                root,
                COMMAND_NAME,
                COMMAND_DESCRIPTION,
                "# Test Command\n\nValidated direct scaffold body.\n",
                overwrite=True,
            )
            validate_install(written)
            valid, messages = validate_portable_command(root, COMMAND_NAME)
            self.assertTrue(valid, messages)


if __name__ == "__main__":
    unittest.main()
