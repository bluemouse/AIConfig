---
name: python-coding
description: Write, review, refactor, test, debug, and package modern Python 3.12+ command-line scripts and utilities using project-local toolchain settings. Use when implementing or fixing Python code, designing argparse CLIs, improving scripts, applying type hints, configuring pyproject.toml, ruff, pyright, pytest, or pip/uv workflows, building small utilities, or producing packaging metadata — even if the user says "Python help" or "fix this script" without naming a framework.
---

# Python Coding

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Write and review Python CLI scripts and utilities against project-local Python version,
`pyproject.toml`, dependency policy, formatter, linter, type checker, and test framework
settings. Read bundled references on demand — do not load all reference files unless the
task requires them.

Target Python 3.12 or newer. Treat "python 12+" as Python 3.12+ unless the user explicitly
says otherwise. Prefer portable CLI scripts and utilities over services, notebooks, GUI apps,
or framework-heavy designs.

## When to Use

- Writing, reviewing, or refactoring Python 3.12+ CLI scripts and utilities
- Explaining Python syntax, semantics, or version-boundary behavior
- Designing argparse CLIs, stdin/stdout/stderr contracts, exit codes, and config precedence
- Choosing venv, pip, uv, ruff, pyright, mypy, pytest, or unittest commands
- Fixing Python errors, test failures, type-checker diagnostics, or packaging issues
- Applying typed, testable CLI patterns with pathlib, dataclasses, and standard-library-first design

## When NOT to Use

- Web frameworks and services (Django, FastAPI, Flask, ASGI deployment) — use framework-specific guidance
- Notebooks, Jupyter, data science, or ML pipelines — use domain-specific skills
- Pure planning with no Python implementation ([plan-guide](../plan-guide/SKILL.md))
- Cross-language debugging methodology without Python code changes ([debugging-guide](../debugging-guide/SKILL.md))
- Review-only diffs with no implementation ([code-review-plus](../code-review-plus/SKILL.md))
- GUI apps, game engines, or large multi-service architectures unless the task is still a small CLI utility

## Operating model

Treat this as a production Python CLI engineering skill. Optimize for correctness first,
then simplicity, then maintainability, then performance. Use the local project's Python
version, `pyproject.toml`, lock files, and tool configuration as the source of truth.

Before editing or generating nontrivial code:

1. Inspect `pyproject.toml`, `requirements*.txt`, lock files, `.python-version`, `tox.ini`,
   `noxfile.py`, CI config, and test layout when available.
2. Identify the target Python version. If unspecified, assume Python 3.12+ for new utilities,
   not the newest language feature on an older runtime.
3. Prefer changes that run under the existing baseline and follow existing naming, module
   layout, logging, and test patterns.
4. After changes, run the smallest meaningful verification first, then broaden: compile,
   format/lint, type check, targeted tests, full tests, realistic CLI invocation.

## Cross-cutting principles

These themes apply to every Python CLI change:

1. **Boundary typing** — validate raw strings, JSON, env vars, and CLI options once at the edge
2. **Project truth** — match Python version, dependency policy, and repo conventions
3. **Explicit IO** — separate stdout data from stderr diagnostics; return exit codes from `main`
4. **Test seams** — keep pure logic callable without subprocess or filesystem side effects
5. **Verify before claiming** — run commands or state what was not verified

## Workflow

### 1. Assess

Before writing or reviewing:

- Restate the concrete outcome: new behavior, bug fix, refactor, performance improvement, or
  explanation.
- Complete the operating-model inspect steps above — confirm Python version, dependency policy,
  formatter, linter, type checker, and test framework.
- Define the CLI contract when applicable: arguments, stdin/stdout/stderr, exit codes, mutation
  flags, and error policy.
- Read every matching row in [Reference routing](#reference-routing) before editing.

### 2. Implement

- Apply [language-spec.md](references/language-spec.md) for syntax, semantics, and version gates.
- Apply [cli-patterns.md](references/cli-patterns.md) for argparse layout, IO, subprocess, and
  configuration.
- Apply [best-practices.md](references/best-practices.md) for design, error handling, security,
  and review standards.
- Apply [testing-debugging.md](references/testing-debugging.md) for test strategy, debugging,
  and failure triage.
- Apply [toolchain.md](references/toolchain.md) for project files, CLI commands, packaging, and
  quality gates.
- Locate the owning module and tests. If no tests exist, identify a test seam before changing
  production code.
- Make the smallest idiomatic change. Avoid architectural rewrites unless the user asks or
  the current structure blocks the fix.

### 3. Verify

Run the quality bar in
[toolchain.md](references/toolchain.md#ci-quality-gate-template) and the completion report in
[testing-debugging.md](references/testing-debugging.md#completion-gate):

- Syntax/import validation first (`python -m compileall` or `py_compile`).
- Targeted tests first, then broader scope.
- Format/lint/type-check verification when repo policy requires it.
- At least one realistic CLI invocation (`--help` or representative args).
- Report changed files, commands run, and remaining risks. Never claim code was tested unless
  a tool actually ran.

## Language rules to enforce

Default to these rules unless project conventions contradict them:

- Use `main(argv: Sequence[str] | None = None) -> int` and
  `if __name__ == "__main__": raise SystemExit(main())`.
- Keep argument parsing outside core logic so tests can call pure functions directly.
- Return process exit codes from `main`; do not call `sys.exit()` deep inside helpers.
- Use `pathlib.Path`, not stringly typed filesystem paths.
- Use `logging` for diagnostics and `print()` only for intended user output.
- Use `argparse` for standard-library CLIs. Use `click` or `typer` only when already present
  or explicitly requested.
- Prefer the standard library before adding dependencies.
- Use `pytest` for new projects when third-party dev dependencies are acceptable; otherwise
  use `unittest`.
- Avoid import-time side effects beyond constants and cheap definitions.
- Never hide destructive behavior — require explicit flags such as `--write`, `--delete`, or
  `--in-place` for mutations.

## Tool usage expectations

When a terminal or code execution tool is available, use it for real projects:

- Discover: `python --version`, `python -m pip list`, `python -m pytest --collect-only`.
- Environment: `python -m venv .venv`, activate, `python -m pip install -e ".[dev]"` when
  applicable.
- Quality: `python -m compileall`, `python -m ruff format --check .`, `python -m ruff check .`,
  `python -m pyright` or `python -m mypy`.
- Test: `python -m pytest -q`, targeted `-k`, or `python -m unittest discover -s tests`.
- Run: `python script.py --help` or `python -m package.module`.

If command planning would help, run or inspect
`<SKILL_ROOT>/scripts/python_cli_plan.py` to generate a compact CLI implementation checklist.

## Reference routing

| Task | Read |
|------|------|
| Syntax, semantics, typing conventions, version gates, async boundaries | [language-spec.md](references/language-spec.md) |
| argparse layout, stdin/stdout/stderr, subprocess, config, destructive safeguards | [cli-patterns.md](references/cli-patterns.md) |
| venv, pip, uv, pyproject.toml, ruff, pyright/mypy, pytest/unittest, packaging, CI gates | [toolchain.md](references/toolchain.md) |
| Test strategy, debugging, profiling, flaky tests, completion gate | [testing-debugging.md](references/testing-debugging.md) |
| Design principles, error handling, security, performance, review red flags | [best-practices.md](references/best-practices.md) |
| Style and review checklist before delivery | [best-practices.md](references/best-practices.md#style-and-review-checklist) |
| CI/local quality gate command template | [toolchain.md](references/toolchain.md#ci-quality-gate-template) |

When a change spans multiple areas, read **every matching row** — e.g. CLI bug fixes need both
[cli-patterns.md](references/cli-patterns.md) and
[testing-debugging.md](references/testing-debugging.md); packaging failures need
[toolchain.md](references/toolchain.md) and possibly [cli-patterns.md](references/cli-patterns.md).

## Quick completion checklist

Complete **both** before marking Python CLI work done:

1. **Code quality** — review checklist in
   [best-practices.md](references/best-practices.md#style-and-review-checklist)
   (typing, IO boundaries, security, tests, destructive safeguards)
2. **Build and verification** — follow
   [toolchain.md](references/toolchain.md#ci-quality-gate-template):
   - `python -m compileall -q src tests` (or `python -m py_compile` for single scripts)
   - `python -m ruff format --check .` and `python -m ruff check .` when ruff is configured
   - `python -m pyright` or `python -m mypy` for non-trivial typed code
   - `python -m pytest -q` or `python -m unittest discover -s tests`
   - at least one realistic CLI invocation

The Verify workflow step (above) is satisfied only when checklist part 2 commands ran or
unverified areas are explicitly stated.

## Output standards

For code answers:

- Provide complete, runnable snippets with required imports and Python version assumptions when
  relevant.
- Explain why the chosen Python feature is appropriate when there are close alternatives.
- Keep examples idiomatic but not over-clever. Prefer readable control flow over dense
  comprehensions when debugging, side effects, or error handling matter.
- Include tests or test guidance for behavior changes.

For reviews:

- Prioritize correctness, input validation, IO boundaries, subprocess safety, resource lifetime,
  security, performance, and test gaps.
- Distinguish confirmed defects from style preferences.
- Provide concrete fixes and the command that would catch the issue next time.

## Resources

- [language-spec.md](references/language-spec.md) — Python 3.12+ syntax, semantics, and version gates
- [cli-patterns.md](references/cli-patterns.md) — CLI layout, argparse, IO, and subprocess patterns
- [toolchain.md](references/toolchain.md) — venv, pip/uv, pyproject.toml, ruff, typing, packaging
- [testing-debugging.md](references/testing-debugging.md) — Tests, debugging, and completion gate
- [best-practices.md](references/best-practices.md) — Design, safety, and review standards
- [SOURCES.md](SOURCES.md) — Provenance and external references (read for attribution only)

External reference: [Python documentation](https://docs.python.org/3/)
