# Sources

## Vulkan Specification and reference pages

- **URLs:**
  - Vulkan specification (1.3) — https://registry.khronos.org/vulkan/specs/1.3/html/
  - Vulkan Roadmap milestones — https://docs.vulkan.org/spec/latest/appendices/roadmap.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Version Standard, all subsystem sections
  - Authoritative semantics for every `Vk*` type and `vk*` command; valid-usage, lifetime, feature/extension requirements; roadmap-profile claims
- **Aspects extracted:**
  - Version policy, `VkPhysicalDeviceVulkan1{1,2,3}Features` query/enable chains, extension scope/promotion → `references/capabilities-and-setup.md`
  - Instance/physical-device/`VkDevice` creation, queue families, present support → `references/device-and-queues.md`
  - `VkPhysicalDeviceMemoryProperties`, memory types/heaps, `vkAllocateMemory`, `VkMemoryRequirements`, `bufferImageGranularity` → `references/device-memory.md`
  - `VkImage`/`VkBuffer`, layouts, `VkImageMemoryBarrier2`/`VkBufferMemoryBarrier2`, `vkCmdPipelineBarrier2`, queue-family transfer → `references/resources-and-barriers.md`
  - `VkSemaphore` (binary + timeline), `VkFence`, `vkQueueSubmit2`, stage/access masks → `references/synchronization.md`
  - `VkDescriptorSetLayout`/`Pool`/`Set`, descriptor indexing / `UPDATE_AFTER_BIND`, push constants → `references/descriptors.md`
  - `VkPipeline`, `VkPipelineCache`, dynamic rendering, dynamic state → `references/pipelines.md`
  - `VkCommandPool`/`VkCommandBuffer`, `VkSwapchainKHR`, acquire/present → `references/commands-and-swapchain.md`
  - Compute pipelines, workgroup/subgroup limits, dispatch → `references/compute.md`
  - Valid-usage/VUID authority order and audit process → `references/code-review-and-audit.md`

## Khronos Vulkan-Guide and Vulkan-Samples

- **URLs:**
  - Khronos Vulkan-Guide — https://docs.vulkan.org/guide/latest/
  - Vulkan Guide synchronization — https://docs.vulkan.org/guide/latest/synchronization.html
  - Vulkan Guide memory allocation — https://docs.vulkan.org/guide/latest/memory_allocation.html
  - Khronos Vulkan-Samples — https://github.com/KhronosGroup/Vulkan-Samples
  - Dynamic rendering sample — https://github.com/KhronosGroup/Vulkan-Samples/blob/main/samples/extensions/dynamic_rendering/README.adoc
  - Descriptor indexing sample — https://docs.vulkan.org/samples/latest/samples/extensions/descriptor_indexing/README.html
  - Descriptor buffer sample — https://github.com/KhronosGroup/Vulkan-Samples/blob/main/samples/extensions/descriptor_buffer_basic/README.adoc
  - Tile-based rendering best practices — https://github.khronos.org/Vulkan-Site/guide/latest/tile_based_rendering_best_practices.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Modern 1.3 Defaults, Setup and Subsystem Map
  - Recommended modern practice (synchronization2, dynamic rendering, timeline semaphores, descriptor indexing) and tiler bandwidth advice
- **Aspects extracted:**
  - Two-phase enumeration, feature detection, device ranking, WSI policy, format-feature checks → `references/capabilities-and-setup.md`
  - Dynamic rendering vs render passes, pipeline cache persistence → `references/pipelines.md`
  - Bindless via descriptor indexing, set frequency, push constants → `references/descriptors.md`
  - Suballocation, discrete-vs-UMA transfer, staging, lazily-allocated memory → `references/device-memory.md`
  - Tiler load/store, transient attachments, bandwidth advice → `references/best-practices.md`

## Synchronization examples

- **URL:** https://github.com/KhronosGroup/Vulkan-Docs/wiki/Synchronization-Examples
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → subsystem sections (resources & sync)
  - Concrete stage/access-mask pairings for common hazards (write→read, transfer→sample, present)
- **Aspects extracted:**
  - `srcStageMask`/`srcAccessMask` → `dstStageMask`/`dstAccessMask` pairings and layout transitions → `references/resources-and-barriers.md`, `references/synchronization.md`, `references/compute.md`

## Khronos Vulkan performance samples

- **URLs:**
  - Command buffer usage / multithreaded recording — https://github.khronos.org/Vulkan-Site/samples/latest/samples/performance/command_buffer_usage/README.html
  - Descriptor and buffer management — https://github.khronos.org/Vulkan-Site/samples/latest/samples/performance/descriptor_management/README.html
  - Pipeline barriers — https://github.khronos.org/Vulkan-Site/samples/latest/samples/performance/pipeline_barriers/README.html
  - Wait idle — https://docs.vulkan.org/samples/latest/samples/performance/wait_idle/README.html
  - Pipeline cache — https://github.com/KhronosGroup/Vulkan-Samples/blob/main/samples/performance/pipeline_cache/README.adoc
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Anti-patterns, Performance triage
- **Aspects extracted:**
  - Command-pool reset, secondary-buffer overhead, one-time submit → `references/commands-and-swapchain.md`, `references/best-practices.md`
  - Descriptor caching, dynamic offsets, per-draw update overhead → `references/descriptors.md`, `references/best-practices.md`
  - Relaxed vs conservative barriers, pipeline bubbles → `references/resources-and-barriers.md`, `references/best-practices.md`
  - Why fences/timeline values replace frame-loop `WaitIdle` → `references/synchronization.md`, `references/best-practices.md`
  - Pipeline warmup/caching → `references/pipelines.md`

## Memory allocator documentation

- **URLs:**
  - Vulkan Memory Allocator documentation — https://gpuopen.com/learn/vulkan-memory-allocator/
  - VMA usage patterns — https://gpuopen-librariesandsdks.github.io/VulkanMemoryAllocator/html/usage_patterns.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Setup (device memory)
  - Sub-allocation from large blocks, memory-type selection, staging, persistent mapping, defragmentation
- **Aspects extracted:**
  - Few large allocations + sub-allocation, allocation-count cap, alignment, staging upload, budget → `references/device-memory.md`, `references/best-practices.md`

## Vendor performance guidance

- **URLs:**
  - NVIDIA Vulkan dos and don'ts — https://developer.nvidia.com/blog/vulkan-dos-donts/
  - NVIDIA advanced API performance: synchronization — https://developer.nvidia.com/blog/advanced-api-performance-synchronization/
  - AMD GPUOpen RDNA performance guide — https://gpuopen.com/learn/rdna-performance-guide/
  - Samsung Vulkan usage recommendations — https://developer.samsung.com/galaxy-gamedev/resources/articles/usage.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Anti-patterns, Performance triage; mobile/tiler notes
- **Aspects extracted:**
  - CPU/GPU overlap, threading, command-buffer/queue heuristics, semaphore/fence minimalism, async-queue overlap → `references/best-practices.md`
  - Android/mobile tile-based load/store/transient attachment recommendations → `references/best-practices.md`

## Validation and tooling

- **URLs:**
  - LunarG validation layer documentation — https://vulkan.lunarg.com/doc/view/latest/windows/khronos_validation_layer.html
  - LunarG GPU-assisted validation — https://vulkan.lunarg.com/doc/view/latest/windows/gpu_validation.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Workflow Decision Tree (review/validation)
- **Aspects extracted:**
  - Core, synchronization, GPU-assisted, and best-practices validation modes; validation-feature configuration → `references/best-practices.md`, `references/code-review-and-audit.md`

## Game-engine development blog (archive)

- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → subsystem sections (descriptors, commands, pipelines, memory)
  - Shipped Vulkan practice for descriptor management, command-buffer lifecycle, pipeline caching, and device-memory allocation
- **Aspects extracted:**
  - One global `VkDescriptorSet` with a large array per resource class, index embedded in the handle, fence-deferred slot release, device-limit clamping, fallback "null" resources → `references/descriptors.md`
  - Shared sets as read-only blueprints, per-job `VkDescriptorPool` + lazy `VkCopyDescriptorSet`, whole-pool recycling → `references/descriptors.md`
  - Pool per worker thread, fence-gated deferred deletion, recycling reset pools into a free pool-of-pools, primary/secondary split → `references/commands-and-swapchain.md`
  - Deferred pipeline creation hashed on (formats, shader, state overrides), worker-thread-local staging merged post-frame → `references/pipelines.md`
  - Buddy 256 MB blocks ≤ block size vs dedicated above, linear staging allocator recycled by fence, tagged allocations + early visual debugging → `references/device-memory.md`

## Source weighting

When sources disagree: (1) spec, Vulkan Guide, and Khronos samples for API-correctness; (2) vendor guidance for hardware-specific performance heuristics; (3) tool docs for validation/profiling behavior; (4) blogs/talks as clearly-labeled examples, not universal rules. When the right choice is hardware/workload dependent, say so and recommend the measurement that would decide it.

## Refresh Workflow

1. Re-read the upstream source(s) above (spec sections, Vulkan-Guide pages, sync examples, performance samples, allocator/vendor/validation docs)
2. Diff against the prior pull (or scan for newly added sections / API revisions / extension promotions)
3. For each changed area, update the corresponding `references/<topic>.md`
4. Bump **Last reviewed** date above
