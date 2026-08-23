#!/usr/bin/env python3
"""Generate an advisory implementation checklist for a Python CLI utility."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def build_plan(name: str, *, package: bool, dependencies: str, tests: str) -> str:
    layout = "package under src/" if package else "single-file script"
    dep_line = {
        "none": "Use only the Python standard library unless requirements change.",
        "minimal": "Allow a small number of justified runtime dependencies.",
        "modern": "Use pyproject.toml with locked dependencies, preferably via the project-standard tool or uv.",
    }[dependencies]
    test_line = {
        "pytest": "Use pytest for tests and CLI output capture.",
        "unittest": "Use unittest for standard-library-only tests.",
        "both": "Use pytest for new tests unless repository policy requires unittest compatibility.",
    }[tests]

    return f"""# Python CLI plan for {name}

## Shape
- Target Python: >=3.12
- Layout: {layout}
- Entry point: main(argv: Sequence[str] | None = None) -> int
- Script guard: if __name__ == \"__main__\": raise SystemExit(main())

## CLI contract
- Define positional args, options, stdin/stdout/stderr behavior, and exit codes before coding.
- Keep stdout for intended data output; send diagnostics to stderr via logging or explicit error prints.
- Require an explicit mutation flag for writes/deletes/in-place edits.

## Implementation
- Put argparse parsing in cli.py or parse_args().
- Keep pure domain logic separate from filesystem, subprocess, network, environment, and time.
- Use pathlib.Path, dataclasses, TypedDict/Literal/Protocol where useful.
- Validate raw inputs once at the boundary and convert to typed internal values.
- {dep_line}

## Tests
- {test_line}
- Cover success, invalid args, missing files, malformed input, and failure exit codes.
- Use tmp_path/tempfile for filesystem tests.

## Quality gates
- python -m compileall -q src tests
- python -m ruff format --check .
- python -m ruff check .
- python -m pyright  # or mypy
- python -m pytest -q  # or python -m unittest discover -s tests
"""


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="CLI command or utility name")
    parser.add_argument("--package", action="store_true", help="plan for an installable src-layout package")
    parser.add_argument(
        "--dependencies",
        choices=["none", "minimal", "modern"],
        default="none",
        help="dependency policy",
    )
    parser.add_argument(
        "--tests",
        choices=["pytest", "unittest", "both"],
        default="pytest",
        help="test framework preference",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    print(build_plan(args.name, package=args.package, dependencies=args.dependencies, tests=args.tests))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
