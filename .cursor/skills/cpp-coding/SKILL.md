---
name: cpp-coding
description: "Write, review, and refactor modern C++20 code following C++ Core Guidelines \u2014 RAII, concepts, value semantics, and safe concurrency. Use when implementing C++ classes or functions, reviewing C++ diffs, choosing between language alternatives (enum vs enum class, raw pointer vs smart pointer), refactoring C++ modules, or enforcing idiomatic C++20 style \u2014 even if the user says \"C++ help\" or \"fix this C++ code\" without naming a standard."
---

# cpp-coding (Cursor)

Read the shared skill first — it is the source of truth for C++20 workflow, reference
routing, and completion checklists:

`../../../.shared/skills/cpp-coding/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/cpp-coding/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for C++
content and workflow.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under
  `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the
  agent rediscovers them

## Install or refresh cpp-coding

From repo root:

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
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
