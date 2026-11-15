# voronoi-cellular-noise: Voronoi and Cellular Noise

## Guideline

Voronoi noise = **spatial partitioning**: scatter feature points, assign each pixel to the "cell" of its nearest feature point.

## Rationale

Algorithm flow:
1. `floor` divides into an integer grid; each cell contains a randomly offset feature point
2. Search the 3x3 (2D) or 3x3x3 (3D) neighborhood for all feature points
3. Record the nearest distance F1 (optionally second-nearest F2)
4. Map F1, F2, or F2-F1 to color/height/shape

Distance metrics:
- Euclidean: `dot(r,r)` (squared, fast) -> final `sqrt`
- Manhattan: `abs(r.x)+abs(r.y)`
- Chebyshev: `max(abs(r.x), abs(r.y))`

Exact border distance (two-pass algorithm): `dot(0.5*(mr+r), normalize(r-mr))`
Rounded borders (harmonic mean): `1/(1/(d2-d1) + 1/(d3-d1))`

## How to Apply

1. **Step 1: Hash Functions** — Hash cell IDs to random feature-point offsets.
2. **Step 2: Basic F1 Voronoi** — Search 3×3 neighborhood and return distance to nearest feature point.
3. **Step 3: F1 + F2 (Edge Detection)** — Track second-nearest distance; `F2 - F1` highlights cell borders.
4. **Step 4: Exact Border Distance (Two-Pass Algorithm)** — Compute precise distance to Voronoi edges via neighbor midpoints.
5. **Step 5: Feature Point Animation** — Offset feature positions with `uTime` for flowing cellular motion.
6. **Step 6: Coloring & Visualization** — Map F1, F2-F1, or cell ID to color, height, or mask shapes.
## Example

```glsl
// sin-dot hash (suitable for most cases)
vec2 hash2(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)),
             dot(p, vec2(269.5, 183.3)));
    return fract(sin(p) * 43758.5453);
}

// 3D version
vec3 hash3(vec3 p) {
    float n = sin(dot(p, vec3(7.0, 157.0, 113.0)));
    return fract(vec3(2097152.0, 262144.0, 32768.0) * n);
}

// High-quality integer hash (ES 3.0+, more uniform)
vec3 hash3_uint(vec3 p) {
    uvec3 q = uvec3(ivec3(p)) * uvec3(1597334673U, 3812015801U, 2798796415U);
    q = (q.x ^ q.y ^ q.z) * uvec3(1597334673U, 3812015801U, 2798796415U);
    return vec3(q) / float(0xffffffffU);
}
```

```glsl
// Returns (F1 distance, cell ID)
vec2 voronoi(vec2 x) {
    vec2 n = floor(x);
    vec2 f = fract(x);
    vec3 m = vec3(8.0);

    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 g = vec2(float(i), float(j));
        vec2 o = hash2(n + g);
        vec2 r = g - f + o;
        float d = dot(r, r);
        if (d < m.x) {
            m = vec3(d, o);
        }
    }
    return vec2(sqrt(m.x), m.y + m.z);
}
```

```glsl
// Returns vec2(F1, F2), edge value = F2 - F1
vec2 voronoi_f1f2(vec2 x) {
    vec2 p = floor(x);
    vec2 f = fract(x);
    vec2 res = vec2(8.0);

    for (int j = -1; j <= 1; j++)
    for (int i = -1; i <= 1; i++) {
        vec2 b = vec2(i, j);
        vec2 r = b - f + hash2(p + b);
        float d = dot(r, r);
        if (d < res.x) {
            res.y = res.x;
            res.x = d;
        } else if (d < res.y) {
            res.y = d;
        }
    }
    return sqrt(res);
}
```

## Advanced

- **GLSL Basic Syntax**: `vec2/vec3`, `floor/fract`, `dot`, `smoothstep` and other built-in functions
- **Vector Math**: dot product, distance calculation, vector normalization
- **Pseudo-Random Hash Function Concepts**: input coordinates -> pseudo-random values, deterministic but appearing random
- **fBm (Fractional Brownian Motion) Basics**: multi-layer noise summation, used for advanced variants

## Gotchas

- Checking only nearest cell misses edge artifacts — include second-nearest for crack-free F1-F2 patterns.
- Cell jitter amplitude 1.0 can collapse cells — keep jitter below 0.5 for stable Voronoi partitions.
- Manhattan distance cells look axis-aligned — use Euclidean `length` for natural cell shapes.

## Combine With

- [color-palette](color-palette.md)
- [procedural-noise](procedural-noise.md)
