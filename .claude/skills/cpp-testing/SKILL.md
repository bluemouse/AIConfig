---
name: cpp-testing
description: "Write, fix, and configure C++20 unit and integration tests with GoogleTest/GoogleMock, CMake/CTest, coverage, and sanitizers. Use when adding or updating C++ tests, fixing failing or flaky tests, setting up test targets, diagnosing gtest failures, or adding regression/coverage/sanitizer test builds \u2014 even if the user says \"add tests\" or \"this test is flaky\" without naming a framework."
---

# cpp-testing (Claude Code)

Read the shared skill first — it is the source of truth for C++ test workflow, reference
routing, and completion checklists:

`../../../.shared/skills/cpp-testing/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/cpp-testing/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh cpp-testing

```bash
python .shared/skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name cpp-testing --source skills/cpp-testing --overwrite
```

If bootstrap source exists at `skills/cpp-testing/`, use that path for `--source` only.

## Companion skill

For production C++ code under test (RAII, ownership, concurrency, Core Guidelines), use
`../../../.shared/skills/cpp-coding/SKILL.md`.

## Wrapper policy

- Edit cross-tool test behavior in `../../../.shared/skills/cpp-testing/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
