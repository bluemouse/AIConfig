---
name: shader-guide
description: "Author, review, and debug creative real-time GLSL visual effects: ray marching, 2D/3D SDFs, CSG, domain warping, FBM terrain, voronoi patterns, procedural noise, soft shadows, AO, Monte Carlo path tracing, volumetrics, Gerstner waves, fluids, ping-pong simulation, Turing/reaction-diffusion patterns, particles, bloom/ACES post-processing, and multi-pass buffers. Use for generative art, implicit-surface scenes, domain-warped organic blobs, or standalone fragment-shader demos \u2014 even when the user does not say SDF, ray marching, or ping-pong."
---

# shader-guide wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/shader-guide/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/shader-guide` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/shader-guide/`.
- Keep only GitHub Copilot-specific information in this wrapper.
