# best-practices: Vulkan 1.3 Best-Practice Hierarchy and Performance Triage

Use this reference for broad best practices, architecture advice, performance triage, and migration from OpenGL-style rendering. Prioritize correctness first, then CPU/GPU parallelism, then platform-specific performance. The API-agnostic architecture (render graph, binding model, frames-in-flight, memory strategy) lives in [gpu-rendering-guide](../../gpu-rendering-guide/SKILL.md); this reference is the Vulkan-specific policy layer.

## 1. Architecture first

Vulkan exposes responsibility older APIs hid in the driver. A good renderer owns: resource lifetime and deferred destruction; image layouts and buffer/image hazards; queue ownership and synchronization; CPU/GPU and GPU/GPU synchronization; memory sub-allocation and budget; descriptor allocation/update/binding frequency; pipeline creation/caching/warmup; command-buffer reuse and multithreaded recording; profiling and validation modes.

If an answer only says which function to call, it is usually incomplete — explain where that call belongs in the renderer's ownership model.

## 2. Synchronization

Prefer synchronization2 on Vulkan 1.3 (`vkCmdPipelineBarrier2`, `VkDependencyInfo`, `Vk{Memory,Buffer,Image}MemoryBarrier2`, `vkQueueSubmit2`). Concrete masks and examples are in [resources-and-barriers.md](./resources-and-barriers.md) and [synchronization.md](./synchronization.md).

- Keep `srcStageMask` as early and `dstStageMask` as late as correctness allows; match access masks to the actual use.
- Avoid `ALL_COMMANDS -> ALL_COMMANDS`, `ALL_GRAPHICS -> ALL_GRAPHICS`, and `BOTTOM_OF_PIPE -> TOP_OF_PIPE` as permanent solutions.
- Use image layouts to express real usage; avoid `GENERAL` except when required.
- Semaphores for queue-to-queue and acquire/present; barriers for intra-queue memory/execution; fences/timeline values for CPU-side reuse/destruction.
- Avoid frame-loop `vkDeviceWaitIdle`/`vkQueueWaitIdle`; reserve for teardown, coarse debugging, swapchain reconstruction, or emergency recovery.

A conservative barrier serializes work and creates GPU bubbles; a missing/too-weak barrier corrupts rendering.

## 3. Memory

Do not allocate `VkDeviceMemory` per resource; sub-allocate large blocks (mechanics in [device-memory.md](./device-memory.md)).

- Use VMA or an equivalent allocator unless the engine already has a mature one.
- Device-local for hot GPU resources; staging buffers for discrete-GPU uploads; host-visible device-local directly on UMA only where measured.
- Keep upload buffers persistently mapped; respect `nonCoherentAtomSize` and buffer/image alignment.
- Use dedicated allocations for very large resources when beneficial or required.
- Track budget; defer destruction until the last timeline/fence use completes.

Failure modes: slow OS/driver allocations, allocation-count limits, fragmentation, PCIe bottlenecks, GPU use-after-free.

## 4. Descriptors

Design around update frequency (set 0 frame/view, set 1 pass, set 2 material/bindless table, set 3 or buffer-device-address per-object). Mechanics in [descriptors.md](./descriptors.md).

- Avoid per-draw descriptor allocation/update; cache sets by content or ring descriptor pools per frame.
- Push constants for tiny hot data; dynamic offsets or object buffers for per-object data.
- Use descriptor indexing for bindless tables only after enabling the required feature bits.
- Treat update-after-bind as a lifetime contract: never mutate a descriptor in-flight unless the feature/binding rules explicitly allow it.
- Treat `VK_EXT_descriptor_buffer` / heap-style paths as optional, behind a backend abstraction, after verifying support.

## 5. Pipelines and shaders

Do not surprise-create pipelines on the render path (mechanics in [pipelines.md](./pipelines.md)).

- Compile shaders to SPIR-V in a controlled build/loading path; validate SPIR-V and reflection against the pipeline layout.
- Build stable pipeline keys; persist the pipeline cache; warm known pipelines before interactive rendering.
- Reduce permutation explosion via dynamic state, specialization constants, material bucketing before adding runtime state.
- Use background compilation only behind fallback pipelines where stutter is acceptable.

## 6. Command buffers and CPU parallelism

- Per-frame/per-thread command pools; reset pools rather than allocate/free per frame (mechanics in [commands-and-swapchain.md](./commands-and-swapchain.md)).
- `ONE_TIME_SUBMIT_BIT` for one-frame buffers; avoid `SIMULTANEOUS_USE_BIT` unless needed.
- Re-record each frame by default; cache only when it demonstrably helps and invalidation is manageable.
- Secondary buffers help multithreaded recording only with enough work to amortize overhead; do not exceed useful CPU parallelism.
- Batch submissions to cut overhead without adding avoidable latency.

## 7. Queues and async

Extra queues are not free. Start with the fewest that express real needs; use transfer queues for meaningful upload batches, not tiny copies; use async compute only when timestamps/profiler show overlap; avoid unnecessary queue-family ownership transfers; prefer timeline semaphores for complex GPU-GPU progress.

## 8. Frame graph

For non-trivial renderers, centralize pass ordering, image layouts, barriers, transient lifetime/aliasing, load/store ops, queue-ownership transfers, semaphore waits/signals, per-frame versioning, and destruction safety in a frame graph. The agnostic render-graph model is in [gpu-rendering-guide render-graph](../../gpu-rendering-guide/references/render-graph.md). Scattered ad-hoc barriers are fine for small samples but fragile under resize, streaming, async compute, and temporal resources.

## 9. Validation and debugging

Use validation as multiple modes, not one switch: core validation (routine dev), synchronization validation (regular/targeted), GPU-assisted validation (shader/descriptor/device-address defects), best-practices validation (periodic hygiene). Always name objects and command-buffer regions via debug utils to speed up RenderDoc/Nsight/RGP/AGI/Arm tools and validation logs. Validation does not guarantee correctness — timing hazards, external sync, and driver behavior still need review + profiling.

## 10. Mobile / tile-based GPUs

Bandwidth and attachment behavior are first-order on tilers:

- `LOAD_OP_CLEAR`/`LOAD_OP_DONT_CARE` instead of `LOAD` when previous contents are unneeded; `STORE_OP_DONT_CARE` for temporary attachments.
- Transient/lazily-allocated attachments for depth/MSAA/intermediate G-buffer data that never needs system-memory storage.
- Prefer subpass/local-read (or dynamic-rendering local-read) for tile-local intermediate data where available.
- Avoid unnecessary full-screen bandwidth passes; use compact formats when quality allows.

Desktop immediate renderers and mobile tilers can prefer different pass structures — do not present one as universal.

## 11. Feature-adoption tiers

- **compatibility**: conservative 1.1/1.2 style, classic descriptors, render passes where necessary.
- **modern default**: Vulkan 1.3, synchronization2, timeline semaphores, dynamic rendering, descriptor indexing.
- **high-end**: roadmap-profile limits/features, mesh/task shaders, VRS, ray tracing, descriptor buffer/heap, advanced GPU-driven rendering.

Always query features, properties, limits, and formats; do not infer support from API version alone, see [capabilities-and-setup.md](./capabilities-and-setup.md).

## 12. Anti-patterns to flag aggressively

- per-draw descriptor allocation/update
- per-resource `vkAllocateMemory`
- frame-loop `vkDeviceWaitIdle`/`vkQueueWaitIdle`
- global barriers as permanent synchronization; `GENERAL` layout for convenience
- updating/freeing descriptors or resources still used by older frames
- creating pipelines during gameplay without warmup/cache/fallback
- too many queues or tiny async tasks; too many small secondary command buffers
- unbounded frames-in-flight; ignoring swapchain image/semaphore reuse rules
- treating mobile tilers like desktop immediate-mode GPUs

## Performance triage workflow

1. Determine CPU-bound vs GPU-bound vs bandwidth-bound vs stutter-bound.
2. CPU-bound: inspect descriptor updates, command recording, submissions, pipeline creation, allocation churn, validation overhead, scene traversal.
3. GPU-bound: inspect timestamp ranges, pipeline bubbles, barrier precision, bandwidth-heavy passes, overdraw, shader cost, occupancy, format choices.
4. Stutter-bound: inspect pipeline/shader compilation, resource allocation, residency/budget pressure, streaming uploads.
5. Suspected async: verify overlap via queue timelines/timestamps, do not assume.

When recommending an optimization, state which bottleneck it targets, what measurement confirms it, what hardware class it depends on, and what correctness constraints it adds. Prefer "measure this" only when followed by the exact signal (GPU timestamp gaps, queue bubbles, CPU submit time, descriptor-update time, pipeline-creation spikes, memory-budget pressure).

## Related

[capabilities-and-setup.md](./capabilities-and-setup.md), [code-review-and-audit.md](./code-review-and-audit.md), [resources-and-barriers.md](./resources-and-barriers.md), [synchronization.md](./synchronization.md), [descriptors.md](./descriptors.md), [pipelines.md](./pipelines.md), [commands-and-swapchain.md](./commands-and-swapchain.md)
