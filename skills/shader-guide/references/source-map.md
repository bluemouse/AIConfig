# source-map: Provenance from skills-ref/shader-dev

Each `references/<topic>.md` file was migrated from the uncommitted `skills-ref/shader-dev/` tree. **Bootstrap paths under `skills/shader-guide/references/` are canonical** — edit them directly; there is no bundled regen script.

> **2026-11-15 prune:** the encyclopedic technique walkthroughs were removed — frontier models write canonical ray marching, SDF, FBM, shadow, and pattern techniques fluently without them. Only `effect-recipes`, `multipass-buffer`, `performance-budget`, `sdf-tricks`, `shader-debugging`, and `source-map` remain as files.

## Neutralization Changes

| Original | Neutral |
|---|---|
| `iResolution` | `uResolution` |
| `iTime` | `uTime` |
| `iFrame` | `uFrame` |
| `iMouse` | `uMouse` |
| `fragCoord` | `gl_FragCoord.xy` |

`mainImage` wrappers were removed; standard `void main()` is assumed. ShaderToy/WebGL host setup and the `webgl-pitfalls` topic were dropped; relevant GLSL rules live in [shader-debugging](shader-debugging.md).
