# effect-recipes: Multi-Technique Rendering Pipelines

## Guideline

Assemble complete visual effects by chaining techniques in a fixed order — geometry, march/trace, lighting, atmosphere, post — instead of improvising pass order each time.

## Rationale

Individual techniques (SDF primitives, soft shadows, FBM terrain) are written directly from model knowledge. Production-looking results come from predictable pipelines that reuse the same module boundaries: build implicit geometry, trace rays, estimate normals, apply direct lighting with shadows/AO, add atmosphere, then tone-map and anti-alias.

## Photorealistic SDF Scene

1. **Geometry** — 3D SDF primitives + CSG cubic/quartic `smin`
2. **Rendering** — sphere tracing + tetrahedron normal estimation
3. **Lighting** — outdoor three-light model + soft shadows + SDF AO
4. **Atmosphere** — height-based fog with sun tint
5. **Post** — ACES tone mapping + 2× SSAA + vignette

## Organic / Biological Forms

1. **Geometry** — SDF twist/bend deformations + gradient-aware `smin`
2. **Detail** — FBM with derivatives + domain warping
3. **Surface** — subsurface scattering approximation via half-Lambert

## Procedural Landscape

1. **Terrain** — heightfield ray marching + erosion FBM with derivatives
2. **Texturing** — biplanar mapping + no-tile sampling
3. **Sky** — Rayleigh/Mie scattering + height fog
4. **Water** — Gerstner waves + Fresnel reflections

## Stylized 2D Art

1. **Shapes** — 2D SDF library + [sdf-tricks](sdf-tricks.md) layered edges and hollowing
2. **Color** — cosine palettes + polar/kaleidoscope UV mapping
3. **Polish** — SDF analytical AA + bloom and chromatic aberration

## Gotchas

- Skipping normal estimation before lighting produces faceted or flickering shading on curved SDF surfaces.
- Adding atmosphere before shadows/AO are correct makes it hard to isolate lighting bugs — stabilize direct lighting first.
- Raising march steps for final polish before the SDF and camera are correct wastes GPU time — debug with [shader-debugging](shader-debugging.md) first.

## Combine With

- [shader-debugging](shader-debugging.md)
- [performance-budget](performance-budget.md)
