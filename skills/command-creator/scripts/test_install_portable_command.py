#!/usr/bin/env python3
"""Tests for command-skill installs (install_portable_command.py) and validation.

Commands install as command-skills: a single .agents/skills/cmd-<name>/SKILL.md
with `disable-model-invocation: true`, a <=120-char invocation-gated
description, and `allowed-tools` transferred when the source declares it.
The slash command stays /<name>; only the install dir carries the prefix.
"""

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


install_mod = load_module(
    "install_portable_command_test", SCRIPTS_DIR / "install_portable_command.py"
)
validate_mod = load_module("quick_validate_command_test", SCRIPTS_DIR / "quick_validate.py")
create_mod = load_module("create_command_test", SCRIPTS_DIR / "create_command.py")

CommandCreatorError = install_mod.CommandCreatorError
install_portable_command = install_mod.install_portable_command
validate_bootstrap_command = validate_mod.validate_bootstrap_command
validate_portable_command = validate_mod.validate_portable_command
validate_command = validate_mod.validate_command
quick_validate_main = validate_mod.main
parse_frontmatter = validate_mod.parse_frontmatter
create_command = create_mod.create_command
validate_install = create_mod.validate_install

COMMAND_NAME = "test-command"
COMMAND_DESCRIPTION = "Run the test workflow when the user explicitly invokes /test-command."
COMMAND_BODY = "# Test Command\n\nShared command body for tests.\n"


def command_md(
    *,
    name: str = COMMAND_NAME,
    description: str = COMMAND_DESCRIPTION,
    allowed_tools: str | None = None,
    body: str = COMMAND_BODY,
) -> str:
    lines = ["---", f"name: {name}", f"description: {description}"]
    if allowed_tools is not None:
        lines.append(f"allowed-tools: {allowed_tools}")
    lines.append("---")
    return "\n".join(lines) + f"\n\n{body}\n"


def skill_md(
    *,
    name: str = COMMAND_NAME,
    description: str = COMMAND_DESCRIPTION,
    disable_model_invocation: bool | None = True,
    allowed_tools: str | None = None,
    body: str = COMMAND_BODY,
) -> str:
    lines = ["---", f"name: {name}", f"description: {description}"]
    if disable_model_invocation is not None:
        lines.append(f"disable-model-invocation: {str(disable_model_invocation).lower()}")
    if allowed_tools is not None:
        lines.append(f"allowed-tools: {allowed_tools}")
    lines.append("---")
    return "\n".join(lines) + f"\n\n{body}\n"


def write_bootstrap(source: Path, content: str | None = None) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "COMMAND.md").write_text(content or command_md(), encoding="utf-8")


def write_skill(root: Path, name: str, content: str) -> Path:
    skill_dir = root / ".agents" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path


class InstallCommandSkillTests(unittest.TestCase):
    def test_command_installs_as_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)

            written, removed = install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            skill_path = root / ".agents" / "skills" / f"cmd-{COMMAND_NAME}" / "SKILL.md"
            self.assertEqual(written, [skill_path])
            self.assertEqual(removed, [])
            self.assertTrue(skill_path.is_file())

            frontmatter, error = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            assert frontmatter is not None
            self.assertEqual(frontmatter.get("name"), COMMAND_NAME)
            self.assertIs(frontmatter.get("disable-model-invocation"), True)
            description = str(frontmatter.get("description", ""))
            self.assertLessEqual(len(description), 120)
            self.assertIn("explicitly invokes", description)
            self.assertIn("Shared command body for tests.", skill_path.read_text(encoding="utf-8"))

            self.assertFalse((root / ".ai" / "commands").exists())
            self.assertFalse((root / ".cursor" / "commands").exists())
            self.assertFalse((root / ".claude" / "commands").exists())
            self.assertFalse((root / ".github" / "prompts").exists())

            valid, message = validate_command(skill_path)
            self.assertTrue(valid, message)

    def test_command_rejects_skill_name_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            existing_skill = write_skill(
                root,
                f"cmd-{COMMAND_NAME}",
                skill_md(
                    description="A plain model-invocable skill.",
                    disable_model_invocation=None,
                ),
            )
            original = existing_skill.read_text(encoding="utf-8")

            with self.assertRaises(CommandCreatorError) as ctx:
                install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            self.assertIn("collision", str(ctx.exception))
            self.assertIn(str(existing_skill.parent), str(ctx.exception))
            self.assertEqual(existing_skill.read_text(encoding="utf-8"), original)

    def test_reinstall_overwrites_existing_command_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            write_bootstrap(source, command_md(body="# Test Command\n\nUpdated body.\n"))
            written, removed = install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            self.assertIn("Updated body.", written[0].read_text(encoding="utf-8"))
            self.assertEqual(removed, [], "no legacy outputs exist to remove")

    def test_no_overwrite_refuses_existing_command_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            skill_path = install_portable_command(
                root, source, COMMAND_NAME, overwrite=True
            )[0][0]
            original = skill_path.read_text(encoding="utf-8")

            with self.assertRaises(CommandCreatorError) as ctx:
                install_portable_command(root, source, COMMAND_NAME, overwrite=False)

            self.assertIn(str(skill_path), str(ctx.exception))
            self.assertEqual(skill_path.read_text(encoding="utf-8"), original)

    def test_reinstall_removes_legacy_command_outputs(self) -> None:
        """fd-015: overwrite removes pre-single-root command outputs.

        Older installs wrote .ai/commands/, .cursor/commands/,
        .claude/commands/, and .github/prompts/; a target upgraded by
        reinstalling must not keep a stale slash-command a host still reads.
        Mirrors agent-creator's remove_legacy_outputs.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            legacy = [
                root / ".ai" / "commands" / f"{COMMAND_NAME}.md",
                root / ".cursor" / "commands" / f"{COMMAND_NAME}.md",
                root / ".claude" / "commands" / f"{COMMAND_NAME}.md",
                root / ".github" / "prompts" / f"{COMMAND_NAME}.prompt.md",
            ]
            for path in legacy:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("stale legacy output", encoding="utf-8")

            written, removed = install_portable_command(
                root, source, COMMAND_NAME, overwrite=True
            )

            self.assertTrue(
                written, "the command-skill must still install"
            )
            self.assertEqual(
                sorted(str(p) for p in removed),
                sorted(str(p) for p in legacy),
                "all four legacy outputs must be removed on overwrite",
            )
            for path in legacy:
                self.assertFalse(path.exists(), f"stale output left behind: {path}")

    def test_no_overwrite_keeps_legacy_outputs(self) -> None:
        """fd-015 scope check: legacy cleanup runs only on overwrite."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            stale = root / ".claude" / "commands" / f"{COMMAND_NAME}.md"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("stale legacy output", encoding="utf-8")

            with self.assertRaises(CommandCreatorError):
                install_portable_command(
                    root, source, COMMAND_NAME, overwrite=False
                )
            self.assertTrue(stale.exists(), "refused install must not clean up")

    def test_allowed_tools_transfers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source, command_md(allowed_tools="Bash, Read, Grep, Glob"))

            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            skill_path = root / ".agents" / "skills" / f"cmd-{COMMAND_NAME}" / "SKILL.md"
            raw = skill_path.read_text(encoding="utf-8")
            self.assertIn("allowed-tools: Bash, Read, Grep, Glob", raw)
            frontmatter, _ = parse_frontmatter(raw)
            assert frontmatter is not None
            self.assertEqual(frontmatter.get("allowed-tools"), "Bash, Read, Grep, Glob")

    def test_allowed_tools_absent_when_not_declared(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)

            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            skill_path = root / ".agents" / "skills" / f"cmd-{COMMAND_NAME}" / "SKILL.md"
            raw = skill_path.read_text(encoding="utf-8")
            self.assertNotIn("allowed-tools", raw)
            frontmatter, _ = parse_frontmatter(raw)
            assert frontmatter is not None
            self.assertNotIn("allowed-tools", frontmatter)

    def test_source_name_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source, command_md(name="different-name"))

            with self.assertRaises(CommandCreatorError) as ctx:
                install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            self.assertIn("different-name", str(ctx.exception))

    def test_non_string_description_rejected(self) -> None:
        """cr-012: a non-string description is rejected, not str()-coerced.

        A YAML list would otherwise become the literal "[a, b]" and can
        validate; the agent installer's clean-error pattern applies here too.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(
                source,
                "---\n"
                f"name: {COMMAND_NAME}\n"
                "description: [a, b]\n"
                "---\n\n"
                f"{COMMAND_BODY}\n",
            )

            with self.assertRaises(CommandCreatorError) as ctx:
                install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            self.assertIn("string", str(ctx.exception))
            self.assertIn("description", str(ctx.exception))

    def test_non_string_name_rejected(self) -> None:
        """cr-012: a non-string name is rejected with a clean error."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(
                source,
                "---\n"
                "name: [a, b]\n"
                f"description: {COMMAND_DESCRIPTION}\n"
                "---\n\n"
                f"{COMMAND_BODY}\n",
            )

            with self.assertRaises(CommandCreatorError) as ctx:
                install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            self.assertIn("string", str(ctx.exception))
            self.assertIn("name", str(ctx.exception))


class CommandSkillValidationTests(unittest.TestCase):
    def test_command_skill_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            valid_path = write_skill(root, f"cmd-{COMMAND_NAME}", skill_md())
            valid, message = validate_command(valid_path)
            self.assertTrue(valid, message)

            missing_flag_path = write_skill(
                root,
                "missing-flag",
                skill_md(name="missing-flag", disable_model_invocation=None),
            )
            valid, message = validate_command(missing_flag_path)
            self.assertFalse(valid)
            self.assertIn("disable-model-invocation", message)

            long_description = (
                "Use when the user explicitly invokes /long-command. " + "y" * 90
            )
            self.assertGreater(len(long_description), 130)
            long_path = write_skill(
                root, "long-command", skill_md(name="long-command", description=long_description)
            )
            valid, message = validate_command(long_path)
            self.assertFalse(valid)
            self.assertIn("too long", message)

            not_gated_path = write_skill(
                root,
                "not-gated",
                skill_md(name="not-gated", description="Reviews staged changes."),
            )
            valid, message = validate_command(not_gated_path)
            self.assertFalse(valid)
            self.assertIn("invocation-gated", message)

    def test_command_skill_rejects_dirname_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_skill(root, "cmd-other-name", skill_md())
            valid, message = validate_command(path)
            self.assertFalse(valid)
            self.assertIn("must be", message)

    def test_command_skill_rejects_false_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = write_skill(
                root,
                "false-flag",
                skill_md(name="false-flag", disable_model_invocation=False),
            )
            valid, message = validate_command(path)
            self.assertFalse(valid)
            self.assertIn("must be true", message)

    def test_validate_portable_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "commands" / COMMAND_NAME
            write_bootstrap(source)
            install_portable_command(root, source, COMMAND_NAME, overwrite=True)

            valid, messages = validate_portable_command(root, COMMAND_NAME)
            self.assertTrue(valid, messages)


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

    def test_bootstrap_rejects_non_gated_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "commands" / COMMAND_NAME
            write_bootstrap(source, command_md(description="Runs the test workflow end to end."))
            valid, messages = validate_bootstrap_command(source)
            self.assertFalse(valid)
            self.assertTrue(any("invocation-gated" in m for m in messages), messages)

    def test_bootstrap_rejects_long_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "commands" / COMMAND_NAME
            long_description = (
                "Use when the user explicitly invokes /test-command. " + "x" * 80
            )
            self.assertGreater(len(long_description), 120)
            write_bootstrap(source, command_md(description=long_description))
            valid, messages = validate_bootstrap_command(source)
            self.assertFalse(valid)
            self.assertTrue(any("too long" in m for m in messages), messages)

    def test_bootstrap_rejects_unexpected_frontmatter_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "commands" / COMMAND_NAME
            content = (
                "---\n"
                f"name: {COMMAND_NAME}\n"
                f"description: {COMMAND_DESCRIPTION}\n"
                "model: claude-opus-4-8\n"
                "---\n\n"
                f"{COMMAND_BODY}\n"
            )
            write_bootstrap(source, content)
            valid, messages = validate_bootstrap_command(source)
            self.assertFalse(valid)
            self.assertTrue(any("Unexpected key" in m for m in messages), messages)

    def test_bootstrap_rejects_dirname_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "commands" / COMMAND_NAME
            write_bootstrap(source, command_md(name="different-name"))
            valid, messages = validate_bootstrap_command(source)
            self.assertFalse(valid)
            self.assertTrue(any("must match" in m for m in messages), messages)


class CreateCommandTests(unittest.TestCase):
    def test_create_command_installs_command_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            written = create_command(
                root,
                COMMAND_NAME,
                COMMAND_DESCRIPTION,
                "# Test Command\n\nDirect scaffold body.\n",
                overwrite=True,
            )

            skill_path = root / ".agents" / "skills" / f"cmd-{COMMAND_NAME}" / "SKILL.md"
            self.assertEqual(written, [skill_path])
            self.assertTrue(skill_path.is_file())
            frontmatter, _ = parse_frontmatter(skill_path.read_text(encoding="utf-8"))
            assert frontmatter is not None
            self.assertIs(frontmatter.get("disable-model-invocation"), True)

            self.assertFalse((root / ".ai" / "commands").exists())
            self.assertFalse((root / ".cursor" / "commands").exists())
            self.assertFalse((root / ".claude" / "commands").exists())
            self.assertFalse((root / ".github" / "prompts").exists())

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

    def test_create_command_rejects_skill_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                f"cmd-{COMMAND_NAME}",
                skill_md(description="A plain skill.", disable_model_invocation=None),
            )
            with self.assertRaises(CommandCreatorError) as ctx:
                create_command(
                    root,
                    COMMAND_NAME,
                    COMMAND_DESCRIPTION,
                    "# Test Command\n\nBody.\n",
                    overwrite=True,
                )
            self.assertIn("collision", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
