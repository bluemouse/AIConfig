# cellular-automata: Cellular Automata

## Guideline

Run discrete grid simulations on ping-pong buffers: each cell updates from neighbor state via Conway CA rules or Gray-Scott reaction-diffusion, reading the prior frame through self-feedback samplers.

## Rationale

Each cell on a discrete grid updates based on **its own state** and **neighbor states** according to fixed rules. Conway B3/S23 rules:
- Dead cell with exactly 3 live neighbors → birth
- Live cell with 2 or 3 live neighbors → survival
- Otherwise → death

Neighbor computation (Moore neighborhood, 8 neighbors): `k = Σ cell(px + offset)`

### Reaction-Diffusion (RD)
Gray-Scott model — two substances u (activator) and v (inhibitor) diffuse and react:
```
∂u/∂t = Du·∇²u - u·v² + F·(1-u)
∂v/∂t = Dv·∇²v + u·v² - (F+k)·v
```
- `Du, Dv`: diffusion coefficients (Du > Dv produces patterns)
- `F`: feed rate, `k`: kill rate
- `∇²`: Laplacian, discretized using a nine-point stencil

Key parameters `(F, k)` determine the pattern:
| F | k | Pattern |
|---|---|---------|
| 0.035 | 0.065 | spots |
| 0.040 | 0.060 | stripes |
| 0.025 | 0.055 | labyrinthine |
| 0.050 | 0.065 | solitons |

## How to Apply


1. **Step 1: Grid State Storage and Self-Feedback** — Bind the simulation pass to read its own prior frame (`uChannel0` self-feedback) via `texelFetch` for discrete CA or `texture` for continuous RD.
2. **Step 2: Initialization (Noise Seeding)** — Initialize the grid with pseudo-random noise on the first frame (or first few frames) to provide seeds for the simulation.
3. **Step 3: Neighbor Sampling and Laplacian Computation** — Perform weighted sampling of the current pixel's 8 (or 4) neighbors, computing the Laplacian or neighbor count.
4. **Step 4: State Update Rules** — Apply CA B3/S23 from neighbor count `k`, or integrate Gray-Scott `(F,k)` reaction-diffusion with the nine-point Laplacian and write the next state to the ping-pong buffer.

## Example

```glsl
// passA: uChannel0 bound to passA itself (self-feedback)
vec4 prevState = texelFetch(uChannel0, ivec2(gl_FragCoord.xy), 0);
// UV sampling (supports texture filtering)
vec2 uv = gl_FragCoord.xy / uResolution.xy;
vec4 prevSmooth = texture(uChannel0, uv);
```

```glsl
float hash1(float n) {
    return fract(sin(n) * 138.5453123);
}
vec3 hash33(in vec2 p) {
    float n = sin(dot(p, vec2(41, 289)));
    return fract(vec3(2097152, 262144, 32768) * n);
}

if (uFrame < 2) {
    // CA: random binary
    float f = step(0.9, hash1(gl_FragCoord.xy.x * 13.0 + hash1(gl_FragCoord.xy.y * 71.1)));
    fragColor = vec4(f, 0.0, 0.0, 0.0);
} else if (uFrame < 10) {
    // RD: random continuous values
    vec3 noise = hash33(gl_FragCoord.xy / uResolution.xy + vec2(53, 43) * float(uFrame));
    fragColor = vec4(noise, 1.0);
}
```

```glsl
// --- Method A: Discrete CA neighbor counting ---
int cell(in ivec2 p) {
    ivec2 r = ivec2(textureSize(uChannel0, 0));
    p = (p + r) % r;  // wrap-around boundary
    return (texelFetch(uChannel0, p, 0).x > 0.5) ? 1 : 0;
}
ivec2 px = ivec2(gl_FragCoord.xy);
int k = cell(px+ivec2(-1,-1)) + cell(px+ivec2(0,-1)) + cell(px+ivec2(1,-1))
      + cell(px+ivec2(-1, 0))                        + cell(px+ivec2(1, 0))
      + cell(px+ivec2(-1, 1)) + cell(px+ivec2(0, 1)) + cell(px+ivec2(1, 1));

// --- Method B: Nine-point Laplacian (for RD) ---
// Weights: diagonal 0.5, cross 1.0, center -6.0
vec2 laplacian(vec2 uv) {
    vec2 px = 1.0 / uResolution.xy;
    vec4 P = vec4(px, 0.0, -px.x);
    return
        0.5 * texture(uChannel0, uv - P.xy).xy
      +       texture(uChannel0, uv - P.zy).xy
      + 0.5 * texture(uChannel0, uv - P.wy).xy
      +       texture(uChannel0, uv - P.xz).xy
      - 6.0 * texture(uChannel0, uv).xy
      +       texture(uChannel0, uv + P.xz).xy
      + 0.5 * texture(uChannel0, uv + P.wy).xy
      +       texture(uChannel0, uv + P.zy).xy
      + 0.5 * texture(uChannel0, uv + P.xy).xy;
}

// --- Method C: 3x3 weighted blur (Gaussian approximation) ---
// Weights: corner 1, edge 2, center 4, total 16
float blur3x3(vec2 uv) {
    vec3 e = vec3(1, 0, -1);
    vec2 px = 1.0 / uResolution.xy;
    float res = 0.0;
    res += texture(uChannel0, uv + e.xx*px).x + texture(uChannel0, uv + e.xz*px).x
         + texture(uChannel0, uv + e.zx*px).x + texture(uChannel0, uv + e.zz*px).x;
    res += (texture(uChannel0, uv + e.xy*px).x + texture(uChannel0, uv + e.yx*px).x
          + texture(uChannel0, uv + e.yz*px).x + texture(uChannel0, uv + e.zy*px).x) * 2.;
    res += texture(uChannel0, uv + e.yy*px).x * 4.;
    return res / 16.0;
}
```

## Advanced

### Step 1: Grid State Storage and Self-Feedback

**What**: Store simulation state in a ping-pong framebuffer pass that reads its own prior frame output each tick.
**Why**: GPU shaders are inherently stateless; buffer inter-frame feedback is required for time-step iteration. State is stored in RGBA channels — CA can use a single channel for alive/dead, while RD uses two channels for u and v respectively.

**Code**:
```glsl
// passA: read previous frame's own state
// uChannel0 is bound to passA itself (self-feedback)
vec4 prevState = texelFetch(uChannel0, ivec2(gl_FragCoord.xy), 0);

// Can also sample with UV coordinates (supports texture filtering)
vec2 uv = gl_FragCoord.xy / uResolution.xy;
vec4 prevSmooth = texture(uChannel0, uv);
```

**Key points**:
- `texelFetch` performs no filtering, reads a single pixel exactly, suitable for discrete CA
- `texture` uses hardware bilinear interpolation, blending adjacent pixel values near pixel boundaries, suitable for continuous RD
- The four RGBA channels can store different state variables (e.g., u, v, velocity field components, etc.)

### Step 2: Initialization (Noise Seeding)

**What**: Initialize the grid with pseudo-random noise on the first frame (or first few frames) to provide seeds for the simulation.

**Why**: Both CA and RD need initial perturbation to start evolution. Different initial conditions produce different final patterns. In practice, seeding is often repeated for the first 2~10 frames, since 
**Code**:
```glsl
// Simple hash noise function
float hash1(float n) {
    return fract(sin(n) * 138.5453123);
}

vec3 hash33(in vec2 p) {
    float n = sin(dot(p, vec2(41, 289)));
    return fract(vec3(2097152, 262144, 32768) * n);
}

// Initialization branch in main()
if (uFrame < 2) {
    // CA: random binary initialization
    float f = step(0.9, hash1(gl_FragCoord.xy.x * 13.0 + hash1(gl_FragCoord.xy.y * 71.1)));
    fragColor = vec4(f, 0.0, 0.0, 0.0);
} else if (uFrame < 10) {
    // RD: random continuous value initialization
    vec3 noise = hash33(gl_FragCoord.xy / uResolution.xy + vec2(53, 43) * float(uFrame));
    fragColor = vec4(noise, 1.0);
}
```

**Key points**:
- `hash1` is a simple pseudo-random number generator based on `sin`, producing values in [0, 1)
- `hash33` generates a 3D random vector from 2D coordinates, used for multi-channel RD initialization
- CA initialization uses `step(0.9, ...)` to produce approximately 10% density of living cells
- RD initialization uses continuous random values, with `uFrame` added so each frame seeds differently
- Multi-frame seeding (`uFrame < 10`) ensures sufficiently rich initial perturbation

### Step 3: Neighbor Sampling and Laplacian Computation

**What**: Perform weighted sampling of the current pixel's 8 (or 4) neighbors, computing the Laplacian or neighbor count.

**Why**: This is the core of CA/RD — local rules drive state updates through neighbor information. The Laplacian describes how much a point's value deviates from the surrounding average, physically corresponding to diffusion. The nine-point stencil is more accurate and isotropic than a simple cross stencil.

**Three Sampling Methods Compared**:

| Method | Use Case | Advantages | Disadvantages |
|------|----------|------|------|
| Method A: Discrete neighbor counting | CA | Exact integer coordinates, no filtering error | Can only handle discrete states |
| Method B: Nine-point Laplacian | RD | Good isotropy, high accuracy | 9 texture samples |
| Method C: 3x3 Gaussian blur | Simplified RD | Good smoothing effect | Not a true Laplacian |

**Method A Code Details**:
```glsl
// Discrete CA neighbor counting using texelFetch for exact reads
int cell(in ivec2 p) {
    ivec2 r = ivec2(textureSize(uChannel0, 0));
    p = (p + r) % r;  // Wrap-around boundary (toroidal topology), left overflow appears on right
    return (texelFetch(uChannel0, p, 0).x > 0.5) ? 1 : 0;
}

ivec2 px = ivec2(gl_FragCoord.xy);
// Moore neighborhood: sum of 8 neighbors
int k = cell(px + ivec2(-1,-1)) + cell(px + ivec2(0,-1)) + cell(px + ivec2(1,-1))
      + cell(px + ivec2(-1, 0))                          + cell(px + ivec2(1, 0))
      + cell(px + ivec2(-1, 1)) + cell(px + ivec2(0, 1)) + cell(px + ivec2(1, 1));
```

**Method B Code Details**:
```glsl
// Nine-point Laplacian stencil (for RD)
// Weights: diagonal 0.5, cross 1.0, center -6.0 (sum = 0, ensuring Laplacian of a constant field is zero)
vec2 laplacian(vec2 uv) {
    vec2 px = 1.0 / uResolution.xy;
    vec4 P = vec4(px, 0.0, -px.x);
    return
        0.5 * texture(uChannel0, uv - P.xy).xy   // bottom-left
      +       texture(uChannel0, uv - P.zy).xy   // bottom
      + 0.5 * texture(uChannel0, uv - P.wy).xy   // bottom-right
      +       texture(uChannel0, uv - P.xz).xy   // left
      - 6.0 * texture(uChannel0, uv).xy           // center
      +       texture(uChannel0, uv + P.xz).xy   // right
      + 0.5 * texture(uChannel0, uv + P.wy).xy   // top-left
      +       texture(uChannel0, uv + P.zy).xy   // top
      + 0.5 * texture(uChannel0, uv + P.xy).xy;  // top-right
}
```

**Method C Code Details**:
```glsl
// 3x3 weighted blur (Gaussian approximation)
// Weights: diagonal 1, cross 2, center 4, total 16
// Uses vec3 swizzle to cleverly encode 9 offset directions
float blur3x3(vec2 uv) {
    vec3 e = vec3(1, 0, -1);  // e.x=1, e.y=0, e.z=-1
    vec2 px = 1.0 / uResolution.xy;
    float res = 0.0;
    // e.xx=(1,1), e.xz=(1,-1), e.zx=(-1,1), e.zz=(-1,-1) → four diagonals
    res += texture(uChannel0, uv + e.xx * px).x + texture(uChannel0, uv + e.xz * px).x
         + texture(uChannel0, uv + e.zx * px).x + texture(uChannel0, uv + e.zz * px).x;       // ×1
    // e.xy=(1,0), e.yx=(0,1), e.yz=(0,-1), e.zy=(-1,0) → four edges
    res += (texture(uChannel0, uv + e.xy * px).x + texture(uChannel0, uv + e.yx * px).x
          + texture(uChannel0, uv + e.yz * px).x + texture(uChannel0, uv + e.zy * px).x) * 2.; // ×2
    // e.yy=(0,0) → center
    res += texture(uChannel0, uv + e.yy * px).x * 4.;                                          // ×4
    return res / 16.0;
}
```

### Step 4: State Update Rules

**What**: Apply the local update rule — Conway B3/S23 for discrete CA, or Gray-Scott reaction-diffusion for continuous `(u,v)` fields.

**Why**: Neighbor sampling only gathers context; the rule determines how each cell evolves to the next frame.

**CA update (Method A)**:
```glsl
ivec2 px = ivec2(gl_FragCoord.xy);
int alive = cell(px);
int k = /* Moore neighborhood sum from Step 3 */;
float next = (alive == 1 && (k == 2 || k == 3)) || (alive == 0 && k == 3) ? 1.0 : 0.0;
fragColor = vec4(next, 0.0, 0.0, 1.0);
```

**Gray-Scott update (Method B)**:
```glsl
vec2 uv = gl_FragCoord.xy / uResolution.xy;
vec2 uvLap = laplacian(uv);
vec2 uvCur = texture(uChannel0, uv).xy;
float F = 0.037, kKill = 0.060, Du = 0.16, Dv = 0.08, dt = 1.0;
float u = uvCur.x, v = uvCur.y;
float uvv = u * v * v;
float du = Du * uvLap.x - uvv + F * (1.0 - u);
float dv = Dv * uvLap.y + uvv - (F + kKill) * v;
fragColor = vec4(u + du * dt, v + dv * dt, 0.0, 1.0);
```

**Key points**:
- CA needs exact `texelFetch` reads — bilinear filtering blurs discrete states
- RD needs stable `(F,k)` pairs; see the parameter table in Rationale
- Clamp or damp RD values to avoid blow-up on large `dt`

## Gotchas

- Moore vs Von Neumann neighborhood changes rule semantics — document neighbor count for each rule ID.
- Double-buffer ping-pong missing reads stale state — sample previous pass texture, write to current buffer.
- Edge cells without toroidal wrap show boundary artifacts — wrap coordinates or pad with ghost cells.

## Combine With

- [multipass-buffer](multipass-buffer.md)
- [color-palette](color-palette.md)
