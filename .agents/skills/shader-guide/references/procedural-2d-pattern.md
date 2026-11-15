# procedural-2d-pattern: Procedural 2D Patterns

## Guideline

2D procedural patterns = **domain transforms + distance fields + color mapping**:

## Rationale

1. **Domain repetition**: `fract()`/`mod()` folds the infinite plane into repeating cells
2. **Cell identification**: `floor()` extracts integer coordinates as hash seeds, driving per-cell random variations
3. **Distance field (SDF)**: mathematical functions compute pixel-to-shape distance, `smoothstep` renders edges
4. **Color mapping**: cosine palette `a + b*cos(2pi(c*t+d))` or HSV
5. **Layer compositing**: multi-layer loop results blended via addition/multiplication/`mix`

Key formulas:
```glsl
// UV normalization
uv = (gl_FragCoord.xy * 2.0 - uResolution.xy) / uResolution.y;
// Domain repetition
cell_uv = fract(uv * SCALE) - 0.5;
cell_id = floor(uv * SCALE);
// Cosine palette
col = a + b * cos(6.28318 * (c * t + d));
// Hexagon SDF
hex(p) = max(dot(abs(p), vec2(0.5, 0.866025)), abs(p).x);
// 2D rotation
mat2(cos(a), -sin(a), sin(a), cos(a));
```

## How to Apply


1. **Step 1: UV Coordinate Normalization and Aspect Ratio Correction** — Convert pixel coordinates to normalized coordinates centered on the screen with Y-axis range [-1, 1]
2. **Step 2: Domain Repetition — Dividing Space into Repeating Cells** — Scale UV coordinates and take the fractional part to generate repeating local coordinates; simultaneously extract cell IDs using `floor`
3. **Step 3: Cell Randomization** — Use cell IDs to generate pseudo-random numbers, giving each cell different attributes (size, position, color offset)
4. **Step 4: Distance Field Shape Rendering** — Compute the distance from the pixel to the target shape, then convert to visualization using `smoothstep`
5. **Step 5: Polar Coordinate Conversion and Ring/Arc Patterns** — Convert Cartesian coordinates to polar coordinates, using radial distance to draw concentric rings and angle to draw sectors/arc segments
6. **Step 6: Cosine Palette** — Generate a continuous rainbow color mapping function using four vec3 parameters
7. **Step 7: Iterative Stacking and Glow Effects** — Repeatedly perform domain repetition + distance field calculation in a loop, accumulating color; use `pow(1/d)` to produce glow
8. **Step 8: Trigonometric Interference Patterns** — Use `sin`/`cos` to mutually perturb coordinates in iterations, generating water caustic-like interference patterns

## Example

```glsl
vec2 uv = (gl_FragCoord.xy * 2.0 - uResolution.xy) / uResolution.y;
```

```glsl
#define SCALE 4.0
vec2 cell_uv = fract(uv * SCALE) - 0.5;
vec2 cell_id = floor(uv * SCALE);
```

```glsl
const vec2 s = vec2(1, 1.7320508);
vec4 hC = floor(vec4(p, p - vec2(0.5, 1.0)) / s.xyxy) + 0.5;
vec4 h = vec4(p - hC.xy * s, p - (hC.zw + 0.5) * s);
vec4 hex_data = dot(h.xy, h.xy) < dot(h.zw, h.zw)
    ? vec4(h.xy, hC.xy)
    : vec4(h.zw, hC.zw + vec2(0.5, 1.0));
```

## Advanced

### Step 1: UV Coordinate Normalization and Aspect Ratio Correction

**What**: Convert pixel coordinates to normalized coordinates centered on the screen with Y-axis range [-1, 1]

**Why**: A unified coordinate system ensures patterns don't distort with resolution changes; using Y-axis as reference maintains square pixels

```glsl
vec2 uv = (gl_FragCoord.xy * 2.0 - uResolution.xy) / uResolution.y;
```

### Step 2: Domain Repetition — Dividing Space into Repeating Cells

**What**: Scale UV coordinates and take the fractional part to generate repeating local coordinates; simultaneously extract cell IDs using `floor`

**Why**: `fract()` folds an infinite plane into a repeating [0,1) space, `floor()` provides a unique cell identifier for subsequent randomization. Subtracting 0.5 centers the origin

```glsl
#define SCALE 4.0 // Tunable: repetition density, higher = more cells
vec2 cell_uv = fract(uv * SCALE) - 0.5;
vec2 cell_id = floor(uv * SCALE);
```

For hexagonal grids, domain repetition requires special handling (two offset rectangular grids, taking the nearest):

```glsl
const vec2 s = vec2(1, 1.7320508); // 1 and sqrt(3)
vec4 hC = floor(vec4(p, p - vec2(0.5, 1.0)) / s.xyxy) + 0.5;
vec4 h = vec4(p - hC.xy * s, p - (hC.zw + 0.5) * s);
// Take the nearest hexagonal center
vec4 hex_data = dot(h.xy, h.xy) < dot(h.zw, h.zw)
    ? vec4(h.xy, hC.xy)
    : vec4(h.zw, hC.zw + vec2(0.5, 1.0));
```

### Step 3: Cell Randomization

**What**: Use cell IDs to generate pseudo-random numbers, giving each cell different attributes (size, position, color offset)

**Why**: Pure repetition looks mechanical; randomization gives patterns a "procedural yet lively" quality

```glsl
float hash21(vec2 p) {
    return fract(sin(dot(p, vec2(141.173, 289.927))) * 43758.5453);
}

float rnd = hash21(cell_id);
float radius = 0.15 + 0.1 * rnd; // Tunable: base radius and random range
```

### Step 4: Distance Field Shape Rendering

**What**: Compute the distance from the pixel to the target shape, then convert to visualization using `smoothstep`

**Why**: SDF is the cornerstone of procedural graphics — a single scalar value simultaneously encodes shape, edges, and glow effects

```glsl
// Circle SDF
float d = length(cell_uv) - radius;

// Hexagon SDF
float hex_sdf(vec2 p) {
    p = abs(p);
    return max(dot(p, vec2(0.5, 0.866025)), p.x);
}

// Line segment SDF (for networks/grid lines)
float line_sdf(vec2 a, vec2 b, vec2 p) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

// Anti-aliased rendering with smoothstep
float shape = 1.0 - smoothstep(radius - 0.008, radius + 0.008, length(cell_uv));
```

### Step 5: Polar Coordinate Conversion and Ring/Arc Patterns

**What**: Convert Cartesian coordinates to polar coordinates, using radial distance to draw concentric rings and angle to draw sectors/arc segments

**Why**: Polar coordinates are naturally suited for radar sweeps, concentric circles, spirals, and other radially symmetric patterns

```glsl
vec2 polar = vec2(length(uv), atan(uv.y, uv.x));
float ring_id = floor(polar.x * NUM_RINGS + 0.5) / NUM_RINGS; // Tunable: NUM_RINGS ring count

// Concentric rings
float ring = 1.0 - pow(abs(sin(polar.x * 3.14159 * NUM_RINGS)) * 1.25, 2.5);

// Arc segment clipping
float arc_end = polar.y + sin(uTime + ring_id * 5.5) * 1.52 - 1.5;
ring *= smoothstep(0.0, 0.05, arc_end);
```

### Step 6: Cosine Palette

**What**: Generate a continuous rainbow color mapping function using four vec3 parameters

**Why**: A single line of code generates infinite smooth color schemes, more flexible and GPU-friendly than lookup tables

```glsl
vec3 palette(float t) {
    // Tunable: modify a/b/c/d to change color scheme
    vec3 a = vec3(0.5, 0.5, 0.5);       // Brightness offset
    vec3 b = vec3(0.5, 0.5, 0.5);       // Amplitude
    vec3 c = vec3(1.0, 1.0, 1.0);       // Frequency
    vec3 d = vec3(0.263, 0.416, 0.557);  // Phase offset
    return a + b * cos(6.28318 * (c * t + d));
}
```

### Step 7: Iterative Stacking and Glow Effects

**What**: Repeatedly perform domain repetition + distance field calculation in a loop, accumulating color; use `pow(1/d)` to produce glow

**Why**: A single layer pattern is too simple; multi-layer iterative stacking produces fractal-like visual complexity with minimal code. Exponentially decaying glow gives patterns a neon light feel

```glsl
#define NUM_LAYERS 4.0 // Tunable: number of iteration layers, more = more complex
vec3 finalColor = vec3(0.0);
vec2 uv0 = uv; // Preserve original UV for global coloring

for (float i = 0.0; i < NUM_LAYERS; i++) {
    uv = fract(uv * 1.5) - 0.5;    // Tunable: 1.5 is the scale factor
    float d = length(uv) * exp(-length(uv0));
    vec3 col = palette(length(uv0) + i * 0.4 + uTime * 0.4);
    d = sin(d * 8.0 + uTime) / 8.0; // Tunable: 8.0 is the ripple frequency
    d = abs(d);
    d = pow(0.01 / d, 1.2);         // Tunable: 0.01 is glow width, 1.2 is decay exponent
    finalColor += col * d;
}
```

### Step 8: Trigonometric Interference Patterns

**What**: Use `sin`/`cos` to mutually perturb coordinates in iterations, generating water caustic-like interference patterns

**Why**: Superposition of trigonometric functions produces complex Moire-like interference patterns; a few iterations yield highly organic visual effects

```glsl
#define MAX_ITER 5 // Tunable: iteration count, more = richer detail
vec2 p = mod(uv * TAU, TAU) - 250.0; // TAU period ensures tileability
vec2 i = p;
float c = 1.0;
float inten = 0.005; // Tunable: intensity coefficient

for (int n = 0; n < MAX_ITER; n++) {
    float t = uTime * (1.0 - 3.5 / float(n + 1));
    i = p + vec2(cos(t - i.x) + sin(t + i.y),
                 sin(t - i.y) + cos(t + i.x));
    c += 1.0 / length(vec2(p.x / (sin(i.x + t) / inten),
                            p.y / (cos(i.y + t) / inten)));
}
c /= float(MAX_ITER);
c = 1.17 - pow(c, 1.4); // Tunable: 1.4 is the contrast exponent
vec3 colour = vec3(0.5 + 0.5 * cos(vec3(0.0, 2.0, 4.0) + c * 6.0));
fragColor = vec4(colour, 1.0);
```

### Step 6: main() Template

**What**: Center UVs, apply domain repetition, evaluate pattern function, map to palette.

```glsl
void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution.xy) / uResolution.y;
    fragColor = vec4(pattern(uv), 1.0);
}
```

## Gotchas

- Polar UVs at the origin diverge — offset center or blend to Cartesian near `r < epsilon`.
- Fractal iteration count fixed for all pixels wastes GPU on converged pixels — early exit when `|z| > escapeRadius`.
- Palette phase tied only to iteration count banding appears — mix orbit trap or smooth iteration count.

## Combine With

- [polar-uv-manipulation](polar-uv-manipulation.md)
- [color-palette](color-palette.md)
