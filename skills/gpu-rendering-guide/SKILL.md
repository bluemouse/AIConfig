---
name: gpu-rendering-guide
description: "Design and review explicit-API renderer architecture (Vulkan/D3D12/Metal/WebGPU): render graphs, RDG, shader systems, binding model, bindless, sync, frames-in-flight, GPU memory, scene submission, GPU-driven rendering, indirect draw, Nanite-style culling, HDR output. Use when architecting or debugging a custom renderer, render passes, barriers, pipeline stalls, async compute, or draw submission — even without naming an API. Patterns align with Unreal RDG, Unity RenderGraph/SRP, and Frostbite FrameGraph at the conceptual level."
---

# GPU Rendering Guidelines (Explicit-API Architecture)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` from that directory.

API-agnostic architecture for a low-level GPU renderer. The concepts hold across explicit APIs (Vulkan, D3D12, Metal, WebGPU); names differ but the model is the same.

## When to Use

- Designing or reviewing a custom explicit-API renderer (render graph, sync, memory, draw submission)
- Debugging barriers, pipeline stalls, bindless binding, frames-in-flight, or HDR encode issues
- Mapping production-engine patterns (RDG, RenderGraph, mesh passes, GPU culling) to your architecture

## When NOT to Use

- High-level engine runtime work (Unity C# SRP scripts, Unreal C++ gameplay/render plugins) — use engine docs; this skill covers architecture only
- Concrete API calls (`Vk*`, `vkCmd*`, `ID3D12*`, Metal objects) — use [vulkan-dev](../vulkan-dev/SKILL.md) for Vulkan (or the matching API skill when available)
- Immediate-mode UI draw streams — use **imgui-guide**
- GLSL shader effect authoring — use **shader-dev**
- WebGL-only or driver-managed rendering with no explicit memory/sync ownership
- CPU-side C++ allocator/ownership design (arenas, PMR, smart pointers) — use [cpp-memory-guide](../cpp-memory-guide/SKILL.md) (GPU device memory stays in [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md))

## Requirements

- Target an explicit, low-level API where the app owns memory, synchronization, and pipeline state — not a driver that hides them.
- Assume validation/debug layers and a frame debugger are available during development.
- Optionally sit a thin RHI/backend abstraction (Unreal RHI, Godot RenderingDevice pattern) above the explicit API — the architecture below still applies; only call sites change.

## Essentials

- **Declare, don't sequence** - Passes declare resource reads/writes; the graph derives order, barriers, and layout transitions, see [references/render-graph.md](references/render-graph.md)
- **Shaders are build artifacts** - Author → compile to a binary intermediate offline → reflect for layouts, see [references/shader-system.md](references/shader-system.md)
- **You own GPU memory** - Sub-allocate from a few large blocks; never one allocation per resource, see [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md)
- **You own synchronization** - Nothing is implicit; barriers, queue waits, and fences are explicit, see [references/synchronization.md](references/synchronization.md)

## Architecture

- **Render graph** - Per-frame DAG that prunes dead passes, orders work, and aliases transient targets, see [references/render-graph.md](references/render-graph.md)
- **Shader system** - Permutations vs ubershaders, pipeline keyed by shader+state, hot-reload, caching, see [references/shader-system.md](references/shader-system.md)
- **Binding model** - Frequency-grouped bindings, bindless arrays, inline constants; precompile and cache PSOs, see [references/binding-model.md](references/binding-model.md)
- **Command recording** - One recording context per thread per frame, multi-threaded record, see [references/command-recording-and-frames.md](references/command-recording-and-frames.md)
- **Frames in flight** - Double/triple-buffer per-frame resource sets behind a fence so the CPU can't outrun the GPU, see [references/command-recording-and-frames.md](references/command-recording-and-frames.md)
- **Sort keys** - A 64-bit key per command decouples GPU submission order from CPU record order; merge worker streams and sort before submit, see [references/command-recording-and-frames.md](references/command-recording-and-frames.md)
- **Scene submission** - Cull visible geometry, sort draws by PSO/material, minimize state changes, see [references/scene-rendering-culling.md](references/scene-rendering-culling.md)
- **GPU-driven rendering** - GPU cull + compact + indirect draw when CPU submission can't scale, see [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md)
- **Pipeline composition** - Core graph + pluggable extension passes at injection points, see [references/render-pipeline-composition.md](references/render-pipeline-composition.md)
- **Async compute** - Schedule compute on a separate queue; model cross-queue edges in the graph with ownership transfer + queue waits, see [references/render-graph.md](references/render-graph.md), [references/synchronization.md](references/synchronization.md)
- **Programmable vertex fetch** - Pull vertices from storage buffers behind a loader interface; skin in-shader from an indirected influence list, see [references/vertex-assembly-skinning.md](references/vertex-assembly-skinning.md)
- **GPU-resident simulation** - GPU buffers + compute + indirect draw/dispatch; no CPU enumeration or readback, see [references/gpu-compute-simulation.md](references/gpu-compute-simulation.md)
- **HDR output** - Linear scene pipeline, explicit final encode to swapchain color space, see [references/hdr-output.md](references/hdr-output.md)

## Engine Pattern Map

Conceptual parallels only — not engine API how-tos.

| Engine pattern | Maps to |
|----------------|---------|
| Unreal RDG / Unity RenderGraph / Frostbite FrameGraph | [references/render-graph.md](references/render-graph.md) |
| UE PSO precache / Unity shader variant stripping | [references/shader-system.md](references/shader-system.md), [references/binding-model.md](references/binding-model.md) |
| UE bindless descriptor indexing | [references/binding-model.md](references/binding-model.md) |
| Unity SRP Batcher (compatible CB layout batching) | [references/binding-model.md](references/binding-model.md), [references/scene-rendering-culling.md](references/scene-rendering-culling.md) |
| UE mesh draw commands / sorted mesh passes | [references/scene-rendering-culling.md](references/scene-rendering-culling.md) |
| id Tech clustered forward+ / many-light forward | [references/scene-rendering-culling.md](references/scene-rendering-culling.md), [references/binding-model.md](references/binding-model.md) |
| Nanite / Unity BRG / GPU culling | [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md) |
| Unity RendererFeatures / UE render plugins | [references/render-pipeline-composition.md](references/render-pipeline-composition.md) |
| UE timeline semaphores / RDG barrier automation | [references/synchronization.md](references/synchronization.md) |
| Unity HDR Output / UE HDR display pipeline | [references/hdr-output.md](references/hdr-output.md) |

## Reference Routing

| Task | Read |
|------|------|
| Pass ordering, barriers, transient aliasing, async compute in the graph | [references/render-graph.md](references/render-graph.md) |
| Shader compile, variants/permutations, reflection, hot-reload | [references/shader-system.md](references/shader-system.md) |
| PSO layout, descriptors, bindless, inline constants | [references/binding-model.md](references/binding-model.md) |
| Barriers, queue waits, fences, cross-queue sync | [references/synchronization.md](references/synchronization.md) |
| Command recording, threading, frames-in-flight, sort keys | [references/command-recording-and-frames.md](references/command-recording-and-frames.md) |
| GPU memory tiers, sub-allocation, staging, ring buffers | [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md) |
| Culling, draw sorting, PSO/material batching | [references/scene-rendering-culling.md](references/scene-rendering-culling.md) |
| GPU culling, indirect draw, scaling submission | [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md) |
| Pluggable render features, extension passes | [references/render-pipeline-composition.md](references/render-pipeline-composition.md) |
| Vertex fetch, packing, morph targets, GPU skinning | [references/vertex-assembly-skinning.md](references/vertex-assembly-skinning.md) |
| GPU compute simulation, indirect dispatch | [references/gpu-compute-simulation.md](references/gpu-compute-simulation.md) |
| HDR output, swapchain color space, display encode | [references/hdr-output.md](references/hdr-output.md) |

## Gotchas

- A barrier scoped too broadly (everything → everything) is correct but serializes the GPU; scope stage/access to what actually waits.
- Forgetting an image-layout transition is undefined behavior even when the data is "obviously" ready — layout is part of the contract, not a hint.
- One allocation per resource exhausts the (small, capped) device allocation limit and is slow; sub-allocate from large blocks.
- Host-coherent memory skips explicit flush/invalidate but is not free; use persistently mapped rings for per-frame dynamic data — reserve staging copies for static device-local uploads.
- Recording into a per-frame context whose previous submission's fence has not signaled corrupts in-flight GPU work — gate reuse on the fence.
- Re-using a transient target the graph aliased to another lifetime, then reading it later, returns garbage; lifetimes must not overlap.
- Applying a display transfer function twice (an automatic sRGB backbuffer plus your own HDR encode) double-darkens and loses precision in the shadows — encode exactly once.
- Reading GPU-simulation results back to the CPU each frame reintroduces the full pipeline stall you went to the GPU to avoid; consume them on the GPU via indirect draw.
- Submitting draws in scene order instead of PSO/material order silently tanks throughput — sort before record, see [references/scene-rendering-culling.md](references/scene-rendering-culling.md).
- Reading the GPU visible count back to size a CPU draw loop defeats GPU-driven rendering — use indirect draw, see [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md).
- Async-compute passes need queue ownership + cross-queue waits at graph boundaries, not just intra-queue barriers.

## Progressive Disclosure

- Read [references/render-graph.md](references/render-graph.md) - Load when ordering passes, automating barriers/transitions, or aliasing transient targets
- Read [references/shader-system.md](references/shader-system.md) - Load when compiling shaders, handling variants/permutations, reflection, or hot-reload
- Read [references/binding-model.md](references/binding-model.md) - Load when designing pipeline state and the descriptor/binding model, or going bindless
- Read [references/synchronization.md](references/synchronization.md) - Load when placing barriers, queue waits, fences, or reasoning about queue timelines
- Read [references/command-recording-and-frames.md](references/command-recording-and-frames.md) - Load when recording commands, threading recording, or sizing frames-in-flight
- Read [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md) - Load when planning GPU memory tiers, sub-allocation, or uploads
- Read [references/scene-rendering-culling.md](references/scene-rendering-culling.md) - Load when culling, sorting draws, or minimizing pipeline state changes
- Read [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md) - Load when GPU culling, indirect draw, or scaling draw submission beyond CPU limits
- Read [references/render-pipeline-composition.md](references/render-pipeline-composition.md) - Load when adding pluggable render features or extension passes
- Read [references/vertex-assembly-skinning.md](references/vertex-assembly-skinning.md) - Load when designing vertex fetch, vertex packing, morph targets, or GPU skinning
- Read [references/gpu-compute-simulation.md](references/gpu-compute-simulation.md) - Load when simulating many elements (particles/agents) on the GPU with compute and indirect dispatch
- Read [references/hdr-output.md](references/hdr-output.md) - Load when adding HDR output, picking a swapchain color space/format, or encoding for the display

## Companion Skills

Paths below assume `<SKILL_ROOT>` is the directory containing this skill's `SKILL.md` (bootstrap: `skills/gpu-rendering-guide/`; installed: `.shared/skills/gpu-rendering-guide/`).

| Task | Path |
|------|------|
| C++ CPU allocator (arenas, pools, ownership, PMR) | [../cpp-memory-guide/SKILL.md](../cpp-memory-guide/SKILL.md) |
| Concrete Vulkan API (`Vk*`, `vkCmd*`, swapchain) | [../vulkan-dev/SKILL.md](../vulkan-dev/SKILL.md) |
| Slang shader authoring and SPIR-V/MSL emission | [../slang-dev/SKILL.md](../slang-dev/SKILL.md) |
| OpenUSD Hydra 2.0 scene-index pipelines | [../usd-hydra2-dev/SKILL.md](../usd-hydra2-dev/SKILL.md) |
| GLSL shader effects and techniques | **shader-dev** — `.shared/skills/shader-dev/SKILL.md` when installed |
| Immediate-mode UI draw stream to GPU | **imgui-guide** — `.shared/skills/imgui-guide/SKILL.md` when installed |

When a companion is installed to `.shared/skills/<name>/`, read that copy and resolve `<SKILL_ROOT>` from its directory.
