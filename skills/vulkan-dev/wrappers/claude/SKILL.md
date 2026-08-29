---
name: vulkan-dev
description: "Develop, modernize, review, and debug Vulkan 1.3 renderers and GPU-compute programs: instance/device/queue setup, pNext feature chains and extension detection, VkDeviceMemory sub-allocation and staging, VkImageMemoryBarrier2 and layout transitions, timeline/binary semaphores and fences, descriptor sets and descriptor-indexing bindless, VkPipeline + pipeline cache + dynamic rendering, command pools and swapchain, compute dispatch, validation and performance triage. Use for Vk*/vkCmd*/vkCreate* code and Vulkan API decisions even when the user does not say 'Vulkan'."
---

# vulkan-dev (Claude Code)

Read the shared skill first — it is the source of truth for Vulkan 1.3 workflow, reference
routing, and review checklists:

`../../../.ai/skills/vulkan-dev/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.ai/skills/vulkan-dev/`. Resolve paths to
`references/` and `scripts/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.ai/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh vulkan-dev

```bash
python .ai/skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name vulkan-dev --source skills/vulkan-dev --overwrite
```

If bootstrap source exists at `skills/vulkan-dev/`, use that path for `--source` only.

## Anti-pattern scanner

For code review, run the bundled scanner from the shared skill root (review prompts only,
not a validator):

```bash
python .ai/skills/vulkan-dev/scripts/vulkan_antipattern_scan.py <paths> [--severity info|medium|high]
```

## Companion Skills

| Task | Path |
|------|------|
| API-agnostic renderer architecture | `.ai/skills/gpu-rendering-guide/SKILL.md` |
| General C++20 style, Core Guidelines | `.ai/skills/cpp-coding/SKILL.md` |
| C++ CPU allocator (arenas, pools, PMR) | `.ai/skills/cpp-memory-guide/SKILL.md` |

Install companions with `install_portable_skill.py` when bootstrap sources exist under `skills/<name>/`.

## Wrapper policy

- Edit cross-tool Vulkan behavior in `../../../.ai/skills/vulkan-dev/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
