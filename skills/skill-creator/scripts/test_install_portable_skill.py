#!/usr/bin/env python3
"""Tests for install_portable_skill.py description sync behavior."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
AGENT_SCRIPTS_DIR = SCRIPTS_DIR.parents[1] / "agent-creator" / "scripts"
for path in (str(AGENT_SCRIPTS_DIR), str(SCRIPTS_DIR)):
    while path in sys.path:
        sys.path.remove(path)
sys.path.insert(0, str(SCRIPTS_DIR))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


for mod_name in (
    "quick_validate",
    "install_portable_skill",
    "scaffold_skill",
    "create_agent",
    "install_portable_agent",
):
    sys.modules.pop(mod_name, None)

validate_mod = load_module(
    "skill_quick_validate_test",
    SCRIPTS_DIR / "quick_validate.py",
)
create_mod = load_module(
    "create_agent_test_for_skill",
    AGENT_SCRIPTS_DIR / "create_agent.py",
)

install_mod = load_module(
    "install_portable_skill_test",
    SCRIPTS_DIR / "install_portable_skill.py",
)

install_portable_skill = install_mod.install_portable_skill
parse_frontmatter = validate_mod.parse_frontmatter
frontmatter = create_mod.frontmatter

SKILL_NAME = "test-skill"
SKILL_DESCRIPTION = "Test skill for unit tests."
UPDATED_DESCRIPTION = "Updated shared skill description after bootstrap edit."


def normalize_description(description: str) -> str:
    return " ".join(description.strip().split())


def shared_skill_md(*, description: str = SKILL_DESCRIPTION) -> str:
    return f"""---
name: {SKILL_NAME}
description: {description}
---

# Test Skill

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`.

Shared skill body for tests.
"""


def write_bootstrap(
    source: Path,
    *,
    wrapper_content: str | None = None,
    description: str = SKILL_DESCRIPTION,
) -> None:
    source.mkdir(parents=True, exist_ok=True)
    (source / "SKILL.md").write_text(shared_skill_md(description=description), encoding="utf-8")
    if wrapper_content is not None:
        wrapper_dir = source / "wrappers" / "cursor"
        wrapper_dir.mkdir(parents=True, exist_ok=True)
        (wrapper_dir / "SKILL.md").write_text(wrapper_content, encoding="utf-8")


class InstallPortableSkillTests(unittest.TestCase):
    def test_sync_description_with_folded_block_wrapper(self) -> None:
        old_description = "Original folded description for wrapper sync test."
        wrapper_body = """\
# test-skill wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/test-skill/SKILL.md`

Before following this skill, read that shared `SKILL.md` first.
"""
        wrapper_content = frontmatter(SKILL_NAME, old_description) + "\n" + wrapper_body

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(
                source,
                wrapper_content=wrapper_content,
                description=UPDATED_DESCRIPTION,
            )

            install_portable_skill(
                root,
                source,
                SKILL_NAME,
                overwrite=True,
            )

            wrapper_path = root / ".cursor" / "skills" / SKILL_NAME / "SKILL.md"
            wrapper_fm, error = parse_frontmatter(wrapper_path.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            self.assertIsNotNone(wrapper_fm)
            self.assertEqual(
                normalize_description(wrapper_fm["description"]),
                normalize_description(UPDATED_DESCRIPTION),
            )

    def test_sync_description_preserves_tool_frontmatter(self) -> None:
        wrapper_content = f"""---
name: {SKILL_NAME}
description: {SKILL_DESCRIPTION}
disable-model-invocation: true
---

# test-skill wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/{SKILL_NAME}/SKILL.md`

Before following this skill, read that shared `SKILL.md` first.
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "skills" / SKILL_NAME
            write_bootstrap(
                source,
                wrapper_content=wrapper_content,
                description=UPDATED_DESCRIPTION,
            )

            install_portable_skill(
                root,
                source,
                SKILL_NAME,
                overwrite=True,
            )

            wrapper_path = root / ".cursor" / "skills" / SKILL_NAME / "SKILL.md"
            wrapper_fm, error = parse_frontmatter(wrapper_path.read_text(encoding="utf-8"))
            self.assertIsNone(error)
            self.assertIsNotNone(wrapper_fm)
            self.assertEqual(
                normalize_description(wrapper_fm["description"]),
                normalize_description(UPDATED_DESCRIPTION),
            )
            self.assertTrue(wrapper_fm.get("disable-model-invocation"))


if __name__ == "__main__":
    unittest.main()
