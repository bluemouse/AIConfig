---
name: gpu-rendering-guide
description: "Design and review explicit-API renderer architecture (Vulkan/D3D12/Metal/WebGPU): render graphs, RDG, shader systems, binding model, bindless, sync, frames-in-flight, GPU memory, scene submission, GPU-driven rendering, indirect draw, Nanite-style culling, HDR output. Use when architecting or debugging a custom renderer, render passes, barriers, pipeline stalls, async compute, or draw submission \u2014 even without naming an API. Patterns align with Unreal RDG, Unity RenderGraph/SRP, and Frostbite FrameGraph at the conceptual level."
---

# gpu-rendering-guide (Cursor)

Read the shared skill first — it is the source of truth for renderer architecture, reference
routing, and engine pattern mappings:

`../../../.shared/skills/gpu-rendering-guide/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/gpu-rendering-guide/`. Resolve paths to
`references/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for
renderer content and workflow.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under
  `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the
  agent rediscovers them

## Install or refresh gpu-rendering-guide

From repo root:

```bash
python .shared/skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name gpu-rendering-guide --source skills/gpu-rendering-guide --overwrite
```

If bootstrap source exists at `skills/gpu-rendering-guide/`, use that path for `--source` only.

## Companion skills

| Task | Path |
|------|------|
| C++ CPU allocator (arenas, pools, ownership, PMR) | `.shared/skills/cpp-memory-guide/SKILL.md` |
| Concrete Vulkan API | `.shared/skills/vulkan-dev/SKILL.md` |
| GLSL language and SPIR-V layouts | `.shared/skills/glsl-coding/SKILL.md` when installed |
| GLSL shader effects | `.shared/skills/shader-guide/SKILL.md` when installed |
| Immediate-mode UI draw stream | `.shared/skills/imgui-guide/SKILL.md` when installed |

Install companions with `install_portable_skill.py` when bootstrap sources exist under `skills/<name>/`.

## Wrapper policy

- Edit cross-tool renderer behavior in `../../../.shared/skills/gpu-rendering-guide/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
