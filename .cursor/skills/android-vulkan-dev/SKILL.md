---
name: android-vulkan-dev
description: "vulkan-through-ndk gpu rendering guidance for android 16/api 36+ apps. use when designing, implementing, reviewing, or troubleshooting android vulkan renderers, native surfaces, swapchains, devices, queues, command buffers, render passes, dynamic rendering, shaders, spir-v, descriptor sets, synchronization, validation layers, android vulkan profiles, wide color, camera/media interop, painting engines, image filters, and gpu performance. use android-ndk-dev for cmake/jni/native-library integration and android-dev for kotlin app architecture, compose ui, permissions, and sdk camera/media flows."
---

# android-vulkan-dev wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/android-vulkan-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/android-vulkan-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/android-vulkan-dev/`.
- Keep only Cursor-specific information in this wrapper.
