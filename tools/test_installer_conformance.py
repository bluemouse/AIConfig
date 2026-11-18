#!/usr/bin/env python3
"""Conformance tests for the cr-010 twin sites.

tools/installer.py and the bootstrap skill/command scripts re-declare the
same directory-layout constants and command-flag semantics in independent
script directories (bootstrap layout mandates that). Cross-reference
comments hold the duplicates together; these tests mechanically assert the
sites still agree:

- t-009: shared .agents/skills/ dir constants and the cmd- prefix
- t-010: is_command_skill verdicts on a well-formed input matrix
- t-011: the "disable-model-invocation" flag literal, plus the documented
  intentional parse divergence on embedded `---` lines
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

INSTALLER_PATH = TOOLS_DIR / "installer.py"
IPS_PATH = (
    REPO_ROOT / "skills" / "skill-creator" / "scripts" / "install_portable_skill.py"
)
SC_QV_PATH = IPS_PATH.parent / "quick_validate.py"
SCAFFOLD_COMMAND_PATH = (
    REPO_ROOT / "skills" / "command-creator" / "scripts" / "scaffold_command.py"
)
CC_QV_PATH = (
    REPO_ROOT / "skills" / "command-creator" / "scripts" / "quick_validate.py"
)


def load_script_module(
    path: Path,
    module_name: str,
    sibling_names: tuple[str, ...] = (),
) -> tuple[types.ModuleType, dict[str, types.ModuleType]]:
    """Load a script by file path, isolating its sibling imports.

    Bootstrap scripts import siblings (`quick_validate`, `scaffold_skill`)
    from their own directory, which a bare spec_from_file_location cannot
    resolve. Pre-existing sys.modules entries of those names (another test
    file may have registered a different directory's module) are stashed and
    restored, entries this load creates are removed afterwards, and the
    scripts dir sits on sys.path only for the duration of the exec — the
    same isolation pattern as tools/installer.py::_load_ensure_bridge_
    symlink. Returns the module and the sibling modules this exec created
    (they stay alive via the loaded module's own namespace after cleanup).
    """
    stashed = {
        name: sys.modules.pop(name)
        for name in sibling_names
        if name in sys.modules
    }
    old_path = list(sys.path)
    created: dict[str, types.ModuleType] = {}
    try:
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load module from {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        for name in sibling_names:
            sibling = sys.modules.get(name)
            if sibling is not None:
                created[name] = sibling
    finally:
        sys.path[:] = old_path
        for name in sibling_names:
            sys.modules.pop(name, None)
        sys.modules.update(stashed)
    return module, created


installer_mod, _ = load_script_module(INSTALLER_PATH, "conformance_installer")

# install_portable_skill.py pulls parse_frontmatter (and more) from its
# sibling quick_validate/scaffold_skill — capture those so later assertions
# can prove which quick_validate the module actually wired to.
ips_mod, ips_siblings = load_script_module(
    IPS_PATH,
    "conformance_install_portable_skill",
    sibling_names=("quick_validate", "scaffold_skill"),
)
skill_creator_qv = ips_siblings["quick_validate"]

cc_qv_mod, _ = load_script_module(CC_QV_PATH, "conformance_command_quick_validate")

scaffold_command_mod, scaffold_siblings = load_script_module(
    SCAFFOLD_COMMAND_PATH,
    "conformance_scaffold_command",
    sibling_names=("quick_validate",),
)
cc_qv_via_scaffold = scaffold_siblings["quick_validate"]


class ModuleScaffoldTests(unittest.TestCase):
    """Prove the by-path loading scaffold before t-009/t-010/t-011 rely on it.

    Each twin site must be the module from its own script directory — a
    mis-wired sibling import would silently compare one file against itself
    and pass vacuously.
    """

    def test_expected_attributes_present(self) -> None:
        self.assertTrue(hasattr(installer_mod, "SHARED_SKILL_DIR"))
        self.assertTrue(hasattr(installer_mod, "COMMAND_SKILL_DIR_PREFIX"))
        self.assertTrue(hasattr(installer_mod, "COMMAND_SKILL_DIR"))
        self.assertTrue(hasattr(installer_mod, "COMMAND_SKILL_FLAG"))
        self.assertTrue(callable(installer_mod.is_command_skill))
        self.assertTrue(hasattr(ips_mod, "SHARED_SKILL_DIR"))
        self.assertTrue(callable(ips_mod.is_command_skill))
        self.assertTrue(callable(scaffold_command_mod.is_command_skill))
        self.assertTrue(callable(scaffold_command_mod.command_skill_content))
        self.assertTrue(hasattr(cc_qv_mod, "COMMAND_SKILL_DIR_PARTS"))
        self.assertTrue(callable(cc_qv_mod.command_skill_dir_name))

    def test_sibling_import_wiring(self) -> None:
        # install_portable_skill's parse_frontmatter must be the
        # skill-creator quick_validate, not a same-named module from
        # another directory (e.g. command-creator's).
        self.assertIs(ips_mod.parse_frontmatter, skill_creator_qv.parse_frontmatter)
        self.assertEqual(
            Path(skill_creator_qv.__file__).resolve(), SC_QV_PATH.resolve()
        )
        self.assertNotEqual(
            Path(skill_creator_qv.__file__).resolve(), CC_QV_PATH.resolve()
        )
        self.assertIn("scaffold_skill", ips_siblings)
        # scaffold_command wires to the command-creator quick_validate.
        self.assertIs(
            scaffold_command_mod.parse_frontmatter, cc_qv_via_scaffold.parse_frontmatter
        )
        self.assertEqual(
            Path(cc_qv_via_scaffold.__file__).resolve(), CC_QV_PATH.resolve()
        )


class SharedSkillDirConstantsTests(unittest.TestCase):
    """t-009: every dir-layout constant site resolves to the same install paths."""

    def test_shared_skill_dir_constants_agree(self) -> None:
        """All sites that declare a dir-layout constant agree on .agents/skills/.

        Sites under test: installer.py:SHARED_SKILL_DIR,
        install_portable_skill.py:SHARED_SKILL_DIR, and command-creator
        quick_validate.py:COMMAND_SKILL_DIR_PARTS (joined with a sample
        name). scaffold_command.py is an exempt site by design: it builds
        command-skill content, not install paths, and declares no
        dir-layout constant — every dir path it touches flows in from
        quick_validate's helpers. The absence is pinned below so a new
        constant appearing there gets consciously routed through this test.
        """
        self.assertEqual(installer_mod.SHARED_SKILL_DIR, ips_mod.SHARED_SKILL_DIR)
        self.assertEqual(installer_mod.COMMAND_SKILL_DIR_PREFIX, cc_qv_mod.COMMAND_SKILL_DIR_PREFIX)

        for name in ("demo", "commit-message"):
            with self.subTest(name=name):
                expected_shared = Path(".agents") / "skills" / name
                self.assertEqual(
                    Path(installer_mod.SHARED_SKILL_DIR.format(name=name)),
                    expected_shared,
                )
                self.assertEqual(
                    Path(ips_mod.SHARED_SKILL_DIR.format(name=name)),
                    expected_shared,
                )
                self.assertEqual(
                    Path(*cc_qv_mod.COMMAND_SKILL_DIR_PARTS) / name,
                    expected_shared,
                )
                # The cmd- prefix installer strips is the one command-creator
                # embeds in command_skill_dir_name.
                self.assertEqual(
                    cc_qv_mod.command_skill_dir_name(name),
                    installer_mod.COMMAND_SKILL_DIR_PREFIX + name,
                )
                expected_command = (
                    Path(*cc_qv_mod.COMMAND_SKILL_DIR_PARTS)
                    / cc_qv_mod.command_skill_dir_name(name)
                )
                self.assertEqual(
                    Path(installer_mod.COMMAND_SKILL_DIR.format(name=name)),
                    expected_command,
                )

        for attr in (
            "SHARED_SKILL_DIR",
            "COMMAND_SKILL_DIR",
            "COMMAND_SKILL_DIR_PARTS",
            "COMMAND_SKILL_DIR_PREFIX",
        ):
            with self.subTest(exempt_attr=attr):
                self.assertFalse(
                    hasattr(scaffold_command_mod, attr),
                    "scaffold_command.py is the documented no-dir-constant "
                    f"exemption; a new {attr} there must join this conformance "
                    "test or route through quick_validate helpers",
                )


class IsCommandSkillMatrixTests(unittest.TestCase):
    """t-010: is_command_skill verdicts agree across the three twin sites."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def _write(self, relative: str, content: str) -> Path:
        skill_md = self.tmp / relative
        skill_md.parent.mkdir(parents=True, exist_ok=True)
        skill_md.write_text(content, encoding="utf-8")
        return skill_md

    def test_is_command_skill_matrix_agrees(self) -> None:
        """Identical verdicts from installer.py, install_portable_skill.py,
        and scaffold_command.py on a WELL-FORMED input matrix.

        Embedded-`---` inputs are EXCLUDED by design: installer.py's
        parse_frontmatter was fixed to find the true closing delimiter,
        while the twins deliberately keep the old non-greedy regex. That
        accepted divergence is asserted in t-011
        (test_command_flag_literal_agrees) and pinned for installer.py by
        tools/test_installer_tooltips.py::ParseFrontmatterEmbeddedDelimTests.
        """
        plain_md = self._write(
            "demo/SKILL.md",
            "---\nname: demo\ndescription: plain skill\n---\n\n# demo\n",
        )
        command_md = self._write(
            "cmd-demo/SKILL.md",
            "---\n"
            "name: demo\n"
            "description: explicitly invokes the demo command\n"
            "disable-model-invocation: true\n"
            "---\n"
            "\n"
            "# demo\n",
        )
        malformed_md = self._write(
            "malformed/SKILL.md",
            "---\nname: demo\ndescription: plain skill\n",
        )
        missing_md = self.tmp / "missing" / "SKILL.md"
        # A path that exists but is not a file: is_file() is False in all
        # three implementations, exercising the same unreadable-shape guard.
        unreadable = self.tmp / "unreadable"
        unreadable.mkdir()

        cases = [
            ("plain skill", plain_md, False),
            ("command skill", command_md, True),
            ("malformed frontmatter (unclosed)", malformed_md, False),
            ("missing file", missing_md, False),
            ("unreadable (path is a directory)", unreadable, False),
        ]
        for label, skill_md, expected in cases:
            with self.subTest(case=label):
                verdicts = {
                    "installer": installer_mod.is_command_skill(skill_md),
                    "install_portable_skill": ips_mod.is_command_skill(skill_md),
                    "scaffold_command": scaffold_command_mod.is_command_skill(skill_md),
                }
                self.assertEqual(
                    len(set(verdicts.values())), 1, f"verdicts diverged: {verdicts}"
                )
                self.assertEqual(verdicts["installer"], expected)


class CommandFlagLiteralTests(unittest.TestCase):
    """t-011: the command flag literal agrees across all sites that use it."""

    FLAG_SITES = {
        "tools/installer.py": INSTALLER_PATH,
        "skill-creator/install_portable_skill.py": IPS_PATH,
        "skill-creator/quick_validate.py": SC_QV_PATH,
        "command-creator/scaffold_command.py": SCAFFOLD_COMMAND_PATH,
        "command-creator/quick_validate.py": CC_QV_PATH,
    }

    @staticmethod
    def _ast_nodes(path: Path) -> list[ast.AST]:
        source = path.read_text(encoding="utf-8")
        return [node for node in ast.walk(ast.parse(source, filename=str(path)))]

    def test_command_flag_literal_agrees(self) -> None:
        """The "disable-model-invocation" literal is identical at every site.

        Each site's source must contain the exact flag literal (AST string
        constants — docstrings and comments mentioning the flag in prose do
        not count), every frontmatter.get() key that names the flag must be
        the exact literal, and the runtime key sets/flag constant must carry
        it. Also documents the accepted parse divergence: on an embedded
        column-0 `--- `-prefixed line, installer.py's equality scan finds
        the true closing delimiter and rejects the malformed marker (None),
        while the twin quick_validate regexes silently truncate at the first
        `---`-prefixed line — installer.py's behavior is pinned by
        tools/test_installer_tooltips.py::ParseFrontmatterEmbeddedDelimTests,
        and embedded inputs are excluded from t-010's matrix by design.
        """
        flag = installer_mod.COMMAND_SKILL_FLAG
        self.assertEqual(flag, "disable-model-invocation")

        for label, path in self.FLAG_SITES.items():
            with self.subTest(site=label):
                nodes = self._ast_nodes(path)
                literals = [
                    node.value
                    for node in nodes
                    if isinstance(node, ast.Constant) and isinstance(node.value, str)
                ]
                self.assertIn(flag, literals)
                for node in nodes:
                    if (
                        isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "get"
                        and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)
                        and "invocation" in node.args[0].value
                    ):
                        self.assertEqual(node.args[0].value, flag)

        self.assertIn(flag, skill_creator_qv.ALLOWED_PROPERTIES)
        self.assertIn(flag, cc_qv_mod.COMMAND_SKILL_ALLOWED_KEYS)

        # scaffold_command writes the flag; the command-creator parser
        # reads it back — a closed loop over both literal-bearing sites.
        content = scaffold_command_mod.command_skill_content(
            "demo", "explicitly invokes the demo command", "Demo body.\n"
        )
        parsed, error = cc_qv_mod.parse_frontmatter(content)
        self.assertIsNone(error)
        assert parsed is not None
        self.assertIs(parsed[flag], True)

        # Accepted divergence (see docstring): the twins keep the old
        # non-greedy regex, so an embedded `--- ` line silently truncates
        # instead of failing like installer.py's fixed scan.
        embedded = (
            "---\n"
            "name: my-skill\n"
            "description: >-\n"
            "  line one\n"
            "--- \n"
            "  line two\n"
            "---\n"
            "body\n"
        )
        self.assertIsNone(installer_mod.parse_frontmatter(embedded))
        for twin_label, twin in (
            ("skill-creator/quick_validate.py", skill_creator_qv),
            ("command-creator/quick_validate.py", cc_qv_mod),
        ):
            with self.subTest(twin=twin_label):
                frontmatter, error = twin.parse_frontmatter(embedded)
                self.assertIsNone(error)
                self.assertEqual(
                    frontmatter, {"name": "my-skill", "description": "line one"}
                )


if __name__ == "__main__":
    unittest.main()
