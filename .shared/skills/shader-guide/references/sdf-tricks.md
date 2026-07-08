# sdf-tricks: SDF Tricks and Optimization

## Guideline

Optimize and extend SDF scenes with bounding culls, hollow shells, binary refinement, and debug views without adding mesh complexity.

## Rationale

- Adding fine detail to SDF surfaces without increasing geometric complexity
- Creating special effects with SDF manipulation (hollowing, layered edges, interior structures)
- Debugging and visualizing SDF fields

## How to Apply

1. **Bounding volume cull** — Skip expensive `map()` when coarse bound SDF exceeds march budget.
2. **Hollow / shell** — Use `abs(d) - thickness` for thin walls and interior structures.
3. **Binary search refine** — Bisect last march segment for tighter surface hits.
4. **Debug visualization** — Color by distance bands, iteration count, or material ID.

## Example

```glsl
float hollowed = abs(sdf) - thickness;
// Example: hollow sphere with 0.02 wall thickness
float d = abs(sdSphere(p, 1.0)) - 0.02;
```

```glsl
float spacing = 0.2;
float thickness = 0.02;
float layered = abs(mod(d + spacing * 0.5, spacing) - spacing * 0.5) - thickness;
```

```glsl
float map(vec3 p) {
    float d = sdBasicShape(p);
    // Only add expensive FBM detail when close to surface
    if (d < 1.0) {
        d += 0.02 * fbm(p * 8.0) * smoothstep(1.0, 0.0, d);
    }
    return d;
}
```

## Advanced

### Step 1: Bounding Volume Cull

**What**: Skip full `map()` when a cheap bound SDF exceeds the march distance budget.

**Why**: Avoids evaluating expensive FBM or detail far from the surface where a coarse bound already proves a miss.

```glsl
float bound = sdSphere(p - center, radius);
if (bound > maxDist) return maxDist;
float d = map(p);  // expensive detail only when close
```

### Step 2: Hollow / Shell SDF

**What**: Use `abs(d) - thickness` to turn solid primitives into thin walls or layered shells.

**Why**: Creates interior structures and edge highlights without adding mesh geometry.

```glsl
float d = abs(sdSphere(p, 1.0)) - 0.02;  // 0.02 wall thickness
```

### Step 3: Binary Search Refine

**What**: After ray march bracketing, bisect the last segment to tighten the surface hit.

**Why**: Fixed-step or coarse sphere tracing can overshoot; bisection lands closer to the zero isosurface.

```glsl
float t0 = t - lastStep, t1 = t;
for (int i = 0; i < 8; i++) {
    float tm = 0.5 * (t0 + t1);
    float d = map(ro + rd * tm);
    if (d > 0.0) t0 = tm; else t1 = tm;
}
t = 0.5 * (t0 + t1);
```

### Step 4: Debug Visualization

**What**: Color by distance bands, march iteration count, or material ID to isolate bugs.

**Why**: Visual substitution localizes whether errors are in the SDF, march budget, or shading composite.

```glsl
fragColor = vec4(vec3(float(i) / float(MAX_STEPS)), 1.0);  // step heatmap
```

## Gotchas

- Cheap SDF approximations (boxes for rounded shapes) drift from true distance — normals and AO become inaccurate.
- Onion / shell operations double-hit thin geometry — reduce shell thickness below march precision.
- Twist and bend warps distort distance non-uniformly — increase march steps after strong domain warps.

## Combine With

- [sdf-3d](sdf-3d.md)
- [ray-marching](ray-marching.md)
