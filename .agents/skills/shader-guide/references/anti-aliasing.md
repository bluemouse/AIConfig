# anti-aliasing: Anti-Aliasing

## Guideline

Anti-aliasing in shaders differs from rasterization pipelines. Without hardware MSAA on procedural geometry, we rely on analytical or post-process approaches.

## Rationale

- **SSAA**: brute-force subpixel supersampling in the fragment shader when hardware MSAA is unavailable.
- **Analytical SDF AA**: `fwidth(d)` gives one-pixel edge width without extra rays.
- **Temporal AA**: blend current frame with history buffer — see [multipass-buffer](multipass-buffer.md).

## How to Apply

1. **SSAA subpixel loop** — Nest `AA×AA` offset loops, jitter `gl_FragCoord.xy`, average `render(uv)` results.
2. **Analytical SDF AA** — Use `fwidth(d)` or manual pixel width with `smoothstep(fw, -fw, d)` on signed distance.
3. **Distance-scaled edge fade** — After ray marching, fade edges with `smoothstep` scaled by hit distance `t` for consistent width.
4. **Temporal AA (optional)** — Accumulate frames in a ping-pong history buffer per [multipass-buffer](multipass-buffer.md).

## Example

```glsl
#define AA 2  // 1=off, 2=4x, 3=9x
void main() {
    vec3 totalColor = vec3(0.0);
    for (int m = 0; m < AA; m++)
    for (int n = 0; n < AA; n++) {
        vec2 offset = vec2(float(m), float(n)) / float(AA) - 0.5;
        vec2 uv = (2.0 * (gl_FragCoord.xy + offset) - uResolution.xy) / uResolution.y;
        vec3 col = render(uv);
        totalColor += col;
    }
    fragColor = vec4(totalColor / float(AA * AA), 1.0);
}
```

```glsl
float d = sdShape(uv);
float fw = fwidth(d);  // screen-space derivative of SDF
float alpha = smoothstep(fw, -fw, d);  // smooth edge over exactly 1 pixel

// Alternative: manual pixel width for more control
float pixelWidth = 2.0 / uResolution.y;  // approximate pixel size in UV space
float alpha2 = smoothstep(pixelWidth, -pixelWidth, d);
```

```glsl
// After ray marching, at the surface:
float edgeFade = 1.0 - smoothstep(0.0, 0.01 * t, lastSdfValue);
// t = ray distance — scales threshold with distance for consistent edge width
```

## Advanced

- Understanding of screen-space derivatives (`dFdx`, `dFdy`, `fwidth`)
- Multipass buffer setup (for TAA)
- Basic signal processing concepts

## Gotchas

- FXAA on high-contrast HDR bloom edges smears energy — tone-map before FXAA or use luma-only edge detection.
- MSAA does not help shader-generated edges inside a full-screen quad — use analytic `fwidth` AA on procedural boundaries.
- Supersampling without jitter still aliases animated noise — add temporal offset or interleaved gradient noise.

## Combine With

- [sdf-2d](sdf-2d.md)
- [post-processing](post-processing.md)
