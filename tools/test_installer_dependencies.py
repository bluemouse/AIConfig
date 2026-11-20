#!/usr/bin/env python3
"""Tests for the installer dependency map (tools/dependencies.json).

Covers the plan in
.agents/workflow/installer-dependency-map/20-implementation-plan.md:

- t-001: the map loads and every target is a discovered plain skill
- t-002: selecting a command pulls its transitive skill closure
- t-003: unknown / prefixed / non-skill targets error
- t-004: closure is transitive across multiple levels
- t-005: resolve_cli_selection expands install selections (explicit + bundle)
- t-006: uninstall selections never expand (gate seam:
  resolve_cli_selection(uninstall=True))
- t-007: (pg-003) GUI wiring + bundle path routing
- t-008/t-009: (pg-004) map-vs-body consistency, forward + curated-reverse

Run from the repository root: python -m pytest tools/test_installer_dependencies.py -q
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"
REPO_ROOT = TOOLS_DIR.parent


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_deps", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_deps"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()


def write_skill(root: Path, name: str) -> None:
    """Write a plain skill under root/.agents/skills/<name>/."""
    skill_md = root / ".agents" / "skills" / name / "SKILL.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(
        f"---\nname: {name}\ndescription: {name} skill\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def write_command_skill(root: Path, name: str) -> None:
    """Write a command-skill (cmd-<name>/SKILL.md) under .agents/skills/.

    The flag mirrors is_command_skill: a command is a skill whose frontmatter
    carries disable-model-invocation: true.
    """
    skill_md = root / ".agents" / "skills" / f"cmd-{name}" / "SKILL.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(
        f"---\nname: cmd-{name}\ndescription: {name} command\n"
        "disable-model-invocation: true\n---\n\n"
        f"# {name}\n",
        encoding="utf-8",
    )


def write_map(root: Path, payload: dict) -> Path:
    """Write a dependency map at root/tools/dependencies.json."""
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    path = tools / "dependencies.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class MapLoadingTests(unittest.TestCase):
    """t-001, t-003: map loading and target validation."""

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def test_map_loads_and_every_target_is_discovered_skill(self) -> None:
        # t-001: a valid map loads; every target is a discovered plain skill.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "skill-a")
            write_skill(root, "skill-b")
            write_map(root, {"skills": {"skill-a": {"depends": ["skill-b"]}}})
            mod.REPO_ROOT = root
            deps = mod.load_dependencies()
            self.assertEqual(
                deps["skills"], {"skill-a": {"depends": ["skill-b"]}}
            )
            self.assertEqual(deps["commands"], {})
            self.assertEqual(deps["agents"], {})

    def test_missing_map_file_is_empty(self) -> None:
        # Back-compat: an older checkout without a map resolves no edges.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "skill-a")
            mod.REPO_ROOT = root
            self.assertEqual(mod.load_dependencies(), {})

    def test_unknown_target_errors(self) -> None:
        # t-003: an edge naming an unknown member raises with the edge named.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "skill-a")
            write_map(
                root,
                {"commands": {"cmd-x": {"depends": ["typo-name"]}}},
            )
            mod.REPO_ROOT = root
            with self.assertRaises(mod.InstallerError) as ctx:
                mod.load_dependencies()
            self.assertIn("typo-name", str(ctx.exception))
            self.assertIn("cmd-x", str(ctx.exception))

    def test_prefixed_and_non_skill_targets_error(self) -> None:
        # t-003 (rr-003/rr-005): guidelines- and cmd- prefixed targets are
        # rejected, and an agent-only name is not a valid skill target.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "shared-name")
            write_map(
                root,
                {
                    "skills": {
                        "shared-name": {
                            "depends": ["guidelines-response", "cmd-commit"]
                        }
                    }
                },
            )
            mod.REPO_ROOT = root
            with self.assertRaises(mod.InstallerError):
                mod.load_dependencies()

            # An agent-only name (no skill of that name) is also rejected.
            write_map(root, {"skills": {"shared-name": {"depends": ["agent-only"]}}})
            with self.assertRaises(mod.InstallerError):
                mod.load_dependencies()

    def test_target_colliding_with_agent_name_means_skill(self) -> None:
        # A name existing as both skill and agent always means the skill.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "shared-name")
            write_map(root, {"agents": {"agent-x": {"depends": ["shared-name"]}}})
            mod.REPO_ROOT = root
            deps = mod.load_dependencies()
            self.assertIn("shared-name", deps["agents"]["agent-x"]["depends"])


class ResolverTests(unittest.TestCase):
    """t-002, t-004, t-006: closure computation and install-only gating."""

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def test_select_command_pulls_transitive_skills(self) -> None:
        # t-002: command -> engine + mid, and mid -> leaf transitively.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_skill(root, "mid")
            write_skill(root, "leaf")
            write_map(
                root,
                {
                    "commands": {"starter": {"depends": ["engine", "mid"]}},
                    "skills": {"mid": {"depends": ["leaf"]}},
                },
            )
            mod.REPO_ROOT = root
            selection = mod.BundleSelection(
                skills=[], agents=[], commands=["starter"]
            )
            resolved = mod.resolve_dependencies(selection, uninstall=False)
            self.assertEqual(resolved.skills, ["engine", "leaf", "mid"])
            self.assertEqual(resolved.commands, ["starter"])

    def test_closure_transitive_multi_level(self) -> None:
        # t-004: a three-level chain resolves fully.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("top", "middle", "bottom"):
                write_skill(root, name)
            write_map(
                root,
                {
                    "skills": {
                        "top": {"depends": ["middle"]},
                        "middle": {"depends": ["bottom"]},
                    }
                },
            )
            mod.REPO_ROOT = root
            selection = mod.BundleSelection(skills=["top"], agents=[], commands=[])
            resolved = mod.resolve_dependencies(selection, uninstall=False)
            self.assertEqual(resolved.skills, ["bottom", "middle", "top"])

    def test_uninstall_selection_not_expanded(self) -> None:
        # t-006: the gate seam — resolve_cli_selection with uninstall=True
        # must return the selection unexpanded, while the same inputs with
        # uninstall=False expand. Red phase: the paired install-mode
        # assertion fails pre-implementation (no expansion exists); the
        # uninstall-half guards the gate in green.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            base = dict(
                bundle_ids=None,
                skill_names=None,
                agent_names=None,
                command_names=["starter"],
                guideline_names=None,
                target_root=root,
            )
            install_sel = mod.resolve_cli_selection(**base, uninstall=False)
            self.assertEqual(install_sel.skills, ["engine"])
            self.assertEqual(install_sel.commands, ["starter"])

            uninstall_sel = mod.resolve_cli_selection(**base, uninstall=True)
            self.assertEqual(uninstall_sel.skills, [])
            self.assertEqual(uninstall_sel.commands, ["starter"])

    def test_resolver_idempotent_and_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            selection = mod.BundleSelection(skills=["engine"], agents=[], commands=["starter"])
            once = mod.resolve_dependencies(selection, uninstall=False)
            twice = mod.resolve_dependencies(once, uninstall=False)
            self.assertEqual(once.skills, twice.skills)


class SelectionWiringTests(unittest.TestCase):
    """t-005, t-007: resolve_cli_selection expansion for explicit and bundle paths."""

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def test_explicit_selection_expands(self) -> None:
        # t-005 explicit: --commands starter expands to the engine skill.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            selection = mod.resolve_cli_selection(
                bundle_ids=None,
                skill_names=None,
                agent_names=None,
                command_names=["starter"],
                guideline_names=None,
                target_root=root,
            )
            self.assertEqual(selection.skills, ["engine"])

    def test_agent_selection_expands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "criteria-skill")
            write_map(root, {"agents": {"watcher": {"depends": ["criteria-skill"]}}})
            mod.REPO_ROOT = root
            selection = mod.resolve_cli_selection(
                bundle_ids=None,
                skill_names=None,
                agent_names=["watcher"],
                command_names=None,
                guideline_names=None,
                target_root=root,
            )
            self.assertEqual(selection.skills, ["criteria-skill"])
            self.assertEqual(selection.agents, ["watcher"])

    def test_bundle_selection_expands(self) -> None:
        # t-005 bundle path: a bundle member with an unmet dependency is
        # expanded through the same single hook.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            bundles = {"bases": [], "bundles": [
                {
                    "id": "test-bundle",
                    "name": "Test",
                    "description": "d",
                    "commands": ["starter"],
                }
            ]}
            tools = root / "tools"
            tools.mkdir(parents=True, exist_ok=True)
            (tools / "bundles.json").write_text(json.dumps(bundles), encoding="utf-8")
            mod.REPO_ROOT = root
            selection = mod.resolve_cli_selection(
                bundle_ids=["test-bundle"],
                skill_names=None,
                agent_names=None,
                command_names=None,
                guideline_names=None,
                target_root=root,
            )
            self.assertEqual(selection.commands, ["starter"])
            self.assertEqual(selection.skills, ["engine"])


class PanelSelectionTests(unittest.TestCase):
    """cr-006: the headless seam behind the GUI Install press.

    resolve_panel_selection carries the selection math _run performs at
    Install press, so the expansion and mode pass-through are verifiable
    on hosts without a display; GuiWiringTests below stays the Tk-level
    integration layer.
    """

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def test_install_mode_expands_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            selection = mod.resolve_panel_selection(
                [], [], ["starter"], [], uninstall=False
            )
            self.assertEqual(selection.skills, ["engine"])
            self.assertEqual(selection.commands, ["starter"])

    def test_uninstall_mode_passes_selection_through(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            selection = mod.resolve_panel_selection(
                [], [], ["starter"], [], uninstall=True
            )
            self.assertEqual(selection.skills, [])
            self.assertEqual(selection.commands, ["starter"])

    def test_invalid_map_raises_installer_error(self) -> None:
        # cr-001 companion: the seam raises InstallerError, so the GUI
        # guard can surface it; run() catches it on the CLI side.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_command_skill(root, "starter")
            write_map(
                root, {"commands": {"starter": {"depends": ["typo"]}}}
            )
            mod.REPO_ROOT = root
            with self.assertRaises(mod.InstallerError):
                mod.resolve_panel_selection(
                    [], [], ["starter"], [], uninstall=False
                )


class GuiWiringTests(unittest.TestCase):
    """t-007: the real InstallerApp._run routes its selection through the
    resolver with the panel mode (AC-5 GUI entry point).

    Instantiates the real InstallerApp (skipTest guards per the existing
    GuiSharedSlugBundleStateTests pattern), stubs run_operation and
    messagebox, and asserts on the selection actually passed through.
    """

    def test_gui_run_passes_mode_into_resolver(self) -> None:
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            # A command panel entry needs a real command-skill (cmd-
            # prefixed dir with the disable-model-invocation flag), not
            # just a map edge.
            write_command_skill(root, "starter")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            tk_root = None
            captured: dict[str, object] = {}

            def fake_run_operation(**kwargs):
                captured.update(kwargs)
                return 0, "ok"

            try:
                try:
                    tk_root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                tk_root.withdraw()
                app = mod.InstallerApp(tk_root)
                app.target_var.set(str(root / "target"))
                app.command_vars["starter"].set(True)

                with (
                    mock.patch.object(mod, "run_operation", fake_run_operation),
                    mock.patch.object(mod.messagebox, "showerror"),
                    mock.patch.object(mod.messagebox, "showwarning"),
                    mock.patch.object(app, "_append_log"),
                ):
                    # Install mode: the selection passed to run_operation
                    # carries the dependency-expanded skill.
                    app.mode_var.set("install")
                    app._run()
                    self.assertEqual(captured["skills"], ["engine"])
                    self.assertEqual(captured["commands"], ["starter"])
                    self.assertIs(captured["uninstall"], False)

                    # Uninstall mode: same panels, no expansion.
                    app.mode_var.set("uninstall")
                    app._run()
                    self.assertEqual(captured["skills"], [])
                    self.assertEqual(captured["commands"], ["starter"])
                    self.assertIs(captured["uninstall"], True)
            finally:
                mod.REPO_ROOT = original_root
                if tk_root is not None:
                    tk_root.destroy()

    def test_gui_invalid_map_shows_error_dialog(self) -> None:
        # cr-001: an invalid dependency map must reach the InstallerError
        # guard — showerror dialog, no run_operation call — instead of
        # escaping the Tk callback as a silent stderr traceback.
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_command_skill(root, "starter")
            write_map(root, {"commands": {"starter": {"depends": ["typo"]}}})
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            tk_root = None
            captured: dict[str, object] = {}

            def fake_run_operation(**kwargs):
                captured.update(kwargs)
                return 0, "ok"

            try:
                try:
                    tk_root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                tk_root.withdraw()
                app = mod.InstallerApp(tk_root)
                app.target_var.set(str(root / "target"))
                app.command_vars["starter"].set(True)
                app.mode_var.set("install")

                with (
                    mock.patch.object(mod, "run_operation", fake_run_operation),
                    mock.patch.object(mod.messagebox, "showerror") as showerror,
                    mock.patch.object(mod.messagebox, "showwarning"),
                    mock.patch.object(app, "_append_log"),
                ):
                    app._run()
                self.assertEqual(captured, {})
                self.assertEqual(showerror.call_count, 1)
                self.assertIn("typo", str(showerror.call_args))
            finally:
                mod.REPO_ROOT = original_root
                if tk_root is not None:
                    tk_root.destroy()


class MapBodyConsistencyTests(unittest.TestCase):
    """t-008/t-009 (fr-6): map vs member bodies, both directions.

    Forward (edge => body reference): every map edge's dependent body must
    reference the target — guards against typos and stale entries.

    Curated reverse (load-bearing link => edge): every load-bearing body
    link class must have a map edge — guards against missing dependencies.
    Load-bearing classes (the curation policy that makes ledger AC-6's
    cross-check safe; see plan pg-004):
      1. links into ../<name>/references/... (operational templates)
      2. the first sibling link directly governed by a "Follow [../..."
         directive (capital or lowercase)
      3. dev-workflow-orchestrator's Companion Skills dispatch table only
    Routing-exclusion contexts ("When NOT to use", "Does not trigger",
    handoff bullets) and other skills' deferral tables are exempt by design
    (the exclusion-link hazard).

    The curated-hybrid is an accepted mechanism deviation from ledger AC-6's
    literal "against the existing body scanners" wording (rr-002 disposition).
    """

    SKILLS_ROOT = REPO_ROOT / "skills"
    AGENTS_ROOT = REPO_ROOT / "agents"
    COMMANDS_ROOT = REPO_ROOT / "commands"

    def setUp(self) -> None:
        # Earlier classes rebind mod.REPO_ROOT to temp fixtures; pin it to
        # the real repo so the map/body reads here are order-independent.
        self._original_root = mod.REPO_ROOT
        mod.REPO_ROOT = REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def _member_body(self, kind: str, name: str) -> str:
        if kind == "skills":
            path = self.SKILLS_ROOT / name / "SKILL.md"
        elif kind == "agents":
            path = self.AGENTS_ROOT / name / "AGENT.md"
        else:
            path = self.COMMANDS_ROOT / name / "COMMAND.md"
        if not path.is_file():
            return ""
        return path.read_text(encoding="utf-8")

    def _body_references(self, kind: str, name: str, target: str) -> bool:
        body = self._member_body(kind, name)
        if not body:
            return False
        if kind == "skills":
            return f"](../{target}/" in body
        # Agents and commands reference installed absolute paths.
        return f".agents/skills/{target}/" in body

    def test_map_edges_have_body_references(self) -> None:
        # t-008 forward: every map edge must be anchored in the dependent's
        # body. No exemptions: agent-runner's routing-style body link
        # satisfies the forward predicate; the pr-005 asymmetry is
        # reverse-direction only (ia-005).
        deps = mod.load_dependencies()
        self.assertTrue(deps["skills"] or deps["commands"] or deps["agents"])
        for kind in ("skills", "commands", "agents"):
            for member, spec in deps[kind].items():
                for target in spec["depends"]:
                    self.assertTrue(
                        self._body_references(kind, member, target),
                        f"map edge {kind}.{member} -> {target} has no "
                        f"body reference in the {kind[:-1]} body",
                    )

    def _load_bearing_links(self) -> set[tuple[str, str]]:
        """Extract curated load-bearing (source skill, target skill) links."""
        pairs: set[tuple[str, str]] = set()
        for skill_dir in sorted(self.SKILLS_ROOT.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
                continue
            body_path = skill_dir / "SKILL.md"
            if not body_path.is_file():
                continue
            lines = body_path.read_text(encoding="utf-8").splitlines()
            in_companion_table = False
            for line in lines:
                if line.startswith("## Companion Skills"):
                    # Class 3 is the orchestrator's dispatch table only;
                    # other skills' Companion Skills sections are
                    # deferral/routing tables (ia-001).
                    in_companion_table = (
                        skill_dir.name == "dev-workflow-orchestrator"
                    )
                    continue
                if in_companion_table and line.startswith("## "):
                    in_companion_table = False
                if in_companion_table:
                    for target in re.findall(r"\.\./([a-z0-9-]+)/SKILL\.md", line):
                        pairs.add((skill_dir.name, target))
                # Class 1: operational links into ../<name>/references/...
                for target in re.findall(
                    r"\.\./([a-z0-9-]+)/references/", line
                ):
                    pairs.add((skill_dir.name, target))
                # Class 2: the first sibling link directly governed by a
                # "Follow [../..." directive, capital or lowercase (ia-004);
                # broad forms catch illustrative asides.
                m2 = re.search(r"[Ff]ollow \[\.\./([a-z0-9-]+)/", line)
                if m2:
                    pairs.add((skill_dir.name, m2.group(1)))
        return pairs

    def test_load_bearing_links_have_edges(self) -> None:
        # t-009 curated reverse: every load-bearing link must have a map
        # edge. Red proof: deleting any expected edge from the map makes
        # this test fail (verified manually against the orchestrator's
        # companion edges after the ia-001 arming fix).
        deps = mod.load_dependencies()
        skill_edges = {
            (member, target)
            for member, spec in deps["skills"].items()
            for target in spec["depends"]
        }
        for source, target in sorted(self._load_bearing_links()):
            self.assertIn(
                (source, target),
                skill_edges,
                f"load-bearing skill link {source} -> {target} has no "
                "dependency map edge",
            )


if __name__ == "__main__":
    unittest.main()
