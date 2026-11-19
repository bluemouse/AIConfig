# multipass-buffer: Multi-Pass Ping-Pong Framebuffers

## Guideline
Split simulation or post work across ping-pong framebuffers so each pass reads the previous pass output (or its own prior frame) via `sampler2D`/`texelFetch`.

**Uniform naming:** prose uses `uPrevPass` for prior-frame self-feedback; examples use `uChannel0`/`uChannel1` as concrete sampler bindings for the same roles.

## Rationale

Multi-pass rendering splits work across ping-pong framebuffers: each pass outputs a texture consumed by the next stage or by its own next frame.

### Self-Feedback
A Buffer reads its own previous frame output, achieving cross-frame state persistence: `x(n+1) = f(x(n))`
```
passA (frame N) reads → passA (frame N-1) output
```

### Pipeline Chaining
Multiple Buffers process in sequence:
```
passA (geometry) → passB (blur H) → passC (blur V) → Image (compositing)
```

### Structured Data Storage
Specific pixels serve as data registers, read precisely via `texelFetch`:
```
texel (0,0) = ball position+velocity (vec4)
texel (1,0) = paddle position
texel (x,1)-(x,12) = brick grid state
```

### Key Mathematical Patterns

- **Fluid self-advection**: `newPos = texture(buf, uv - dt * velocity * texelSize)`
- **Gaussian blur**: `sum += texture(buf, uv + offset_i) * weight_i`
- **Temporal blending**: `result = mix(newFrame, prevFrame, blendWeight)`
- **Vorticity confinement**: `vortForce = curl × normalize(gradient(|curl|))`

## How to Apply

1. **Minimal self-feedback loop** — one pass samples `uPrevPass` (prior frame of the same pass) and writes the next state.
2. **Fluid self-advection** — advect a field with `texture(uPrevPass, uv - dt * velocity * texelSize)`.
3. **Navier-Stokes solver chain** — split pressure/velocity/diffusion across multiple passes with identical solver entry points.
4. **Separable Gaussian blur** — horizontal pass (`passB`) then vertical pass (`passC`) reading the prior pass output.
5. **Structured state storage** — reserve texels as registers via `texelFetch` for game/sim state.
6. **Pointer state tracking** — store mouse/pointer state in dedicated texels for inter-frame continuity.

## Example

```glsl
// Helpers: hash-based value noise / FBM (authored inline); GLSL builtin noise() is invalid for SPIR-V
void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;

    vec4 prev = texture(uChannel0, uv);

    // New content: procedural noise contour lines
    float n = hashNoise(vec3(uv * 8.0, 0.1 * uTime));
    float v = sin(6.2832 * 10.0 * n);
    v = smoothstep(1.0, 0.0, 0.5 * abs(v) / fwidth(v));
    vec4 newContent = 0.5 + 0.5 * sin(12.0 * n + vec4(0, 2.1, -2.1, 0));

    // Decay + offset blending
    vec4 decayed = exp(-33.0 / uResolution.y) * texture(uChannel0, (gl_FragCoord.xy + vec2(1.0, sin(uTime))) / uResolution.xy);
    fragColor = mix(decayed, newContent, v);

    // Initialization guard
    if (uFrame < 4) fragColor = vec4(0.5);
}
```

```glsl
void main() {
    fragColor = texture(uChannel0, gl_FragCoord.xy / uResolution.xy);
}
```

```glsl
// Minimal ping-pong: one Buffer pass self-advecting its own prior frame
void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;
    vec2 texelSize = 1.0 / uResolution.xy;
    vec2 velocity = texture(uChannel0, uv).xy;

    // Self-advection: sample where this texel came from, then damp the field
    vec2 advected = texture(uChannel0, fract(uv - 0.016 * velocity * texelSize)).xy;
    fragColor = vec4(advected * 0.99, 0.0, 1.0);

    // Initialization guard: seed early frames with a resting field
    if (uFrame < 4) fragColor = vec4(0.0);
}
```

## Gotchas

- Pass N reading pass N output without ping-pong feeds back instantly — alternate `uChannel0`/`uChannel1` each frame.
- Buffer resolution mismatch with display UVs misaligns simulation — match sim buffer size or scale sample UVs.
- First-frame uninitialized buffer shows garbage — seed with `uFrame < N` init pass or clear texture on create.
- Simulation state buffers accumulating velocity/positions across frames need float internal formats (RG32F/RGBA32F) — RGBA8 velocity buffers drift within seconds; avoid sin-hash random in precision-sensitive paths (use PCG/integer-hash).

## Combine With

- [performance-budget](performance-budget.md) — move heavy solvers to lower-resolution passes
