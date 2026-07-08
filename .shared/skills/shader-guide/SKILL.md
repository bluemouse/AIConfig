---
name: shader-guide
description: "Author, review, and debug creative real-time GLSL visual effects: ray marching, 2D/3D SDFs, CSG, domain warping, FBM terrain, voronoi patterns, procedural noise, soft shadows, AO, Monte Carlo path tracing, volumetrics, Gerstner waves, fluids, ping-pong simulation, Turing/reaction-diffusion patterns, particles, bloom/ACES post-processing, and multi-pass buffers. Use for generative art, implicit-surface scenes, domain-warped organic blobs, or standalone fragment-shader demos — even when the user does not say SDF, ray marching, or ping-pong."
---

# Shader Guide (Creative GLSL Effects)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` from that directory.

This skill covers **creative real-time GLSL effect authoring**: implicit surfaces, procedural generation, lighting, simulation, and post-processing in neutral GLSL. GLSL language rules, stage layouts, and Vulkan SPIR-V binding guidance live in [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) — link up for syntax, layouts, and maintainability instead of restating them.

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

- **Route first** — use the Technique Routing Table below; load only the matching `references/<topic>.md` files.
- **One reference at a time** — progressive disclosure; do not load all 36 topics unless the task spans them.
- **Respect the performance budget** — see [references/performance-budget.md](references/performance-budget.md) before raising loop counts or FBM octaves.
- **Visual-debug before tuning** — substitute debug colors (normals, SDF bands, step heatmaps) per [references/shader-debugging.md](references/shader-debugging.md).
- **Neutral GLSL output** — templates use `uResolution`/`uTime`/`uFrame`; adapt bindings to the host API via [glsl-coding](../glsl-coding/SKILL.md) when integrating into OpenGL/Vulkan.
- **Validate references after edits** — run [scripts/validate_references.py](scripts/validate_references.py) on `references/` before reinstalling.

## Technique Routing Table

| User wants to create... | Primary technique | Combine with |
|---|---|---|
| 3D objects / scenes from math | [ray-marching](references/ray-marching.md) + [sdf-3d](references/sdf-3d.md) | lighting-model, shadow-techniques |
| Complex 3D shapes (booleans, blends) | [csg-boolean-operations](references/csg-boolean-operations.md) | sdf-3d, ray-marching |
| Infinite repeating patterns in 3D | [domain-repetition](references/domain-repetition.md) | sdf-3d, ray-marching |
| Organic / warped shapes | [domain-warping](references/domain-warping.md) | procedural-noise |
| Fluid / smoke / ink effects | [fluid-simulation](references/fluid-simulation.md) | multipass-buffer |
| Particle effects (fire, sparks, snow) | [particle-system](references/particle-system.md) | procedural-noise, color-palette |
| Physically-based simulations | [simulation-physics](references/simulation-physics.md) | multipass-buffer |
| Game of Life / reaction-diffusion | [cellular-automata](references/cellular-automata.md) | multipass-buffer, color-palette |
| Ocean / water surface | [water-ocean](references/water-ocean.md) | atmospheric-scattering, lighting-model |
| Terrain / landscape | [terrain-rendering](references/terrain-rendering.md) | atmospheric-scattering, procedural-noise |
| Clouds / fog / volumetric fire | [volumetric-rendering](references/volumetric-rendering.md) | procedural-noise, atmospheric-scattering |
| Sky / sunset / atmosphere | [atmospheric-scattering](references/atmospheric-scattering.md) | volumetric-rendering |
| Realistic lighting (PBR, Phong) | [lighting-model](references/lighting-model.md) | shadow-techniques, ambient-occlusion |
| Shadows (soft / hard) | [shadow-techniques](references/shadow-techniques.md) | lighting-model |
| Ambient occlusion | [ambient-occlusion](references/ambient-occlusion.md) | lighting-model, normal-estimation |
| Path tracing / global illumination | [path-tracing-gi](references/path-tracing-gi.md) | analytic-ray-tracing, multipass-buffer |
| Precise ray-geometry intersections | [analytic-ray-tracing](references/analytic-ray-tracing.md) | lighting-model |
| Voxel worlds (Minecraft-style) | [voxel-rendering](references/voxel-rendering.md) | lighting-model, shadow-techniques |
| Noise / FBM textures | [procedural-noise](references/procedural-noise.md) | domain-warping |
| Tiled 2D patterns | [procedural-2d-pattern](references/procedural-2d-pattern.md) | polar-uv-manipulation |
| Voronoi / cell patterns | [voronoi-cellular-noise](references/voronoi-cellular-noise.md) | color-palette |
| Fractals (Mandelbrot, Julia, 3D) | [fractal-rendering](references/fractal-rendering.md) | color-palette, polar-uv-manipulation |
| Color grading / palettes | [color-palette](references/color-palette.md) | — |
| Bloom / tone mapping / glitch | [post-processing](references/post-processing.md) | multipass-buffer |
| Multi-pass ping-pong buffers | [multipass-buffer](references/multipass-buffer.md) | — |
| Texture / sampling techniques | [texture-sampling](references/texture-sampling.md) | — |
| Camera / matrix transforms | [matrix-transform](references/matrix-transform.md) | — |
| Surface normals | [normal-estimation](references/normal-estimation.md) | — |
| Polar coords / kaleidoscope | [polar-uv-manipulation](references/polar-uv-manipulation.md) | procedural-2d-pattern |
| 2D shapes / UI from SDF | [sdf-2d](references/sdf-2d.md) | color-palette |
| Procedural audio / music | [sound-synthesis](references/sound-synthesis.md) | — |
| SDF tricks / optimization | [sdf-tricks](references/sdf-tricks.md) | sdf-3d, ray-marching |
| Anti-aliased rendering | [anti-aliasing](references/anti-aliasing.md) | sdf-2d, post-processing |
| Depth of field / motion blur / lens effects | [camera-effects](references/camera-effects.md) | post-processing, multipass-buffer |
| Advanced texture mapping / no-tile textures | [texture-mapping-advanced](references/texture-mapping-advanced.md) | terrain-rendering, texture-sampling |
| GLSL compilation / validation workflow | [../glsl-coding/SKILL.md](../glsl-coding/SKILL.md) | shader-best-practices |

## Technique Index

### Geometry & SDF
- **sdf-2d** — 2D signed distance functions for shapes, UI, anti-aliased rendering
- **sdf-3d** — 3D signed distance functions for real-time implicit surface modeling
- **csg-boolean-operations** — Constructive solid geometry: union, subtraction, intersection with smooth blending
- **domain-repetition** — Infinite space repetition, folding, and limited tiling
- **domain-warping** — Distort domains with noise for organic, flowing shapes
- **sdf-tricks** — SDF optimization, bounding volumes, binary search refinement, hollowing, layered edges, debug visualization

### Ray Casting & Lighting
- **ray-marching** — Sphere tracing with SDF for 3D scene rendering
- **analytic-ray-tracing** — Closed-form ray-primitive intersections (sphere, plane, box, torus)
- **path-tracing-gi** — Monte Carlo path tracing for photorealistic global illumination
- **lighting-model** — Phong, Blinn-Phong, PBR (Cook-Torrance), and toon shading
- **shadow-techniques** — Hard shadows, soft shadows (penumbra estimation), cascade shadows
- **ambient-occlusion** — SDF-based AO, screen-space AO approximation
- **normal-estimation** — Finite-difference normals, tetrahedron technique

### Simulation & Physics
- **fluid-simulation** — Navier-Stokes fluid solver with advection, diffusion, pressure projection
- **simulation-physics** — GPU-based physics: springs, cloth, N-body gravity, collision
- **particle-system** — Stateless and stateful particle systems (fire, rain, sparks, galaxies)
- **cellular-automata** — Game of Life, reaction-diffusion (Turing patterns), sand simulation

### Natural Phenomena
- **water-ocean** — Gerstner waves, FFT ocean, caustics, underwater fog
- **terrain-rendering** — Heightfield ray marching, FBM terrain, erosion
- **atmospheric-scattering** — Rayleigh/Mie scattering, god rays, SSS approximation
- **volumetric-rendering** — Volume ray marching for clouds, fog, fire, explosions

### Procedural Generation
- **procedural-noise** — Value noise, Perlin, Simplex, Worley, FBM, ridged noise
- **procedural-2d-pattern** — Brick, hexagon, truchet, Islamic geometric patterns
- **voronoi-cellular-noise** — Voronoi diagrams, Worley noise, cracked earth, crystal
- **fractal-rendering** — Mandelbrot, Julia sets, 3D fractals (Mandelbox, Mandelbulb)
- **color-palette** — Cosine palettes, HSL/HSV/Oklab, dynamic color mapping

### Post-Processing & Infrastructure
- **post-processing** — Bloom, tone mapping (ACES, Reinhard), vignette, chromatic aberration, glitch
- **multipass-buffer** — Ping-pong FBO setup, state persistence across frames
- **texture-sampling** — Bilinear, bicubic, mipmap, procedural texture lookup
- **matrix-transform** — Camera look-at, projection, rotation, orbit controls
- **polar-uv-manipulation** — Polar/log-polar coordinates, kaleidoscope, spiral mapping
- **anti-aliasing** — SSAA, SDF analytical AA, temporal anti-aliasing (TAA), FXAA post-process
- **camera-effects** — Depth of field (thin lens), motion blur, lens distortion, film grain, vignette
- **texture-mapping-advanced** — Biplanar mapping, texture repetition avoidance, ray differential filtering

### Audio
- **sound-synthesis** — Procedural audio in GLSL: oscillators, envelopes, filters, FM synthesis

### Debugging & Validation
- **shader-debugging** — Visual debug substitutions for SDF, normals, UV, and march cost
- **performance-budget** — Loop, octave, and nested-iteration limits for real-time effects

## Reference Routing

| Task | Read |
|------|------|
| Route any creative effect request | Technique Routing Table above |
| Full pipeline recipes (SDF scene, landscape, stylized 2D) | [references/effect-recipes.md](references/effect-recipes.md) |
| Visual debug colors for SDF, normals, UV, march cost | [references/shader-debugging.md](references/shader-debugging.md) |
| Loop/octave/nested-iteration limits | [references/performance-budget.md](references/performance-budget.md) |
| 3D implicit surfaces, CSG, domain ops | [references/sdf-3d.md](references/sdf-3d.md), [references/csg-boolean-operations.md](references/csg-boolean-operations.md) |
| Ray marching, normals, shadows, AO | [references/ray-marching.md](references/ray-marching.md), [references/normal-estimation.md](references/normal-estimation.md), [references/shadow-techniques.md](references/shadow-techniques.md), [references/ambient-occlusion.md](references/ambient-occlusion.md) |
| Lighting and atmosphere | [references/lighting-model.md](references/lighting-model.md), [references/atmospheric-scattering.md](references/atmospheric-scattering.md), [references/volumetric-rendering.md](references/volumetric-rendering.md) |
| Procedural noise and patterns | [references/procedural-noise.md](references/procedural-noise.md), [references/domain-warping.md](references/domain-warping.md), [references/voronoi-cellular-noise.md](references/voronoi-cellular-noise.md) |
| Simulation and multi-pass state | [references/fluid-simulation.md](references/fluid-simulation.md), [references/cellular-automata.md](references/cellular-automata.md), [references/multipass-buffer.md](references/multipass-buffer.md) |
| Post-processing and camera FX | [references/post-processing.md](references/post-processing.md), [references/camera-effects.md](references/camera-effects.md), [references/anti-aliasing.md](references/anti-aliasing.md) |
| Provenance from `skills-ref/shader-dev` | [references/source-map.md](references/source-map.md) |

## Gotchas

- **Function signature mismatch** — if `fbm(vec3 p)` is defined, do not call `fbm(uv)` with a `vec2`.
- **Terrain sampling** — height functions often need XZ: `terrainM(pos.xz + offset)`, not `terrainM(pos + offset)`.
- **Performance** — ray march ≤ 128 steps, volume inner loops ≤ 32, FBM ≤ 6 octaves; see [references/performance-budget.md](references/performance-budget.md).
- **GLSL syntax and compile rules** — see [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md).

## Effect Recipes

Complete rendering pipelines assembled from technique modules — see [references/effect-recipes.md](references/effect-recipes.md):

- Photorealistic SDF scene (geometry → march → lighting → atmosphere → post)
- Organic / biological forms (deformed SDF + noise warp + subsurface approx)
- Procedural landscape (terrain + biplanar texturing + sky + water)
- Stylized 2D art (2D SDF + palettes + kaleidoscope + bloom)

## Progressive Disclosure

- Read [references/effect-recipes.md](references/effect-recipes.md) — Load when assembling a multi-technique pipeline
- Read [references/shader-debugging.md](references/shader-debugging.md) — Load when output looks wrong and you need to isolate normals, SDF, UV, or march cost
- Read [references/performance-budget.md](references/performance-budget.md) — Load before increasing loop counts or FBM depth
- Read [references/ray-marching.md](references/ray-marching.md) — Load for sphere tracing, hit tests, and march loops
- Read [references/sdf-3d.md](references/sdf-3d.md) — Load for 3D primitives, booleans, and scene `map()`
- Read [references/lighting-model.md](references/lighting-model.md) — Load for Phong, PBR, toon, or outdoor lighting models
- Read [references/procedural-noise.md](references/procedural-noise.md) — Load for Perlin, Simplex, Worley, FBM, ridged noise
- Read [references/multipass-buffer.md](references/multipass-buffer.md) — Load for ping-pong simulation or persistent frame state
- Read [references/post-processing.md](references/post-processing.md) — Load for bloom, tone mapping, vignette, glitch
- Read [references/source-map.md](references/source-map.md) — Load to trace a reference back to original `skills-ref/shader-dev` provenance (bootstrap references are canonical)

## Companion Skills

| Task | Path |
|------|------|
| GLSL language, layouts, SPIR-V bindings, maintainability | [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) |
| Slang shader modules and slangc integration | [`../slang-dev/SKILL.md`](../slang-dev/SKILL.md) |
| Renderer architecture (render graph, bindless, sync) | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| Concrete Vulkan API (`Vk*`, pipelines, descriptors) | [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md) |

Relative paths resolve from `.shared/skills/shader-guide/` when installed (or `skills/shader-guide/` in bootstrap layout).
