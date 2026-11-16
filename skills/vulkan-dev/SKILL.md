---
name: vulkan-dev
description: "Develop, modernize, review, and debug Vulkan 1.3 renderers and GPU-compute programs: instance/device/queue setup, pNext feature chains and extension detection, VkDeviceMemory sub-allocation and staging, VkImageMemoryBarrier2 and layout transitions, timeline/binary semaphores and fences, descriptor sets and descriptor-indexing bindless, VkPipeline + pipeline cache + dynamic rendering, command pools and swapchain, compute dispatch, validation and performance triage. Use for Vk*/vkCmd*/vkCreate* code and Vulkan API decisions even when the user does not say 'Vulkan'."
---

# Vulkan Development (Vulkan 1.3)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

This skill is the concrete **Vulkan 1.3 implementation** layer: the `Vk*` objects, `vkCreate*`/`vkCmd*` calls, capability detection, and Vulkan-specific best practices. The API-agnostic architecture behind these calls (render graph, binding model, synchronization model, frames-in-flight, GPU memory strategy) lives in [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) — this skill links up to it for the "why" instead of restating it.

## Version Standard

- Target **Vulkan 1.3 core** by default; use 1.3 core struct/function names on the modern path.
- Official extensions are allowed, but only after enumeration + enablement (device/instance scope) and, where required, enabling the feature bit.
- Never infer support from headers or API version — query features/limits/formats and enable what you use, see [references/capabilities-and-setup.md](references/capabilities-and-setup.md).
- Do not invent VUIDs, promotion status, mandatory limits, or exact signatures; when spec wording matters, consult the spec, see [references/code-review-and-audit.md](references/code-review-and-audit.md).

## When to Use

- Writing or modernizing Vulkan setup, rendering, or compute (`VkInstance`/`VkDevice`, memory, barriers, descriptors, pipelines, swapchain, dispatch)
- Reviewing or auditing Vulkan code for valid usage, synchronization hazards, or feature/extension misuse
- Diagnosing validation-layer errors, layout/barrier bugs, or Vulkan-specific performance/stutter
- Deciding what to target: core 1.3 vs optional extension, feature tiers, fallback paths

## When NOT to Use

- API-agnostic renderer architecture (render graph, frames-in-flight model, memory strategy) — use [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md)
- A different explicit API (D3D12, Metal, WebGPU) — Vulkan-specific calls do not transfer
- High-level engine runtime or web/driver-managed 3D (WebGL, high-level frameworks)
- GLSL shader-effect authoring (SDF, lighting, post) — use [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md)
- GLSL language, layouts, SPIR-V bindings, compile/link validation — use [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md)
- CPU-side C++ allocator/ownership design (arenas, PMR, smart pointers) — use [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md)
- Android `Surface`/`ANativeWindow` WSI, AHardwareBuffer interop, Android Vulkan Profiles, wide color — use [`../android-vulkan-dev/SKILL.md`](../android-vulkan-dev/SKILL.md)

## Operating Principles

- Separate three concerns explicitly: **core 1.3 baseline**, **optional extensions** (enumerated + enabled), and **profiled performance** (measured, hardware-specific).
- Correctness before performance: valid usage, lifetime, and synchronization first; a conservative barrier is safe-but-slow, a missing one corrupts.
- The app owns memory, layouts, synchronization, descriptors, pipelines, and command reuse — an answer that only names a function is usually incomplete.
- Prefer synchronization2, dynamic rendering, timeline semaphores, and descriptor indexing as the modern defaults; keep classic paths for compatibility tiers.

## Reference routing

Writing/modernizing: start at [references/capabilities-and-setup.md](references/capabilities-and-setup.md) for the target + gates, then the subsystem row below; apply Modern 1.3 Defaults. Reviewing/auditing: run [scripts/vulkan_antipattern_scan.py](scripts/vulkan_antipattern_scan.py) first, then the checklist row below, correctness before performance.

| Load when | Read |
|------|------|
| Choosing a target, probing features/extensions, ranking devices, or designing fallbacks | [references/capabilities-and-setup.md](references/capabilities-and-setup.md) |
| Creating the instance/device or selecting queue families | [references/device-and-queues.md](references/device-and-queues.md) |
| Allocating/sub-allocating memory, staging uploads, or handling alignment | [references/device-memory.md](references/device-memory.md) |
| Creating images/buffers/views or placing layout transitions and barriers | [references/resources-and-barriers.md](references/resources-and-barriers.md) |
| Wiring semaphores, fences, submit-time waits, or CPU/GPU handoff | [references/synchronization.md](references/synchronization.md) |
| Designing descriptor layouts, pools, bindless tables, or push constants | [references/descriptors.md](references/descriptors.md) |
| Building pipelines, caching them, or using dynamic rendering/state | [references/pipelines.md](references/pipelines.md) |
| Recording command buffers, threading recording, or driving the swapchain | [references/commands-and-swapchain.md](references/commands-and-swapchain.md) |
| Writing compute pipelines, sizing dispatch/workgroups, or considering async compute | [references/compute.md](references/compute.md) |
| Triaging performance, targeting mobile tilers, or choosing feature tiers | [references/best-practices.md](references/best-practices.md) |
| Reviewing Vulkan code, auditing valid usage, or selecting validation modes | [references/code-review-and-audit.md](references/code-review-and-audit.md) |
| Review prompts on a source tree (flags patterns; not a validator) | [scripts/vulkan_antipattern_scan.py](scripts/vulkan_antipattern_scan.py) |

## Modern 1.3 Defaults

- synchronization2 (`vkCmdPipelineBarrier2`, `vkQueueSubmit2`, `Vk*MemoryBarrier2`)
- dynamic rendering (`vkCmdBeginRendering`) over `VkRenderPass`/`VkFramebuffer` where it simplifies
- timeline semaphores for GPU-GPU progress and CPU waits; fences to gate frame-slot reuse
- descriptor indexing + `UPDATE_AFTER_BIND` for bindless material/texture tables
- persistent `VkPipelineCache` on disk; pipelines built at load, never on the draw path
- one command pool per (thread x frame slot), reset wholesale on the slot fence

## Anti-patterns

- per-draw descriptor allocation/update; per-resource `vkAllocateMemory`
- frame-loop `vkDeviceWaitIdle`/`vkQueueWaitIdle`; `ALL_COMMANDS`→`ALL_COMMANDS` as a permanent barrier
- `VK_IMAGE_LAYOUT_GENERAL` for convenience; updating/freeing resources still read by in-flight frames
- creating pipelines during gameplay without cache/warmup/fallback
- too many queues or tiny async-compute tasks; ignoring `OUT_OF_DATE`/`SUBOPTIMAL`
- inferring feature/extension support from API version instead of querying

## Gotchas

- `maxMemoryAllocationCount` is small (often ~4096); per-resource `vkAllocateMemory` works in a demo then fails — sub-allocate from large blocks.
- `oldLayout` in a barrier must equal the image's actual current layout (or `UNDEFINED` to discard); a mismatch is undefined behavior.
- Updating a descriptor set (without `UPDATE_AFTER_BIND`) or destroying a resource while an in-flight frame may still read it is a data race — gate on the slot `VkFence`.
- Forgetting to set a declared dynamic state (`vkCmdSetViewport`/`Scissor`) leaves it undefined; first use of an uncompiled pipeline stalls — build at load with a warm cache.
- Ignoring `VK_ERROR_OUT_OF_DATE_KHR`/`VK_SUBOPTIMAL_KHR` from acquire/present leaves a stale swapchain after resize — recreate it.
- A queue-family release barrier without a matching acquire (or vice versa) corrupts the resource; semaphores order queues but do not replace intra-queue barriers.
- Enabling/using a feature (descriptor indexing, timeline semaphores) without enabling its bit at device creation is invalid — query and enable first.

## Companion Skills

| Task | Path |
|------|------|
| API-agnostic renderer architecture (render graph, sync model, memory strategy) | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| General C++20 style, Core Guidelines, build/verification | [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md) |
| C++ CPU allocator principle behind the sub-allocator (arenas, pools, PMR) | [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md) |
| Android surface lifecycle, WSI, AHB interop, AVP, wide color | [`../android-vulkan-dev/SKILL.md`](../android-vulkan-dev/SKILL.md) |
| GLSL source, layouts, GLSL-to-SPIR-V compile validation | [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) |

Relative paths above resolve from `.agents/skills/vulkan-dev/` when installed (or `skills/vulkan-dev/` in bootstrap layout). Read companions from the same `.agents/skills/<name>/` tree when available.

## Tool notes

### Anti-pattern scanner

For code review, run the bundled scanner from the skill root (review prompts only, not a validator):

```bash
python .agents/skills/vulkan-dev/scripts/vulkan_antipattern_scan.py <paths> [--severity info|medium|high]
```

### Per-host notes

After installing or editing the skill, reload the coding agent so the skill is rediscovered.
