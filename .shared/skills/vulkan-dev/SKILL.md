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
- GLSL shader-effect authoring (SDF, lighting, post) — out of scope here
- CPU-side C++ allocator/ownership design (arenas, PMR, smart pointers) — use [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md)

## Operating Principles

- Separate three concerns explicitly: **core 1.3 baseline**, **optional extensions** (enumerated + enabled), and **profiled performance** (measured, hardware-specific).
- Correctness before performance: valid usage, lifetime, and synchronization first; a conservative barrier is safe-but-slow, a missing one corrupts.
- The app owns memory, layouts, synchronization, descriptors, pipelines, and command reuse — an answer that only names a function is usually incomplete.
- Prefer synchronization2, dynamic rendering, timeline semaphores, and descriptor indexing as the modern defaults; keep classic paths for compatibility tiers.

## Setup and Subsystem Map

- **Capability + setup** - Version policy, `VkPhysicalDeviceFeatures2` query/enable chains, extension enumeration, device ranking, format-feature checks, WSI, dynamic-rendering default, see [references/capabilities-and-setup.md](references/capabilities-and-setup.md)
- **Device + queues** - `VkInstance`/`VkPhysicalDevice`/`VkDevice`, queue-family selection, present support, see [references/device-and-queues.md](references/device-and-queues.md)
- **Memory** - `VkDeviceMemory` types/heaps, few large blocks + sub-allocation, staging, alignment, see [references/device-memory.md](references/device-memory.md)
- **Resources + barriers** - `VkImage`/`VkBuffer`, views, `VkImageMemoryBarrier2`, layout transitions, queue transfer, see [references/resources-and-barriers.md](references/resources-and-barriers.md)
- **Synchronization** - binary/timeline `VkSemaphore`, `VkFence`, `vkQueueSubmit2`, stage/access scoping, see [references/synchronization.md](references/synchronization.md)
- **Descriptors** - set layouts by frequency, pools, descriptor-indexing bindless, push constants, see [references/descriptors.md](references/descriptors.md)
- **Pipelines** - `VkPipeline`, `VkPipelineCache` persistence, dynamic rendering, dynamic state, see [references/pipelines.md](references/pipelines.md)
- **Commands + swapchain** - command pools per thread/frame, primary/secondary, acquire/present, frames-in-flight, see [references/commands-and-swapchain.md](references/commands-and-swapchain.md)
- **Compute** - compute pipelines, dispatch/workgroup sizing, subgroups, async-compute caution, see [references/compute.md](references/compute.md)

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

## Workflow Decision Tree

- **Writing / modernizing** → start at [references/capabilities-and-setup.md](references/capabilities-and-setup.md) for the target + gates, then the relevant subsystem reference; apply Modern 1.3 Defaults.
- **Reviewing / auditing** → run [scripts/vulkan_antipattern_scan.py](scripts/vulkan_antipattern_scan.py) for review prompts, then work the checklist in [references/code-review-and-audit.md](references/code-review-and-audit.md), correctness before performance.
- **Spec / validation question** → follow the authority order and audit process in [references/code-review-and-audit.md](references/code-review-and-audit.md); do not guess VUIDs/limits.
- **Compute work** → [references/compute.md](references/compute.md) for dispatch/workgroups/subgroups; link up to [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) for GPU-driven architecture.
- **Performance / stutter** → the triage workflow in [references/best-practices.md](references/best-practices.md) (classify CPU/GPU/bandwidth/stutter bound first).

## Reference Routing

| Task | Read |
|------|------|
| Version policy, feature/extension detection, device ranking, WSI, dynamic-rendering default | [references/capabilities-and-setup.md](references/capabilities-and-setup.md) |
| Instance/device/queue creation, queue-family + present selection | [references/device-and-queues.md](references/device-and-queues.md) |
| Memory types/heaps, sub-allocation, staging upload, alignment | [references/device-memory.md](references/device-memory.md) |
| Images/buffers/views, `VkImageMemoryBarrier2`, layout transitions, queue transfer | [references/resources-and-barriers.md](references/resources-and-barriers.md) |
| Binary/timeline semaphores, fences, `vkQueueSubmit2`, stage/access scoping | [references/synchronization.md](references/synchronization.md) |
| Descriptor set layouts by frequency, pools, bindless, push constants | [references/descriptors.md](references/descriptors.md) |
| `VkPipeline`, pipeline cache, dynamic rendering, dynamic state | [references/pipelines.md](references/pipelines.md) |
| Command pools, primary/secondary, swapchain acquire/present, frames-in-flight | [references/commands-and-swapchain.md](references/commands-and-swapchain.md) |
| Compute pipelines, dispatch/workgroup sizing, subgroups, async compute | [references/compute.md](references/compute.md) |
| Best-practice hierarchy, mobile/tiler bandwidth, feature tiers, perf triage | [references/best-practices.md](references/best-practices.md) |
| Code-review checklist, spec-audit process, validation-mode selection | [references/code-review-and-audit.md](references/code-review-and-audit.md) |

## Gotchas

- `maxMemoryAllocationCount` is small (often ~4096); per-resource `vkAllocateMemory` works in a demo then fails — sub-allocate from large blocks.
- `oldLayout` in a barrier must equal the image's actual current layout (or `UNDEFINED` to discard); a mismatch is undefined behavior.
- Updating a descriptor set (without `UPDATE_AFTER_BIND`) or destroying a resource while an in-flight frame may still read it is a data race — gate on the slot `VkFence`.
- Forgetting to set a declared dynamic state (`vkCmdSetViewport`/`Scissor`) leaves it undefined; first use of an uncompiled pipeline stalls — build at load with a warm cache.
- Ignoring `VK_ERROR_OUT_OF_DATE_KHR`/`VK_SUBOPTIMAL_KHR` from acquire/present leaves a stale swapchain after resize — recreate it.
- A queue-family release barrier without a matching acquire (or vice versa) corrupts the resource; semaphores order queues but do not replace intra-queue barriers.
- Enabling/using a feature (descriptor indexing, timeline semaphores) without enabling its bit at device creation is invalid — query and enable first.

## Progressive Disclosure

- Read [references/capabilities-and-setup.md](references/capabilities-and-setup.md) — Load when choosing a target, probing features/extensions, ranking devices, or designing fallbacks
- Read [references/device-and-queues.md](references/device-and-queues.md) — Load when creating the instance/device or selecting queue families
- Read [references/device-memory.md](references/device-memory.md) — Load when allocating/sub-allocating memory, staging uploads, or handling alignment
- Read [references/resources-and-barriers.md](references/resources-and-barriers.md) — Load when creating images/buffers/views or placing layout transitions and barriers
- Read [references/synchronization.md](references/synchronization.md) — Load when wiring semaphores, fences, submit-time waits, or CPU/GPU handoff
- Read [references/descriptors.md](references/descriptors.md) — Load when designing descriptor layouts, pools, bindless tables, or push constants
- Read [references/pipelines.md](references/pipelines.md) — Load when building pipelines, caching them, or using dynamic rendering/state
- Read [references/commands-and-swapchain.md](references/commands-and-swapchain.md) — Load when recording command buffers, threading recording, or driving the swapchain
- Read [references/compute.md](references/compute.md) — Load when writing compute pipelines, sizing dispatch/workgroups, or considering async compute
- Read [references/best-practices.md](references/best-practices.md) — Load when triaging performance, targeting mobile tilers, or choosing feature tiers
- Read [references/code-review-and-audit.md](references/code-review-and-audit.md) — Load when reviewing Vulkan code, auditing valid usage, or selecting validation modes
- Run [scripts/vulkan_antipattern_scan.py](scripts/vulkan_antipattern_scan.py) — Review prompts on a source tree (flags patterns; not a validator)

## Companion Skills

| Task | Path |
|------|------|
| API-agnostic renderer architecture (render graph, sync model, memory strategy) | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| General C++20 style, Core Guidelines, build/verification | [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md) |
| C++ CPU allocator principle behind the sub-allocator (arenas, pools, PMR) | [`../cpp-memory-guide/SKILL.md`](../cpp-memory-guide/SKILL.md) |

Relative paths above resolve from `.shared/skills/vulkan-dev/` when installed (or `skills/vulkan-dev/` in bootstrap layout). Wrappers point to the shared copy; read companions from the same `.shared/skills/<name>/` tree when available.
