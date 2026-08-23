# color-palette: Color Palettes

## Guideline

Core: **map a scalar t in [0,1] to an RGB vec3**.

## Rationale


### Cosine Palette
```
color(t) = a + b * cos(2pi * (c * t + d))
```
- **a** = brightness offset (~0.5), **b** = amplitude (~0.5), **c** = frequency, **d** = phase (the key parameter controlling color style)

### HSV/HSL Branchless Conversion
```
rgb = clamp(abs(mod(H*6 + vec3(0,4,2), 6) - 3) - 1, 0, 1)
```
Uses piecewise linear functions to approximate RGB variation with hue. C1 continuity can be achieved via `rgb*rgb*(3-2*rgb)`.

### CIE Lab/Lch Perceptually Uniform Interpolation
RGB -> XYZ -> Lab -> Lch pipeline; interpolate in perceptually uniform space to avoid brightness discontinuities in RGB/HSV.

### Blackbody Radiation Palette
Temperature T -> Planckian locus approximation -> CIE chromaticity -> XYZ -> RGB, with Stefan-Boltzmann (T^4) controlling brightness.

## How to Apply

1. **Normalize scalar** — Map effect parameter (distance, density, height) into `[0,1]`.
2. **Cosine palette** — Apply `a + b * cos(TAU * (c * t + d))`; tune `d` phase for hue style.
3. **HSL/Oklab remap** — Convert when perceptually uniform hue shifts are required.
4. **Range adjust** — Clamp or tone-map before final composite.

## Example

```glsl
// a: offset, b: amplitude, c: frequency, d: phase, t: input scalar
vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d) {
    return a + b * cos(6.28318 * (c * t + d));
}
```

```glsl
// Rainbow: d=(0.0, 0.33, 0.67)
// Warm: d=(0.0, 0.10, 0.20)
// Blue-purple to orange: c=(1,0.7,0.4) d=(0.0, 0.15, 0.20)
// Warm-cool mix: a=(.8,.5,.4) b=(.2,.4,.2) c=(2,1,1) d=(0.0, 0.25, 0.25)

// Simplified version: fixed a/b/c, only adjust d
vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.263, 0.416, 0.557);
    return a + b * cos(6.28318 * (c * t + d));
}
```

```glsl
// Standard HSV -> RGB (branchless)
vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    return c.z * mix(vec3(1.0), rgb, c.y);
}

// Smooth version (C1 continuous)
vec3 hsv2rgb_smooth(vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    rgb = rgb * rgb * (3.0 - 2.0 * rgb); // Hermite smoothing
    return c.z * mix(vec3(1.0), rgb, c.y);
}
```

## Advanced

- GLSL basic syntax: `vec3`, `mix`, `clamp`, `smoothstep`, `fract`, `mod`
- Basic properties of trigonometric functions `cos`/`sin` (periodicity, range [-1, 1])
- Color space fundamentals: RGB is a cube, HSV/HSL is cylindrical coordinates, Lab/Lch is a perceptually uniform space
- Gamma correction concept: monitors store sRGB (nonlinear), shading computations should be performed in linear space

## Gotchas

- Cosine palette without input clamping saturates on HDR values — clamp or tone-map palette index to [0,1].
- Single palette for shadows and highlights reduces contrast — remap index with `pow(t, gamma)` per region.
- Phase offset in radians vs normalized `t` mismatches — document whether palette input is [0,1] or angle.

## Combine With

- [post-processing](post-processing.md)
