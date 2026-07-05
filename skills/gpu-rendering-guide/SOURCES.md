# Sources

## Explicit-API rendering architecture (cross-API)

- **URLs:**
  - Microsoft Direct3D 12 programming guide — https://learn.microsoft.com/en-us/windows/win32/direct3d12/directx-12-programming-guide
  - Apple Metal documentation — https://developer.apple.com/documentation/metal
  - WebGPU specification — https://www.w3.org/TR/webgpu/
  - Vulkan specification — https://registry.khronos.org/vulkan/specs/1.3/html/
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Requirements, Architecture, Resources, Synchronization
  - Cross-API confirmation that pipeline-state objects, explicit barriers, frequency-grouped binding, bindless, frames-in-flight, and queue-side waits are general explicit-API concepts, not specific to one API
- **Aspects extracted:**
  - Pipeline objects + cache, binding frequency, bindless, inline constants → `references/binding-model.md`
  - Frames-in-flight, multi-threaded command recording, swapchain loop → `references/command-recording-and-frames.md`
  - Resource barriers (stage/access scopes), layout transitions, cross-queue waits, timeline values, fences → `references/synchronization.md`
  - Memory tiers (device-local vs host-visible), allocation limits, alignment, staging → `references/gpu-memory-strategy.md`

## FrameGraph: Extensible Rendering Architecture (GDC 2017)

- **URL:** https://www.gdcvault.com/play/1024612/FrameGraph-Extensible-Rendering-Architecture-in
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Essentials, Architecture, Engine Pattern Map
  - The declarative-pass / derived-execution framing and transient resource aliasing
- **Aspects extracted:**
  - Passes declare reads/writes; graph derives order, barriers, and layout transitions; culls dead passes → `references/render-graph.md`
  - Transient render-target memory aliasing by disjoint lifetime → `references/render-graph.md`
  - Nested modules with extension points → `references/render-pipeline-composition.md`

## Unreal Engine rendering documentation

- **URLs:**
  - Render Dependency Graph — https://docs.unrealengine.com/en-US/RenderingOverview/RenderDependencyGraph/
  - RHI overview — https://docs.unrealengine.com/en-US/API/Runtime/RHI/
  - Nanite overview — https://docs.unrealengine.com/en-US/nanite-in-unreal-engine/
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Engine Pattern Map
  - Conceptual parallels only (not UE API how-tos)
- **Aspects extracted:**
  - Declarative RDG passes, automatic barrier insertion → `references/render-graph.md`, `references/synchronization.md`
  - PSO precache, shader permutations → `references/shader-system.md`, `references/binding-model.md`
  - Bindless resource model → `references/binding-model.md`
  - Mesh draw commands, sorted mesh passes → `references/scene-rendering-culling.md`
  - Nanite GPU cluster culling + indirect draw → `references/gpu-driven-rendering.md`
  - Render plugins / extension passes → `references/render-pipeline-composition.md`
  - Timeline semaphores → `references/synchronization.md`
  - HDR display pipeline → `references/hdr-output.md`

## Unity rendering documentation

- **URLs:**
  - Scriptable Render Pipeline — https://docs.unity3d.com/Manual/scriptable-render-pipeline-introduction.html
  - RenderGraph (Unity 6+) — https://docs.unity3d.com/Manual/urp/render-graph-introduction.html
  - BatchRendererGroup — https://docs.unity3d.com/ScriptReference/Rendering.BatchRendererGroup.html
  - HDR Output — https://docs.unity3d.com/Manual/hdr-output.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Engine Pattern Map
  - Conceptual parallels only (not Unity C# API how-tos)
- **Aspects extracted:**
  - RenderGraph declarative passes → `references/render-graph.md`
  - SRP Batcher constant batching → `references/binding-model.md`
  - Shader keyword variant stripping → `references/shader-system.md`
  - RendererFeatures / pluggable passes → `references/render-pipeline-composition.md`
  - BRG / GPU Resident Drawer GPU-driven path → `references/gpu-driven-rendering.md`
  - HDR Output linear pipeline + encode → `references/hdr-output.md`

## Godot 4 rendering documentation

- **URLs:**
  - RenderingDevice — https://docs.godotengine.org/en/stable/classes/class_renderingdevice.html
  - Rendering pipeline — https://docs.godotengine.org/en/stable/contributing/development/core_and_modules/internal_rendering_architecture.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Requirements (optional RHI abstraction layer)
- **Aspects extracted:**
  - Thin backend abstraction over explicit API → `SKILL.md` Requirements note

## Render-graph / frame-graph technique writeups

- **URLs:**
  - "Render graphs and Vulkan — a deep dive" — https://themaister.net/blog/2017/08/15/render-graphs-and-vulkan-a-deep-dive/
  - "Organizing GPU Work with Directed Acyclic Graphs" — https://levelup.gitconnected.com/organizing-gpu-work-with-directed-acyclic-graphs-f3fd5f2c2af3
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Architecture, Gotchas
  - Practical per-frame graph compilation, barrier derivation, and aliasing edge cases
- **Aspects extracted:**
  - Topological sort, lifetime computation, automatic barrier/transition placement → `references/render-graph.md`
  - Async-compute/multi-queue edges needing cross-queue waits + ownership transfers → `references/render-graph.md`, `references/synchronization.md`

## GPU memory strategy

- **URLs:**
  - GPU memory allocator documentation — https://gpuopen.com/learn/vulkan-memory-allocator/
  - "Writing an efficient Vulkan renderer" — https://zeux.io/2020/02/27/writing-an-efficient-vulkan-renderer/
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Resources, Essentials
  - Sub-allocation from large blocks, staging, persistent mapping, defragmentation (the strategy, not one API's calls)
- **Aspects extracted:**
  - Few large allocations + sub-allocation, allocation-count cap, placement alignment → `references/gpu-memory-strategy.md`
  - Staging upload to device-local, persistent mapping, ring buffers, defragmentation → `references/gpu-memory-strategy.md`
  - C++ CPU allocator principles deferred to cpp-memory-guide → `references/gpu-memory-strategy.md`

## Shader compilation and reflection tooling

- **URLs:**
  - glslang — https://github.com/KhronosGroup/glslang
  - SPIRV-Reflect — https://github.com/KhronosGroup/SPIRV-Reflect
  - DirectX Shader Compiler (DXC) — https://github.com/microsoft/DirectXShaderCompiler
  - SPIR-V specification — https://registry.khronos.org/SPIR-V/specs/unified1/SPIRV.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Essentials, Architecture
  - Offline compile to a binary intermediate, reflection-derived layouts, variants, caching
- **Aspects extracted:**
  - Source → binary intermediate offline, reflection for binding/layout info → `references/shader-system.md`
  - Permutations vs ubershader + specialization constants, pipeline keying, hot-reload, disk cache → `references/shader-system.md`, `references/binding-model.md`

## Game-engine development blog (archive)

- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Architecture, Resources, Output, Synchronization, Gotchas
  - A worked, shipped instance of the cross-API architecture: declarative passes, frequency-grouped binding, sort-key scheduling, sub-allocated device memory, multi-GPU, programmable vertex fetch, GPU compute simulation, and HDR output
- **Aspects extracted:**
  - "A modern rendering architecture", "Simple Parallel Rendering" — 64-bit sort key per command decoupling GPU order from CPU record order, merge-and-sort worker streams before submit → `references/command-recording-and-frames.md`, `references/scene-rendering-culling.md`
  - "High-Level Rendering Using Render Graphs" — setup/execute pass split, root-pass culling, transient lifetimes, nested modules with extension points → `references/render-graph.md`, `references/render-pipeline-composition.md`
  - "Efficient binding of shader resources" — resource binders grouped by update frequency (UPDATABLE vs DYNAMIC); commands carry only handles so streams translate in parallel → `references/binding-model.md`
  - "the engine Shader System (parts 1–3)" — declarative composable shader declarations (imports/code/state, last-write-wins), generated accessors, system-bitmask variant selection, materials as a superset binder → `references/shader-system.md`
  - "Device Memory Management" — few large blocks + sub-allocation, buddy ≤256 MB vs dedicated above, build visual allocator debugging early → `references/gpu-memory-strategy.md`
  - "Explicit Multi-GPU Programming", "Moving the engine to Bindless" — device-affinity masks; single global descriptor array with indices embedded in handles (the bindless principle behind the binding model) → `references/binding-model.md`, `references/synchronization.md`
  - "Vertex Assembly and Skinning" — programmable vertex pull from byte-address buffers behind a loader interface, active-channel bitflags + offset/stride, packed skin-influence word (count + offset into a shared influence buffer), in-shader linear blend skinning, ping-pong bone matrices for motion vectors → `references/vertex-assembly-skinning.md`
  - "GPU Simulation" — GPU-resident element state in ring buffers, event-triggered init/spawn/update compute stages, GPU-tracked live count feeding indirect dispatch/draw, double-buffered state, atomics/append for spawn and compaction → `references/gpu-compute-simulation.md`
  - "Supporting Native HDR Monitors" — wide-gamut PQ (Rec.2020/ST2084) vs extended-linear scRGB swapchains, ≥10-bit/FP16 to avoid banding, linear pipeline with an explicit final color-space (3×3 to output primaries) + transfer encode, paper-white scaling to the display's real peak nits, encode-once / row-vs-column matrix pitfalls → `references/hdr-output.md`

## Refresh Workflow

1. Re-read the upstream source(s) above (spec sections, talk, allocator/tooling docs, engine docs)
2. Diff against the prior pull (or scan for newly added sections / API revisions)
3. For each changed area, update the corresponding `references/<topic>.md`
4. Bump **Last reviewed** date above
