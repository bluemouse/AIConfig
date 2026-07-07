---
name: mypaint-engine-dev
description: "Write, review, debug, and implement MyPaint and libmypaint brush engines, stroke-to-dab rendering, tiled surfaces, layers, symmetry, smudge/pigment behavior, and GPU surface backends. Use when working on mypaint/mypaint or mypaint/libmypaint source navigation, .myb presets, live drawing, brush-engine parity, resource management, or designing a new painting application inspired by MyPaint \u2014 even if the user doesn't say MyPaint. Triggers on libmypaint, mypaint_brush_stroke_to, BrushInfo, BrushworkModeMixin, MyPaintTiledSurface, .myb, smudge buckets, paint_mode, and dab scheduling."
---

# mypaint-engine-dev wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/mypaint-engine-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/mypaint-engine-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/mypaint-engine-dev/`.
- Keep only Claude Code-specific information in this wrapper.
