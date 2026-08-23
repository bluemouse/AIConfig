# procedural-noise: Procedural Noise

## Guideline

Build procedural textures from lattice hash functions, smooth interpolation (value or simplex noise), stacked FBM octaves, and optional domain warping.

## Rationale

Generate random values at integer lattice points, then smoothly interpolate between them.

- **Value Noise**: random scalars at lattice points + bilinear Hermite interpolation. `N(p) = mix(mix(h00,h10,u), mix(h01,h11,u), v)`
- **Simplex Noise**: triangular lattice gradient dot products + radial falloff kernel. Skew `K1=(sqrt(3)-1)/2`, unskew `K2=(3-sqrt(3))/6`. Fewer lattice lookups, no axis-aligned artifacts.

### Hash Functions

Map integer coordinates to pseudo-random values:

- **sin-based** (short but precision-sensitive): `fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453)`
- **sin-free** (cross-platform stable): `fract(p * 0.1031)` + dot mixing + fract

### FBM (Fractal Brownian Motion)

Multi-octave noise summation: `FBM(p) = sum of amplitude_i * noise(frequency_i * p)`

- Lacunarity ~2.0, Gain ~0.5, inter-octave rotation to eliminate artifacts

### Domain Warping

Feed noise output back as coordinate offset: `fbm(p + fbm(p))` or cascaded `fbm(p + fbm(p + fbm(p)))`

### FBM Variant Quick Reference

| Variant | Formula | Effect |
|---------|---------|--------|
| Standard | `sum a*noise(p)` | Soft clouds |
| Ridged | `sum a*abs(noise(p))` | Sharp ridges/lightning |
| Sinusoidal ridged | `sum a*sin(noise(p)*k)` | Periodic ridges/lava |
| Erosion | `sum a*noise(p)/(1+dot(d,d))` | Realistic terrain |
| Ocean waves | `sum a*sea_octave(p)` | Peaked wave crests |

## How to Apply

1. **Hash at lattice points** — Map integer cell coordinates to pseudo-random scalars or gradient vectors (sin-based or sin-free hash).
2. **Value noise** — Bilinear Hermite interpolation between four corner hashes for smooth scalar noise.
3. **Simplex noise** — Skew to triangular lattice, evaluate three corner gradients with radial falloff kernel.
4. **FBM stacking** — Sum scaled octaves (lacunarity ~2, gain ~0.5) with optional inter-octave rotation for decorrelation.
5. **Domain warp** — Offset input coordinates by FBM output (`fbm(p + fbm(p))`) for organic distortion.
6. **Variant selection** — Choose standard, ridged, erosion, or ocean-wave FBM variants from the quick-reference table for the target look.

## Example

```glsl
// Sin-free hash (Dave Hoskins) — cross-platform stable
float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * .1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

vec2 hash22(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * vec3(.1031, .1030, .0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx + p3.yz) * p3.zy);
}

// Sin hash — shorter code, precision-sensitive on some GPUs
float hash(vec2 p) {
    float h = dot(p, vec2(127.1, 311.7));
    return fract(sin(h) * 43758.5453123);
}

vec2 hash2(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)),
             dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}
```

```glsl
// Hermite smooth bilinear interpolation
float noise(in vec2 x) {
    vec2 p = floor(x);
    vec2 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(p + vec2(0.0, 0.0));
    float b = hash(p + vec2(1.0, 0.0));
    float c = hash(p + vec2(0.0, 1.0));
    float d = hash(p + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
```

```glsl
// 2D Simplex (skewed triangular grid + h^4 falloff kernel)
float noise(in vec2 p) {
    const float K1 = 0.366025404;  // (sqrt(3)-1)/2
    const float K2 = 0.211324865;  // (3-sqrt(3))/6
    vec2 i = floor(p + (p.x + p.y) * K1);
    vec2 a = p - i + (i.x + i.y) * K2;
    vec2 o = (a.x > a.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec2 b = a - o + K2;
    vec2 c = a - 1.0 + 2.0 * K2;
    vec3 h = max(0.5 - vec3(dot(a, a), dot(b, b), dot(c, c)), 0.0);
    vec3 n = h * h * h * h * vec3(
        dot(a, hash2(i + 0.0)),
        dot(b, hash2(i + o)),
        dot(c, hash2(i + 1.0))
    );
    return dot(n, vec3(70.0));
}
```

## Advanced

- **GLSL Basics**: uniform, varying, built-in functions (`fract`, `floor`, `mix`, `smoothstep`, `dot`, `sin`/`cos`)
- **Vector Math**: dot product, cross product, matrix multiplication (`mat2` rotation matrix)
- **Coordinate Spaces**: UV coordinate normalization, screen aspect ratio correction
- **Interpolation Theory**: linear interpolation, Hermite interpolation `3t^2-2t^3` (smoothstep)

## Gotchas

- Hash noise at single scale looks sparkly when animated — layer octaves with lacunarity and persistence.
- Periodic noise without prime lattice periods tiles visibly — offset each octave by coprime constants.
- Gradient noise without derivative correction in warp chains explodes — reduce warp gain per octave.

## Combine With

- [domain-warping](domain-warping.md)
- [terrain-rendering](terrain-rendering.md)
