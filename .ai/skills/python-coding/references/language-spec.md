# Python 3.12+ language specification guide

Use this reference when exact Python grammar, syntax, semantics, or version boundaries matter.

## Baseline

- Target Python 3.12+. Do not emit Python 3.13+ or 3.14+ features unless the user asks for them and the runtime supports them.
- Prefer code that is valid under CPython 3.12, 3.13, and 3.14 when feasible.
- Use the official Python Language Reference as the authority for exact syntax and semantics; the Python Tutorial is an informal introduction.

## Source files, lexical structure, and layout

- Source text is decoded as UTF-8 by default. Add an encoding declaration only when a non-UTF-8 encoding is genuinely required.
- Logical lines normally end at NEWLINE. Prefer implicit line joining inside `()`, `[]`, or `{}` over backslash continuation.
- Comments start with `#` outside string literals and continue to the end of the physical line.
- Indentation determines block structure. Use spaces, not tabs; four spaces per level is the default convention.
- A statement list after a colon can appear on one line, but avoid it except for extremely small examples; multi-line suites are clearer.
- Names are case-sensitive identifiers. Avoid shadowing builtins such as `list`, `dict`, `id`, `input`, `file`, `type`, and `str`.
- Soft keywords such as `match`, `case`, and `_` have contextual meaning and can still appear as ordinary names in non-keyword positions, but avoid confusing reuse.

## Literals and core data types

- Use `None`, `True`, and `False` as singletons; compare with `is` / `is not`.
- Use f-strings for readable interpolation. Keep format logic simple; move complex formatting into named helpers.
- Use raw strings for regex and Windows-like path patterns only when they do not end with a single trailing backslash.
- Use list, dict, set, and tuple literals over constructor calls for literal values.
- Use tuples for fixed-position records only when position semantics are obvious or named elsewhere. Use dataclasses or NamedTuple for richer records.
- Use `bytes` for binary data and `str` for text. Decode/encode explicitly at IO boundaries.
- Floating point has representation limitations. Use `decimal.Decimal` for exact decimal finance-like arithmetic and `math.isclose()` for approximate comparisons.

## Expressions and evaluation

- Understand truthiness: empty containers, `0`, `0.0`, `False`, and `None` are falsey. Do not use truthiness when distinguishing empty from missing.
- `and` and `or` short-circuit and return one operand, not necessarily `bool`.
- Comparisons chain: `a < b < c` evaluates `b` once and means `a < b and b < c`.
- Assignment expressions (`:=`) are useful for avoiding duplicate work, but should not reduce readability.
- Comprehensions are appropriate for simple mapping/filtering. Use loops when logic requires multiple branches, side effects, error handling, or named intermediate values.
- Generator expressions and generator functions are preferred for large streams and pipelines.
- `yield from` delegates to sub-iterators; use it when a generator simply forwards another iterable.
- `match` uses structural pattern matching, not switch/case. Use it for shaped data, tagged states, AST-like values, or command dispatch; avoid it for simple equality cases where a dict dispatch is clearer.

## Statements and control flow

- `if` / `elif` / `else` is the ordinary branching structure; keep conditions named when complex.
- `for` iterates over any iterable. Prefer `enumerate`, `zip(strict=True)`, and direct iteration over index loops.
- Loop `else` runs only if the loop did not terminate with `break`; use sparingly and only when it improves clarity.
- Use `with` for deterministic cleanup of files, locks, temporary resources, context managers, and redirected IO.
- Use `try` blocks narrowly around the operation that can fail. Avoid wrapping large functions in one broad handler.
- Use `raise ... from exc` when converting lower-level errors into domain-specific errors.
- Use `ExceptionGroup` and `except*` only when handling multiple independent concurrent or batch failures.

## Functions

- Function definition order for parameters is: positional-only, positional-or-keyword, varargs, keyword-only, kwargs.
- Use positional-only parameters (`/`) mainly for stable public APIs or functions that mirror builtins.
- Use keyword-only parameters (`*`) for boolean flags, options, and values whose meaning is not obvious positionally.
- Avoid mutable default arguments. Use `None` plus initialization or an immutable sentinel.
- Return values consistently. Avoid functions that sometimes return a value and sometimes implicitly return `None` unless the type says so.
- Use small private helpers to name concepts, not to split every two lines into a pass-through function.
- Use decorators only when they clarify a repeated cross-cutting concern such as caching, registration, validation, timing, or CLI wiring.

## Classes, data model, and protocols

- Use functions for behavior without state. Use classes when they protect invariants, carry state, or expose a meaningful abstraction.
- Use `@dataclass(frozen=True, slots=True)` for immutable internal data records unless mutation is required.
- Avoid inheritance-first designs. Prefer composition, Protocols, callables, and plain data structures.
- Use properties to preserve invariants or computed attributes; do not hide expensive or side-effecting work behind property syntax.
- Implement special methods only when the object genuinely behaves like that protocol (`__iter__`, `__len__`, `__enter__`, `__exit__`, ordering methods, etc.).
- Keep equality, hashing, and mutability consistent. Do not make mutable objects hashable unless identity hashing is intentional.

## Modules, packages, and imports

- A module is executed once at import time. Keep import-time work cheap and side-effect free.
- Place imports at the top unless delaying an import solves a real cycle, optional dependency, or startup-cost issue.
- Import standard library, third-party, then local modules in separate groups.
- Avoid wildcard imports outside package `__init__.py` re-export patterns.
- Avoid `sys.path` mutation in scripts. Fix package layout, use editable installs, or invoke modules with `python -m package.module`.
- Use `if __name__ == "__main__": raise SystemExit(main())` for executable modules.

## Type system conventions for Python 3.12+

- Use built-in generics: `list[str]`, `dict[str, int]`, `tuple[str, ...]`.
- Use union syntax: `str | None`, not `Optional[str]` unless project style requires it.
- Use `type` statements for type aliases in Python 3.12+ when readability improves: `type JsonObject = dict[str, JsonValue]`.
- Use `typing.Self` for fluent methods returning the current class type.
- Use `typing.Protocol` for structural interfaces and dependency injection.
- Use `typing.TypedDict` for JSON/config objects at the boundary; convert to dataclasses for internal logic if invariants matter.
- Use `typing.Literal` for closed sets of string states, modes, or formats.
- Use `typing.NewType` when two runtime-identical primitives carry different domain meaning.
- Use `typing.Never` / `NoReturn` for functions that always raise or exit.
- Use `assert_never()` when exhaustiveness checking matters for discriminated unions.

## Async, concurrency, and generators

- Use `asyncio` for I/O concurrency only when dependencies and operations are async-aware.
- Do not mark code `async` just because it may be slow; CPU work needs multiprocessing, native libraries, or algorithmic improvements.
- Keep cancellation semantics in mind: use `try/finally` for cleanup and avoid swallowing `CancelledError`.
- Use `asyncio.TaskGroup` for structured concurrency in Python 3.11+.
- Use `concurrent.futures.ThreadPoolExecutor` for blocking I/O adapters and `ProcessPoolExecutor` for CPU-bound pure-Python work when overhead is justified.

## Version-boundary reminders

- Python 3.12 introduced PEP 695 type parameter syntax and `type` alias statements. Use them only if the project baseline is truly 3.12+.
- Avoid 3.13/3.14-only syntax, library APIs, or behavior unless runtime is confirmed.
- If compatibility with older Python unexpectedly appears in a user request, stop using 3.12-only features and state the revised baseline.
