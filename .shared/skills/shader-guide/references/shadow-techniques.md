# shadow-techniques: Shadow Techniques

## Guideline

March from the surface point toward the light source, using the **ratio of nearest distance to marching distance** to estimate penumbra width.

## Rationale

### Key Formulas

Classic formula: `shadow = min(shadow, k * h / t)`
- `h` = SDF value at current position, `t` = distance traveled, `k` = penumbra hardness

Improved formula (geometric triangulation) — eliminates sharp edge banding artifacts:
```
y = h² / (2 * ph)       // ph = SDF value from previous step
d = sqrt(h² - y²)       // true closest distance perpendicular to the ray
shadow = min(shadow, d / (w * max(0, t - y)))
```

Negative extension — allows `res` to drop to -1, remapped with a C1 continuous function to eliminate hard creases:
```
res = max(res, -1.0)
shadow = 0.25 * (1 + res)² * (2 - res)
```
This is equivalent to `smoothstep` over [-1, 1] instead of [0, 1]. The step size is clamped with `clamp(h, 0.005, 0.50)` to ensure the ray penetrates slightly into geometry, capturing both outer and inner penumbra. This produces results close to ground truth for varying light sizes.

## How to Apply


1. **Step 1: Scene SDF Definition** — Define the scene's signed distance function, returning the distance from any point in space to the nearest surface.
2. **Step 2: Classic Soft Shadow Function** — March from a surface point toward the light source, progressively accumulating the minimum `k*h/t` ratio as the shadow factor.
3. **Step 3: Improved Soft Shadow (Geometric Triangulation)** — Use SDF values from the current and previous steps to estimate a more accurate nearest point position via geometric triangulation, eliminating penumbra artifacts near sharp edges.
4. **Step 4: Negative Extension Version (Smoothest Penumbra)** — Allow the shadow factor to drop into the negative range [-1, 0], then remap to [0, 1] with a custom quadratic smooth function, eliminating hard creases.
5. **Step 5: Bounding Volume Optimization** — Before starting the march, use simple geometric tests (plane clipping or AABB ray intersection) to narrow the shadow ray's effective range.
6. **Step 6: Shadow Color Rendering (Color Bleeding)** — Instead of using a uniform scalar shadow value, apply different shadow attenuation curves to the RGB channels.

## Example

```glsl
float sdSphere(vec3 p, float r) { return length(p) - r; }
float sdPlane(vec3 p) { return p.y; }
float sdRoundBox(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

float map(vec3 p) {
    float d = sdPlane(p);
    d = min(d, sdSphere(p - vec3(0.0, 0.5, 0.0), 0.5));
    d = min(d, sdRoundBox(p - vec3(-1.2, 0.3, 0.5), vec3(0.3), 0.05));
    return d;
}
```

```glsl
// Classic SDF soft shadow
float calcSoftShadow(vec3 ro, vec3 rd, float mint, float tmax) {
    float res = 1.0;
    float t = mint;
    for (int i = 0; i < MAX_SHADOW_STEPS; i++) {
        float h = map(ro + rd * t);
        float s = clamp(SHADOW_K * h / t, 0.0, 1.0);
        res = min(res, s);
        t += clamp(h, MIN_STEP, MAX_STEP);
        if (res < 0.004 || t > tmax) break;
    }
    res = clamp(res, 0.0, 1.0);
    return res * res * (3.0 - 2.0 * res);  // smoothstep smoothing
}
```

```glsl
// Improved version - geometric triangulation using adjacent SDF values
float calcSoftShadowImproved(vec3 ro, vec3 rd, float mint, float tmax, float w) {
    float res = 1.0;
    float t = mint;
    float ph = 1e10;
    for (int i = 0; i < MAX_SHADOW_STEPS; i++) {
        float h = map(ro + rd * t);
        float y = h * h / (2.0 * ph);
        float d = sqrt(h * h - y * y);
        res = min(res, d / (w * max(0.0, t - y)));
        ph = h;
        t += h;
        if (res < 0.0001 || t > tmax) break;
    }
    res = clamp(res, 0.0, 1.0);
    return res * res * (3.0 - 2.0 * res);
}
```

## Advanced

### Step 1: Scene SDF Definition

**What**: Define the scene's signed distance function, returning the distance from any point in space to the nearest surface.

**Why**: Shadow ray marching needs `map(p)` queries to determine step size and penumbra estimation.

```glsl
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdPlane(vec3 p) {
    return p.y;
}

float sdRoundBox(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

float map(vec3 p) {
    float d = sdPlane(p);
    d = min(d, sdSphere(p - vec3(0.0, 0.5, 0.0), 0.5));
    d = min(d, sdRoundBox(p - vec3(-1.2, 0.3, 0.5), vec3(0.3), 0.05));
    return d;
}
```

### Step 2: Classic Soft Shadow Function

**What**: March from a surface point toward the light source, progressively accumulating the minimum `k*h/t` ratio as the shadow factor.

**Why**: This is the foundational framework for all SDF soft shadows. At each step, `h/t` approximates the angular width of occlusion at that point; the minimum across the entire ray serves as the final penumbra estimate. The k value controls penumbra softness.

```glsl
// Classic SDF soft shadow
// ro: shadow ray origin (surface position)
// rd: light direction (normalized)
// mint: starting offset (to avoid self-shadowing)
// tmax: maximum march distance
float calcSoftShadow(vec3 ro, vec3 rd, float mint, float tmax) {
    float res = 1.0;
    float t = mint;

    for (int i = 0; i < MAX_SHADOW_STEPS; i++) {
        float h = map(ro + rd * t);
        float s = clamp(SHADOW_K * h / t, 0.0, 1.0);
        res = min(res, s);
        t += clamp(h, MIN_STEP, MAX_STEP);    // Step size clamping
        if (res < 0.004 || t > tmax) break;    // Early exit
    }

    res = clamp(res, 0.0, 1.0);
    return res * res * (3.0 - 2.0 * res);      // Smoothstep smoothing
}
```

### Step 3: Improved Soft Shadow (Geometric Triangulation)

**What**: Use SDF values from the current and previous steps to estimate a more accurate nearest point position via geometric triangulation, eliminating penumbra artifacts near sharp edges.

**Why**: The classic `h/t` formula assumes the nearest surface point is directly below the current sample position, but the actual nearest point may lie between two steps. Using the intersection relationship of SDF spheres from two adjacent steps provides a more accurate estimate of perpendicular distance `d` and corrected depth `t-y` along the ray.

```glsl
// Improved SDF soft shadow
float calcSoftShadowImproved(vec3 ro, vec3 rd, float mint, float tmax, float w) {
    float res = 1.0;
    float t = mint;
    float ph = 1e10;  // Previous step SDF value, initialized large so first step y≈0

    for (int i = 0; i < MAX_SHADOW_STEPS; i++) {
        float h = map(ro + rd * t);

        // Geometric triangulation: estimate corrected nearest distance
        float y = h * h / (2.0 * ph);         // Step-back distance along ray
        float d = sqrt(h * h - y * y);         // True nearest distance perpendicular to ray
        res = min(res, d / (w * max(0.0, t - y)));

        ph = h;                                // Save current h for next step
        t += h;

        if (res < 0.0001 || t > tmax) break;
    }

    res = clamp(res, 0.0, 1.0);
    return res * res * (3.0 - 2.0 * res);
}
```

### Step 4: Negative Extension Version (Smoothest Penumbra)

**What**: Allow the shadow factor to drop into the negative range [-1, 0], then remap to [0, 1] with a custom quadratic smooth function, eliminating hard creases.

**Why**: The classic method produces a C0 continuous (non-smooth) crease at `clamp(0,1)`. By allowing `res` to enter the negative domain and remapping with the C1 continuous function `0.25*(1+res)²*(2-res)`, a completely smooth penumbra gradient is achieved.

```glsl
// Negative extension soft shadow
float calcSoftShadowSmooth(vec3 ro, vec3 rd, float mint, float tmax, float w) {
    float res = 1.0;
    float t = mint;

    for (int i = 0; i < MAX_SHADOW_STEPS; i++) {
        float h = map(ro + rd * t);
        res = min(res, h / (w * t));
        t += clamp(h, MIN_STEP, MAX_STEP);
        if (res < -1.0 || t > tmax) break;    // Allow res to drop to -1
    }

    res = max(res, -1.0);                      // Clamp to [-1, 1]
    return 0.25 * (1.0 + res) * (1.0 + res) * (2.0 - res);  // Smooth remapping
}
```

### Step 5: Bounding Volume Optimization

**What**: Before starting the march, use simple geometric tests (plane clipping or AABB ray intersection) to narrow the shadow ray's effective range.

**Why**: If the shadow ray cannot possibly hit any object outside a bounded region (e.g., above the scene is empty), `tmax` can be shortened early or 1.0 returned immediately, saving many march iterations.

```glsl
// Method A: Plane clipping — clip ray to scene upper bound plane
float tp = (SCENE_Y_MAX - ro.y) / rd.y;
if (tp > 0.0) tmax = min(tmax, tp);

// Method B: AABB bounding box clipping
vec2 iBox(vec3 ro, vec3 rd, vec3 rad) {
    vec3 m = 1.0 / rd;
    vec3 n = m * ro;
    vec3 k = abs(m) * rad;
    vec3 t1 = -n - k;
    vec3 t2 = -n + k;
    float tN = max(max(t1.x, t1.y), t1.z);
    float tF = min(min(t2.x, t2.y), t2.z);
    if (tN > tF || tF < 0.0) return vec2(-1.0);
    return vec2(tN, tF);
}

// Usage in shadow function
vec2 dis = iBox(ro, rd, BOUND_SIZE);
if (dis.y < 0.0) return 1.0;       // Ray completely misses bounding box
tmin = max(tmin, dis.x);
tmax = min(tmax, dis.y);
```

### Step 6: Shadow Color Rendering (Color Bleeding)

**What**: Instead of using a uniform scalar shadow value, apply different shadow attenuation curves to the RGB channels.

**Why**: In the real world, penumbra regions exhibit a warm color shift due to subsurface scattering and atmospheric effects — red light penetrates the most while blue light is blocked first. By applying per-channel power operations on the shadow value, this physical phenomenon can be approximated at low cost.

```glsl
// Method A: Classic color shadow
vec3 warmShadow = pow(vec3(shadow), vec3(1.2, 1.0, 0.8));
col *= warmShadow;
```

### Step 5: Composite with Lighting

**What**: Multiply diffuse/specular by shadow factor in the final shade function.

```glsl
float sha = softShadow(p, l, 0.02, 2.5, 16.0);
vec3 col = base * (0.15 + 0.85 * sha);
```

## Gotchas

- Hard shadow binary tests alias at grazing angles — widen penumbra with `smoothstep` or PCF kernel width tied to `fwidth`.
- Shadow rays sharing surface normal bias self-intersect — offset origin along normal by epsilon scaled to scene units.
- Colored shadow tint on uncorrected HDR lighting clips warm channels — tone-map or clamp after composite.

## Combine With

- [lighting-model](lighting-model.md)
- [ray-marching](ray-marching.md)
