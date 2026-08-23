# post-processing: Post-Processing

## Guideline

The essence of post-processing is **per-pixel transformation of an already-rendered image** — input is a framebuffer texture, output is the transformed color value.

## Rationale

- **Tone Mapping**: HDR [0, ∞) → LDR [0, 1]. Reinhard `c/(1+c)`, Filmic Reinhard (white point/shoulder parameters), ACES (3×3 matrix + rational polynomial), generic rational polynomial
- **Gaussian Blur**: 2D Gaussian kernel is separable into two 1D passes, O(n²) → O(2n)
- **Bloom**: Bright-pass extraction → multi-level Gaussian blur → additive blend back to original
- **Vignette**: Brightness falloff based on pixel distance to center. Multiplicative or radial
- **Chromatic Aberration**: Sample the same texture at different scales for R/G/B channels

## How to Apply

1. **Tone mapping** — Map HDR scene radiance to display range using Reinhard, Filmic Reinhard, or ACES before any LDR-only effects.
2. **Gamma correction** — Apply `pow(color, 1/2.2)` only when the tone mapper does not already encode display gamma (ACES includes gamma; skip this step after ACES).
3. **Contrast enhancement** — Shape midtones with a Hermite S-curve or similar shoulder/toe curve after tone mapping.
4. **Color grading** — Tint the image with per-channel multipliers or a LUT-style color transform.
5. **Vignette** — Darken pixels toward the frame edges with radial distance from center.
6. **Gaussian blur** — Run separable horizontal and vertical passes with a 1D Gaussian kernel.
7. **Bloom** — Extract bright regions, blur across a mip pyramid, and additively recomposite over the base image.
8. **Chromatic aberration** — Offset R/G/B sample UVs radially from the image center to simulate lens dispersion.
9. **Film grain** — Modulate luma with high-frequency noise for a photographic texture.
10. **Input texture** — The post chain requires a valid color input; without one the output is solid black.
11. **Motion blur** — Smear samples along a velocity buffer to approximate camera or object motion.
12. **Depth of field** — Blur samples by depth relative to a focal distance to simulate aperture.
13. **FXAA** — Apply edge-directed luma smoothing as a final anti-aliasing pass.

## Example

```glsl
// Reinhard
vec3 reinhard(vec3 color) { return color / (1.0 + color); }

// Filmic Reinhard (W=white point, T2=shoulder parameter)
// IMPORTANT: GLSL critical rule: function parameters must be defined before use; using a variable name in its own initializer is forbidden
const float W = 1.2, T2 = 7.5; // adjustable
float filmic_reinhard_curve(float x) {
    float q = (T2 * T2 + 1.0) * x * x;
    return q / (q + x + T2 * T2);
}
vec3 filmic_reinhard(vec3 x) {
    float w = filmic_reinhard_curve(W);  // compute w using constant W first
    return vec3(filmic_reinhard_curve(x.r), filmic_reinhard_curve(x.g), filmic_reinhard_curve(x.b)) / w;
}

// ACES industry standard
vec3 aces_tonemap(vec3 color) {
    mat3 m1 = mat3(0.59719,0.07600,0.02840, 0.35458,0.90834,0.13383, 0.04823,0.01566,0.83777);
    mat3 m2 = mat3(1.60475,-0.10208,-0.00327, -0.53108,1.10813,-0.07276, -0.07367,-0.00605,1.07602);
    vec3 v = m1 * color;
    vec3 a = v * (v + 0.0245786) - 0.000090537;
    vec3 b = v * (0.983729 * v + 0.4329510) + 0.238081;
    return clamp(m2 * (a / b), 0.0, 1.0);
}

// Generic rational polynomial
vec3 rational_tonemap(vec3 x) {
    float a=0.010, b=0.132, c=0.010, d=0.163, e=0.101; // adjustable
    return (x * (a * x + b)) / (x * (c * x + d) + e);
}
```

```glsl
color = pow(color, vec3(1.0 / 2.2)); // after tone mapping; ACES already includes gamma, skip this step
```

```glsl
color = clamp(color, 0.0, 1.0);
color = color * color * (3.0 - 2.0 * color);
// Controllable intensity: color = mix(color, color*color*(3.0-2.0*color), strength);
// smoothstep equivalent: color = smoothstep(-0.025, 1.0, color);
```

## Advanced

- **GLSL fundamentals**: basic vector and matrix operations for per-pixel color transforms.
- **Linear vs gamma color space**: tone mapping and gamma correction apply in different spaces — know which your chain uses.
- **Texture sampling and UV conventions**: post chains read prior-pass framebuffers via normalized UVs.
- **Convolution basics**: kernel size, weights, and normalization for blur and bloom passes.
- **Multi-pass roles**: simulation/update passes feed the final Image pass — see [multipass-buffer](multipass-buffer.md) for ping-pong setup.

## Gotchas

- Bloom before tone mapping blows out fireflies — extract bright pass after HDR clamp or knee.
- Gamma correction applied twice (ACES + manual) washes contrast — skip gamma when tone mapper already encodes it.
- Blur passes without padding sample black borders — use clamp-to-edge or shrink UVs by kernel radius.

## Combine With

- [multipass-buffer](multipass-buffer.md)
- [anti-aliasing](anti-aliasing.md)
