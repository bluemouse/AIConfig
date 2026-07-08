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
// Helpers: use hashNoise/FBM from procedural-noise.md; GLSL builtin noise() is invalid for SPIR-V
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
#define ROT_NUM 5
#define SCALE_NUM 20

const float ang = 6.2832 / float(ROT_NUM);
mat2 m = mat2(cos(ang), sin(ang), -sin(ang), cos(ang));

float getRot(vec2 pos, vec2 b) {
    vec2 p = b;
    float rot = 0.0;
    for (int i = 0; i < ROT_NUM; i++) {
        rot += dot(texture(uChannel0, fract((pos + p) / uResolution.xy)).xy - vec2(0.5),
                   p.yx * vec2(1, -1));
        p = m * p;
    }
    return rot / float(ROT_NUM) / dot(b, b);
}

void main() {
    vec2 pos = gl_FragCoord.xy;
    float rnd = fract(sin(float(uFrame) * 12.9898) * 43758.5453);
    vec2 b = vec2(cos(ang * rnd), sin(ang * rnd));

    // Multi-scale rotation sampling
    vec2 v = vec2(0);
    float bbMax = 0.7 * uResolution.y;
    bbMax *= bbMax;
    for (int l = 0; l < SCALE_NUM; l++) {
        if (dot(b, b) > bbMax) break;
        vec2 p = b;
        for (int i = 0; i < ROT_NUM; i++) {
            v += p.yx * getRot(pos + p, b);
            p = m * p;
        }
        b *= 2.0;
    }

    // Self-advection
    fragColor = texture(uChannel0, fract((pos + v * vec2(-1, 1) * 2.0) / uResolution.xy));

    // Center driving force
    vec2 scr = (gl_FragCoord.xy / uResolution.xy) * 2.0 - 1.0;
    fragColor.xy += 0.01 * scr / (dot(scr, scr) / 0.1 + 0.3);

    if (uFrame <= 4) fragColor = texture(uChannel1, gl_FragCoord.xy / uResolution.xy);
}
```

## Advanced

### GLSL Fundamentals

- GLSL basic syntax: `uniform`, `varying`, `sampler2D`
- Difference between `texture()` and `texelFetch()`:
  - `texture()` performs interpolated sampling (bilinear filtering), suitable for continuous field sampling
  - `texelFetch()` reads a specific texel exactly, without interpolation, suitable for data storage reads
- `textureLod()` is used for explicit MIP level sampling, avoiding the blur caused by automatic MIP selection
- passA/B/C/D map to ping-pong simulation passes via `uChannel0`/`uChannel1` in neutral GLSL.

### Basic Math

- Basic vector math and matrix transforms
- Finite difference method: using neighboring pixels to approximate gradients and the Laplacian operator
- Iterative mapping: the concept of `x(n+1) = f(x(n))`, the mathematical basis for self-feedback

## Gotchas

- Pass N reading pass N output without ping-pong feeds back instantly — alternate `uChannel0`/`uChannel1` each frame.
- Buffer resolution mismatch with display UVs misaligns simulation — match sim buffer size or scale sample UVs.
- First-frame uninitialized buffer shows garbage — seed with `uFrame < N` init pass or clear texture on create.

## Combine With

- [fluid-simulation](fluid-simulation.md)
- [cellular-automata](cellular-automata.md)
