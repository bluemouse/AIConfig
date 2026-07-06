---
name: cmake-dev
description: "Write, review, and refactor modern CMake 3.20+ build files for C/C++ projects using target-based builds. Use when editing CMakeLists.txt or *.cmake files; adding or linking targets; configuring PUBLIC/PRIVATE/INTERFACE visibility; integrating dependencies with find_package or FetchContent; wiring CTest; structuring multi-directory projects; applying generator expressions; or writing install/export rules \u2014 even if the user says \"fix my build\" without naming CMake."
---

# cmake-dev wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/cmake-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/cmake-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/cmake-dev/`.
- Keep only Claude Code-specific information in this wrapper.
