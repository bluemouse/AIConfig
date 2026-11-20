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

Selection dynamics plan
(.agents/workflow/installer-selection-dynamics/20-implementation-plan.md):

- t-001..t-005: (pg-002) reverse map + event-aware selection reconciliation
- t-006/t-007: (pg-003) CLI "also selecting" accounting
- t-008..t-011: (pg-004) post-uninstall orphan report (never auto-removes)
- t-012: (pg-005) GUI auto-check / cascade seam

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

                    # Uninstall mode: no expansion. Auto-check visibly
                    # checked engine during the install run (AC-1), so
                    # uncheck it first — this uninstall selection is
                    # exactly-what-you-selected.
                    app.mode_var.set("uninstall")
                    app.skill_vars["engine"].set(False)
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


class ReconcileSelectionTests(unittest.TestCase):
    """t-001..t-005 (pg-002): reverse map + pure event-aware reconciliation.

    reconcile_selection is the headless seam behind the GUI checkbox
    dynamics: it maps one observed panel-state transition to the next
    selection state, so the auto-check / cascade / closure-wins rules are
    testable without Tk. pr-001: it is a pure state transition — the
    caller applies the result to the checkbox vars.
    """

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def _fixture(self, root: Path) -> None:
        # Chain: A -> B -> C. A checked member must pull in B and C
        # transitively; unchecking C must cascade to B and A.
        for name in ("skill-a", "skill-b", "skill-c"):
            write_skill(root, name)
        write_map(
            root,
            {
                "skills": {
                    "skill-a": {"depends": ["skill-b"]},
                    "skill-b": {"depends": ["skill-c"]},
                }
            },
        )
        mod.REPO_ROOT = root

    def test_reverse_dependencies_maps_all_edges(self) -> None:
        # t-001: direct edges land in the reverse map (B is depended on by
        # A and C), and transitivity reaches through the chain (C's
        # dependents include A through B).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("skill-a", "skill-b", "skill-c", "skill-d"):
                write_skill(root, name)
            write_map(
                root,
                {
                    "skills": {
                        "skill-a": {"depends": ["skill-b"]},
                        "skill-c": {"depends": ["skill-b"]},
                        "skill-b": {"depends": ["skill-d"]},
                    }
                },
            )
            mod.REPO_ROOT = root
            reverse = mod.reverse_dependencies(mod.load_dependencies())
            self.assertEqual(reverse["skill-b"], {"skill-a", "skill-c"})
            self.assertEqual(reverse["skill-d"], {"skill-a", "skill-b", "skill-c"})

    def test_reconcile_auto_checks(self) -> None:
        # t-002 (AC-1): a "check" event on skill-a adds its transitive
        # dependency skills (skill-b, then skill-c through it).
        with tempfile.TemporaryDirectory() as tmp:
            self._fixture(Path(tmp))
            selection = mod.BundleSelection(skills=["skill-a"])
            result = mod.reconcile_selection(
                selection, event="check", member="skill-a", uninstall=False
            )
            self.assertEqual(result.skills, ["skill-a", "skill-b", "skill-c"])

    def test_reconcile_check_walks_own_kind_edges(self) -> None:
        # ia-004 + ia-006: check walks the member's OWN-KIND map entry
        # first, then the skills map transitively. A command check pulls
        # its real edge (AC-1 covers all three panels, not just skills);
        # the shared-slug agent walks agents.<name>'s edges, never the
        # same-named skill's.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("engine", "skill-a"):
                write_skill(root, name)
            write_map(
                root,
                {
                    "skills": {"skill-a": {"depends": ["engine"]}},
                    "commands": {"starter": {"depends": ["engine"]}},
                    "agents": {"skill-a": {"depends": []}},
                },
            )
            mod.REPO_ROOT = root

            # Command check pulls the command's own edge (ia-006).
            selection = mod.BundleSelection(commands=["starter"])
            result = mod.reconcile_selection(
                selection,
                event="check",
                member="starter",
                member_kind="commands",
                uninstall=False,
            )
            self.assertEqual(result.skills, ["engine"])
            self.assertEqual(result.commands, ["starter"])

            # Shared slug: the AGENT skill-a has no edges; its check adds
            # nothing even though the same-named skill depends on engine.
            selection = mod.BundleSelection(agents=["skill-a"])
            result = mod.reconcile_selection(
                selection,
                event="check",
                member="skill-a",
                member_kind="agents",
                uninstall=False,
            )
            self.assertEqual(result.skills, [])
            self.assertEqual(result.agents, ["skill-a"])

    def test_reconcile_cascade_on_uncheck(self) -> None:
        # t-003 (AC-2): unchecking a dependency removes it plus every
        # member that transitively depends on it; unchecking a non-dep
        # removes only the named member (no cascade).
        with tempfile.TemporaryDirectory() as tmp:
            self._fixture(Path(tmp))
            selection = mod.BundleSelection(
                skills=["skill-a", "skill-b", "skill-c"]
            )
            result = mod.reconcile_selection(
                selection, event="uncheck", member="skill-c", uninstall=False
            )
            self.assertEqual(result.skills, [])

            # Non-dependency uncheck: nothing depends on skill-a.
            selection = mod.BundleSelection(skills=["skill-a", "skill-b"])
            result = mod.reconcile_selection(
                selection, event="uncheck", member="skill-a", uninstall=False
            )
            self.assertEqual(result.skills, ["skill-b"])

    def test_reconcile_batch_closure_wins(self) -> None:
        # t-004: batch state (dependent checked, dependency unchecked)
        # resolves with the closure winning — the dependency is re-checked
        # (a checked dependent forces its dependency; never ship a known
        # gap). Also covers auto-check inside a batch: unchecked deps of
        # checked members are added.
        with tempfile.TemporaryDirectory() as tmp:
            self._fixture(Path(tmp))
            selection = mod.BundleSelection(
                skills=["skill-a", "skill-c"], commands=[], agents=[]
            )
            result = mod.reconcile_selection(
                selection, event="batch", member=None, uninstall=False
            )
            self.assertEqual(result.skills, ["skill-a", "skill-b", "skill-c"])

    def test_reconcile_batch_shared_slug_stays_own_kind(self) -> None:
        # cr-001: the batch fixpoint walks (kind, name) pairs, never the
        # merged bare-name map — a checked shared-slug skill must not
        # inherit its agent twin's edges. Fixture mirrors the real map's
        # shape: skills.code-reviewer has no entry (the skill adds
        # nothing on install), while agents.code-reviewer carries the
        # twin chain.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("code-reviewer", "dev-workflow-orchestrator"):
                write_skill(root, name)
            write_map(
                root,
                {
                    "agents": {
                        "code-reviewer": {
                            "depends": [
                                "code-reviewer",
                                "dev-workflow-orchestrator",
                            ]
                        }
                    }
                },
            )
            mod.REPO_ROOT = root

            # Skill-only batch: the skill has no own-kind edges, so the
            # kind-correct closure is the selection itself, unchanged.
            selection = mod.BundleSelection(skills=["code-reviewer"])
            result = mod.reconcile_selection(
                selection, event="batch", member=None, uninstall=False
            )
            self.assertEqual(result.skills, ["code-reviewer"])
            self.assertEqual(result.agents, [])
            self.assertEqual(result.commands, [])

            # Agent-direction companion: the agent's own-kind chain still
            # pulls its dependency skills.
            selection = mod.BundleSelection(agents=["code-reviewer"])
            result = mod.reconcile_selection(
                selection, event="batch", member=None, uninstall=False
            )
            self.assertEqual(
                result.skills, ["code-reviewer", "dev-workflow-orchestrator"]
            )
            self.assertEqual(result.agents, ["code-reviewer"])

    def test_reconcile_noop_in_uninstall_mode(self) -> None:
        # t-005: uninstall selections are never reconciled — teardown stays
        # exactly-what-you-selected; the orphan report is the uninstall
        # mode's dependency awareness instead.
        with tempfile.TemporaryDirectory() as tmp:
            self._fixture(Path(tmp))
            selection = mod.BundleSelection(skills=["skill-a"])
            result = mod.reconcile_selection(
                selection, event="check", member="skill-a", uninstall=True
            )
            self.assertEqual(result.skills, ["skill-a"])
            result = mod.reconcile_selection(
                selection, event="batch", member=None, uninstall=True
            )
            self.assertEqual(result.skills, ["skill-a"])


class CliAccountingTests(unittest.TestCase):
    """t-006/t-007/t-013 (pg-003): CLI "also selecting" accounting.

    The added-set is known at resolve time but rendered inside
    format_result, so it threads through an out-parameter (rr-012: the
    return type stays unchanged — default None keeps every existing
    caller byte-identical) → run_cli → run_operation → OperationResult.
    """

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def test_cli_selection_reports_added(self) -> None:
        # t-006 (AC-3): resolve_cli_selection populates added_out with the
        # auto-added dependencies while returning the same expanded
        # selection as before (out-param, not a return-type change).
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
            added: list[str] = []
            selection = mod.resolve_cli_selection(
                bundle_ids=None,
                skill_names=None,
                agent_names=None,
                command_names=["starter"],
                guideline_names=None,
                target_root=root,
                uninstall=False,
                added_out=added,
            )
            self.assertEqual(selection.skills, ["engine", "leaf", "mid"])
            self.assertEqual(selection.commands, ["starter"])
            self.assertEqual(sorted(added), ["engine", "leaf", "mid"])
            # rr-012: without the out-param the same expansion resolves.
            plain = mod.resolve_cli_selection(
                bundle_ids=None,
                skill_names=None,
                agent_names=None,
                command_names=["starter"],
                guideline_names=None,
                target_root=root,
                uninstall=False,
            )
            self.assertEqual(plain.skills, selection.skills)

    def test_run_operation_renders_also_selecting(self) -> None:
        # t-007 (AC-3): run_operation installs the selection and renders
        # one "Also selecting (dependencies):" line listing the added
        # names inside the operation message.
        # The target must live outside the fixture root: validate_target
        # refuses a target inside (or equal to) the rebound repository.
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            write_skill(root, "engine")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            code, message = mod.run_operation(
                target=Path(target_tmp),
                skills=["engine"],
                agents=[],
                commands=[],
                uninstall=False,
                dependency_added=["engine"],
            )
            self.assertEqual(code, 0)
            self.assertIn("Also selecting (dependencies):", message)
            self.assertIn("engine", message)

    def test_run_operation_without_accounting_renders_no_lines(self) -> None:
        # t-013 companion: the default dependency_added=() renders no
        # accounting section (the common default-selection install stays
        # silent — risk 6: no "also selecting 45 skills" noise).
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            write_skill(root, "engine")
            mod.REPO_ROOT = root
            code, message = mod.run_operation(
                target=Path(target_tmp),
                skills=["engine"],
                agents=[],
                commands=[],
                uninstall=False,
            )
            self.assertEqual(code, 0)
            self.assertNotIn("Also selecting", message)


class OrphanReportTests(unittest.TestCase):
    """t-008..t-011 (pg-004): post-uninstall orphan report.

    After the named members are removed, the report lists installed
    skills no remaining installed member depends on (AC-4) — with a
    removal hint, never an automatic removal (AC-5). rr-001: guidelines-
    and cmd- prefixed dirs are never orphan candidates.
    """

    def setUp(self) -> None:
        self._original_root = mod.REPO_ROOT

    def tearDown(self) -> None:
        mod.REPO_ROOT = self._original_root

    def test_uninstall_reports_orphans(self) -> None:
        # t-008 + t-010 (AC-4/AC-5): uninstalling the dependent leaves the
        # dependency installed but orphaned; the message reports it with
        # the removal hint, and the skill dir stays on disk.
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            target = Path(target_tmp)
            write_skill(root, "engine")
            write_command_skill(root, "starter")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            mod.install_items(
                source_root=root,
                target_root=target,
                skills=["engine"],
                agents=[],
                commands=["starter"],
                guidelines=[],
            )
            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=[],
                commands=["starter"],
                guidelines=[],
                uninstall=True,
            )
            self.assertEqual(code, 0)
            self.assertIn(
                "No longer needed by any installed member", message
            )
            self.assertIn("engine", message)
            # t-010 (AC-5): the orphan was never removed.
            self.assertTrue(
                (target / ".agents" / "skills" / "engine").is_dir(),
                "orphaned dependency must remain installed on disk",
            )

    def test_uninstall_keeps_needed_dependencies(self) -> None:
        # AC-4 complement: a dependency still needed by a remaining
        # installed member is not reported as orphaned.
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            target = Path(target_tmp)
            write_skill(root, "engine")
            write_command_skill(root, "starter")
            write_skill(root, "keeper")
            write_map(
                root,
                {
                    "commands": {"starter": {"depends": ["engine"]}},
                    "skills": {"keeper": {"depends": ["engine"]}},
                },
            )
            mod.REPO_ROOT = root
            mod.install_items(
                source_root=root,
                target_root=target,
                skills=["engine", "keeper"],
                agents=[],
                commands=["starter"],
                guidelines=[],
            )
            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=[],
                commands=["starter"],
                guidelines=[],
                uninstall=True,
            )
            self.assertEqual(code, 0)
            self.assertNotIn("No longer needed", message)

    def test_uninstall_dry_run_orphan_preview(self) -> None:
        # t-009 (oq-2): a dry-run uninstall previews what would be
        # orphaned, computing the remaining set from result.removed
        # (rr-011 — guard-refused members stay counted as remaining
        # dependents, unlike a selection-based subtraction). The fixture
        # covers all three removed-path shapes: a plain skill dir, a
        # command-skill dir, and a dual-target agent's two .md paths.
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            target = Path(target_tmp)
            write_skill(root, "engine")
            write_command_skill(root, "starter")
            write_map(
                root,
                {
                    "commands": {"starter": {"depends": ["engine"]}},
                    "agents": {"watcher": {"depends": ["engine"]}},
                },
            )
            # An agent installs from two real copies (dual-target layout);
            # write both sources so install_items accepts the agent.
            for rel in (".claude/agents/watcher.md", ".github/agents/watcher.agent.md"):
                src = root / rel
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(
                    "---\nname: watcher\ndescription: watcher agent\n---\n\n"
                    "# watcher\n",
                    encoding="utf-8",
                )
            mod.REPO_ROOT = root
            mod.install_items(
                source_root=root,
                target_root=target,
                skills=["engine"],
                agents=["watcher"],
                commands=["starter"],
                guidelines=[],
            )
            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=["watcher"],
                commands=["starter"],
                guidelines=[],
                uninstall=True,
                dry_run=True,
            )
            self.assertEqual(code, 0)
            # Preview names the would-be orphan even though nothing was
            # removed (a dry run removes nothing; the preview derives
            # from the removed-path -> member-name mapping). The heading
            # reads conditionally under dry-run (cr-006), matching the
            # would-be remove verb above it.
            self.assertIn(
                "Would be no longer needed by any installed member",
                message,
            )
            self.assertIn("engine", message)
            # Dry run removed nothing on disk.
            self.assertTrue(
                (target / ".agents" / "skills" / "cmd-starter").is_dir()
            )

    def test_uninstall_dry_run_agent_dual_path_mapping(self) -> None:
        # t-009 companion: the removed-path -> name mapping must collapse
        # a dual-target agent's two .md paths (CLAUDE_AGENT_FILE and
        # GITHUB_AGENT_FILE) to the one agent name — with the agent's
        # criteria skill orphaned in the preview.
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            target = Path(target_tmp)
            write_skill(root, "engine")
            write_map(root, {"agents": {"watcher": {"depends": ["engine"]}}})
            for rel in (".claude/agents/watcher.md", ".github/agents/watcher.agent.md"):
                src = root / rel
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(
                    "---\nname: watcher\ndescription: watcher agent\n---\n\n"
                    "# watcher\n",
                    encoding="utf-8",
                )
            mod.REPO_ROOT = root
            mod.install_items(
                source_root=root,
                target_root=target,
                skills=["engine"],
                agents=["watcher"],
                commands=[],
                guidelines=[],
            )
            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=["watcher"],
                commands=[],
                guidelines=[],
                uninstall=True,
                dry_run=True,
            )
            self.assertEqual(code, 0)
            self.assertIn("engine", message)

    def test_dry_run_shared_slug_subtracts_own_kind_only(self) -> None:
        # cr-002: a dry-run preview subtracts kind-tagged removed names —
        # removing agent "shared" must not count the same-named installed
        # skill as removed (and so must not advise removing the skill's
        # still-needed dependency "other"). The preview must agree with
        # the real run's orphans.
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            target = Path(target_tmp)
            write_skill(root, "shared")
            write_skill(root, "other")
            write_map(
                root,
                {
                    "agents": {"shared": {"depends": ["other"]}},
                    "skills": {"consumer": {"depends": ["shared"]}},
                },
            )
            for rel in (".claude/agents/shared.md", ".github/agents/shared.agent.md"):
                src = root / rel
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(
                    "---\nname: shared\ndescription: shared agent\n---\n\n"
                    "# shared\n",
                    encoding="utf-8",
                )
            mod.REPO_ROOT = root
            mod.install_items(
                source_root=root,
                target_root=target,
                skills=["shared", "other"],
                agents=["shared"],
                commands=[],
                guidelines=[],
            )
            common = {
                "target": target,
                "skills": [],
                "agents": ["shared"],
                "commands": [],
                "guidelines": [],
                "uninstall": True,
            }
            code, preview = mod.run_operation(dry_run=True, **common)
            self.assertEqual(code, 0)
            # The still-installed skill twin keeps "other" needed; only
            # the skill twin itself (no remaining dependent) surfaces as
            # an orphan — the agent's removal must not flip the advice to
            # "remove other".
            self.assertIn("\n  - shared", preview)
            self.assertNotIn("\n  - other", preview)

            code, real = mod.run_operation(**common)
            self.assertEqual(code, 0)
            self.assertIn("\n  - shared", real)
            self.assertNotIn("\n  - other", real)
            # AC-5: nothing was auto-removed.
            self.assertTrue(
                (target / ".agents" / "skills" / "other").is_dir()
            )

    def test_orphans_exclude_guideline_and_cmd_prefixes(self) -> None:
        # t-011 (rr-001): guidelines-<n> packages and cmd-<n> dirs are
        # never orphan candidates — guidelines are explicit-only, and
        # command-skills are never depends targets (their dependents are
        # read from the commands panel kind, not the skills list).
        with (
            tempfile.TemporaryDirectory() as repo_tmp,
            tempfile.TemporaryDirectory() as target_tmp,
        ):
            root = Path(repo_tmp)
            target = Path(target_tmp)
            write_skill(root, "engine")
            write_command_skill(root, "starter")
            write_command_skill(root, "cmd-x")
            write_map(root, {"commands": {"starter": {"depends": ["engine"]}}})
            mod.REPO_ROOT = root
            mod.install_items(
                source_root=root,
                target_root=target,
                skills=["engine"],
                agents=[],
                commands=["starter"],
                guidelines=[],
            )
            # A guidelines-<n> dir in the target's shared skills root:
            # discovered by discover_skills_in_project but filtered from
            # orphan candidacy by prefix.
            guideline_dir = target / ".agents" / "skills" / "guidelines-code-comment"
            guideline_dir.mkdir(parents=True)
            (guideline_dir / "SKILL.md").write_text(
                "---\nname: guidelines-code-comment\ndescription: g\n---\n\n# g\n",
                encoding="utf-8",
            )
            code, message = mod.run_operation(
                target=target,
                skills=[],
                agents=[],
                commands=["starter"],
                guidelines=[],
                uninstall=True,
            )
            self.assertEqual(code, 0)
            self.assertIn("No longer needed by any installed member", message)
            self.assertNotIn("guidelines-code-comment", message)
            self.assertNotIn("cmd-x", message)


class MapBodyConsistencyTests(unittest.TestCase):
    """t-008/t-009 (fr-6): map vs member bodies, both directions.

    Forward (edge => body reference): every map edge's dependent body must
    reference the target — guards against typos and stale entries.

    Curated reverse (load-bearing link => edge): every load-bearing body
    link class must have a map edge — guards against missing dependencies.
    Load-bearing classes (the curation policy that makes ledger AC-6's
    cross-check safe; see plan pg-004):
      1. links into ../<name>/references/... (operational templates)
      2. the first sibling link directly governed by a requirement
         directive inside a workflow step ("Follow"/"switch to"/
         "hand off to"/"start with"/"apply [../...", capital or lowercase)
      3. dev-workflow-orchestrator's Companion Skills dispatch table only
    Routing-exclusion contexts ("When NOT to use", "Does not trigger",
    handoff bullets) and other skills' deferral tables are exempt by design
    (the exclusion-link hazard). A workflow rule can restate a boundary in
    hand-off phrasing (code-professor: "candidate fixes are proposals
    only; hand off to debugging-guide for verified repairs" — the guide's
    own task completes without the repair); those pairs are exempted
    explicitly below with their rationale, like the pr-005 asymmetry.

    The curated-hybrid is an accepted mechanism deviation from ledger AC-6's
    literal "against the existing body scanners" wording (rr-002 disposition).

    Reverse protection covers classes 1-3 only. Edges whose anchors use
    other requirement phrasings ("live in", "see X", "per X", arrow-routing
    rows, "Use ... when available") are forward-anchored only — the same
    deliberate over-inclusion status: the forward check proves every map
    edge is real, and deleting one of these changes install sets silently
    (accepted; documented in tools/bundles.md § Dependency map). The
    pr-005 agent-runner → dev-workflow-orchestrator edge was the one such
    over-inclusion ever taken; it was removed so agent-runner stays a
    dispatch primitive under the orchestrator (one-way edge), not a
    member of the dev-workflow cycle.
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
        # Skills: the full installed package (SKILL.md + references/*.md) —
        # an anchor in a bundled reference is as load-bearing as one in the
        # body, and the whole package ships in one install. Agents and
        # commands are single-file.
        if kind == "skills":
            skill_dir = self.SKILLS_ROOT / name
            parts = []
            skill_md = skill_dir / "SKILL.md"
            if skill_md.is_file():
                parts.append(skill_md.read_text(encoding="utf-8"))
            refs_dir = skill_dir / "references"
            if refs_dir.is_dir():
                for ref in sorted(refs_dir.glob("*.md")):
                    parts.append(ref.read_text(encoding="utf-8"))
            return "\n".join(parts)
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
            # SKILL.md links are sibling-relative (](../<target>/); bundled
            # references/*.md files are two levels up (](../../<target>/).
            return (
                f"](../{target}/" in body or f"](../../{target}/" in body
            )
        # Agents and commands reference installed absolute paths.
        return f".agents/skills/{target}/" in body

    def test_map_edges_have_body_references(self) -> None:
        # t-008 forward: every map edge must be anchored in the dependent's
        # body. No exemptions — the reverse-direction-only pr-005
        # asymmetry was removed with its edge (agent-runner no longer
        # depends on dev-workflow-orchestrator).
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
            # Scan the full package (SKILL.md + references/*.md): bundled
            # references ship in the same install, so an operational link
            # there is as load-bearing as one in the body. Only class 1
            # (references/ targets) and class 2 (requirement directives)
            # apply to reference files; class 3 is a SKILL.md section.
            body_paths = [skill_dir / "SKILL.md"]
            refs_dir = skill_dir / "references"
            if refs_dir.is_dir():
                body_paths += sorted(refs_dir.glob("*.md"))
            lines: list[str] = []
            for body_path in body_paths:
                if body_path.is_file():
                    lines.extend(body_path.read_text(encoding="utf-8").splitlines())
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
                # requirement directive inside a workflow step ("Follow",
                # "switch to", "hand off to", "start with", "apply" —
                # capital or lowercase, ia-004/cr-gap); scope boundaries
                # ("use X instead" in When-NOT lists) are excluded above,
                # and broad forms catch illustrative asides.
                m2 = re.search(
                    r"(?:[Ff]ollow|[Ss]witch to|[Hh]and off to|"
                    r"[Ss]tart with|[Aa]pply) \[\.\./([a-z0-9-]+)/",
                    line,
                )
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
        # Boundary-in-workflow-phrasing exemptions (no edge by design):
        # code-professor's rule 6 hands a DIFFERENT task (verified repair)
        # to debugging-guide; code-professor's own task (a learning guide)
        # completes without it, and debugging-guide self-triggers on
        # repair requests via its description.
        boundary_restatements = {("code-professor", "debugging-guide")}
        for source, target in sorted(self._load_bearing_links()):
            if (source, target) in boundary_restatements:
                continue
            self.assertIn(
                (source, target),
                skill_edges,
                f"load-bearing skill link {source} -> {target} has no "
                "dependency map edge",
            )


class GuiSelectionDynamicsTests(unittest.TestCase):
    """t-012 (pg-005): GUI checkbox auto-check / cascade / uninstall-noop.

    Drives the real InstallerApp var wiring (real trace handlers, real
    reconcile pass) on a display host; skipTest guards otherwise. The
    pure rules are pinned headlessly in ReconcileSelectionTests — this
    class pins the Tk wrapper (guard discipline, snapshot updates).
    """

    def _make_app(self, root: Path, tk_root):
        app = mod.InstallerApp(tk_root)
        app.target_var.set(str(root / "target"))
        return app

    def test_check_auto_checks_dependencies_and_cascade_unchecks(self) -> None:
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Chain: skill-a -> skill-b -> skill-c (all plain skills so
            # they appear on the Skills panel).
            for name in ("skill-a", "skill-b", "skill-c"):
                write_skill(root, name)
            write_map(
                root,
                {
                    "skills": {
                        "skill-a": {"depends": ["skill-b"]},
                        "skill-b": {"depends": ["skill-c"]},
                    }
                },
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            tk_root = None
            try:
                try:
                    tk_root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                tk_root.withdraw()
                app = self._make_app(root, tk_root)
                app.mode_var.set("install")

                # User check of skill-a: auto-check pulls in skill-b and,
                # transitively, skill-c (AC-1).
                app.skill_vars["skill-a"].set(True)
                self.assertTrue(app.skill_vars["skill-b"].get())
                self.assertTrue(app.skill_vars["skill-c"].get())

                # User uncheck of skill-c: cascade removes skill-b and
                # skill-a (AC-2).
                app.skill_vars["skill-c"].set(False)
                self.assertFalse(app.skill_vars["skill-a"].get())
                self.assertFalse(app.skill_vars["skill-b"].get())
                self.assertFalse(app.skill_vars["skill-c"].get())

                # A non-dependency uncheck cascades nothing.
                app.skill_vars["skill-a"].set(True)
                self.assertTrue(app.skill_vars["skill-b"].get())
                app.skill_vars["skill-a"].set(False)
                self.assertTrue(app.skill_vars["skill-b"].get())
                self.assertTrue(app.skill_vars["skill-c"].get())
            finally:
                mod.REPO_ROOT = original_root
                if tk_root is not None:
                    tk_root.destroy()

    def test_uninstall_mode_does_not_reconcile(self) -> None:
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("skill-a", "skill-b"):
                write_skill(root, name)
            write_map(
                root, {"skills": {"skill-a": {"depends": ["skill-b"]}}}
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            tk_root = None
            try:
                try:
                    tk_root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                tk_root.withdraw()
                app = self._make_app(root, tk_root)
                app.mode_var.set("uninstall")

                # Neither auto-check nor cascade in uninstall mode:
                # teardown stays exactly-what-you-selected.
                app.skill_vars["skill-a"].set(True)
                self.assertFalse(app.skill_vars["skill-b"].get())
                app.skill_vars["skill-b"].set(True)
                app.skill_vars["skill-b"].set(False)
                self.assertTrue(app.skill_vars["skill-a"].get())
            finally:
                mod.REPO_ROOT = original_root
                if tk_root is not None:
                    tk_root.destroy()

    def test_agent_check_auto_checks_skill_chain(self) -> None:
        # cr-004: pin the Tk wrapper's kind threading for the Agents
        # panel — checking an agent with real edges visibly auto-checks
        # its dependency skill (AC-1), and unchecking the agent drops
        # only the agent (an uncheck never auto-unchecks its deps, and
        # the cascade reads dependents, which an agent has none of).
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "engine")
            write_map(root, {"agents": {"watcher": {"depends": ["engine"]}}})
            for rel in (".claude/agents/watcher.md", ".github/agents/watcher.agent.md"):
                src = root / rel
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text(
                    "---\nname: watcher\ndescription: watcher agent\n---\n\n"
                    "# watcher\n",
                    encoding="utf-8",
                )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            tk_root = None
            try:
                try:
                    tk_root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                tk_root.withdraw()
                app = self._make_app(root, tk_root)
                app.mode_var.set("install")

                app.agent_vars["watcher"].set(True)
                self.assertTrue(app.skill_vars["engine"].get())

                app.agent_vars["watcher"].set(False)
                self.assertFalse(app.agent_vars["watcher"].get())
                self.assertTrue(app.skill_vars["engine"].get())
            finally:
                mod.REPO_ROOT = original_root
                if tk_root is not None:
                    tk_root.destroy()

    def test_batch_toggle_reconciles_once(self) -> None:
        # Select-all (a batch mutator under the bundle guard) must land on
        # the closure — and the reconcile pass must not re-enter against a
        # stale snapshot. Indirectly pins pr-014's guard sequence.
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("skill-a", "skill-b"):
                write_skill(root, name)
            write_map(
                root, {"skills": {"skill-a": {"depends": ["skill-b"]}}}
            )
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = root
            tk_root = None
            try:
                try:
                    tk_root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                tk_root.withdraw()
                app = self._make_app(root, tk_root)
                app.mode_var.set("install")

                calls = []
                original = app._reconcile_after_batch
                app._reconcile_after_batch = lambda: (
                    calls.append(1),
                    original(),
                )

                app._set_all_skills(True)
                # Both members checked; closure holds.
                self.assertTrue(app.skill_vars["skill-a"].get())
                self.assertTrue(app.skill_vars["skill-b"].get())

                # Select none is also a batch: closure-wins over an empty
                # selection is empty — nothing re-checked.
                app._set_all_skills(False)
                self.assertFalse(app.skill_vars["skill-a"].get())
                self.assertFalse(app.skill_vars["skill-b"].get())
                self.assertEqual(len(calls), 2)
            finally:
                mod.REPO_ROOT = original_root
                if tk_root is not None:
                    tk_root.destroy()


if __name__ == "__main__":
    unittest.main()
