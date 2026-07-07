---
name: usd-hydra2-dev
description: "Source-grounded OpenUSD Hydra 2.0 development guidance for scene indices, data sources, schema authoring, filtering scene indices, dependency forwarding, retained scene indices, Hydra renderer and scene-index plugin integration, Hdx task-controller use, USD imaging pipelines, materials, transparency, instancing, dirty propagation, code review, API migration from Hydra 1.0, and compile-ready C++ snippets. Use when implementing, reviewing, debugging, designing, or documenting rendering functionality with OpenUSD Hydra 2.0, Hd, Hdx, USD imaging, plugInfo.json plugins, or Hydra renderer pipelines \u2014 even if the user does not say 'Hydra 2.0'. For API-agnostic renderer architecture (render graph, frames-in-flight, binding model), use gpu-rendering-guide. For Vulkan implementation details, use vulkan-dev."
---

# usd-hydra2-dev wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/usd-hydra2-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/usd-hydra2-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/usd-hydra2-dev/`.
- Keep only GitHub Copilot-specific information in this wrapper.
