#!/usr/bin/env python3
"""
Install or uninstall portable skills and agents from this repo into another project.

Copies the shared-first layout (.shared/ plus tool wrappers under .cursor/, .claude/,
.github/) from AIConfig into a target project root.

Examples:
    python tools/install-skills.py /path/to/other-project
    python tools/install-skills.py /path/to/other-project --skills cpp-coding vulkan-dev
    python tools/install-skills.py /path/to/other-project --agents skill-bootstrapper --uninstall
    python tools/install-skills.py   # GUI when no arguments
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import tkinter as tk
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

REPO_ROOT = Path(__file__).resolve().parent.parent

SHARED_SKILL_DIR = ".shared/skills/{name}"
SHARED_AGENT_FILE = ".shared/agents/{name}.md"

TOOL_SKILL_DIRS = {
    "cursor": ".cursor/skills/{name}",
    "claude": ".claude/skills/{name}",
    "github": ".github/skills/{name}",
}

TOOL_AGENT_FILES = {
    "cursor": ".cursor/agents/{name}.md",
    "claude": ".claude/agents/{name}.md",
    "github": ".github/agents/{name}.agent.md",
}

TOOL_SKILL_SCAN_REL_DIRS = (
    ".cursor/skills",
    ".claude/skills",
    ".github/skills",
)

TOOL_AGENT_SCAN_REL_DIRS = (
    (".cursor/agents", ".md"),
    (".claude/agents", ".md"),
    (".github/agents", ".agent.md"),
)

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

RELOAD_REMINDER = (
    "Reload Cursor, VS Code (Copilot), and Claude Code so each tool "
    "rediscovers the installed skills and agents."
)


class InstallSkillsError(Exception):
    """Raised for user-correctable errors."""


@dataclass
class OperationResult:
    installed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def slugify_name(value: str) -> str:
    """Normalize and validate a skill or agent slug."""
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-")
    if not normalized:
        raise InstallSkillsError("Name cannot be empty after normalization.")
    if len(normalized) > 64:
        raise InstallSkillsError("Name must be 64 characters or fewer.")
    if not SLUG_PATTERN.fullmatch(normalized):
        raise InstallSkillsError(f"Invalid name: {value!r}")
    return normalized


def normalize_names(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        slug = slugify_name(value)
        if slug not in seen:
            seen.add(slug)
            ordered.append(slug)
    return ordered


def discover_skills() -> list[str]:
    names: set[str] = set()
    for rel_dir in TOOL_SKILL_SCAN_REL_DIRS:
        scan_root = REPO_ROOT / rel_dir
        if not scan_root.is_dir():
            continue
        for child in scan_root.iterdir():
            if child.is_dir() and (child / "SKILL.md").is_file():
                names.add(child.name)
    return sorted(names)


def discover_agents() -> list[str]:
    names: set[str] = set()
    for rel_dir, suffix in TOOL_AGENT_SCAN_REL_DIRS:
        scan_root = REPO_ROOT / rel_dir
        if not scan_root.is_dir():
            continue
        for child in scan_root.iterdir():
            if not child.is_file() or child.name.startswith("."):
                continue
            if suffix == ".agent.md" and child.name.endswith(".agent.md"):
                names.add(child.name[: -len(".agent.md")])
            elif suffix == ".md" and child.suffix == ".md" and not child.name.endswith(".agent.md"):
                names.add(child.stem)
    return sorted(names)


def validate_target(source: Path, target: Path, *, create: bool) -> Path:
    target = target.resolve()
    source = source.resolve()
    if target == source:
        raise InstallSkillsError("Target cannot be the AIConfig repository root.")
    if source in target.parents:
        raise InstallSkillsError(
            "Target cannot be inside the AIConfig repository "
            f"({target} is under {source})."
        )
    if not target.exists():
        if create:
            target.mkdir(parents=True, exist_ok=True)
        return target
    if not target.is_dir():
        raise InstallSkillsError(f"Target is not a directory: {target}")
    return target


def format_rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def skill_copy_pairs(source_root: Path, target_root: Path, name: str) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    shared_src = source_root / SHARED_SKILL_DIR.format(name=name)
    shared_dest = target_root / SHARED_SKILL_DIR.format(name=name)
    pairs.append((shared_src, shared_dest))
    for rel_template in TOOL_SKILL_DIRS.values():
        src = source_root / rel_template.format(name=name)
        if src.exists():
            pairs.append((src, target_root / rel_template.format(name=name)))
    return pairs


def agent_copy_pairs(source_root: Path, target_root: Path, name: str) -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    shared_src = source_root / SHARED_AGENT_FILE.format(name=name)
    shared_dest = target_root / SHARED_AGENT_FILE.format(name=name)
    pairs.append((shared_src, shared_dest))
    for rel_template in TOOL_AGENT_FILES.values():
        src = source_root / rel_template.format(name=name)
        if src.exists():
            pairs.append((src, target_root / rel_template.format(name=name)))
    return pairs


def skill_remove_paths(target_root: Path, name: str) -> list[Path]:
    paths = [target_root / SHARED_SKILL_DIR.format(name=name)]
    for rel_template in TOOL_SKILL_DIRS.values():
        paths.append(target_root / rel_template.format(name=name))
    return paths


def agent_remove_paths(target_root: Path, name: str) -> list[Path]:
    paths = [target_root / SHARED_AGENT_FILE.format(name=name)]
    for rel_template in TOOL_AGENT_FILES.values():
        paths.append(target_root / rel_template.format(name=name))
    return paths


def remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.is_file():
        path.unlink()


def copy_path(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest)
    elif src.is_file():
        shutil.copy2(src, dest)
    else:
        raise InstallSkillsError(f"Source path does not exist: {src}")


def install_items(
    *,
    source_root: Path,
    target_root: Path,
    skills: Sequence[str],
    agents: Sequence[str],
    override: bool,
) -> OperationResult:
    result = OperationResult()
    target_root = validate_target(source_root, target_root, create=True)

    for name in skills:
        slug = slugify_name(name)
        pairs = skill_copy_pairs(source_root, target_root, slug)
        shared_src = pairs[0][0]
        if not shared_src.is_dir():
            result.errors.append(
                f"skill {slug}: missing shared source {format_rel(shared_src, source_root)}"
            )
            continue

        for src, dest in pairs:
            rel_dest = format_rel(dest, target_root)
            if dest.exists():
                if not override:
                    result.skipped.append(rel_dest)
                    continue
                remove_path(dest)
            try:
                copy_path(src, dest)
                result.installed.append(rel_dest)
            except OSError as exc:
                result.errors.append(f"{rel_dest}: {exc}")

    for name in agents:
        slug = slugify_name(name)
        pairs = agent_copy_pairs(source_root, target_root, slug)
        shared_src = pairs[0][0]
        if not shared_src.is_file():
            result.errors.append(
                f"agent {slug}: missing shared source {format_rel(shared_src, source_root)}"
            )
            continue

        for src, dest in pairs:
            rel_dest = format_rel(dest, target_root)
            if dest.exists():
                if not override:
                    result.skipped.append(rel_dest)
                    continue
                remove_path(dest)
            try:
                copy_path(src, dest)
                result.installed.append(rel_dest)
            except OSError as exc:
                result.errors.append(f"{rel_dest}: {exc}")

    return result


def uninstall_items(
    *,
    target_root: Path,
    skills: Sequence[str],
    agents: Sequence[str],
) -> OperationResult:
    result = OperationResult()
    target_root = validate_target(REPO_ROOT, target_root, create=False)
    if not target_root.exists():
        return result

    for name in skills:
        slug = slugify_name(name)
        for path in skill_remove_paths(target_root, slug):
            if path.exists():
                try:
                    remove_path(path)
                    result.removed.append(format_rel(path, target_root))
                except OSError as exc:
                    result.errors.append(f"{format_rel(path, target_root)}: {exc}")

    for name in agents:
        slug = slugify_name(name)
        for path in agent_remove_paths(target_root, slug):
            if path.exists():
                try:
                    remove_path(path)
                    result.removed.append(format_rel(path, target_root))
                except OSError as exc:
                    result.errors.append(f"{format_rel(path, target_root)}: {exc}")

    return result


def format_result(result: OperationResult, *, uninstall: bool) -> str:
    lines: list[str] = []
    if uninstall:
        if result.removed:
            lines.append("Removed:")
            lines.extend(f"  - {path}" for path in result.removed)
        else:
            lines.append("Removed: (nothing matched)")
    else:
        if result.installed:
            lines.append("Installed:")
            lines.extend(f"  - {path}" for path in result.installed)
        if result.skipped:
            lines.append("Skipped (already exists; use --override to replace):")
            lines.extend(f"  - {path}" for path in result.skipped)
        if not result.installed and not result.skipped:
            lines.append("Installed: (nothing copied)")

    if result.errors:
        lines.append("Errors:")
        lines.extend(f"  - {msg}" for msg in result.errors)

    if result.ok and not uninstall and result.installed:
        lines.append("")
        lines.append(RELOAD_REMINDER)

    return "\n".join(lines)


def run_operation(
    *,
    target: Path,
    skills: Sequence[str],
    agents: Sequence[str],
    uninstall: bool,
    override: bool,
) -> tuple[int, str]:
    if not skills and not agents:
        raise InstallSkillsError("Select at least one skill or agent.")

    if uninstall:
        result = uninstall_items(target_root=target, skills=skills, agents=agents)
    else:
        result = install_items(
            source_root=REPO_ROOT,
            target_root=target,
            skills=skills,
            agents=agents,
            override=override,
        )

    message = format_result(result, uninstall=uninstall)
    if result.errors:
        return 1, message
    return 0, message


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install or uninstall portable skills and agents from this AIConfig "
            "repository into another project."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/install-skills.py /path/to/project\n"
            "  python tools/install-skills.py /path/to/project --skills cpp-coding\n"
            "  python tools/install-skills.py /path/to/project --uninstall --agents skill-bootstrapper\n"
            "\n"
            "Run without arguments to open the GUI."
        ),
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Destination project root.",
    )
    parser.add_argument(
        "--skills",
        nargs="+",
        metavar="NAME",
        help="Skill names to install or uninstall (default: all discovered skills).",
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        metavar="NAME",
        help="Agent names to install or uninstall (default: all discovered agents).",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove the selected skills and agents from the target project.",
    )
    parser.add_argument(
        "--override",
        action="store_true",
        help="Replace existing skills and agents in the target project.",
    )
    return parser.parse_args(argv)


def run_cli(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.target is None:
        print("error: TARGET is required in CLI mode.", file=sys.stderr)
        print("Run without arguments to open the GUI.", file=sys.stderr)
        return 2

    try:
        target = Path(args.target).expanduser().resolve()
        skills = normalize_names(args.skills) if args.skills else discover_skills()
        agents = normalize_names(args.agents) if args.agents else discover_agents()
        code, message = run_operation(
            target=target,
            skills=skills,
            agents=agents,
            uninstall=args.uninstall,
            override=args.override,
        )
    except InstallSkillsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(message)
    return code


class InstallSkillsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Install AIConfig Skills and Agents")
        self.root.minsize(640, 520)

        self.skills = discover_skills()
        self.agents = discover_agents()
        self.skill_vars: dict[str, tk.BooleanVar] = {}
        self.agent_vars: dict[str, tk.BooleanVar] = {}

        self.target_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="install")
        self.override_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)

        target_frame = ttk.LabelFrame(outer, text="Target project", padding=8)
        target_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Entry(target_frame, textvariable=self.target_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(target_frame, text="Browse…", command=self._browse_target).pack(side=tk.LEFT)

        lists = ttk.Frame(outer)
        lists.pack(fill=tk.BOTH, expand=True)

        self._add_checkbox_list(
            lists,
            title="Skills",
            items=self.skills,
            var_map=self.skill_vars,
            column=0,
        )
        self._add_checkbox_list(
            lists,
            title="Agents",
            items=self.agents,
            var_map=self.agent_vars,
            column=1,
        )

        options = ttk.LabelFrame(outer, text="Options", padding=8)
        options.pack(fill=tk.X, pady=8)
        ttk.Radiobutton(options, text="Install", variable=self.mode_var, value="install").pack(
            side=tk.LEFT, padx=(0, 12)
        )
        ttk.Radiobutton(
            options, text="Uninstall", variable=self.mode_var, value="uninstall"
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(options, text="Override existing", variable=self.override_var).pack(
            side=tk.LEFT
        )

        actions = ttk.Frame(outer)
        actions.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(actions, text="Run", command=self._run).pack(side=tk.LEFT)
        ttk.Button(actions, text="Close", command=self.root.destroy).pack(side=tk.LEFT, padx=8)

        log_frame = ttk.LabelFrame(outer, text="Output", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.log.pack(fill=tk.BOTH, expand=True)

    def _add_checkbox_list(
        self,
        parent: ttk.Frame,
        *,
        title: str,
        items: list[str],
        var_map: dict[str, tk.BooleanVar],
        column: int,
    ) -> None:
        frame = ttk.LabelFrame(parent, text=title, padding=8)
        frame.grid(row=0, column=column, sticky="nsew", padx=(0, 8 if column == 0 else 0))
        parent.columnconfigure(column, weight=1)
        parent.rowconfigure(0, weight=1)

        controls = ttk.Frame(frame)
        controls.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(
            controls,
            text="Select all",
            command=lambda: self._set_all(var_map, True),
        ).pack(side=tk.LEFT)
        ttk.Button(
            controls,
            text="Select none",
            command=lambda: self._set_all(var_map, False),
        ).pack(side=tk.LEFT, padx=6)

        canvas = tk.Canvas(frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind(
            "<Configure>",
            lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for item in items:
            var = tk.BooleanVar(value=True)
            var_map[item] = var
            ttk.Checkbutton(inner, text=item, variable=var).pack(anchor=tk.W)

        if not items:
            ttk.Label(inner, text="(none discovered)").pack(anchor=tk.W)

    def _set_all(self, var_map: dict[str, tk.BooleanVar], value: bool) -> None:
        for var in var_map.values():
            var.set(value)

    def _browse_target(self) -> None:
        selected = filedialog.askdirectory(title="Select target project root")
        if selected:
            self.target_var.set(selected)

    def _append_log(self, text: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _selected(self, var_map: dict[str, tk.BooleanVar]) -> list[str]:
        return sorted(name for name, var in var_map.items() if var.get())

    def _run(self) -> None:
        target_text = self.target_var.get().strip()
        if not target_text:
            messagebox.showerror("Missing target", "Choose a target project folder.")
            return

        skills = self._selected(self.skill_vars)
        agents = self._selected(self.agent_vars)
        if not skills and not agents:
            messagebox.showerror("Nothing selected", "Select at least one skill or agent.")
            return

        try:
            target = Path(target_text).expanduser().resolve()
            code, message = run_operation(
                target=target,
                skills=skills,
                agents=agents,
                uninstall=self.mode_var.get() == "uninstall",
                override=self.override_var.get(),
            )
        except InstallSkillsError as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._append_log(message)
        if code != 0:
            messagebox.showwarning("Completed with errors", "See output for details.")


def run_gui() -> int:
    if not sys.platform.startswith("win") and not os.environ.get("DISPLAY"):
        print(
            "error: No display available for the GUI.\n"
            "Use the CLI instead, for example:\n"
            "  python tools/install-skills.py /path/to/project",
            file=sys.stderr,
        )
        return 2

    try:
        root = tk.Tk()
    except tk.TclError as exc:
        print(f"error: Could not start GUI: {exc}", file=sys.stderr)
        print(
            "Use the CLI instead, for example:\n"
            "  python tools/install-skills.py /path/to/project",
            file=sys.stderr,
        )
        return 2

    InstallSkillsApp(root)
    root.mainloop()
    return 0


def main() -> int:
    if len(sys.argv) == 1:
        return run_gui()
    return run_cli(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
