---
name: gpu-rendering-guide
description: "Design and review explicit-API GPU renderer architecture (Vulkan/D3D12/Metal/WebGPU): render graphs (RDG/FrameGraph), shader/binding models, bindless, barriers/sync, frames-in-flight, GPU memory, indirect GPU-driven culling, async compute, and HDR output — even without naming an API."
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
- Immediate-mode UI draw streams — out of scope for this skill set
- GLSL language, layouts, SPIR-V bindings, compile validation — use [glsl-coding](../glsl-coding/SKILL.md)
- WebGL-only or driver-managed rendering with no explicit memory/sync ownership
- CPU-side C++ allocator/ownership design (arenas, PMR, smart pointers) — use [cpp-memory-guide](../cpp-memory-guide/SKILL.md) (GPU device memory stays in [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md))
- Android Vulkan renderer (`Surface`, swapchain lifecycle, AHB interop, AVP) — use [android-vulkan-dev](../android-vulkan-dev/SKILL.md)

## Requirements

- Target an explicit, low-level API where the app owns memory, synchronization, and pipeline state — not a driver that hides them.
- Assume validation/debug layers and a frame debugger are available during development.
- Optionally sit a thin RHI/backend abstraction (Unreal RHI, Godot RenderingDevice pattern) above the explicit API — the architecture below still applies; only call sites change.

## Essentials

- **Declare, don't sequence** - Passes declare resource reads/writes; the graph derives order, barriers, and layout transitions, see [references/render-graph.md](references/render-graph.md)
- **Shaders are build artifacts** - Author → compile to a binary intermediate offline → reflect for layouts, see [references/shader-system.md](references/shader-system.md)
- **You own GPU memory** - Sub-allocate from a few large blocks; never one allocation per resource, see [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md)
- **You own synchronization** - Nothing is implicit; barriers, queue waits, and fences are explicit, see [references/synchronization.md](references/synchronization.md)

## Reference routing

Conceptual parallels only — not engine API how-tos.

| Read when | Read | Engine parallel |
|-----------|------|-----------------|
| Pass ordering; barrier/layout-transition automation; transient aliasing; async compute edges in the graph | [references/render-graph.md](references/render-graph.md) | Unreal RDG / Unity RenderGraph / Frostbite FrameGraph; UE RDG barrier automation |
| Shader compile; variants/permutations; reflection; hot-reload | [references/shader-system.md](references/shader-system.md) | UE PSO precache / Unity shader variant stripping |
| PSO layout; descriptors; bindless; inline constants | [references/binding-model.md](references/binding-model.md) | UE bindless descriptor indexing; Unity SRP Batcher; id Tech clustered forward+ |
| Barriers; queue waits; fences; cross-queue sync | [references/synchronization.md](references/synchronization.md) | UE timeline semaphores |
| Command recording; threading; frames-in-flight; sort keys | [references/command-recording-and-frames.md](references/command-recording-and-frames.md) | — |
| GPU memory tiers; sub-allocation; staging; ring buffers | [references/gpu-memory-strategy.md](references/gpu-memory-strategy.md) | — |
| Culling; draw sorting; PSO/material batching | [references/scene-rendering-culling.md](references/scene-rendering-culling.md) | UE sorted mesh passes; id Tech many-light forward |
| GPU culling; compact + indirect draw; scaling submission beyond CPU limits | [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md) | Nanite / Unity BRG |
| Pluggable render features; extension passes | [references/render-pipeline-composition.md](references/render-pipeline-composition.md) | Unity RendererFeatures / UE render plugins |
| Vertex fetch; packing; morph targets; GPU skinning | [references/vertex-assembly-skinning.md](references/vertex-assembly-skinning.md) | — |
| GPU compute simulation; indirect dispatch; no CPU readback | [references/gpu-compute-simulation.md](references/gpu-compute-simulation.md) | — |
| HDR output; swapchain color space; display encode | [references/hdr-output.md](references/hdr-output.md) | Unity HDR Output / UE HDR display pipeline |

## Gotchas

- A barrier scoped too broadly (everything → everything) is correct but serializes the GPU; scope stage/access to what actually waits.
- Forgetting an image-layout transition is undefined behavior even when the data is "obviously" ready — layout is part of the contract, not a hint.
- One allocation per resource exhausts the (small, capped) device allocation limit and is slow; sub-allocate from large blocks.
- Host-coherent memory skips explicit flush/invalidate but is not free; use persistently mapped rings for per-frame dynamic data — reserve staging copies for static device-local uploads.
- Recording into a per-frame context before its fence has signaled corrupts in-flight work — see the fence gotcha in [references/synchronization.md](references/synchronization.md).
- Re-using a transient target the graph aliased to another lifetime, then reading it later, returns garbage; lifetimes must not overlap.
- Applying a display transfer function twice (an automatic sRGB backbuffer plus your own HDR encode) double-darkens and loses precision in the shadows — encode exactly once.
- Reading GPU-simulation results back to the CPU each frame reintroduces the full pipeline stall you went to the GPU to avoid; consume them on the GPU via indirect draw.
- Submitting draws in scene order instead of PSO/material order silently tanks throughput — sort before record, see [references/scene-rendering-culling.md](references/scene-rendering-culling.md).
- Reading the GPU visible count back to size a CPU draw loop defeats GPU-driven rendering — use indirect draw, see [references/gpu-driven-rendering.md](references/gpu-driven-rendering.md).
- Async-compute passes need queue ownership + cross-queue waits at graph boundaries, not just intra-queue barriers.

## Companion Skills

Paths below assume `<SKILL_ROOT>` is the directory containing this skill's `SKILL.md` (bootstrap: `skills/gpu-rendering-guide/`; installed: `.agents/skills/gpu-rendering-guide/`).

| Task | Path |
|------|------|
| C++ CPU allocator (arenas, pools, ownership, PMR) | [../cpp-memory-guide/SKILL.md](../cpp-memory-guide/SKILL.md) |
| Concrete Vulkan API (`Vk*`, `vkCmd*`, swapchain) | [../vulkan-dev/SKILL.md](../vulkan-dev/SKILL.md) |
| Android Vulkan platform (surface, WSI, AHB, AVP) | [../android-vulkan-dev/SKILL.md](../android-vulkan-dev/SKILL.md) |
| Slang shader authoring and SPIR-V/MSL emission | [../slang-dev/SKILL.md](../slang-dev/SKILL.md) |
| OpenUSD Hydra 2.0 scene-index pipelines | [../usd-hydra2-dev/SKILL.md](../usd-hydra2-dev/SKILL.md) |
| GLSL language, layouts, SPIR-V bindings | [../glsl-coding/SKILL.md](../glsl-coding/SKILL.md) |
| GLSL shader effects and techniques | [../shader-guide/SKILL.md](../shader-guide/SKILL.md) |

When a companion is installed to `.agents/skills/<name>/`, read that copy and resolve `<SKILL_ROOT>` from its directory.

## Tool notes

- After installing or editing the skill, reload the coding agent (restart or reload the Claude Code session; reload the Cursor window; reload VS Code for Copilot) so the skill is rediscovered.
