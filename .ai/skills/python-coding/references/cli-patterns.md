# Python CLI script and utility patterns

Use this reference when designing command-line interfaces, single-file scripts, and utility packages.

## Standard layout for a single-file script

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from collections.abc import Sequence

LOG = logging.getLogger(__name__)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Do one clear job.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def run(input_path: Path) -> int:
    # Domain logic or orchestration. Keep it testable.
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    try:
        return run(args.input)
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

Remember to import `sys` if printing to stderr or using `sys.stdin` / `sys.stdout`.

## Standard package layout for a CLI utility

```text
my-tool/
  pyproject.toml
  README.md
  src/
    my_tool/
      __init__.py
      cli.py          # argparse and main()
      core.py         # pure logic
      io.py           # filesystem/network/subprocess adapters
      models.py       # dataclasses and TypedDicts
  tests/
    test_cli.py
    test_core.py
```

Split only when each file has a stable responsibility. Do not create empty architecture for a 40-line script.

## CLI contract checklist

Define these before writing code:

- Command purpose and non-goals.
- Positional arguments and options.
- Which inputs can come from files, stdin, environment variables, or config files.
- Output format: human text, JSON, CSV, table, newline-delimited records, or no output.
- Exit codes: normally `0` success, `1` unexpected failure, `2` command-line usage or validation failure. Document custom codes.
- Mutating behavior: dry-run default, explicit `--write`, `--in-place`, `--delete`, or `--force` flags.
- Idempotency: what happens when the command is rerun.
- Error policy: fail fast, skip bad records with warnings, or collect/report all errors.

## argparse guidance

Use `argparse` for standard library CLIs:

- `ArgumentParser(description=...)` with concise help.
- `type=Path` for paths, then validate existence and file/directory kind explicitly.
- `choices=[...]` for closed sets.
- `action="store_true"` for booleans; avoid `type=bool`.
- `subparsers = parser.add_subparsers(dest="command", required=True)` for multi-command tools.
- Use `parser.error("message")` for CLI usage errors inside parsing helpers.
- Keep parser construction separate from execution so tests can parse argv directly.

## stdin, stdout, and stderr

- Use stdout for intended data output.
- Use stderr for diagnostics, progress, warnings, and errors.
- Never mix logs into stdout when stdout might be piped into another tool.
- Support `-` as stdin/stdout only when useful and documented.
- For machine-readable output, prefer JSON or JSON Lines. Ensure deterministic key order only if consumers need stable text diffs.
- Avoid progress bars unless the command is interactive and stdout is not data output.

## Filesystem patterns

- Use `pathlib.Path` throughout internal APIs.
- Use `with path.open("r", encoding="utf-8") as f:` for text.
- Use binary mode for binary formats and explicit decode/encode at boundaries.
- Use `tempfile.NamedTemporaryFile` or write to a sibling temp file then `replace()` for safer atomic-ish writes.
- Use `path.mkdir(parents=True, exist_ok=True)` for ensure-directory semantics.
- Use `shutil` for copying/removing trees rather than manual recursion.
- Avoid following symlinks destructively unless the behavior is intentional and documented.

## JSON, CSV, and TOML

- Use `json.load` / `json.dump` with explicit encoding and helpful errors.
- Use `json.dumps(..., indent=2, sort_keys=True)` for deterministic human-readable config only when key order does not carry semantic meaning.
- Use `csv` module rather than splitting by commas.
- Use `newline=""` when opening CSV files.
- Use `tomllib` for reading TOML in Python 3.11+. Writing TOML requires a third-party library or a focused serializer.

## Subprocess patterns

Prefer argument lists and no shell:

```python
result = subprocess.run(
    ["git", "status", "--short"],
    cwd=repo,
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
    check=False,
)
if result.returncode != 0:
    raise RuntimeError(result.stderr.strip() or "git status failed")
```

Rules:

- Use `check=True` when a non-zero status should raise immediately and stderr does not need custom parsing.
- Use `capture_output=True` only when you need the output; otherwise let the child inherit streams.
- Preserve semantic whitespace when parsing CLI output. Use `rstrip("\n\r")`, not blanket `.strip()`, if leading spaces have meaning.
- Use `shlex.join(args)` for diagnostic display, not execution.
- Use `shell=True` only for deliberate shell syntax; never with untrusted user input.

## Logging pattern

Libraries and helpers should use loggers, not print:

```python
LOG = logging.getLogger(__name__)
LOG.debug("loading %s", path)
```

The CLI boundary configures logging once. Avoid configuring logging at import time.

## Configuration precedence

Use a clear order, typically:

1. CLI flags.
2. Environment variables.
3. Config file.
4. Defaults.

Document names and types. Convert all raw config values into a typed config dataclass before core logic.

## Error reporting pattern

Define domain-specific exceptions when they improve messages:

```python
class ConfigError(Exception):
    """Raised when user-provided configuration is invalid."""
```

At the CLI boundary:

- Convert expected user errors into concise messages and non-zero exit codes.
- Let programmer errors surface during development unless the user requested a polished production CLI.
- Use `--debug` or `--traceback` to optionally show tracebacks.

## Machine-readable output

For JSON output:

- Do not log to stdout.
- Prefer one JSON value for whole-result output and JSON Lines for streaming records.
- Use stable field names and documented schema.
- Use `None` deliberately; avoid missing keys unless schema allows them.

## Destructive command safeguards

For file mutations, deletions, network writes, or subprocess changes:

- Default to dry-run when risk is high.
- Require `--write`, `--apply`, or `--yes` for changes.
- Show a summary before applying destructive changes in interactive contexts.
- Ensure repeated execution is safe or clearly documented.
