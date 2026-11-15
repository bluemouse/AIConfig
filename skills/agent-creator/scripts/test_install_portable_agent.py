#!/usr/bin/env python3
"""Tests for install_portable_agent.py dual-target install and validation."""

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


install_mod = load_module("install_portable_agent_test", SCRIPTS_DIR / "install_portable_agent.py")
validate_mod = load_module("quick_validate_test", SCRIPTS_DIR / "quick_validate.py")
create_mod = load_module("create_agent_test", SCRIPTS_DIR / "create_agent.py")

AgentCreatorError = install_mod.AgentCreatorError
install_portable_agent = install_mod.install_portable_agent
detect_mode = validate_mod.detect_mode
validate_agent = validate_mod.validate_agent
validate_bootstrap_agent = validate_mod.validate_bootstrap_agent
validate_portable_agent = validate_mod.validate_portable_agent
parse_frontmatter = validate_mod.parse_frontmatter
normalize_description = validate_mod.normalize_description
create_agent = create_mod.create_agent

AGENT_NAME = "test-agent"
AGENT_DESCRIPTION = "Test agent for unit tests."

NEUTRAL_BODY = (
    "# test-agent\n"
    "\n"
    "Shared agent body for tests. Review the diff and report findings.\n"
)

TOOL_NOTES_BODY = (
    NEUTRAL_BODY
    + "\n"
    + "## Tool notes\n"
    + "\n"
    + "### Claude Code\n"
    + "\n"
    + "Restart or reload the Claude Code session after editing this agent.\n"
    + "\n"
    + "### GitHub Copilot\n"
    + "\n"
    + "Reload VS Code after editing this agent so Copilot rediscovers it.\n"
)


def agent_md(
    body: str = NEUTRAL_BODY,
    *,
    name: str = AGENT_NAME,
    description: str = AGENT_DESCRIPTION,
    extra_lines: tuple[str, ...] = (),
) -> str:
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        *extra_lines,
        "---",
        "",
    ]
    return "\n".join(lines) + body


def write_bootstrap(
    source: Path,
    body: str = NEUTRAL_BODY,
    *,
    name: str = AGENT_NAME,
    description: str = AGENT_DESCRIPTION,
    extra_lines: tuple[str, ...] = (),
) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "AGENT.md").write_text(
        agent_md(body, name=name, description=description, extra_lines=extra_lines),
        encoding="utf-8",
    )


def claude_path(root: Path, name: str = AGENT_NAME) -> Path:
    return root / ".claude" / "agents" / f"{name}.md"


def github_path(root: Path, name: str = AGENT_NAME) -> Path:
    return root / ".github" / "agents" / f"{name}.agent.md"


class InstallDualTargetTests(unittest.TestCase):
    def test_agent_dual_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)

            written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            claude_target = claude_path(root)
            github_target = github_path(root)
            self.assertTrue(claude_target.is_file())
            self.assertTrue(github_target.is_file())
            self.assertEqual(written, [claude_target, github_target])
            self.assertEqual(removed, [])

            # Claude Code target is the real content, verbatim from AGENT.md.
            source_content = (source / "AGENT.md").read_text(encoding="utf-8")
            self.assertEqual(claude_target.read_text(encoding="utf-8"), source_content)

            # GitHub Copilot target carries the real body plus matching frontmatter.
            github_content = github_target.read_text(encoding="utf-8")
            github_fm, error = parse_frontmatter(github_content)
            self.assertIsNone(error)
            self.assertIsNotNone(github_fm)
            self.assertEqual(github_fm["name"], AGENT_NAME)
            self.assertEqual(github_fm["description"], AGENT_DESCRIPTION)
            self.assertIn("Shared agent body for tests.", github_content)

            # No shared layer and no wrapper outputs.
            self.assertFalse((root / ".ai" / "agents" / f"{AGENT_NAME}.md").exists())
            self.assertFalse((root / ".ai").exists())
            self.assertFalse((root / ".cursor").exists())

    def test_github_transform_drops_claude_only_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, extra_lines=("model: inherit", "tools: Read, Grep, Glob, Bash"))

            install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            claude_target = claude_path(root)
            github_target = github_path(root)
            source_content = (source / "AGENT.md").read_text(encoding="utf-8")
            self.assertEqual(claude_target.read_text(encoding="utf-8"), source_content)
            self.assertIn("model: inherit", claude_target.read_text(encoding="utf-8"))

            github_fm, error = parse_frontmatter(github_target.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            self.assertIsNotNone(github_fm)
            self.assertEqual(set(github_fm.keys()), {"name", "description"})
            self.assertNotIn("model", github_target.read_text(encoding="utf-8"))
            self.assertNotIn("tools:", github_target.read_text(encoding="utf-8"))

    def test_no_overwrite_refuses_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)

            claude_target = claude_path(root)
            claude_target.parent.mkdir(parents=True, exist_ok=True)
            claude_target.write_text("stale target content", encoding="utf-8")

            with self.assertRaises(AgentCreatorError) as ctx:
                install_portable_agent(root, source, AGENT_NAME, overwrite=False)

            self.assertIn(str(claude_target), str(ctx.exception))
            self.assertEqual(claude_target.read_text(encoding="utf-8"), "stale target content")
            self.assertFalse(github_path(root).exists())

    def test_overwrite_removes_legacy_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)

            legacy_paths = [
                root / ".ai" / "agents" / f"{AGENT_NAME}.md",
                root / ".cursor" / "agents" / f"{AGENT_NAME}.md",
            ]
            for path in legacy_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("legacy output", encoding="utf-8")

            _written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            for path in legacy_paths:
                self.assertFalse(path.is_file())
                self.assertIn(path, removed)
            self.assertTrue(claude_path(root).is_file())
            self.assertTrue(github_path(root).is_file())

    def test_no_overwrite_leaves_legacy_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)

            legacy_shared = root / ".ai" / "agents" / f"{AGENT_NAME}.md"
            legacy_shared.parent.mkdir(parents=True, exist_ok=True)
            legacy_shared.write_text("legacy shared output", encoding="utf-8")

            _written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=False)

            self.assertEqual(removed, [])
            self.assertEqual(legacy_shared.read_text(encoding="utf-8"), "legacy shared output")
            self.assertTrue(claude_path(root).is_file())
            self.assertTrue(github_path(root).is_file())

    def test_name_mismatch_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, name="other-agent")

            with self.assertRaises(AgentCreatorError) as ctx:
                install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            self.assertIn("other-agent", str(ctx.exception))
            self.assertFalse(claude_path(root).exists())
            self.assertFalse(github_path(root).exists())

    def test_missing_description_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, description="")

            with self.assertRaises(AgentCreatorError) as ctx:
                install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            self.assertIn("description", str(ctx.exception))
            self.assertFalse(claude_path(root).exists())

    def test_missing_agent_md_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            source.mkdir(parents=True, exist_ok=True)

            with self.assertRaises(AgentCreatorError) as ctx:
                install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            self.assertIn("AGENT.md", str(ctx.exception))


class CreateAgentTests(unittest.TestCase):
    def test_create_agent_dual_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            written = create_agent(
                root=root,
                name=AGENT_NAME,
                description=AGENT_DESCRIPTION,
                instructions="Direct scaffold body for tests.",
                overwrite=True,
            )

            claude_target = claude_path(root)
            github_target = github_path(root)
            self.assertEqual(set(written), {claude_target, github_target})
            self.assertTrue(claude_target.is_file())
            self.assertTrue(github_target.is_file())

            claude_fm, error = parse_frontmatter(claude_target.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            self.assertEqual(claude_fm["name"], AGENT_NAME)
            self.assertIn("Direct scaffold body for tests.", claude_target.read_text(encoding="utf-8"))

            github_fm, github_error = parse_frontmatter(github_target.read_text(encoding="utf-8"))
            self.assertIsNone(github_error)
            self.assertEqual(github_fm["name"], AGENT_NAME)
            self.assertEqual(
                normalize_description(github_fm["description"]),
                normalize_description(AGENT_DESCRIPTION),
            )
            self.assertIn("Direct scaffold body for tests.", github_target.read_text(encoding="utf-8"))

            self.assertFalse((root / ".ai").exists())
            self.assertFalse((root / ".cursor").exists())


class BootstrapValidationTests(unittest.TestCase):
    def test_agent_tool_notes_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, body=TOOL_NOTES_BODY)

            valid, messages = validate_bootstrap_agent(source)
            self.assertTrue(valid, msg="\n".join(messages))
            self.assertTrue(any("Bootstrap agent 'test-agent' is valid." in m for m in messages))

            # Installed targets with Tool notes also pass validation.
            install_portable_agent(root, source, AGENT_NAME, overwrite=True)
            for target in (claude_path(root), github_path(root)):
                target_valid, target_message = validate_agent(target)
                self.assertTrue(target_valid, msg=f"{target}: {target_message}")

    def test_tool_specific_body_outside_tool_notes_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "agents" / AGENT_NAME
            write_bootstrap(source, body="# test-agent\n\nUse the Task tool to dispatch subagents.\n")

            valid, messages = validate_bootstrap_agent(source)

            self.assertFalse(valid)
            self.assertTrue(any("Tool notes" in message for message in messages))

    def test_bootstrap_missing_description_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "agents" / AGENT_NAME
            write_bootstrap(source, description="")

            valid, messages = validate_bootstrap_agent(source)

            self.assertFalse(valid)
            self.assertTrue(any("description" in message.lower() for message in messages))


class WrapperValidationRemovedTests(unittest.TestCase):
    def test_wrapper_validation_removed(self) -> None:
        for symbol in (
            "validate_wrapper_agent",
            "check_wrapper_sync",
            "RELATIVE_SHARED_PATH",
            "WRAPPER_PATHS",
            "expected_wrapper_tools",
        ):
            self.assertFalse(
                hasattr(validate_mod, symbol),
                msg=f"quick_validate.py still defines wrapper-mode symbol: {symbol}",
            )

    def test_detect_mode_returns_bootstrap_claude_github_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            modes = {
                root / "agents" / AGENT_NAME / "AGENT.md": "bootstrap",
                claude_path(root): "claude",
                root / ".ai" / "agents" / f"{AGENT_NAME}.md": "claude",
                github_path(root): "github",
            }
            for path, expected in modes.items():
                self.assertEqual(detect_mode(path), expected, msg=str(path))


class PortableValidationTests(unittest.TestCase):
    def test_validate_portable_agent_checks_both_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)
            install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            valid, messages = validate_portable_agent(root, AGENT_NAME)

            self.assertTrue(valid, msg="\n".join(messages))
            self.assertTrue(
                any("valid across 2 installed file(s)" in message for message in messages)
            )

    def test_validate_portable_agent_missing_target_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)
            install_portable_agent(root, source, AGENT_NAME, overwrite=True)
            github_path(root).unlink()

            valid, messages = validate_portable_agent(root, AGENT_NAME)

            self.assertFalse(valid)
            self.assertTrue(any("not found" in message for message in messages))

    def test_validate_portable_agent_description_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source)
            install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            github_target = github_path(root)
            github_target.write_text(
                agent_md(description="Drifted description for tests."),
                encoding="utf-8",
            )

            valid, messages = validate_portable_agent(root, AGENT_NAME)

            self.assertFalse(valid)
            self.assertTrue(
                any("description" in message.lower() for message in messages),
                msg="\n".join(messages),
            )


if __name__ == "__main__":
    unittest.main()
