# sdf-2d: 2D Signed Distance Functions

## Guideline

For each pixel, compute the signed distance `d` to the shape boundary: `d < 0` inside, `d = 0` boundary, `d > 0` outside.

## Rationale

Map to color via `smoothstep`/`clamp`:
- **Fill**: color when `d < 0`
- **Anti-aliasing**: `smoothstep(-aa, aa, d)`
- **Stroke**: apply smoothstep to `abs(d) - strokeWidth`
- **Boolean operations**: `min(d1, d2)` union, `max(d1, d2)` intersection, `max(-d1, d2)` subtraction

Key formulas:
```
Circle:       d = length(p - center) - radius
Rectangle:    d = length(max(abs(p) - halfSize, 0.0)) + min(max(abs(p).x - halfSize.x, abs(p).y - halfSize.y), 0.0)
Line segment: d = length(p - a - clamp(dot(p-a, b-a)/dot(b-a, b-a), 0, 1) * (b-a)) - width/2
Smooth union: d = mix(d2, d1, h) - k*h*(1-h),  h = clamp(0.5 + 0.5*(d2-d1)/k, 0, 1)
```

## How to Apply


1. **Step 1: Coordinate Normalization and Aspect Ratio Correction** — Convert screen pixel coordinates to normalized coordinates centered at the screen center, with the y range of [-1, 1].
2. **Step 2: Defining SDF Primitive Functions** — Write basic primitive functions that return signed distances. Each function takes the current point `p` and shape parameters, and returns a `float` distance value.
3. **Step 3: CSG Boolean Operations** — Combine two SDF distance values using min/max operations to achieve union, subtraction, and intersection of shapes.
4. **Step 4: Coordinate Transforms** — Transform coordinates before computing the SDF so that shapes appear at desired positions and angles.
5. **Step 5: Distance Field Visualization and Rendering** — Convert the SDF distance value to final color output. Includes fill, anti-aliasing, stroke, contour lines, and other visualization methods.

## Example

```glsl
// Stage: fragment | Version: 450 | Uniforms: uResolution, uTime, uFrame, uMouse

#define AA_WIDTH 1.0           // Anti-aliasing width factor
#define STROKE_WIDTH 0.015     // Stroke width
#define SMOOTH_K 0.05          // Smooth union transition width
#define CONTOUR_FREQ 80.0      // Contour line frequency (for debugging)
#define ANIM_SPEED 1.0         // Animation speed multiplier

// --- SDF Primitives ---
float sdCircle(vec2 p, float r) { return length(p) - r; }

float sdBox(vec2 p, vec2 b, float r) {
    b -= vec2(r);
    vec2 d = abs(p) - b;
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - r;
}

float sdLine(vec2 p, vec2 a, vec2 b, float w) {
    vec2 d = b - a;
    float h = clamp(dot(p - a, d) / dot(d, d), 0.0, 1.0);
    return length(p - a - d * h) - w * 0.5;
}

float sdTriangle(vec2 p, vec2 p0, vec2 p1, vec2 p2) {
    vec2 e0 = p1 - p0, v0 = p - p0;
    vec2 e1 = p2 - p1, v1 = p - p1;
    vec2 e2 = p0 - p2, v2 = p - p2;
    float d0 = dot(v0 - e0 * clamp(dot(v0,e0)/dot(e0,e0),0.0,1.0),
                   v0 - e0 * clamp(dot(v0,e0)/dot(e0,e0),0.0,1.0));
    float d1 = dot(v1 - e1 * clamp(dot(v1,e1)/dot(e1,e1),0.0,1.0),
                   v1 - e1 * clamp(dot(v1,e1)/dot(e1,e1),0.0,1.0));
    float d2 = dot(v2 - e2 * clamp(dot(v2,e2)/dot(e2,e2),0.0,1.0),
                   v2 - e2 * clamp(dot(v2,e2)/dot(e2,e2),0.0,1.0));
    float o = e0.x*e2.y - e0.y*e2.x;
    vec2 dd = min(min(vec2(d0, o*(v0.x*e0.y-v0.y*e0.x)),
                      vec2(d1, o*(v1.x*e1.y-v1.y*e1.x))),
                      vec2(d2, o*(v2.x*e2.y-v2.y*e2.x)));
    return -sqrt(dd.x) * sign(dd.y);
}

// --- CSG ---
float opUnion(float a, float b) { return min(a, b); }
float opSubtract(float a, float b) { return max(-a, b); }
float opIntersect(float a, float b) { return max(a, b); }
float opSmoothUnion(float a, float b, float k) {
    float h = clamp(0.5 + 0.5*(b - a)/k, 0.0, 1.0);
    return mix(b, a, h) - k*h*(1.0-h);
}
float opXor(float a, float b) { return min(max(-a, b), max(-b, a)); }

// --- Coordinate Transforms ---
vec2 translate(vec2 p, vec2 t) { return p - t; }
vec2 rotateCCW(vec2 p, float a) {
    return mat2(cos(a), sin(a), -sin(a), cos(a)) * p;
}

// --- Rendering Utilities ---
vec4 render(float d, vec3 color, float stroke) {
    float anti = fwidth(d) * AA_WIDTH;
    vec4 strokeLayer = vec4(vec3(0.05), 1.0 - smoothstep(-anti, anti, d - stroke));
    vec4 colorLayer  = vec4(color,      1.0 - smoothstep(-anti, anti, d));
    if (stroke < 0.0001) return colorLayer;
    return vec4(mix(strokeLayer.rgb, colorLayer.rgb, colorLayer.a), strokeLayer.a);
}

float fillAA(float d, float px) { return smoothstep(px, -px, d); }

// --- Scene ---
float sceneDist(vec2 p) {
    float t = uTime * ANIM_SPEED;
    float c = sdCircle(translate(p, vec2(-0.6, 0.3)), 0.25);
    float b = sdBox(translate(p, vec2(0.0, 0.3)), vec2(0.25, 0.18), 0.05);
    vec2 tp = rotateCCW(translate(p, vec2(0.6, 0.3)), t * 0.5);
    float tr = sdTriangle(tp, vec2(0.0, 0.25), vec2(-0.22, -0.12), vec2(0.22, -0.12));
    float row1 = opUnion(c, opUnion(b, tr));

    float c2 = sdCircle(translate(p, vec2(-0.5, -0.35)), 0.2);
    float b2 = sdBox(translate(p, vec2(-0.3, -0.35)), vec2(0.15, 0.15), 0.0);
    float smooth_demo = opSmoothUnion(c2, b2, SMOOTH_K);

    float c3 = sdCircle(translate(p, vec2(0.15, -0.35)), 0.22);
    float b3 = sdBox(translate(p, vec2(0.15, -0.35 + sin(t) * 0.15)), vec2(0.3, 0.08), 0.0);
    float sub_demo = opSubtract(b3, c3);

    float c4 = sdCircle(translate(p, vec2(0.65, -0.35)), 0.2);
    float b4 = sdBox(translate(p, vec2(0.65, -0.35 + sin(t + 1.0) * 0.15)), vec2(0.3, 0.08), 0.0);
    float xor_demo = opXor(b4, c4);

    float row2 = opUnion(smooth_demo, opUnion(sub_demo, xor_demo));
    return opUnion(row1, row2);
}

// --- Main Function ---
void main() {
    vec2 p = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    float px = 2.0 / uResolution.y;
    float d = sceneDist(p);

    vec3 bgCol = vec3(0.15, 0.15, 0.18) + 0.05 * p.y;
    bgCol *= 1.0 - 0.3 * length(p);

    vec3 col = (d > 0.0) ? vec3(0.9, 0.6, 0.3) : vec3(0.4, 0.7, 1.0);
    col *= 1.0 - exp(-10.0 * abs(d));
    col *= 0.8 + 0.2 * cos(CONTOUR_FREQ * d);
    col = mix(col, vec3(1.0), smoothstep(1.5 * px, 0.0, abs(d) - 0.002));
    col = mix(bgCol, col, 0.85);

    // Uncomment to switch to solid rendering mode:
    // vec3 shapeCol = vec3(0.2, 0.8, 0.6);
    // float mask = fillAA(d, px);
    // col = mix(bgCol, shapeCol, mask);

    col = pow(col, vec3(1.0 / 2.2));
    fragColor = vec4(col, 1.0);
}
```

```glsl
// Origin at center, y range [-1, 1] (standard approach)
vec2 p = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;

// Pixel space (suitable for fixed pixel-size UI)
vec2 p = gl_FragCoord.xy;
vec2 center = uResolution.xy * 0.5;

// [0, 1] range (requires manual aspect ratio handling)
vec2 uv = gl_FragCoord.xy / uResolution.xy;
```

```glsl
float sdCircle(vec2 p, float radius) {
    return length(p) - radius;
}

// halfSize is half-width/half-height, radius is corner rounding
float sdBox(vec2 p, vec2 halfSize, float radius) {
    halfSize -= vec2(radius);
    vec2 d = abs(p) - halfSize;
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - radius;
}

float sdLine(vec2 p, vec2 start, vec2 end, float width) {
    vec2 dir = end - start;
    float h = clamp(dot(p - start, dir) / dot(dir, dir), 0.0, 1.0);
    return length(p - start - dir * h) - width * 0.5;
}

// Exact signed distance, requires only one sqrt
float sdTriangle(vec2 p, vec2 p0, vec2 p1, vec2 p2) {
    vec2 e0 = p1 - p0, v0 = p - p0;
    vec2 e1 = p2 - p1, v1 = p - p1;
    vec2 e2 = p0 - p2, v2 = p - p2;
    float d0 = dot(v0 - e0 * clamp(dot(v0, e0) / dot(e0, e0), 0.0, 1.0),
                   v0 - e0 * clamp(dot(v0, e0) / dot(e0, e0), 0.0, 1.0));
    float d1 = dot(v1 - e1 * clamp(dot(v1, e1) / dot(e1, e1), 0.0, 1.0),
                   v1 - e1 * clamp(dot(v1, e1) / dot(e1, e1), 0.0, 1.0));
    float d2 = dot(v2 - e2 * clamp(dot(v2, e2) / dot(e2, e2), 0.0, 1.0),
                   v2 - e2 * clamp(dot(v2, e2) / dot(e2, e2), 0.0, 1.0));
    float o = e0.x * e2.y - e0.y * e2.x;
    vec2 d = min(min(vec2(d0, o * (v0.x * e0.y - v0.y * e0.x)),
                     vec2(d1, o * (v1.x * e1.y - v1.y * e1.x))),
                     vec2(d2, o * (v2.x * e2.y - v2.y * e2.x)));
    return -sqrt(d.x) * sign(d.y);
}

// Approximate ellipse SDF
float sdEllipse(vec2 p, vec2 center, float a, float b) {
    float a2 = a * a, b2 = b * b;
    vec2 d = p - center;
    return (b2 * d.x * d.x + a2 * d.y * d.y - a2 * b2) / (a2 * b2);
}
```

## Advanced

### Step 1: Coordinate Normalization and Aspect Ratio Correction

**What**: Convert screen pixel coordinates to normalized coordinates centered at the screen center, with the y range of [-1, 1].

**Why**: Pixel coordinates depend on resolution. After normalization, SDF parameters (such as radius) have resolution-independent physical meaning. Dividing by `uResolution.y` (not `.x`) ensures correct aspect ratio so circles don't become ellipses.

**Code**:
```glsl
// Method 1: Origin at center, y range [-1, 1] (most common, standard practice)
vec2 p = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;

// Method 2: If you need to work in pixel space (suitable for fixed pixel-size UI)
vec2 p = gl_FragCoord.xy;
vec2 center = uResolution.xy * 0.5;

// Method 3: [0, 1] range normalization (requires manual aspect ratio handling)
vec2 uv = gl_FragCoord.xy / uResolution.xy;
```

### Step 2: Defining SDF Primitive Functions

**What**: Write basic primitive functions that return signed distances. Each function takes the current point `p` and shape parameters, and returns a `float` distance value.

**Why**: These are the atomic building blocks for all 2D SDF graphics. Encapsulating them as independent functions allows free combination, transformation, and reuse.

**Code**:
```glsl
// ---- Circle ----
// The most basic SDF: distance from point to center minus radius
float sdCircle(vec2 p, float radius) {
    return length(p) - radius;
}

// ---- Rectangle (optional rounded corners) ----
// halfSize is half-width and half-height, radius is the corner radius
float sdBox(vec2 p, vec2 halfSize, float radius) {
    halfSize -= vec2(radius);
    vec2 d = abs(p) - halfSize;
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0)) - radius;
}

// ---- Line Segment ----
// Line segment from start to end, with width
float sdLine(vec2 p, vec2 start, vec2 end, float width) {
    vec2 dir = end - start;
    float h = clamp(dot(p - start, dir) / dot(dir, dir), 0.0, 1.0);
    return length(p - start - dir * h) - width * 0.5;
}

// ---- Triangle (exact signed distance) ----
// Three vertices p0, p1, p2, only one sqrt needed
float sdTriangle(vec2 p, vec2 p0, vec2 p1, vec2 p2) {
    vec2 e0 = p1 - p0, v0 = p - p0;
    vec2 e1 = p2 - p1, v1 = p - p1;
    vec2 e2 = p0 - p2, v2 = p - p2;

    // Squared distance to each edge (projection + clamp)
    float d0 = dot(v0 - e0 * clamp(dot(v0, e0) / dot(e0, e0), 0.0, 1.0),
                   v0 - e0 * clamp(dot(v0, e0) / dot(e0, e0), 0.0, 1.0));
    float d1 = dot(v1 - e1 * clamp(dot(v1, e1) / dot(e1, e1), 0.0, 1.0),
                   v1 - e1 * clamp(dot(v1, e1) / dot(e1, e1), 0.0, 1.0));
    float d2 = dot(v2 - e2 * clamp(dot(v2, e2) / dot(e2, e2), 0.0, 1.0),
                   v2 - e2 * clamp(dot(v2, e2) / dot(e2, e2), 0.0, 1.0));

    // Determine inside/outside using cross product sign
    float o = e0.x * e2.y - e0.y * e2.x;
    vec2 d = min(min(vec2(d0, o * (v0.x * e0.y - v0.y * e0.x)),
                     vec2(d1, o * (v1.x * e1.y - v1.y * e1.x))),
                     vec2(d2, o * (v2.x * e2.y - v2.y * e2.x)));
    return -sqrt(d.x) * sign(d.y);
}

// ---- Ellipse (approximate) ----
// Simplified ellipse SDF based on scaled space
float sdEllipse(vec2 p, vec2 center, float a, float b) {
    float a2 = a * a, b2 = b * b;
    vec2 d = p - center;
    return (b2 * d.x * d.x + a2 * d.y * d.y - a2 * b2) / (a2 * b2);
}
```

### Step 3: CSG Boolean Operations

**What**: Combine two SDF distance values using min/max operations to achieve union, subtraction, and intersection of shapes.

**Why**: This is the most powerful capability of SDFs — building arbitrarily complex shapes from simple primitives. `min` takes the smaller of the two field values to produce a union (since smaller distance means "closer" to the shape interior); `max` takes the larger value for intersection; `max(a, -b)` inverts b's inside/outside and intersects for subtraction.

**Code**:
```glsl
// Union: take the nearest shape
float opUnion(float d1, float d2) {
    return min(d1, d2);
}

// Intersection: overlapping region of both shapes
float opIntersect(float d1, float d2) {
    return max(d1, d2);
}

// Subtraction: carve d1 out of d2
float opSubtract(float d1, float d2) {
    return max(-d1, d2);
}

// Smooth union: produces a rounded transition at the junction, k controls transition width
float opSmoothUnion(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}

// XOR: non-overlapping region of both shapes
float opXor(float d1, float d2) {
    return min(max(-d1, d2), max(-d2, d1));
}
```

### Step 4: Coordinate Transforms

**What**: Transform coordinates before computing the SDF so that shapes appear at desired positions and angles.

**Why**: SDF functions define shapes centered at the origin by default. By transforming the input coordinates (rather than the shape itself), you can freely place and rotate multiple primitives in the scene without affecting the mathematical properties of the distance field.

**Code**:
```glsl
// Translation: move the coordinate origin to position t
vec2 translate(vec2 p, vec2 t) {
    return p - t;
}

// Counter-clockwise rotation
vec2 rotateCCW(vec2 p, float angle) {
    mat2 m = mat2(cos(angle), sin(angle), -sin(angle), cos(angle));
    return p * m;
}

// Usage example: translate then rotate
float d = sdBox(rotateCCW(translate(p, vec2(0.5, 0.3)), uTime), vec2(0.2), 0.05);
```

### Step 5: Distance Field Visualization and Rendering

**What**: Convert the SDF distance value to final color output. Includes fill, anti-aliasing, stroke, contour lines, and other visualization methods.

**Why**: The distance value itself is just a scalar that needs a mapping strategy to become a visual effect. `smoothstep` creates sub-pixel smooth transitions at the boundary, avoiding aliasing from hard edges. The `fwidth` function uses screen-space derivatives to automatically calculate pixel width to avoid aliasing.

```glsl
float d = sdShape(uv);
float aa = fwidth(d);
float fill = smoothstep(aa, -aa, d);
vec3 col = palette(fill) * fill;
fragColor = vec4(col, 1.0);
```

### Step 6: main() and Composition

**What**: Normalize UVs, evaluate SDF, apply AA fill or stroke, output color.

```glsl
void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    fragColor = vec4(renderShape(uv), 1.0);
}
```

## Gotchas

- Aspect-correct UVs are required — raw `gl_FragCoord.xy` without centering skews circles into ellipses.
- Hard `step` on distance fields aliases at edges — use `smoothstep` with `fwidth(d)` for sub-pixel AA.
- CSG unions without `min`/`max` smooth blends produce sharp creases that break normal-based lighting if reused in 3D.

## Combine With

- [color-palette](color-palette.md)
- [anti-aliasing](anti-aliasing.md)
