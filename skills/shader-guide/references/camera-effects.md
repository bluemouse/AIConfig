# camera-effects: Camera Effects

## Guideline

Add cinematic depth of field, motion blur, lens distortion, and film grain as post passes on rendered color/depth buffers.

## Rationale

- Motion blur for dynamic scenes
- Lens distortion and chromatic aberration
- Film grain and photographic realism

## How to Apply

1. **Depth / CoC pass** — Derive circle of confusion from ray-hit distance vs focal plane.
2. **Bokeh gather** — Sample random aperture disk offsets; accumulate defocused color.
3. **Motion blur** — Blend along velocity vector from previous-frame position buffer.
4. **Lens distortion and vignette** — Apply radial UV warp, chromatic split, and edge falloff.

## Example

```glsl
// For each sample:
vec2 lens = randomDisk(seed) * apertureSize;  // random point on aperture
vec3 focalPoint = ro + rd * focalDistance;     // point on focal plane
vec3 newRo = ro + cameraRight * lens.x + cameraUp * lens.y;  // offset origin
vec3 newRd = normalize(focalPoint - newRo);   // new ray toward focal point

// Accumulate multiple samples (16-64) for smooth bokeh
// Use with AA loop or temporal accumulation

// Disk sampling helper:
vec2 randomDisk(float seed) {
    float angle = hash11(seed) * 6.2831853;
    float radius = sqrt(hash11(seed + 1.0));
    return vec2(cos(angle), sin(angle)) * radius;
}
```

```glsl
vec3 dofPostProcess(sampler2D colorTex, sampler2D depthTex, vec2 uv) {
    float depth = texture(depthTex, uv).r;
    float coc = abs(depth - focalDepth) * apertureSize;  // circle of confusion
    coc = clamp(coc, 0.0, maxBlur);

    vec3 color = vec3(0.0);
    float total = 0.0;
    // 16-tap Poisson disk sampling
    for (int i = 0; i < 16; i++) {
        vec2 offset = poissonDisk[i] * coc / uResolution.xy;
        color += texture(colorTex, uv + offset).rgb;
        total += 1.0;
    }
    return color / total;
}
```

```glsl
// Simple radial motion blur (camera rotation)
vec3 motionBlur(vec2 uv, float amount) {
    vec3 color = vec3(0.0);
    vec2 center = vec2(0.5);
    int samples = 8;
    for (int i = 0; i < samples; i++) {
        float t = float(i) / float(samples - 1) - 0.5;
        vec2 sampleUV = mix(uv, center, t * amount);
        color += texture(uChannel0, sampleUV).rgb;
    }
    return color / float(samples);
}

// Time-based motion blur for ray marching
// Sample multiple time offsets within the frame:
// float t_shutter = uTime + (hash11(seed) - 0.5) * shutterSpeed;
// Use t_shutter instead of uTime for scene animation
```

## Advanced

- Ray marching fundamentals (ray origin, ray direction)
- Multipass buffers (for accumulation-based DoF)
- Hash functions for stochastic sampling

## Gotchas

- DOF blur without depth linearization focuses at wrong distance — convert hyperbolic depth to view-space Z first.
- Motion blur from single velocity sample streaks wrong on rotation — integrate multiple temporal samples.
- Lens distortion applied after vignette shifts dark corners — apply distortion before radial grading effects.

## Combine With

- [post-processing](post-processing.md)
- [multipass-buffer](multipass-buffer.md)
