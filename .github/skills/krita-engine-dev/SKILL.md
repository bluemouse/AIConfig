---
name: krita-engine-dev
description: "Write, review, debug, and implement Krita brush engines, paintops, stroke scheduling, tiled compositing, presets/resources, layer projection, and canvas/GPU display. Use when working on KDE/krita source navigation, adding or modifying a paint engine, designing a new painting application's stroke system, optimizing dab generation and live drawing, or explaining how pixels flow from stylus samples to layers and canvas updates \u2014 even if the user doesn't say Krita. Triggers on KisPaintOp, KisBrushOp, KisStrokesQueue, KisResourcesSnapshot, KisPaintDevice, dab cache, spacing/timing, LOD buddy strokes, KisTransaction, and paintop plugin registration."
---

# krita-engine-dev wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/krita-engine-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/krita-engine-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/krita-engine-dev/`.
- Keep only GitHub Copilot-specific information in this wrapper.
