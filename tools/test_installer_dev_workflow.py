#!/usr/bin/env python3
"""Tests for the --dev-workflow harness install/uninstall in installer.py."""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS_DIR = Path(__file__).resolve().parent
INSTALLER_PATH = TOOLS_DIR / "installer.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("installer_dev_workflow", INSTALLER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {INSTALLER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["installer_dev_workflow"] = module
    spec.loader.exec_module(module)
    return module


mod = load_installer_module()


def write_source_skill(root: Path, name: str) -> None:
    """Write a minimal skill directory under .agents/skills/<name>/."""
    shared = root / ".agents" / "skills" / name / "SKILL.md"
    shared.parent.mkdir(parents=True, exist_ok=True)
    shared.write_text(
        f"---\nname: {name}\ndescription: {name} skill\n---\n\n# {name}\n",
        encoding="utf-8",
    )


def write_source_command(root: Path, name: str) -> None:
    """Write a minimal command-skill: .agents/skills/cmd-<name>/SKILL.md with
    the disable-model-invocation flag (commands share the skill namespace,
    but install into the cmd- prefixed dir)."""
    skill_md = root / ".agents" / "skills" / f"cmd-{name}" / "SKILL.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(
        "---\n"
        f"name: {name}\n"
        "description: Run the commit message writer skill first\n"
        "disable-model-invocation: true\n"
        "---\n\n"
        f"# {name}\n",
        encoding="utf-8",
    )


def write_source_agent(root: Path, name: str) -> None:
    """Write a minimal agent in the dual-target layout.

    Paths mirror the installer's agent sources:
    - .claude/agents/<name>.md
    - .github/agents/<name>.agent.md  (note the .agent.md suffix for Copilot)
    """
    claude = root / ".claude" / "agents" / f"{name}.md"
    claude.parent.mkdir(parents=True, exist_ok=True)
    claude.write_text(
        f"---\nname: {name}\ndescription: {name} agent\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    github = root / ".github" / "agents" / f"{name}.agent.md"
    github.parent.mkdir(parents=True, exist_ok=True)
    github.write_text(f"---\nname: {name}\ndescription: {name} agent\n---\n\n# {name}\n", encoding="utf-8")


def write_full_harness_source(root: Path) -> None:
    """Write the full dev-workflow harness into a source root."""
    for skill in mod.DEV_WORKFLOW_SKILLS:
        write_source_skill(root, skill)
    for command in mod.DEV_WORKFLOW_COMMANDS:
        write_source_command(root, command)
    for agent in mod.DEV_WORKFLOW_AGENTS:
        write_source_agent(root, agent)


class DevWorkflowConstantsTests(unittest.TestCase):
    def test_harness_constants(self) -> None:
        self.assertEqual(
            mod.DEV_WORKFLOW_SKILLS,
            (
                "dev-workflow-orchestrator",
                "prompt-clarifier",
                "research-guide",
                "research-reviewer",
                "plan-guide",
                "plan-reviewer",
                "plan-executor",
                "implementation-auditor",
                "code-review-resolver",
                "code-reviewer",
                "commit-message-writer",
            ),
        )
        self.assertEqual(
            mod.DEV_WORKFLOW_COMMANDS,
            (
                "run-dev-workflow",
                "research",
                "plan",
                "implement",
                "review",
            ),
        )
        self.assertEqual(
            mod.DEV_WORKFLOW_AGENTS,
            (
                "research-reviewer",
                "plan-reviewer",
                "implementation-auditor",
                "code-reviewer",
            ),
        )


class DevWorkflowBundleTests(unittest.TestCase):
    def test_resolve_dev_workflow_harness_bundle(self) -> None:
        selection = mod.resolve_bundle(["dev-workflow-harness"])
        self.assertEqual(
            selection.skills,
            [
                "code-review-resolver",
                "code-reviewer",
                "commit-message-writer",
                "dev-workflow-orchestrator",
                "implementation-auditor",
                "plan-executor",
                "plan-guide",
                "plan-reviewer",
                "prompt-clarifier",
                "research-guide",
                "research-reviewer",
            ],
        )
        self.assertEqual(
            selection.commands,
            [
                "commit",
                "implement",
                "plan",
                "research",
                "review",
                "run-dev-workflow",
            ],
        )
        self.assertEqual(
            selection.agents,
            [
                "code-reviewer",
                "implementation-auditor",
                "plan-reviewer",
                "research-reviewer",
            ],
        )

    def test_dev_workflow_bundle_includes_agents_in_bundles_json(self) -> None:
        """t-013: the dev-workflow-harness bundle in bundles.json has an agents key."""
        import json

        bundles_path = TOOLS_DIR / "bundles.json"
        payload = json.loads(bundles_path.read_text(encoding="utf-8"))
        harness = next(
            b for b in payload["bundles"] if b["id"] == "dev-workflow-harness"
        )
        self.assertIn("agents", harness)
        self.assertEqual(
            sorted(harness["agents"]),
            ["code-reviewer", "implementation-auditor", "plan-reviewer", "research-reviewer"],
        )

    def test_install_harness_via_explicit_params(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            for skill in mod.DEV_WORKFLOW_SKILLS:
                self.assertTrue((target / ".agents" / "skills" / skill / "SKILL.md").is_file())
            self.assertTrue((target / ".agents" / "skills" / "cmd-run-dev-workflow" / "SKILL.md").is_file())
            # t-014: agents are installed via --dev-workflow
            for agent in mod.DEV_WORKFLOW_AGENTS:
                self.assertTrue((target / ".claude" / "agents" / f"{agent}.md").is_file())
                self.assertTrue((target / ".github" / "agents" / f"{agent}.agent.md").is_file())

    def test_install_harness_creates_bridge_symlink(self) -> None:
        """Skill installs into a target also create the Claude Code bridge symlink."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_skill(source, "dev-workflow-orchestrator")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=["dev-workflow-orchestrator"],
                agents=[],
                commands=[],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            bridge = target / ".claude" / "skills"
            self.assertTrue(bridge.is_symlink())
            self.assertEqual(os.readlink(bridge), "../.agents/skills")
            self.assertTrue(
                (bridge / "dev-workflow-orchestrator" / "SKILL.md").is_file()
            )

    def test_uninstall_harness_removes_agents(self) -> None:
        """Uninstalling the harness removes agent files from the target."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            install_result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=False,
            )
            self.assertTrue(install_result.ok, install_result.errors)

            uninstall_result = mod.uninstall_items(
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
            )
            self.assertTrue(uninstall_result.ok, uninstall_result.errors)
            for agent in mod.DEV_WORKFLOW_AGENTS:
                self.assertFalse(
                    (target / ".claude" / "agents" / f"{agent}.md").is_file(),
                    f"Agent {agent} claude copy not removed by uninstall",
                )
                self.assertFalse(
                    (target / ".github" / "agents" / f"{agent}.agent.md").is_file(),
                    f"Agent {agent} copilot copy not removed by uninstall",
                )

    def test_override_replaces_agent_files(self) -> None:
        """--override replaces existing agent files in the target."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            # First install
            result1 = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=[],
                override=False,
            )
            self.assertTrue(result1.ok, result1.errors)

            # Modify a target agent file to simulate stale content
            stale_path = target / ".claude" / "agents" / "implementation-auditor.md"
            stale_path.write_text("STALE CONTENT", encoding="utf-8")

            # Override install
            result2 = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=[],
                override=True,
            )
            self.assertTrue(result2.ok, result2.errors)
            self.assertNotEqual(
                stale_path.read_text(encoding="utf-8"),
                "STALE CONTENT",
                "Override did not replace stale agent file",
            )

    def test_compose_dev_workflow_with_agents(self) -> None:
        """--dev-workflow composes with --agents in a single invocation."""
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=list(mod.DEV_WORKFLOW_SKILLS),
                agents=list(mod.DEV_WORKFLOW_AGENTS),
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=False,
            )
            self.assertTrue(result.ok, result.errors)
            for agent in mod.DEV_WORKFLOW_AGENTS:
                self.assertTrue(
                    (target / ".claude" / "agents" / f"{agent}.md").is_file(),
                    f"Composed install did not install agent {agent}",
                )

    def test_run_operation_no_selection_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target"
            with self.assertRaises(mod.InstallerError) as ctx:
                mod.run_operation(
                    target=target,
                    skills=[],
                    agents=[],
                    commands=[],
                    uninstall=False,
                    override=False,
                )
            self.assertIn("Select at least one", str(ctx.exception))


class BundlesJsonPhaseCommandsTests(unittest.TestCase):
    """Tests that bundles.json dev-workflow-harness includes the per-phase commands."""

    def test_bundles_json_dev_workflow_harness_commands_includes_phases(self) -> None:
        bundles_path = TOOLS_DIR / "bundles.json"
        with bundles_path.open(encoding="utf-8") as f:
            data = json.load(f)

        harness = next(
            (b for b in data["bundles"] if b["id"] == "dev-workflow-harness"),
            None,
        )
        self.assertIsNotNone(harness, "dev-workflow-harness bundle not found")
        assert harness is not None  # for type checkers
        self.assertEqual(
            harness["commands"],
            [
                "run-dev-workflow",
                "research",
                "plan",
                "implement",
                "review",
                "commit",
            ],
        )


class PhaseCommandsInstallTests(unittest.TestCase):
    """Integration tests for install/uninstall/override of the per-phase commands."""

    def test_install_dev_workflow_harness_installs_phase_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            for name in mod.DEV_WORKFLOW_COMMANDS:
                skill_md = target / ".agents" / "skills" / f"cmd-{name}" / "SKILL.md"
                self.assertTrue(
                    skill_md.is_file(),
                    f"Expected installed command-skill missing: {skill_md}",
                )
                self.assertIn(
                    "disable-model-invocation: true",
                    skill_md.read_text(encoding="utf-8"),
                    f"Command-skill {name} must carry the invocation flag",
                )

    def test_uninstall_dev_workflow_harness_removes_phase_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=False,
            )

            result = mod.uninstall_items(
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
            )

            self.assertTrue(result.ok, result.errors)
            for name in mod.DEV_WORKFLOW_COMMANDS:
                self.assertFalse(
                    (target / ".agents" / "skills" / name).exists(),
                    f"Command-skill should be removed after uninstall: {name}",
                )

    def test_install_dev_workflow_harness_override_replaces_phase_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_full_harness_source(source)

            mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=False,
            )

            # Write a stale marker into one of the command-skill paths.
            stale = target / ".agents" / "skills" / "cmd-research" / "SKILL.md"
            stale.write_text("stale content", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=[],
                agents=[],
                commands=list(mod.DEV_WORKFLOW_COMMANDS),
                override=True,
            )

            self.assertTrue(result.ok, result.errors)
            self.assertNotEqual(
                stale.read_text(encoding="utf-8"),
                "stale content",
                "Override should replace stale content",
            )


class GuideTravelsWithOrchestratorTests(unittest.TestCase):
    """The dev-workflow guide ships inside the orchestrator skill's references/.

    The guide moved from the repo root into
    `skills/dev-workflow-orchestrator/references/dev-workflow.md`, so installing
    the skill installs the guide — no separate docs install kind exists.
    """

    def test_install_orchestrator_installs_guide_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_skill(source, "dev-workflow-orchestrator")
            guide = source / ".agents" / "skills" / "dev-workflow-orchestrator" / "references" / "dev-workflow.md"
            guide.parent.mkdir(parents=True, exist_ok=True)
            guide.write_text("# Development Workflow\n", encoding="utf-8")

            result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=["dev-workflow-orchestrator"],
                agents=[],
                commands=[],
                override=False,
            )

            self.assertTrue(result.ok, result.errors)
            installed_guide = (
                target / ".agents" / "skills" / "dev-workflow-orchestrator" / "references" / "dev-workflow.md"
            )
            self.assertTrue(installed_guide.is_file())
            self.assertEqual(
                installed_guide.read_text(encoding="utf-8"),
                "# Development Workflow\n",
            )

    def test_uninstall_orchestrator_removes_guide_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            target = Path(tmp) / "target"
            write_source_skill(source, "dev-workflow-orchestrator")
            guide = source / ".agents" / "skills" / "dev-workflow-orchestrator" / "references" / "dev-workflow.md"
            guide.parent.mkdir(parents=True, exist_ok=True)
            guide.write_text("# Development Workflow\n", encoding="utf-8")

            install_result = mod.install_items(
                source_root=source,
                target_root=target,
                skills=["dev-workflow-orchestrator"],
                agents=[],
                commands=[],
                override=False,
            )
            self.assertTrue(install_result.ok, install_result.errors)

            uninstall_result = mod.uninstall_items(
                target_root=target,
                skills=["dev-workflow-orchestrator"],
                agents=[],
                commands=[],
            )

            self.assertTrue(uninstall_result.ok, uninstall_result.errors)
            installed_guide = (
                target / ".agents" / "skills" / "dev-workflow-orchestrator" / "references" / "dev-workflow.md"
            )
            self.assertFalse(installed_guide.exists())

    def test_repo_guide_lives_in_orchestrator_references(self) -> None:
        """The real repo layout keeps the guide inside the skill, not at the root."""
        repo_root = TOOLS_DIR.parent
        self.assertTrue(
            (repo_root / "skills" / "dev-workflow-orchestrator" / "references" / "dev-workflow.md").is_file(),
            "Guide must live at skills/dev-workflow-orchestrator/references/dev-workflow.md",
        )
        self.assertFalse(
            (repo_root / "dev-workflow.md").exists(),
            "Guide must no longer sit at the repo root",
        )
        # The shared layer is generated and untracked; when a local install
        # exists it must carry the guide, but a fresh clone passes without one.
        installed_guide = (
            repo_root / ".agents" / "skills" / "dev-workflow-orchestrator" / "references" / "dev-workflow.md"
        )
        if installed_guide.exists():
            self.assertTrue(
                installed_guide.is_file(),
                "Shared layer must carry the guide after install_portable_skill.py",
            )

    def test_no_docs_member_kind_remains(self) -> None:
        """The docs install kind is fully removed from the installer."""
        self.assertFalse(hasattr(mod, "INSTALLABLE_DOCS"))
        self.assertFalse(hasattr(mod, "doc_copy_pairs"))
        self.assertFalse(hasattr(mod, "doc_remove_paths"))
        self.assertFalse(hasattr(mod, "doc_is_installer_written"))
        self.assertFalse(hasattr(mod, "discover_docs"))
        self.assertFalse(hasattr(mod, "load_docs_descriptions"))
        self.assertFalse(hasattr(mod, "discover_docs_in_project"))


class GuiSharedSlugBundleStateTests(unittest.TestCase):
    """C-04: unchecking an agent that shares a slug with a skill marks the bundle partial."""

    def test_gui_bundle_partial_when_shared_slug_agent_unchecked(self) -> None:
        if mod.tk is None:
            self.skipTest("tkinter unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            write_full_harness_source(source)
            original_root = mod.REPO_ROOT
            mod.REPO_ROOT = source
            root = None
            try:
                try:
                    root = mod.tk.Tk()
                except mod.tk.TclError as exc:
                    self.skipTest(f"no display for tkinter: {exc}")
                root.withdraw()
                app = mod.InstallerApp(root)
                harness = next(b for b in app.skill_bundles if b.id == "dev-workflow-harness")

                # Toggle bundle ON -> all skills, agents, commands checked.
                app._toggle_bundle(harness)
                self.assertTrue(app.skill_vars["code-reviewer"].get())
                self.assertTrue(app.agent_vars["code-reviewer"].get())
                button = app._bundle_buttons["dev-workflow-harness"]
                self.assertIn("selected", button.state())

                # Uncheck ONLY the agent sharing the 'code-reviewer' slug.
                app.agent_vars["code-reviewer"].set(False)
                self.assertTrue(app.skill_vars["code-reviewer"].get())
                self.assertIn("alternate", button.state())
                self.assertNotIn("selected", button.state())

                # Clicking the partial bundle re-selects the missing agent instead of clearing all.
                app._toggle_bundle(harness)
                self.assertTrue(app.agent_vars["code-reviewer"].get())
                self.assertTrue(app.skill_vars["code-reviewer"].get())
            finally:
                mod.REPO_ROOT = original_root
                if root is not None:
                    try:
                        root.destroy()
                    except mod.tk.TclError:
                        pass

    def test_headless_shared_slug_bundle_toggle_sync_and_help(self) -> None:
        class _StubVar:
            def __init__(self, value: bool = False, on_change=None) -> None:
                self._value = value
                self._on_change = on_change

            def get(self) -> bool:
                return self._value

            def set(self, value: bool) -> None:
                self._value = bool(value)
                if self._on_change is not None:
                    self._on_change()

        class _StubButton:
            def __init__(self) -> None:
                self._flags: set[str] = set()

            def state(self, specs: list[str] | None = None) -> tuple[str, ...]:
                if specs is None:
                    return tuple(sorted(self._flags))
                for spec in specs:
                    if spec.startswith("!"):
                        self._flags.discard(spec[1:])
                    else:
                        self._flags.add(spec)
                return tuple(sorted(self._flags))

        app = mod.InstallerApp.__new__(mod.InstallerApp)
        app._syncing_bundle_selection = False
        # Selection-dynamics wiring the trace handler and the batch
        # reconcile read (the real __init__ sets these; the __new__ stub
        # must mirror them).
        app._reconciling_selection = False
        app._prev_selection = {}

        class _StubModeVar:
            def __init__(self, value: str = "install") -> None:
                self._value = value

            def get(self) -> str:
                return self._value

            def set(self, value: str) -> None:
                self._value = value

        app.mode_var = _StubModeVar()
        app._target_bundle = None
        app.skill_bundles = mod.load_skill_bundles()
        harness = next(b for b in app.skill_bundles if b.id == "dev-workflow-harness")

        sync_calls = 0
        orig_sync = app._sync_bundle_toggles

        def counted_sync() -> None:
            nonlocal sync_calls
            sync_calls += 1
            orig_sync()

        app._sync_bundle_toggles = counted_sync  # type: ignore[method-assign]
        app.skill_vars = {
            name: _StubVar(False, on_change=app._on_selection_changed)
            for name in sorted(harness.skills)
        }
        app.agent_vars = {
            name: _StubVar(False, on_change=app._on_selection_changed)
            for name in sorted(harness.agents)
        }
        app.command_vars = {
            name: _StubVar(False, on_change=app._on_selection_changed)
            for name in sorted(harness.commands)
        }
        app.guideline_vars = {}
        app._bundle_buttons = {b.id: _StubButton() for b in app.skill_bundles}

        with (
            mock.patch.object(mod, "tk", None),
            mock.patch.object(mod, "ttk", None),
            mock.patch.object(app, "_show_help_window") as show_help,
        ):
            app._toggle_bundle(harness)
            button = app._bundle_buttons["dev-workflow-harness"]
            self.assertIn("selected", button.state())
            self.assertNotIn("alternate", button.state())
            self.assertTrue(app.skill_vars["code-reviewer"].get())
            self.assertTrue(app.agent_vars["code-reviewer"].get())

            # Uncheck ONLY the shared-slug agent -> partial state + partial help entry.
            app.agent_vars["code-reviewer"].set(False)
            self.assertTrue(app.skill_vars["code-reviewer"].get())
            self.assertIn("alternate", button.state())
            self.assertNotIn("selected", button.state())

            app._show_bundles_help()
            show_help.assert_called_once()
            help_title, help_body = show_help.call_args.args
            self.assertEqual(help_title, "Bundles — Help")
            self.assertIn("Dev-workflow harness (partial)", help_body)

            # Toggling a partial bundle re-selects all members.
            app._toggle_bundle(harness)
            self.assertTrue(app.agent_vars["code-reviewer"].get())
            self.assertIn("selected", button.state())
            self.assertNotIn("alternate", button.state())

            # _set_all batches trace callbacks into a single sync pass per
            # phase: one inside the guarded batch (toggle highlighting),
            # one from the trailing selection reconcile (pg-005 wiring —
            # a batch's closure-wins pass). 2 sync calls, never 2N.
            before = sync_calls
            app._set_all(app.agent_vars, False)
            self.assertEqual(sync_calls - before, 2)
            self.assertIn("alternate", button.state())


class CopyPathIgnoreNonRuntimeTests(unittest.TestCase):
    """C-12 / T-03 / cr-012: copy_path and install_portable_skill share exact non-runtime exclusions."""

    @staticmethod
    def _load_install_portable_skill():
        ips_path = (
            TOOLS_DIR.parent
            / "skills"
            / "skill-creator"
            / "scripts"
            / "install_portable_skill.py"
        )
        sibling_names = ("quick_validate", "scaffold_skill")
        stashed = {
            name: sys.modules.pop(name)
            for name in sibling_names
            if name in sys.modules
        }
        old_path = list(sys.path)
        try:
            sys.path.insert(0, str(ips_path.parent))
            spec = importlib.util.spec_from_file_location(
                "cr012_install_portable_skill", ips_path
            )
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Could not load {ips_path}")
            ips_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ips_mod)
            return ips_mod
        finally:
            sys.path[:] = old_path
            for name in sibling_names:
                sys.modules.pop(name, None)
            sys.modules.update(stashed)

    def test_copy_path_ignore_patterns_match_install_portable_skill(self) -> None:
        ips_mod = self._load_install_portable_skill()
        expected = ips_mod.IGNORE_DIR_NAMES | set(ips_mod.IGNORE_FILE_GLOBS)
        self.assertEqual(set(mod.COPY_IGNORE_PATTERNS), expected)

        captured_patterns: list[tuple[str, ...]] = []
        real_ignore_patterns = mod.shutil.ignore_patterns

        def spy_ignore_patterns(*patterns: str):
            captured_patterns.append(patterns)
            return real_ignore_patterns(*patterns)

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dest = Path(tmp) / "dest"
            src.mkdir()
            (src / "runtime.py").write_text("x = 1\n", encoding="utf-8")
            with mock.patch.object(
                mod.shutil, "ignore_patterns", side_effect=spy_ignore_patterns
            ):
                mod.copy_path(src, dest)

        self.assertEqual(len(captured_patterns), 1)
        self.assertEqual(set(captured_patterns[0]), expected)

    def test_copy_path_excludes_non_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            dest = Path(tmp) / "dest"
            for dirname in (
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
                ".mypy_cache",
                ".hypothesis",
                "node_modules",
                "testdata",
                "fixtures",
                "evals",
            ):
                (src / dirname).mkdir(parents=True)
                (src / dirname / "artifact.txt").write_text("x", encoding="utf-8")
            (src / "check_pre_phase.py").write_text("x = 1\n", encoding="utf-8")
            (src / "test_dry_run.py").write_text("def test_x(): pass\n", encoding="utf-8")
            (src / "helper_test.py").write_text("def test_y(): pass\n", encoding="utf-8")
            (src / "conftest.py").write_text("pass\n", encoding="utf-8")
            (src / ".DS_Store").write_text("ds", encoding="utf-8")
            (src / ".coverage").write_text("cov", encoding="utf-8")
            (src / ".coverage.worker1").write_text("cov", encoding="utf-8")
            (src / "stale.skill").write_text("zip", encoding="utf-8")
            (src / "cached.pyc").write_bytes(b"\x00")
            (src / "cached.pyo").write_bytes(b"\x00")
            (src / "eval-queries.json").write_text("[]", encoding="utf-8")
            (src / "SOURCES.md").write_text("# Sources\n", encoding="utf-8")

            mod.copy_path(src, dest)
            self.assertTrue((dest / "check_pre_phase.py").is_file())
            for excluded in (
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
                ".mypy_cache",
                ".hypothesis",
                "node_modules",
                "testdata",
                "fixtures",
                "evals",
                "test_dry_run.py",
                "helper_test.py",
                "conftest.py",
                ".DS_Store",
                ".coverage",
                ".coverage.worker1",
                "stale.skill",
                "cached.pyc",
                "cached.pyo",
                "eval-queries.json",
                "SOURCES.md",
            ):
                self.assertFalse((dest / excluded).exists(), f"{excluded} must be excluded")


if __name__ == "__main__":
    unittest.main()
