#!/usr/bin/env python3
"""Tests for install_portable_agent.py and bootstrap validation sync checks."""

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
validate_bootstrap_agent = validate_mod.validate_bootstrap_agent
validate_portable_agent = validate_mod.validate_portable_agent
parse_frontmatter = validate_mod.parse_frontmatter
normalize_description = validate_mod.normalize_description
frontmatter = create_mod.frontmatter

AGENT_NAME = "test-agent"
AGENT_DESCRIPTION = "Test agent for unit tests."


def shared_agent_md(*, name: str = AGENT_NAME, description: str = AGENT_DESCRIPTION) -> str:
    return f"""---
name: {name}
description: {description}
---

# {name}

Shared agent body for tests.
"""


def wrapper_agent_md(
    tool: str,
    *,
    name: str = AGENT_NAME,
    description: str = AGENT_DESCRIPTION,
) -> str:
    return f"""---
name: {name}
description: {description}
---

# {name} wrapper for {tool}

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.shared/agents/{name}.md`

Before doing agent work, read that shared file and treat it as the source of truth.

## {tool}-specific information

Reload after install.
"""


def write_bootstrap(
    source: Path,
    *,
    tools: tuple[str, ...] = ("cursor",),
    description: str = AGENT_DESCRIPTION,
) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "AGENT.md").write_text(shared_agent_md(description=description), encoding="utf-8")
    for tool in tools:
        wrapper_dir = source / "wrappers" / tool
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        (wrapper_dir / "AGENT.md").write_text(
            wrapper_agent_md(tool, description=description),
            encoding="utf-8",
        )


class InstallPortableAgentTests(unittest.TestCase):
    def test_no_overwrite_refuses_existing_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))

            wrapper_path = root / ".cursor" / "agents" / f"{AGENT_NAME}.md"
            wrapper_path.parent.mkdir(parents=True, exist_ok=True)
            wrapper_path.write_text("stale wrapper content", encoding="utf-8")

            with self.assertRaises(AgentCreatorError) as ctx:
                install_portable_agent(root, source, AGENT_NAME, overwrite=False)

            self.assertIn(str(wrapper_path), str(ctx.exception))
            self.assertEqual(wrapper_path.read_text(encoding="utf-8"), "stale wrapper content")

    def test_no_overwrite_does_not_write_shared_when_wrapper_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))

            wrapper_path = root / ".cursor" / "agents" / f"{AGENT_NAME}.md"
            wrapper_path.parent.mkdir(parents=True, exist_ok=True)
            wrapper_path.write_text("stale wrapper content", encoding="utf-8")
            shared_path = root / ".shared" / "agents" / f"{AGENT_NAME}.md"

            with self.assertRaises(AgentCreatorError):
                install_portable_agent(root, source, AGENT_NAME, overwrite=False)

            self.assertFalse(shared_path.exists())

    def test_no_overwrite_keeps_stale_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))

            claude_path = root / ".claude" / "agents" / f"{AGENT_NAME}.md"
            claude_path.parent.mkdir(parents=True, exist_ok=True)
            claude_path.write_text("stale claude wrapper", encoding="utf-8")

            install_portable_agent(root, source, AGENT_NAME, overwrite=False)

            self.assertTrue(claude_path.is_file())
            self.assertEqual(claude_path.read_text(encoding="utf-8"), "stale claude wrapper")
            self.assertTrue((root / ".cursor" / "agents" / f"{AGENT_NAME}.md").is_file())

    def test_overwrite_updates_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))

            wrapper_path = root / ".cursor" / "agents" / f"{AGENT_NAME}.md"
            wrapper_path.parent.mkdir(parents=True, exist_ok=True)
            wrapper_path.write_text("stale wrapper content", encoding="utf-8")

            written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            self.assertIn(wrapper_path, written)
            self.assertNotIn("stale wrapper content", wrapper_path.read_text(encoding="utf-8"))
            self.assertIn("../../.shared/agents/test-agent.md", wrapper_path.read_text(encoding="utf-8"))
            self.assertEqual(removed, [])

    def test_overwrite_removes_stale_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor", "claude"))

            install_portable_agent(root, source, AGENT_NAME, overwrite=True)
            claude_path = root / ".claude" / "agents" / f"{AGENT_NAME}.md"
            self.assertTrue(claude_path.is_file())

            (source / "wrappers" / "claude" / "AGENT.md").unlink()
            written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            self.assertFalse(claude_path.is_file())
            self.assertIn(claude_path, removed)
            self.assertTrue((root / ".cursor" / "agents" / f"{AGENT_NAME}.md").is_file())
            self.assertTrue(any(path == claude_path for path in removed))

    def test_sync_description_with_folded_block_wrapper(self) -> None:
        old_description = "Original folded description for wrapper sync test."
        new_description = "Updated shared description after bootstrap edit."
        wrapper_body = """\
# test-agent wrapper for cursor

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.shared/agents/test-agent.md`

Before doing agent work, read that shared file and treat it as the source of truth.

## cursor-specific information

Reload after install.
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            source.mkdir(parents=True, exist_ok=True)
            (source / "AGENT.md").write_text(
                shared_agent_md(description=new_description),
                encoding="utf-8",
            )
            wrapper_dir = source / "wrappers" / "cursor"
            wrapper_dir.mkdir(parents=True, exist_ok=True)
            (wrapper_dir / "AGENT.md").write_text(
                frontmatter(AGENT_NAME, old_description) + "\n" + wrapper_body,
                encoding="utf-8",
            )

            install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            wrapper_path = root / ".cursor" / "agents" / f"{AGENT_NAME}.md"
            wrapper_fm, error = parse_frontmatter(wrapper_path.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            self.assertIsNotNone(wrapper_fm)
            self.assertEqual(
                normalize_description(wrapper_fm["description"]),
                normalize_description(new_description),
            )

    def test_sync_description_preserves_tool_frontmatter(self) -> None:
        new_description = "Updated shared description with preserved wrapper keys."
        wrapper_content = f"""---
name: {AGENT_NAME}
description: {AGENT_DESCRIPTION}
model: claude-opus-4
readonly: true
---

# {AGENT_NAME} wrapper for cursor

This is a tool-specific wrapper. The canonical shared agent definition is:

`../../.shared/agents/{AGENT_NAME}.md`

Before doing agent work, read that shared file and treat it as the source of truth.

## cursor-specific information

Reload after install.
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            source.mkdir(parents=True, exist_ok=True)
            (source / "AGENT.md").write_text(
                shared_agent_md(description=new_description),
                encoding="utf-8",
            )
            wrapper_dir = source / "wrappers" / "cursor"
            wrapper_dir.mkdir(parents=True, exist_ok=True)
            (wrapper_dir / "AGENT.md").write_text(wrapper_content, encoding="utf-8")

            install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            wrapper_path = root / ".cursor" / "agents" / f"{AGENT_NAME}.md"
            wrapper_fm, error = parse_frontmatter(wrapper_path.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            self.assertIsNotNone(wrapper_fm)
            self.assertEqual(
                normalize_description(wrapper_fm["description"]),
                normalize_description(new_description),
            )
            self.assertEqual(wrapper_fm.get("model"), "claude-opus-4")
            self.assertTrue(wrapper_fm.get("readonly"))

    def test_zero_wrapper_bootstrap_installs_shared_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=())

            written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            shared_path = root / ".shared" / "agents" / f"{AGENT_NAME}.md"
            self.assertEqual(written, [shared_path])
            self.assertEqual(removed, [])
            self.assertFalse((root / ".cursor" / "agents" / f"{AGENT_NAME}.md").exists())

    def test_zero_wrapper_overwrite_removes_all_stale_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=())

            stale_paths = [
                root / ".cursor" / "agents" / f"{AGENT_NAME}.md",
                root / ".claude" / "agents" / f"{AGENT_NAME}.md",
                root / ".github" / "agents" / f"{AGENT_NAME}.agent.md",
            ]
            for path in stale_paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("stale direct-scaffold wrapper", encoding="utf-8")

            _written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            for path in stale_paths:
                self.assertFalse(path.is_file())
                self.assertIn(path, removed)

    def test_migration_direct_to_partial_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))

            claude_path = root / ".claude" / "agents" / f"{AGENT_NAME}.md"
            github_path = root / ".github" / "agents" / f"{AGENT_NAME}.agent.md"
            for path in (claude_path, github_path):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("stale direct-scaffold wrapper", encoding="utf-8")

            cursor_path = root / ".cursor" / "agents" / f"{AGENT_NAME}.md"
            cursor_path.parent.mkdir(parents=True, exist_ok=True)
            cursor_path.write_text("stale cursor wrapper", encoding="utf-8")

            _written, removed = install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            self.assertFalse(claude_path.is_file())
            self.assertFalse(github_path.is_file())
            self.assertIn(claude_path, removed)
            self.assertIn(github_path, removed)
            self.assertTrue(cursor_path.is_file())
            self.assertNotIn("stale cursor wrapper", cursor_path.read_text(encoding="utf-8"))


class PortableValidationTests(unittest.TestCase):
    def test_partial_wrapper_set_passes_portable_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))
            install_portable_agent(root, source, AGENT_NAME, overwrite=True)

            valid, messages = validate_portable_agent(root, AGENT_NAME)

            self.assertTrue(valid)
            self.assertTrue(
                any("valid across 2 installed file(s)" in message for message in messages)
            )


class BootstrapValidationTests(unittest.TestCase):
    def test_description_mismatch_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "agents" / AGENT_NAME
            write_bootstrap(source, tools=("cursor",))
            wrapper_path = source / "wrappers" / "cursor" / "AGENT.md"
            wrapper_path.write_text(
                wrapper_agent_md("cursor", description="Different description."),
                encoding="utf-8",
            )

            valid, messages = validate_bootstrap_agent(source)

            self.assertFalse(valid)
            self.assertTrue(
                any("description does not match shared agent description" in message for message in messages)
            )


if __name__ == "__main__":
    unittest.main()
