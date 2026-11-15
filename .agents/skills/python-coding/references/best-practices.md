# Python CLI best practices and design patterns

Use this reference during implementation, refactoring, and review.

## Design principles

- Manage complexity as the central goal. Working code that is hard to understand is unfinished.
- Prefer deep modules: small interfaces that hide meaningful complexity.
- Pull unavoidable complexity downward into one module rather than making every caller handle it.
- Define operations by postconditions where possible. Example: `ensure_directory(path)` is often easier to use than `create_directory(path)` that fails if it already exists.
- Apply the rule of three: tolerate small duplication until a real pattern appears, then extract a shared abstraction.
- Split modules by responsibility and information ownership, not chronological steps.
- Invest modestly in surrounding cleanup when changing code, but do not derail the task.

## Naming and structure

- Use precise names that expose intent: `records_by_id`, `load_config`, `iter_rows`, `normalize_path`.
- Avoid vague names: `data`, `result`, `obj`, `helper`, `manager`, unless scope is tiny or domain meaning is obvious.
- Private names with `_` are for module internals. If imported by multiple modules, it is public and should be named/documented accordingly.
- Avoid god modules. When a file exceeds roughly 300-500 lines, inspect whether it owns multiple responsibilities.
- Keep constants at module level. Keep mutable global state out of core logic.

## Type-first development

Use types to design contracts:

- `@dataclass(frozen=True, slots=True)` for internal records.
- `TypedDict` for raw JSON/TOML/config schemas.
- `Literal` for small finite sets such as output modes.
- `NewType` when two strings or ints represent different domain concepts.
- `Protocol` for injectable dependencies such as stores, clocks, command runners, or output sinks.
- `type` aliases for complex or recursive data shapes when Python 3.12+ is guaranteed.

Avoid passing raw dictionaries through many layers. Convert them to typed objects at the boundary.

## Error handling

- Use exceptions for exceptional conditions and return values for expected alternate outcomes.
- Use narrow `try` blocks.
- Catch specific exceptions.
- Convert low-level exceptions into user-facing errors at boundaries.
- Preserve context with `raise NewError(...) from exc`.
- Avoid `except Exception: pass`; it hides bugs.
- Do not use `assert` for user input validation because assertions can be disabled.
- At the CLI boundary, produce concise actionable messages and return a non-zero exit code.

## Resource management

- Use context managers for files, temporary directories, locks, redirected streams, and transactions.
- Open text files with explicit `encoding="utf-8"` unless the input format specifies otherwise.
- Avoid leaking file handles from helper functions; return data or use iterators that clearly own a context.
- For large streams, design iterator APIs and document consumption.

## Data processing

- Prefer builtins and standard library modules: `sum`, `any`, `all`, `min`, `max`, `sorted`, `enumerate`, `zip`, `collections`, `itertools`, `heapq`, `bisect`, `csv`, `json`.
- Use `collections.Counter`, `defaultdict`, `deque`, and `ChainMap` when they simplify logic.
- Use generators for pipelines and large data.
- Avoid clever one-liners when a named loop communicates the transformation better.
- Do not repeatedly scan directories, parse files, or compute indexes inside loops; cache or pre-index when needed.

## CLI user experience

- `--help` should explain the command's purpose, inputs, and common flags.
- Error messages should name the bad value and explain the fix.
- Default output should be readable. Add `--json` or `--format json` for automation.
- Support quiet/verbose modes when diagnostics matter.
- Do not write files unless requested or clearly documented.
- Make dry-run behavior clear.

## Security

- Never pass untrusted text to `shell=True`.
- Validate paths for destructive operations. Be careful with symlinks, `..`, and glob expansion.
- Avoid printing secrets from config, environment variables, tokens, URLs, or subprocess commands.
- Use `secrets` for tokens and random security values, not `random`.
- Use `tempfile` safely; do not create predictable temp paths manually.
- Verify archive extraction paths if handling zip/tar files to avoid path traversal.
- Treat YAML, pickle, marshal, and dynamic imports/eval/exec as unsafe unless controlled and justified.

## Performance

- Measure before optimizing.
- Prefer algorithmic improvements over micro-optimizations.
- Use sets/dicts for membership/indexing when appropriate.
- Stream large files line by line.
- Avoid building giant intermediate lists when an iterator is enough.
- Use `functools.cache` / `lru_cache` only for pure functions with bounded or understood input cardinality.
- Use `multiprocessing` or native/vectorized libraries for CPU-bound work; threads help mostly with blocking I/O.
- Keep startup time low for small CLI utilities by avoiding heavy imports until needed.

## Async and concurrency

- Keep synchronous code synchronous unless concurrency is required.
- Async is useful when the whole IO stack supports it.
- Do not mix blocking file/network/subprocess operations into the event loop without adapters.
- Use `TaskGroup` for structured concurrency and cancellation.
- Keep shared mutable state minimal; use queues or immutable data between workers when possible.

## Documentation

- Write docstrings for public modules, classes, functions, and non-obvious private helpers.
- Explain why, invariants, side effects, and error behavior rather than restating the function name.
- Include examples for CLI usage and non-trivial APIs.
- Keep comments close to the code they explain.

## Style and review checklist

Before finalizing Python CLI code, verify:

- Syntax is valid for Python 3.12+ and does not accidentally require 3.13+ or 3.14+ features.
- Public functions have meaningful type annotations and docstrings when behavior is non-obvious.
- Inputs are validated at the boundary and represented internally by typed values.
- CLI output is deterministic, machine-readable when requested, and separates stdout from stderr.
- Errors include actionable messages without stack traces for normal user mistakes.
- Files are opened with explicit encoding when text is involved.
- Subprocess commands pass argument lists, not shell strings, unless shell behavior is explicitly required.
- Tests cover edge cases and failure modes, not just the happy path.
- The solution is simpler than the problem warrants; no premature framework, plugin system,
  inheritance hierarchy, or global mutable registry.

## Review red flags

- Import-time network calls, filesystem writes, or argument parsing.
- `sys.path.insert` to make imports work.
- Broad `except Exception` without re-raise.
- Mutable default arguments.
- Repeated `.get()` chains on raw dictionaries instead of typed boundary parsing.
- `type=bool` in argparse.
- `shell=True` with user input.
- Logs printed to stdout in a machine-readable command.
- Functions that return unrelated types depending on mode flags.
- Huge functions with parsing, IO, transformation, and presentation interleaved.
- Tests that only assert code runs without checking output.
