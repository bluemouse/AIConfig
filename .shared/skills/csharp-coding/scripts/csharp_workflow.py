#!/usr/bin/env python3
"""Generate a compact .NET/C# command checklist for common project workflows.

This helper does not execute dotnet commands. It prints a command plan that an
assistant can adapt after inspecting the repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def find_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    results: list[Path] = []
    for pattern in patterns:
        results.extend(root.glob(pattern))
    return sorted(set(results))


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def command_plan(mode: str, target: str | None, configuration: str) -> list[str]:
    project_arg = f" {target}" if target else ""
    commands = [
        "dotnet --info",
        "dotnet restore",
        f"dotnet build{project_arg} --no-restore -c {configuration}",
    ]

    if mode in {"test", "fix", "ci", "review"}:
        commands.append(f"dotnet test{project_arg} --no-build -c {configuration}")

    if mode in {"format", "ci", "review"}:
        commands.append("dotnet format --verify-no-changes")

    if mode == "pack":
        commands.append(f"dotnet pack{project_arg} --no-build -c {configuration}")
    elif mode == "publish":
        commands.append(f"dotnet publish{project_arg} --no-build -c {configuration}")
    elif mode == "debug":
        commands.extend(
            [
                "dotnet test --list-tests",
                "dotnet test --filter FullyQualifiedName~<FailingTestName> -v normal",
            ]
        )

    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a C#/.NET workflow checklist.")
    parser.add_argument("--root", default=".", help="Repository root to inspect. Defaults to current directory.")
    parser.add_argument(
        "--mode",
        choices=("fix", "test", "format", "ci", "review", "pack", "publish", "debug"),
        default="fix",
        help="Workflow mode.",
    )
    parser.add_argument("--target", help="Optional solution or project path for dotnet commands.")
    parser.add_argument("--configuration", default="Release", help="Build configuration. Defaults to Release.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Root does not exist: {root}")

    files = find_files(
        root,
        (
            "global.json",
            "*.sln",
            "*.slnx",
            "**/*.csproj",
            "Directory.Build.props",
            "Directory.Build.targets",
            ".editorconfig",
            "NuGet.config",
            "Directory.Packages.props",
        ),
    )

    print("# C#/.NET workflow checklist")
    print(f"root: {root}")
    print(f"mode: {args.mode}")
    print()

    if files:
        print("## Discovered project files")
        for file in files:
            print(f"- {rel(file, root)}")
        print()
    else:
        print("## Discovered project files")
        print("- none found; run from the repository root or pass --root")
        print()

    print("## Commands")
    for command in command_plan(args.mode, args.target, args.configuration):
        print(command)

    print()
    print("## Notes")
    print("- Inspect TargetFramework, LangVersion, Nullable, analyzers, and test framework before editing.")
    print("- Use targeted tests during the edit loop, then run broader verification before completion.")
    print("- Do not claim verification unless these commands or equivalent commands actually ran.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
