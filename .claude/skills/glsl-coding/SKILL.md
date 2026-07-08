---
name: glsl-coding
description: "Teach, write, review, debug, and optimize modern GLSL for OpenGL 4.6 core and Vulkan 1.3 SPIR-V: shader stages, layouts, descriptors, push constants, specialization constants, interface matching, precision, and compile/link validation. Use for GLSL syntax, stage I/O, resource bindings, GLSL-to-SPIR-V layout questions, maintainability refactors, and diagnosing shader mistakes \u2014 even when the user does not say 'GLSL' or 'SPIR-V'."
---

# glsl-coding wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/glsl-coding/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/glsl-coding` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/glsl-coding/`.
- Keep only Claude Code-specific information in this wrapper.
