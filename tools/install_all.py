#!/usr/bin/env python3
"""Regenerate every installed skill, agent, command, and guideline package.

A fresh clone ships no .agents/skills/, .claude/agents/, or .github/agents/
(untracked generated output), so tools/installer.py has an empty catalog
until each bootstrap package is installed. This script runs the three
install_portable_* installers over every bootstrap skill, agent, and
command in one pass — the bulk form of the per-package commands in
README.md § Common commands.

Guideline skill packages (guidelines-*) are installer-generated from
guidelines/<name>.md, not bootstrap output; this script regenerates them
too, through the distribution installer's own guideline pass, so the
wrap/inject logic stays in one place. To regenerate a single guideline
without the rest: `python tools/installer.py . --guidelines <name> --override`.

Usage:
    python tools/install_all.py            # install everything, overwrite
    python tools/install_all.py --no-overwrite
    python tools/install_all.py --skip-validate
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

INSTALLER_SPECS = (
    # (kind dir, marker file, creator skill, install func, validate adapter)
    # The validate adapter normalizes each installer's return value to the
    # list of paths validate_install expects: skills return [skill_dir];
    # agents and commands return (written_paths, removed_paths).
    (
        "skills",
        "SKILL.md",
        "skill-creator",
        "install_portable_skill",
        lambda written: written,
    ),
    (
        "agents",
        "AGENT.md",
        "agent-creator",
        "install_portable_agent",
        lambda written: written[0],
    ),
    (
        "commands",
        "COMMAND.md",
        "command-creator",
        "install_portable_command",
        lambda written: written[0],
    ),
)


def load_installer_module(creator_skill: str) -> object:
    """Load an install_portable_* module from its creator skill's scripts dir.

    The creator scripts import siblings (quick_validate, scaffold_*) by
    bare name, so their directory goes on sys.path for the load and is
    restored afterwards — the same isolation pattern tools/installer.py
    uses for the bridge helper.
    """
    scripts_dir = REPO_ROOT / "skills" / creator_skill / "scripts"
    module_path = scripts_dir / f"install_portable_{creator_skill.removesuffix('-creator')}.py"
    if not module_path.is_file():
        raise ImportError(f"Installer script not found: {module_path}")
    old_path = list(sys.path)
    # Each creator's scripts dir has same-named siblings (quick_validate,
    # scaffold_*); drop any the load cached so the next creator's bare-name
    # imports resolve to its own directory, not this one's.
    old_modules = dict(sys.modules)
    try:
        sys.path.insert(0, str(scripts_dir))
        spec = importlib.util.spec_from_file_location(
            f"install_all_{creator_skill}", module_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = old_path
        sys.modules.clear()
        sys.modules.update(old_modules)
    return module


def load_distribution_installer() -> object:
    """Load tools/installer.py, which owns the guideline wrap/inject logic.

    Loaded by file location rather than `import installer` so the module
    resolves whether or not tools/ is on sys.path — the tests load both
    scripts the same way.
    """
    module_path = Path(__file__).resolve().parent / "installer.py"
    spec = importlib.util.spec_from_file_location("install_all_installer", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the module's frozen dataclasses resolve their
    # defining module through sys.modules at class-creation time.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bootstrap_names(kind_dir: Path, marker: str) -> list[str]:
    """Return sorted bootstrap package names under kind_dir carrying marker."""
    if not kind_dir.is_dir():
        return []
    return sorted(
        child.name
        for child in kind_dir.iterdir()
        if child.is_dir() and (child / marker).is_file()
    )


def guideline_names(root: Path, installer: object) -> list[str]:
    """Return sorted guideline names present under root/guidelines/.

    Mirrors bootstrap_names' walk-what's-there discovery: a fresh clone's
    guideline set is whatever sources exist, so a new guideline needs no
    edit here. An absent guidelines/ dir (test fixtures) means no pass.
    Only slug-clean stems qualify: install_items slugifies each name before
    computing its destination, so a non-slug stem (stray editor lock file,
    uppercase draft) would install under a different name than it reports,
    or collide with another stem's slug — filtering here keeps discovery,
    install, and reporting on one name.
    """
    guidelines_dir = root / "guidelines"
    if not guidelines_dir.is_dir():
        return []
    names = []
    for child in guidelines_dir.glob("*.md"):
        try:
            if installer.slugify_name(child.stem) == child.stem:
                names.append(child.stem)
        except installer.InstallerError:
            continue
    return sorted(names)


def install_all(root: Path, *, overwrite: bool = True, skip_validate: bool = False) -> int:
    """Install every bootstrap package; return the number of failures."""
    failures = 0
    seen_warnings: set[str] = set()
    for kind_dir_name, marker, creator_skill, install_func, adapt_written in INSTALLER_SPECS:
        try:
            module = load_installer_module(creator_skill)
        except Exception as exc:
            failures += 1
            print(f"error: {kind_dir_name}: {exc}", file=sys.stderr)
            continue
        install = getattr(module, install_func)
        validate_install = getattr(module, "validate_install", None)
        validator = Path(module.__file__).resolve().parent / "quick_validate.py"
        for name in bootstrap_names(root / kind_dir_name, marker):
            source = root / kind_dir_name / name
            label = f"{kind_dir_name}/{name}"
            try:
                # The skill installer prints a bridge-symlink warning to
                # stderr on hosts without symlink privilege; once per run is
                # informative, once per package is noise. Forward each
                # distinct warning line only the first time it appears.
                stderr_capture = io.StringIO()
                with contextlib.redirect_stderr(stderr_capture):
                    written = install(
                        root=root,
                        source=source,
                        **{f"{creator_skill.removesuffix('-creator')}_name": name},
                        overwrite=overwrite,
                    )
                for line in stderr_capture.getvalue().splitlines():
                    if line not in seen_warnings:
                        seen_warnings.add(line)
                        print(line, file=sys.stderr)
                if not skip_validate and callable(validate_install):
                    if creator_skill == "skill-creator":
                        validate_install(root, name, validator)
                    elif creator_skill == "agent-creator":
                        validate_install(adapt_written(written), validator)
                    else:
                        validate_install(adapt_written(written))
            except Exception as exc:
                failures += 1
                print(f"error: {label}: {exc}", file=sys.stderr)
            else:
                print(f"installed {label}")
    failures += install_guidelines(root, overwrite=overwrite)
    return failures


def install_guidelines(root: Path, *, overwrite: bool) -> int:
    """Regenerate the local guidelines-* skill packages; return failures.

    Guidelines are installer-generated (guidelines/<name>.md wrapped into
    .agents/skills/guidelines-<name>/SKILL.md with injected name
    frontmatter), so this delegates to the distribution installer's own
    pass instead of duplicating the wrap logic. install_items only allows
    a self-target for a guidelines-only selection, which is exactly this
    call's shape.
    """
    try:
        installer = load_distribution_installer()
        names = guideline_names(root, installer)
        if not names:
            return 0
        result = installer.install_items(
            source_root=root,
            target_root=root,
            skills=(),
            agents=(),
            commands=(),
            guidelines=names,
            override=overwrite,
            allow_self=True,
        )
    except Exception as exc:
        print(f"error: guidelines: {exc}", file=sys.stderr)
        return 1
    # Report straight off the installer's own recorded paths instead of
    # re-deriving destinations, so a successfully installed guideline can
    # never miss both lists and print nothing.
    prefix = installer.GUIDELINE_SKILL_PREFIX
    for rel_dest in result.installed:
        print(f"installed guidelines/{guideline_name_from_rel(rel_dest, prefix)}")
    for rel_dest in result.skipped:
        print(
            f"skipped guidelines/{guideline_name_from_rel(rel_dest, prefix)} "
            "(already installed; use --overwrite)"
        )
    for error in result.errors:
        print(f"error: {error}", file=sys.stderr)
    return len(result.errors)


def guideline_name_from_rel(rel_dest: str, prefix: str) -> str:
    """Invert a recorded guideline dest path back to its guideline name.

    A guideline dest is <skills dir>/guidelines-<name>/SKILL.md, so the
    skill directory name minus the guideline prefix is the name. Path()
    parses the rel string on either separator convention.
    """
    return Path(rel_dest).parts[-2].removeprefix(prefix)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate all installed skills, agents, commands, and guideline "
            "packages from bootstrap sources."
        )
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root directory (default: current directory).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Overwrite existing installed output (default: true).",
    )
    parser.add_argument(
        "--no-overwrite",
        action="store_false",
        dest="overwrite",
        help="Refuse to overwrite existing installed output.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip post-install validation (not recommended).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = Path(args.root).resolve()
    if root != REPO_ROOT:
        print(
            f"error: root must be this AIConfig repository ({REPO_ROOT}), got {root}",
            file=sys.stderr,
        )
        return 2
    failures = install_all(
        root, overwrite=args.overwrite, skip_validate=args.skip_validate
    )
    if failures:
        print(f"{failures} install(s) failed", file=sys.stderr)
        return 1
    print(
        "\nRestart or reload Claude Code so it rediscovers installed skills and "
        "command-skills through the .claude/skills bridge (and picks up the "
        "agent files under .claude/agents); VS Code (Copilot) "
        "discover .agents/ and .github/agents/ natively on their next session."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
