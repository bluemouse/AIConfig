# shader-debugging: Visual Debug Techniques

## Guideline

Temporarily replace final color output with diagnostic visualizations — normals, SDF bands, UV checkers, march step heatmaps — to isolate which pipeline stage is wrong before tuning lighting or performance.

## Rationale

Creative shaders fail opaquely: a black screen may be a missed hit, inverted normal, wrong UV scale, or an optimized-away uniform. Substituting a single debug channel localizes the fault without rewriting the whole effect.

## Visual Debug Substitutions

| What to check | Code | What to look for |
|---|---|---|
| Surface normals | `col = nor * 0.5 + 0.5;` | Smooth gradients = correct normals; banding = epsilon too large |
| Ray march step count | `col = vec3(float(steps) / float(MAX_STEPS));` | Red hotspots = performance bottleneck; uniform = wasted iterations |
| Depth / distance | `col = vec3(t / MAX_DIST);` | Verify correct hit distances |
| UV coordinates | `col = vec3(uv, 0.0);` | Check coordinate mapping |
| SDF distance field | `col = (d > 0.0 ? vec3(0.9,0.6,0.3) : vec3(0.4,0.7,0.85)) * (0.8 + 0.2*cos(150.0*d));` | Visualize SDF bands and zero-crossing |
| Checker pattern (UV) | `col = vec3(mod(floor(uv.x*10.)+floor(uv.y*10.), 2.0));` | Verify UV distortion, seams |
| Lighting only | `col = vec3(shadow);` or `col = vec3(ao);` | Isolate shadow/AO contributions |
| Material ID | `col = palette(matId / maxMatId);` | Verify material assignment |

## How to Apply

1. Reproduce the failure with the smallest shader (single primitive or flat UV).
2. Swap output for one row in the visual debug table.
3. Fix the stage that looks wrong (SDF, normals, UV, march budget).
4. Re-enable lighting one contribution at a time (diffuse → specular → shadow → AO → fog).
5. For compile/link or SPIR-V validation, defer to [`../../glsl-coding/SKILL.md`](../../glsl-coding/SKILL.md).

## Gotchas

- Debug colors left in `main()` silently ship to production — gate with a `const bool DEBUG = false` or compile-time define.
- Visualizing raw SDF distance without aspect-correct UVs can mislead about world-space scale.
- Heatmapping march steps on an empty miss scene shows uniform low values — confirm geometry hits first.

## Combine With

- [performance-budget](performance-budget.md)
- [sdf-tricks](sdf-tricks.md)
