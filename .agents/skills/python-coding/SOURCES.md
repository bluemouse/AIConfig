# Sources

## Python Language Reference

- **URL:** https://docs.python.org/3/reference/index.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → language rules, version boundaries
  - `references/language-spec.md` → lexical structure, statements, functions, classes, imports, typing
- **Aspects extracted:**
  - Exact syntax and semantics authority → `references/language-spec.md`
  - Soft keywords, pattern matching, async boundaries → `references/language-spec.md`

## Python Tutorial

- **URL:** https://docs.python.org/3/tutorial/index.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/language-spec.md` → idiomatic usage reminders
  - `references/best-practices.md` → readability and structure guidance
- **Aspects extracted:**
  - Standard-library-first idioms and beginner-to-intermediate patterns → bundled references

## argparse standard library

- **URL:** https://docs.python.org/3/library/argparse.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/cli-patterns.md` → argparse guidance, subparsers, error handling
- **Aspects extracted:**
  - `ArgumentParser`, `store_true`, `choices`, subparsers, `parser.error()` → `references/cli-patterns.md`

## unittest standard library

- **URL:** https://docs.python.org/3/library/unittest.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/testing-debugging.md` → unittest patterns
  - `references/toolchain.md` → stdlib-only test commands
- **Aspects extracted:**
  - `python -m unittest discover -s tests` workflow → `references/testing-debugging.md`, `references/toolchain.md`

## Python Packaging User Guide

- **URL:** https://packaging.python.org/en/latest/tutorials/packaging-projects/
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/toolchain.md` → pyproject.toml, console scripts, build/install commands
- **Aspects extracted:**
  - `[project.scripts]`, `python -m build`, editable installs, distribution basics → `references/toolchain.md`

## python-pro skill (synthesis metadata)

- **URL:** https://github.com/sickn33/antigravity-awesome-skills/tree/main/plugins/antigravity-awesome-skills-claude/skills/python-pro
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Modern tooling emphasis: Python 3.12+, Ruff, uv, pytest, type checking, profiling
- **Aspects extracted:**
  - Toolchain and quality-gate expectations → `references/toolchain.md`, `references/testing-debugging.md`

## python-expert skill (synthesis metadata)

- **URL:** https://github.com/Shubhamsaboo/awesome-llm-apps/blob/main/awesome_agent_skills/python-expert
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Senior-review behavior: clean code, type hints, debugging, optimization, PEP 8 consistency
- **Aspects extracted:**
  - Review and typing discipline → `references/best-practices.md`, `SKILL.md`
- **Access limitation:** Referenced `AGENTS.md` was not fetched; only accessible `SKILL.md` content was used.

## python-design skill (synthesis metadata)

- **URL:** https://github.com/mindfold-ai/Trellis/tree/main/.agents/skills/python-design
- **Last reviewed:** 2026-07-06
- **Used for:**
  - CLI-oriented complexity management: deep modules, type-first development, postcondition APIs
- **Aspects extracted:**
  - Design principles and review red flags → `references/best-practices.md`

## DEV Community best-practices article (synthesis metadata)

- **URL:** https://dev.to/devasservice/python-best-practices-writing-clean-efficient-and-maintainable-code-34bj
- **Last reviewed:** 2026-07-06
- **Used for:**
  - PEP 8 reminders, comprehensions/generators, DRY, virtual environments, docstrings, exception handling
- **Aspects extracted:**
  - Maintainability and review reminders → `references/best-practices.md` only where aligned with official docs

## Integration decisions

- Scope is intentionally narrowed to Python 3.12+ CLI scripts and utilities, not web frameworks,
  notebooks, machine learning, or service deployment.
- The official Language Reference is treated as authoritative for exact syntax and semantics; the
  tutorial informs idiomatic usage.
- `references/source-notes.md` from the template was folded into this file and removed from the
  installed reference set.
