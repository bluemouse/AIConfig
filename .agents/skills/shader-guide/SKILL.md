---
name: shader-guide
description: "Author, review, and debug creative real-time GLSL visual effects: ray marching, 2D/3D SDFs, CSG, domain warping, FBM terrain, voronoi patterns, procedural noise, soft shadows, AO, Monte Carlo path tracing, volumetrics, Gerstner waves, fluids, ping-pong simulation, Turing/reaction-diffusion patterns, particles, bloom/ACES post-processing, and multi-pass buffers. Use for generative art, implicit-surface scenes, domain-warped organic blobs, or standalone fragment-shader demos — even when the user does not say SDF, ray marching, or ping-pong."
---

# Shader Guide (Creative GLSL Effects)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` from that directory.

This skill covers **creative real-time GLSL effect authoring**: implicit surfaces, procedural generation, lighting, simulation, and post-processing in neutral GLSL. The canonical technique canon (ray marching, SDF primitives, CSG blending, FBM, domain warping, soft shadows, AO, volumetric compositing, ping-pong state) is applied directly from model knowledge — `references/` carries only the judgment-heavy material: budgets, debugging method, pipeline assembly, and infra patterns. GLSL language rules, stage layouts, and Vulkan SPIR-V binding guidance live in [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) — link up for syntax, layouts, and maintainability instead of restating them.

## When to Use

- Authoring or debugging creative fragment-shader effects: SDF scenes, ray marching, procedural noise, lighting, shadows, AO, volumetrics, fluids, particles, post-processing
- Combining techniques into full pipelines (photorealistic SDF, organic forms, landscapes, stylized 2D art) — see [references/effect-recipes.md](references/effect-recipes.md)
- Visual debugging of distance fields, normals, UVs, or march step counts — see [references/shader-debugging.md](references/shader-debugging.md)
- Multi-pass GPU simulation or ping-pong state (fluids, reaction-diffusion, cellular automata)

## When NOT to Use

- GLSL language teaching, layout rules, descriptor bindings, or SPIR-V layout — use [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md)
- Slang modules, slangc, reflection, SPIR-V/MSL for production renderers — use [`../slang-dev/SKILL.md`](../slang-dev/SKILL.md)
- Renderer architecture (render graph, bindless, sync, frames-in-flight) — use [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md)
- Concrete `Vk*` pipeline/descriptor/swapchain setup — use [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md)
- Host/runtime glue (canvas setup, JavaScript loaders, browser-specific WebGL quirks) — out of scope; supply only GLSL and uniform assumptions

## Version Standard

- Default **`#version 450`** with explicit `layout(location = N)` stage I/O unless the user targets GLES.
- For GLES targets, use **`#version 300 es`** with `precision highp float;` and `out vec4 fragColor`.
- Declare host uniforms explicitly: `uniform vec2 uResolution`, `uniform float uTime`, `uniform int uFrame`, `uniform vec4 uMouse` (add others as needed).
- Normalize UVs with aspect correction: `vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y`.
- Use standard `void main()` — no `mainImage` wrapper.

## Operating Principles

- **Route first** — use the Technique Routing Table below; load only the `references/` file whose load condition matches.
- **One reference at a time** — progressive disclosure; do not load every reference unless the task spans them.
- **Respect the performance budget** — see [references/performance-budget.md](references/performance-budget.md) before raising loop counts or FBM octaves.
- **Visual-debug before tuning** — substitute debug colors (normals, SDF bands, step heatmaps) per [references/shader-debugging.md](references/shader-debugging.md).
- **Neutral GLSL output** — templates use `uResolution`/`uTime`/`uFrame`; adapt bindings to the host API via [glsl-coding](../glsl-coding/SKILL.md) when integrating into OpenGL/Vulkan.
- **Validate references after edits** — run [scripts/validate_references.py](scripts/validate_references.py) on `references/` before reinstalling.

## Technique Routing Table

| Load condition | Read |
|---|---|
| Assembling a multi-technique pipeline (photorealistic SDF scene, organic forms, landscape, stylized 2D) | [references/effect-recipes.md](references/effect-recipes.md) |
| Output looks wrong and you need to isolate normals, SDF, UV, shadow/AO, or march cost | [references/shader-debugging.md](references/shader-debugging.md) |
| Before increasing loop counts, march steps, or FBM depth — or when frames stall | [references/performance-budget.md](references/performance-budget.md) |
| Ping-pong simulation, persistent cross-frame state, pass chaining, structured texel storage | [references/multipass-buffer.md](references/multipass-buffer.md) |
| Optimizing an SDF scene: bounding culls, hollow shells, hit refinement, field debug views | [references/sdf-tricks.md](references/sdf-tricks.md) |
| Tracing a reference back to original `skills-ref/shader-dev` provenance | [references/source-map.md](references/source-map.md) |
| GLSL compilation, link, or SPIR-V validation workflow | [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) |

Individual techniques (ray marching, SDF primitives, CSG, domain warping/repetition, FBM and noise variants, voronoi, lighting models, soft shadows, AO, volumetrics, water/terrain, fractals, particles, path tracing, tone mapping, AA, camera effects, audio synthesis) have no reference file — write them directly from model knowledge and apply the Gotchas and performance budget below.

## Gotchas

- **Function signature mismatch** — if `fbm(vec3 p)` is defined, do not call `fbm(uv)` with a `vec2`.
- **Terrain sampling** — height functions often need XZ: `terrainM(pos.xz + offset)`, not `terrainM(pos + offset)`.
- **Performance** — ray march ≤ 128 steps, volume inner loops ≤ 32, FBM ≤ 6 octaves, nested loops ≤ 1000 iterations/pixel; see [references/performance-budget.md](references/performance-budget.md).
- **Ping-pong feedback** — a pass reading its own output must alternate `uChannel0`/`uChannel1` each frame; seed the first frame (`uFrame < N` guard).
- **Debug colors left in `main()` ship silently** — gate with `const bool DEBUG = false`.
- **GLSL syntax and compile rules** — see [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md).

## Companion Skills

| Task | Path |
|------|------|
| GLSL language, layouts, SPIR-V bindings, maintainability | [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) |
| Slang shader modules and slangc integration | [`../slang-dev/SKILL.md`](../slang-dev/SKILL.md) |
| Renderer architecture (render graph, bindless, sync) | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| Concrete Vulkan API (`Vk*`, pipelines, descriptors) | [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md) |

Relative paths resolve from `.agents/skills/shader-guide/` when installed (or `skills/shader-guide/` in bootstrap layout).
