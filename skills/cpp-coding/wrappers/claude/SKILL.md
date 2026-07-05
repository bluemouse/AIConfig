---
name: cpp-coding
description: Write, review, and refactor modern C++20 code following C++ Core Guidelines — RAII, concepts, value semantics, and safe concurrency. Use when implementing C++ classes or functions, reviewing C++ diffs, choosing between language alternatives (enum vs enum class, raw pointer vs smart pointer), refactoring C++ modules, or enforcing idiomatic C++20 style — even if the user says "C++ help" or "fix this C++ code" without naming a standard.
---

# cpp-coding (Claude Code)

Read the shared skill first — it is the source of truth for C++20 workflow, reference
routing, and completion checklists:

`../../../.shared/skills/cpp-coding/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/cpp-coding/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh cpp-coding

```bash
python .shared/skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name cpp-coding --source skills/cpp-coding --overwrite
```

If bootstrap source exists at `skills/cpp-coding/`, use that path for `--source` only.

## Companion skill

For C++ test work (GoogleTest, CMake/CTest, coverage, sanitizers), use
`../../../.shared/skills/cpp-testing/SKILL.md` instead of the brief testing notes in
`references/code-quality.md`.

## Wrapper policy

- Edit cross-tool C++ behavior in `../../../.shared/skills/cpp-coding/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
