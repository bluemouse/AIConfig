# source-map: Provenance from skills-ref/shader-dev

## Guideline

Each `references/<topic>.md` file was migrated from `skills-ref/shader-dev/` and restructured to bootstrap conventions. **Bootstrap paths under `skills/shader-guide/references/` are canonical** — edit them directly. The `skills-ref/shader-dev/` tree is not committed; restore it locally only when re-deriving from the original dual-tree source.

## Rationale

The original reference lived under `skills-ref/shader-dev/techniques/` (implementation templates) and `skills-ref/shader-dev/reference/` (extended theory). This skill merges those layers into a single flat `references/` tree. `webgl-pitfalls` was not migrated as a standalone topic; relevant GLSL rules were folded into [shader-debugging](shader-debugging.md).

## Topic Map

| Reference | techniques/ source | reference/ source |
|---|---|---|
| ambient-occlusion | `skills-ref/shader-dev/techniques/ambient-occlusion.md` | `skills-ref/shader-dev/reference/ambient-occlusion.md` |
| analytic-ray-tracing | `skills-ref/shader-dev/techniques/analytic-ray-tracing.md` | `skills-ref/shader-dev/reference/analytic-ray-tracing.md` |
| anti-aliasing | `skills-ref/shader-dev/techniques/anti-aliasing.md` | `skills-ref/shader-dev/reference/anti-aliasing.md` |
| atmospheric-scattering | `skills-ref/shader-dev/techniques/atmospheric-scattering.md` | `skills-ref/shader-dev/reference/atmospheric-scattering.md` |
| camera-effects | `skills-ref/shader-dev/techniques/camera-effects.md` | `skills-ref/shader-dev/reference/camera-effects.md` |
| cellular-automata | `skills-ref/shader-dev/techniques/cellular-automata.md` | `skills-ref/shader-dev/reference/cellular-automata.md` |
| color-palette | `skills-ref/shader-dev/techniques/color-palette.md` | `skills-ref/shader-dev/reference/color-palette.md` |
| csg-boolean-operations | `skills-ref/shader-dev/techniques/csg-boolean-operations.md` | `skills-ref/shader-dev/reference/csg-boolean-operations.md` |
| domain-repetition | `skills-ref/shader-dev/techniques/domain-repetition.md` | `skills-ref/shader-dev/reference/domain-repetition.md` |
| domain-warping | `skills-ref/shader-dev/techniques/domain-warping.md` | `skills-ref/shader-dev/reference/domain-warping.md` |
| fluid-simulation | `skills-ref/shader-dev/techniques/fluid-simulation.md` | `skills-ref/shader-dev/reference/fluid-simulation.md` |
| fractal-rendering | `skills-ref/shader-dev/techniques/fractal-rendering.md` | `skills-ref/shader-dev/reference/fractal-rendering.md` |
| lighting-model | `skills-ref/shader-dev/techniques/lighting-model.md` | `skills-ref/shader-dev/reference/lighting-model.md` |
| matrix-transform | `skills-ref/shader-dev/techniques/matrix-transform.md` | `skills-ref/shader-dev/reference/matrix-transform.md` |
| multipass-buffer | `skills-ref/shader-dev/techniques/multipass-buffer.md` | `skills-ref/shader-dev/reference/multipass-buffer.md` |
| normal-estimation | `skills-ref/shader-dev/techniques/normal-estimation.md` | `skills-ref/shader-dev/reference/normal-estimation.md` |
| particle-system | `skills-ref/shader-dev/techniques/particle-system.md` | `skills-ref/shader-dev/reference/particle-system.md` |
| path-tracing-gi | `skills-ref/shader-dev/techniques/path-tracing-gi.md` | `skills-ref/shader-dev/reference/path-tracing-gi.md` |
| polar-uv-manipulation | `skills-ref/shader-dev/techniques/polar-uv-manipulation.md` | `skills-ref/shader-dev/reference/polar-uv-manipulation.md` |
| post-processing | `skills-ref/shader-dev/techniques/post-processing.md` | `skills-ref/shader-dev/reference/post-processing.md` |
| procedural-2d-pattern | `skills-ref/shader-dev/techniques/procedural-2d-pattern.md` | `skills-ref/shader-dev/reference/procedural-2d-pattern.md` |
| procedural-noise | `skills-ref/shader-dev/techniques/procedural-noise.md` | `skills-ref/shader-dev/reference/procedural-noise.md` |
| ray-marching | `skills-ref/shader-dev/techniques/ray-marching.md` | `skills-ref/shader-dev/reference/ray-marching.md` |
| sdf-2d | `skills-ref/shader-dev/techniques/sdf-2d.md` | `skills-ref/shader-dev/reference/sdf-2d.md` |
| sdf-3d | `skills-ref/shader-dev/techniques/sdf-3d.md` | `skills-ref/shader-dev/reference/sdf-3d.md` |
| sdf-tricks | `skills-ref/shader-dev/techniques/sdf-tricks.md` | `skills-ref/shader-dev/reference/sdf-tricks.md` |
| shadow-techniques | `skills-ref/shader-dev/techniques/shadow-techniques.md` | `skills-ref/shader-dev/reference/shadow-techniques.md` |
| simulation-physics | `skills-ref/shader-dev/techniques/simulation-physics.md` | `skills-ref/shader-dev/reference/simulation-physics.md` |
| sound-synthesis | `skills-ref/shader-dev/techniques/sound-synthesis.md` | `skills-ref/shader-dev/reference/sound-synthesis.md` |
| terrain-rendering | `skills-ref/shader-dev/techniques/terrain-rendering.md` | `skills-ref/shader-dev/reference/terrain-rendering.md` |
| texture-mapping-advanced | `skills-ref/shader-dev/techniques/texture-mapping-advanced.md` | `skills-ref/shader-dev/reference/texture-mapping-advanced.md` |
| texture-sampling | `skills-ref/shader-dev/techniques/texture-sampling.md` | `skills-ref/shader-dev/reference/texture-sampling.md` |
| volumetric-rendering | `skills-ref/shader-dev/techniques/volumetric-rendering.md` | `skills-ref/shader-dev/reference/volumetric-rendering.md` |
| voronoi-cellular-noise | `skills-ref/shader-dev/techniques/voronoi-cellular-noise.md` | `skills-ref/shader-dev/reference/voronoi-cellular-noise.md` |
| voxel-rendering | `skills-ref/shader-dev/techniques/voxel-rendering.md` | `skills-ref/shader-dev/reference/voxel-rendering.md` |
| water-ocean | `skills-ref/shader-dev/techniques/water-ocean.md` | `skills-ref/shader-dev/reference/water-ocean.md` |

## Meta References (authored for bootstrap)

| Reference | Origin |
|---|---|
| effect-recipes.md | `skills-ref/shader-dev/SKILL.md` Quick Recipes section |
| shader-debugging.md | `skills-ref/shader-dev/SKILL.md` debugging + GLSL pitfalls (excluding WebGL host) |
| performance-budget.md | `skills-ref/shader-dev/SKILL.md` Performance Budget section |
| source-map.md | this file |

## Neutralization Changes

References were migrated from `skills-ref/shader-dev/` and restructured to bootstrap conventions with neutral GLSL uniforms. Edit bootstrap references under `skills/shader-guide/references/` directly — there is no bundled regen script.

- `iResolution` → `uResolution`, `iTime` → `uTime`, `iFrame` → `uFrame`, `iMouse` → `uMouse`
- `fragCoord` → `gl_FragCoord.xy`
- `mainImage` wrappers removed; standard `void main()` assumed
- ShaderToy/WebGL host setup and `webgl-pitfalls` topic dropped

## Combine With

- [shader-debugging](shader-debugging.md)
