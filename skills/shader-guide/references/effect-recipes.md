# effect-recipes: Multi-Technique Rendering Pipelines

## Guideline

Assemble complete visual effects by chaining technique references in a fixed order — geometry, march/trace, lighting, atmosphere, post — instead of improvising pass order each time.

## Rationale

Individual technique references cover one concern well (SDF primitives, soft shadows, FBM terrain). Production-looking results come from predictable pipelines that reuse the same module boundaries: build implicit geometry, trace rays, estimate normals, apply direct lighting with shadows/AO, add atmosphere, then tone-map and anti-alias.

## Photorealistic SDF Scene

1. **Geometry** — [sdf-3d](sdf-3d.md) extended primitives + [csg-boolean-operations](csg-boolean-operations.md) cubic/quartic `smin`
2. **Rendering** — [ray-marching](ray-marching.md) + [normal-estimation](normal-estimation.md) tetrahedron method
3. **Lighting** — [lighting-model](lighting-model.md) outdoor three-light model + [shadow-techniques](shadow-techniques.md) soft shadow + [ambient-occlusion](ambient-occlusion.md)
4. **Atmosphere** — [atmospheric-scattering](atmospheric-scattering.md) height-based fog with sun tint
5. **Post** — [post-processing](post-processing.md) ACES tone mapping + [anti-aliasing](anti-aliasing.md) 2× SSAA + [camera-effects](camera-effects.md) vignette

## Organic / Biological Forms

1. **Geometry** — [sdf-3d](sdf-3d.md) twist/bend deformations + [csg-boolean-operations](csg-boolean-operations.md) gradient-aware `smin`
2. **Detail** — [procedural-noise](procedural-noise.md) FBM with derivatives + [domain-warping](domain-warping.md)
3. **Surface** — [lighting-model](lighting-model.md) subsurface scattering approximation via half-Lambert

## Procedural Landscape

1. **Terrain** — [terrain-rendering](terrain-rendering.md) + [procedural-noise](procedural-noise.md) erosion FBM with derivatives
2. **Texturing** — [texture-mapping-advanced](texture-mapping-advanced.md) biplanar mapping + no-tile sampling
3. **Sky** — [atmospheric-scattering](atmospheric-scattering.md) Rayleigh/Mie + height fog
4. **Water** — [water-ocean](water-ocean.md) Gerstner waves + [lighting-model](lighting-model.md) Fresnel reflections

## Stylized 2D Art

1. **Shapes** — [sdf-2d](sdf-2d.md) extended library + [sdf-tricks](sdf-tricks.md) layered edges and hollowing
2. **Color** — [color-palette](color-palette.md) cosine palettes + [polar-uv-manipulation](polar-uv-manipulation.md) kaleidoscope
3. **Polish** — [anti-aliasing](anti-aliasing.md) SDF analytical AA + [post-processing](post-processing.md) bloom and chromatic aberration

## Gotchas

- Skipping normal estimation before lighting produces faceted or flickering shading on curved SDF surfaces.
- Adding atmosphere before shadows/AO are correct makes it hard to isolate lighting bugs — stabilize direct lighting first.
- Raising march steps for final polish before the SDF and camera are correct wastes GPU time — debug with [shader-debugging](shader-debugging.md) first.

## Combine With

- [shader-debugging](shader-debugging.md)
- [performance-budget](performance-budget.md)
