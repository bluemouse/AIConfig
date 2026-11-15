# domain-warping: Domain Warping

## Guideline

Offset input coordinates by FBM noise before evaluating the main SDF or color function — single or nested warps produce organic deformation.

## Rationale

- Offset coordinates by FBM output before evaluating the main SDF or color function.
- Deeper nesting (`fbm(p + fbm(p + fbm(p)))`) yields more organic shapes.
- Requires [procedural-noise](procedural-noise.md) hash and FBM helpers first.

## How to Apply


1. **Step 1: Hash Function** — Implement a hash function that maps 2D integer coordinates to a pseudo-random float.
2. **Step 2: Value Noise** — Implement 2D value noise — take hash values at integer lattice points and interpolate between them with Hermite smoothing.
3. **Step 3: fBM (Fractal Brownian Motion)** — Superpose multiple noise layers at different frequencies/amplitudes to create fractal noise with self-similar properties.
4. **Step 4: Domain Warping (Core)** — Use fBM output as a coordinate offset, recursively nesting to form multi-level warping.
5. **Step 5: Time Animation** — Inject `uTime` into specific fBM octaves so the warp field evolves over time.
6. **Step 6: Coloring** — Map the scalar output of the warp field to colors.

## Example

```glsl
// Helpers: use hashNoise/FBM from procedural-noise.md; GLSL builtin noise() is invalid for SPIR-V
// Stage: fragment | Version: 450 | Uniforms: uResolution, uTime, uFrame, uMouse

#define WARP_DEPTH 3        // Warp nesting depth (1=subtle, 2=moderate, 3=classic)
#define NUM_OCTAVES 6       // FBM octave count (4=coarse fast, 6=fine)
#define TIME_SCALE 1.0      // Animation speed (0.05=very slow, 1.0=fluid, 2.0=fast)
#define WARP_STRENGTH 1.0   // Warp intensity (0.5=subtle, 1.0=standard, 2.0=strong)
#define BASE_SCALE 3.0      // Overall noise scale (larger = denser texture)

const mat2 mtx = mat2(0.80, 0.60, -0.60, 0.80);

float hash(vec2 p) {
    p = fract(p * 0.6180339887);
    p *= 25.0;
    return fract(p.x * p.y * (p.x + p.y));
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), f.x),
        mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
        f.y
    );
}

float fbm(vec2 p) {
    float f = 0.0;
    float amp = 0.5;
    float freq = 1.0;
    float norm = 0.0;

    for (int i = 0; i < NUM_OCTAVES; i++) {
        float t = 0.0;
        if (i == 0) t = uTime * TIME_SCALE;
        if (i == NUM_OCTAVES - 1) t = sin(uTime * TIME_SCALE);

        f += amp * hashNoise(p + t);
        norm += amp;
        p = mtx * p * 2.02;
        amp *= 0.5;
    }
    return f / norm;
}

float pattern(vec2 p) {
    float val = fbm(p);

    #if WARP_DEPTH >= 2
    val = fbm(p + WARP_STRENGTH * val);
    #endif

    #if WARP_DEPTH >= 3
    val = fbm(p + WARP_STRENGTH * val);
    #endif

    return val;
}

vec3 palette(float t) {
    vec3 col = vec3(0.2, 0.1, 0.4);
    col = mix(col, vec3(0.3, 0.05, 0.05), t);
    col = mix(col, vec3(0.9, 0.9, 0.9), t * t);
    col = mix(col, vec3(0.0, 0.2, 0.4), smoothstep(0.6, 0.8, t));
    return col * t * 2.0;
}

void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    uv *= BASE_SCALE;

    float shade = pattern(uv);
    vec3 col = palette(shade);

    // Vignette effect
    vec2 q = gl_FragCoord.xy / uResolution.xy;
    col *= 0.5 + 0.5 * sqrt(16.0 * q.x * q.y * (1.0 - q.x) * (1.0 - q.y));

    fragColor = vec4(col, 1.0);
}
```

```glsl
// Map 2D integer coordinates to a pseudo-random float
float hash(vec2 p) {
    p = fract(p * 0.6180339887); // golden ratio pre-perturbation
    p *= 25.0;
    return fract(p.x * p.y * (p.x + p.y));
}
```

```glsl
// Hash values at integer lattice points, Hermite smooth interpolation
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), f.x),
        mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
        f.y
    );
}
```

## Advanced

### Step 1: Hash Function

**What**: Implement a hash function that maps 2D integer coordinates to a pseudo-random float.

**Why**: This is the foundation of noise functions — producing deterministic "random" values at each lattice point. The `sin-dot` trick compresses 2D input to 1D then takes the fractional part, using sin's high-frequency oscillation to produce a chaotic distribution.

**Code**:
```glsl
float hash(vec2 p) {
    p = fract(p * 0.6180339887); // Golden ratio pre-perturbation
    p *= 25.0;
    return fract(p.x * p.y * (p.x + p.y));
}
```

> Note: The classic `fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453)` version can also be used, but the sin-free version above is more stable in precision on some GPUs.

### Step 2: Value Noise

**What**: Implement 2D value noise — take hash values at integer lattice points and interpolate between them with Hermite smoothing.

**Why**: Value noise is the simplest continuous noise, producing smooth, jump-free output suitable as the foundation for fBM. Hermite interpolation `f*f*(3.0-2.0*f)` ensures the derivative is zero at lattice points, avoiding the angular appearance of linear interpolation.

**Code**:
```glsl
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); // Hermite smooth interpolation

    return mix(
        mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), f.x),
        mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
        f.y
    );
}
```

### Step 3: fBM (Fractal Brownian Motion)

**What**: Superpose multiple noise layers at different frequencies/amplitudes to create fractal noise with self-similar properties.

**Why**: A single noise layer is too uniform. fBM superimposes multiple "octaves" to simulate nature's fractal structures. Each layer doubles in frequency (lacunarity ~ 2.0), halves in amplitude (persistence = 0.5), and uses a rotation matrix to break lattice alignment.

**Code**:
```glsl
// Helpers: use hashNoise/FBM from procedural-noise.md; GLSL builtin noise() is invalid for SPIR-V
const mat2 mtx = mat2(0.80, 0.60, -0.60, 0.80); // Rotation ~36.87°, for decorrelation

float fbm(vec2 p) {
    float f = 0.0;
    f += 0.500000 * hashNoise(p); p = mtx * p * 2.02;
    f += 0.250000 * hashNoise(p); p = mtx * p * 2.03;
    f += 0.125000 * hashNoise(p); p = mtx * p * 2.01;
    f += 0.062500 * hashNoise(p); p = mtx * p * 2.04;
    f += 0.031250 * hashNoise(p); p = mtx * p * 2.01;
    f += 0.015625 * hashNoise(p);
    return f / 0.96875; // Normalize: sum of all amplitudes
}
```

> Using lacunarity values of 2.01~2.04 rather than exact 2.0 is to **avoid visual artifacts caused by lattice regularity**. This is a widely adopted trick in classic implementations.

### Step 4: Domain Warping (Core)

**What**: Use fBM output as a coordinate offset, recursively nesting to form multi-level warping.

**Why**: This is the core of the entire technique. `fbm(p)` generates a scalar field; adding it to the coordinate `p` is equivalent to "pulling and stretching space according to the noise field's shape." Multi-level nesting makes the deformation more complex and organic — each warping level operates in space already deformed by the previous level.

**Code**:
```glsl
float pattern(vec2 p) {
    return fbm(p + fbm(p + fbm(p)));
}
```

This single line is the classic three-level domain warping. It can be decomposed for understanding:

```glsl
float pattern(vec2 p) {
    float warp1 = fbm(p);           // Level 1: noise in original space
    float warp2 = fbm(p + warp1);   // Level 2: noise in first-level warped space
    float result = fbm(p + warp2);  // Level 3: final value in second-level warped space
    return result;
}
```

### Step 5: Time Animation

**What**: Inject `uTime` into specific fBM octaves so the warp field evolves over time.

**Why**: Directly offsetting all octaves causes uniform translation, lacking organic feel. The classic approach is to inject time only in the lowest frequency (first layer) and highest frequency (last layer) — low frequency drives overall flow, high frequency adds detail variation.

**Code**:
```glsl
// Helpers: use hashNoise/FBM from procedural-noise.md; GLSL builtin noise() is invalid for SPIR-V
float fbm(vec2 p) {
    float f = 0.0;
    f += 0.500000 * hashNoise(p + uTime);  // Lowest frequency with time: slow overall flow
    p = mtx * p * 2.02;
    f += 0.250000 * hashNoise(p); p = mtx * p * 2.03;
    f += 0.125000 * hashNoise(p); p = mtx * p * 2.01;
    f += 0.062500 * hashNoise(p); p = mtx * p * 2.04;
    f += 0.031250 * hashNoise(p); p = mtx * p * 2.01;
    f += 0.015625 * hashNoise(p + sin(uTime)); // Highest frequency with time: subtle detail motion
    return f / 0.96875;
}
```

### Step 6: Coloring

**What**: Map the scalar output of the warp field to colors.

**Why**: Domain warping outputs a scalar field (0~1 range) that needs to be mapped to visually meaningful colors. The classic method uses a `mix` chain — interpolating between multiple preset colors using the warp value.

**Code**:
```glsl
vec3 palette(float t) {
    vec3 col = vec3(0.2, 0.1, 0.4);                              // Deep purple base
    col = mix(col, vec3(0.3, 0.05, 0.05), t);                    // Dark red
    col = mix(col, vec3(0.9, 0.9, 0.9), t * t);                  // White at high values
    col = mix(col, vec3(0.0, 0.2, 0.4), smoothstep(0.6, 0.8, t));// Blue highlights
    return col * t * 2.0;                                         // Overall brightness modulation
}
```

## Gotchas

- Strong FBM warp folds space and creates non-injective UVs — reduce warp amplitude or add octave damping.
- Warping before CSG changes boolean semantics — warp operands consistently or warp the final field only once.
- High-frequency warp without extra march steps causes missed hits — see `performance-budget.md` for warp cost.

## Combine With

- [procedural-noise](procedural-noise.md)
- [sdf-3d](sdf-3d.md)
