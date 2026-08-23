# csg-boolean-operations: CSG Boolean Operations

## Guideline

CSG boolean operations are per-point value operations on two distance fields:

## Rationale


| Operation | Expression | Meaning |
|-----------|-----------|---------|
| Union | `min(d1, d2)` | Take nearest surface, keeping both shapes |
| Intersection | `max(d1, d2)` | Take farthest surface, keeping only the overlap |
| Subtraction | `max(d1, -d2)` | Cut d1 using the interior of d2 |

**Smooth booleans** (smooth min/max) introduce a blending band in the transition region. The parameter `k` controls the blend band width (larger = rounder, `k=0` degenerates to hard boolean). Multiple variants exist with different mathematical properties.

## How to Apply


1. **Step 1: Hard Boolean Operations** — Implement the three basic boolean operations — union, intersection, subtraction.
2. **Step 2: Smooth Union — Polynomial Version** — Implement a union operation with a blend transition, producing rounded junctions between two shapes.
3. **Step 3: Smooth Subtraction and Smooth Intersection — Polynomial Version** — Extend the smooth union approach to subtraction and intersection.
4. **Step 4: Quadratic Optimized Smooth Operations** — Implement smin/smax using a more compact quadratic polynomial formula.
5. **Step 5: Basic SDF Primitives** — Define the basic shape SDFs used for combination.
6. **Step 6: CSG Combination for Scene Construction** — Combine primitives with boolean operations to build complex geometry.
7. **Step 7: Organic Body Modeling with Smooth CSG** — Use smin/smax with different k values to blend multiple ellipsoids/capsules into organic characters.
8. **Step 8: Ray Marching Main Loop** — Render the SDF scene using the sphere tracing algorithm.

## Example

```glsl
// === CSG Boolean Operations - // Note: When generating HTML with this template, pass uTime, uResolution, etc. via uniforms

#define MAX_STEPS 128
#define MAX_DIST 50.0
#define SURF_DIST 0.001
#define SMOOTH_K 0.1

// === Hard Boolean Operations ===
float opUnion(float d1, float d2) { return min(d1, d2); }
float opIntersection(float d1, float d2) { return max(d1, d2); }
float opSubtraction(float d1, float d2) { return max(d1, -d2); }

// === Smooth Boolean Operations (Quadratic Optimized) ===
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}

float smax(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return max(a, b) + h * h * 0.25 / k;
}

// === SDF Primitives ===
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

float sdCylinder(vec3 p, float h, float r) {
    vec2 d = abs(vec2(length(p.xz), p.y)) - vec2(r, h);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}

float sdEllipsoid(vec3 p, vec3 r) {
    float k0 = length(p / r);
    float k1 = length(p / (r * r));
    return k0 * (k0 - 1.0) / k1;
}

float sdCapsule(vec3 p, vec3 a, vec3 b, float r) {
    vec3 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

// === Scene Definition ===
float mapScene(vec3 p) {
    // Rotation animation
    float angle = uTime * 0.3;
    float c = cos(angle), s = sin(angle);
    p.xz = mat2(c, -s, s, c) * p.xz;

    // Primitives
    float cube = sdBox(p, vec3(1.0));
    float sphere = sdSphere(p, 1.25);
    float cylR = 0.45;
    float cylX = sdCylinder(p.yzx, 2.0, cylR);
    float cylY = sdCylinder(p.xyz, 2.0, cylR);
    float cylZ = sdCylinder(p.zxy, 2.0, cylR);

    // Hard boolean combination: nut = (cube intersect sphere) - three cylinders
    float nut = opSubtraction(
        opIntersection(cube, sphere),
        opUnion(cylX, opUnion(cylY, cylZ))
    );

    // Organic spheres -- smooth union blending
    float blob1 = sdSphere(p - vec3(1.8, 0.0, 0.0), 0.4);
    float blob2 = sdSphere(p - vec3(-1.8, 0.0, 0.0), 0.4);
    float blob3 = sdSphere(p - vec3(0.0, 1.8, 0.0), 0.4);
    float blobs = smin(blob1, smin(blob2, blob3, 0.3), 0.3);

    return smin(nut, blobs, 0.15);
}

// === Normal Calculation (Tetrahedral Sampling) ===
vec3 calcNormal(vec3 pos) {
    vec2 e = vec2(0.001, -0.001);
    return normalize(
        e.xyy * mapScene(pos + e.xyy) +
        e.yyx * mapScene(pos + e.yyx) +
        e.yxy * mapScene(pos + e.yxy) +
        e.xxx * mapScene(pos + e.xxx)
    );
}

// === Ray Marching ===
float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * t;
        float d = mapScene(p);
        if (d < SURF_DIST) return t;
        t += d;
        if (t > MAX_DIST) break;
    }
    return -1.0;
}

// === Soft Shadows ===
float calcSoftShadow(vec3 ro, vec3 rd, float k) {
    float res = 1.0;
    float t = 0.02;
    for (int i = 0; i < 64; i++) {
        float h = mapScene(ro + rd * t);
        res = min(res, k * h / t);
        t += clamp(h, 0.01, 0.2);
        if (res < 0.001 || t > 20.0) break;
    }
    return clamp(res, 0.0, 1.0);
}

// === AO (Ambient Occlusion) ===
float calcAO(vec3 pos, vec3 nor) {
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.12 * float(i);
        float d = mapScene(pos + h * nor);
        occ += (h - d) * sca;
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

// === Main Function (out vec4 outColor;
void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * uResolution.xy) / uResolution.y;

    // Camera
    float camDist = 4.0;
    float camAngle = 0.3;
    vec3 ro = vec3(
        camDist * cos(uTime * 0.2),
        camDist * sin(camAngle),
        camDist * sin(uTime * 0.2)
    );
    vec3 ta = vec3(0.0, 0.0, 0.0);

    // Camera matrix
    vec3 ww = normalize(ta - ro);
    vec3 uu = normalize(cross(ww, vec3(0.0, 1.0, 0.0)));
    vec3 vv = cross(uu, ww);
    vec3 rd = normalize(uv.x * uu + uv.y * vv + 2.0 * ww);

    // Background color
    vec3 col = vec3(0.4, 0.5, 0.6) - 0.3 * rd.y;

    // Ray marching
    float t = rayMarch(ro, rd);
    if (t > 0.0) {
        vec3 pos = ro + rd * t;
        vec3 nor = calcNormal(pos);

        vec3 lightDir = normalize(vec3(0.8, 0.6, -0.3));
        float dif = clamp(dot(nor, lightDir), 0.0, 1.0);
        float sha = calcSoftShadow(pos + nor * 0.01, lightDir, 16.0);
        float ao = calcAO(pos, nor);
        float amb = 0.5 + 0.5 * nor.y;

        vec3 mate = vec3(0.2, 0.3, 0.4);
        col = vec3(0.0);
        col += mate * 2.0 * dif * sha;
        col += mate * 0.3 * amb * ao;
    }

    col = pow(col, vec3(0.4545));
    outColor = vec4(col, 1.0);
}
```

```glsl
float opUnion(float d1, float d2) { return min(d1, d2); }
float opIntersection(float d1, float d2) { return max(d1, d2); }
float opSubtraction(float d1, float d2) { return max(d1, -d2); }
```

```glsl
// k: blend radius, typical values 0.05~0.5
float opSmoothUnion(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}
```

## Advanced

### Step 1: Hard Boolean Operations

**What**: Implement the three basic boolean operations — union, intersection, subtraction.

**Why**: These are the foundation of all CSG operations. `min` selects the nearest surface to achieve union; `max` selects the farthest surface for intersection; negating the second operand and taking `max` with the first achieves subtraction (keeping the region of d1 that is not inside d2).

```glsl
// Union: keep both shapes
float opUnion(float d1, float d2) {
    return min(d1, d2);
}

// Intersection: keep only the overlapping region
float opIntersection(float d1, float d2) {
    return max(d1, d2);
}

// Subtraction: carve d2 out of d1
float opSubtraction(float d1, float d2) {
    return max(d1, -d2);
}
```

### Step 2: Smooth Union — Polynomial Version

**What**: Implement a union operation with a blend transition, producing rounded junctions between two shapes.

**Why**: Hard `min` produces C0 continuity (sharp creases) at the SDF junction. Polynomial smooth min interpolates within the transition band where `|d1-d2| < k`, producing C1 continuity (smooth transitions). In the formula, `h` is the normalized blend factor, and the `k*h*(1-h)` term ensures the distance field correctly dips in the transition region (producing more accurate distance values than plain `mix`).

```glsl
// Polynomial smooth union
// k: blend radius, typical values 0.05~0.5
float opSmoothUnion(float d1, float d2, float k) {
    float h = clamp(0.5 + 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) - k * h * (1.0 - h);
}
```

### Step 3: Smooth Subtraction and Smooth Intersection — Polynomial Version

**What**: Extend the smooth union approach to subtraction and intersection.

**Why**: Subtraction = intersection with an inverted SDF; intersection = inverted union of inverted inputs. The sign changes in the formulas reflect this duality. Note that subtraction uses `d2+d1` (not `d2-d1`), because d1 is negated in the operation.

```glsl
// Smooth subtraction: smoothly carve d2 out of d1
float opSmoothSubtraction(float d1, float d2, float k) {
    float h = clamp(0.5 - 0.5 * (d2 + d1) / k, 0.0, 1.0);
    return mix(d2, -d1, h) + k * h * (1.0 - h);
}

// Smooth intersection: smoothly keep the overlapping region
float opSmoothIntersection(float d1, float d2, float k) {
    float h = clamp(0.5 - 0.5 * (d2 - d1) / k, 0.0, 1.0);
    return mix(d2, d1, h) + k * h * (1.0 - h);
}
```

### Step 4: Quadratic Optimized Smooth Operations

**What**: Implement smin/smax using a more compact quadratic polynomial formula.

**Why**: This version is mathematically equivalent but more concise with fewer branches. `h = max(k - abs(a-b), 0.0)` directly computes the influence within the transition band, being non-zero only when `|a-b| < k`. `h*h*0.25/k` is the quadratic correction term. smax can be derived directly through smin's duality: `smax(a,b,k) = -smin(-a,-b,k)`.

```glsl
// Quadratic optimized smooth union
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}

// Quadratic optimized smooth intersection / smooth max
float smax(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return max(a, b) + h * h * 0.25 / k;
}

// Subtraction via smax
float sSub(float d1, float d2, float k) {
    return smax(d1, -d2, k);
}
```

### Step 5: Basic SDF Primitives

**What**: Define the basic shape SDFs used for combination.

**Why**: CSG needs operands. Spheres and boxes are the most common primitives; cylinders are often used for drilling holes.

```glsl
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

float sdCylinder(vec3 p, float h, float r) {
    vec2 d = abs(vec2(length(p.xz), p.y)) - vec2(r, h);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}
```

### Step 6: CSG Combination for Scene Construction

**What**: Combine primitives with boolean operations to build complex geometry.

**Why**: The power of CSG lies in combination. Classic example: intersecting a sphere with a cube yields a rounded cube, then subtracting three cylinders produces a nut shape.

```glsl
float mapScene(vec3 p) {
    // Primitives
    float cube = sdBox(p, vec3(1.0));
    float sphere = sdSphere(p, 1.2);
    float cylX = sdCylinder(p.yzx, 2.0, 0.4); // Along X axis
    float cylY = sdCylinder(p.xyz, 2.0, 0.4); // Along Y axis
    float cylZ = sdCylinder(p.zxy, 2.0, 0.4); // Along Z axis

    // CSG combination: (Cube ∩ Sphere) - three cylinders
    float shape = opIntersection(cube, sphere);
    float holes = opUnion(cylX, opUnion(cylY, cylZ));
    return opSubtraction(shape, holes);
}
```

### Step 7: Organic Body Modeling with Smooth CSG

**What**: Use smin/smax with different k values to blend multiple ellipsoids/capsules into organic characters.

**Why**: Different body parts need different blend amounts — large k values for broad connections (torso-legs), small k values for fine details (eyes-head). This is the core technique for organic character modeling with smooth CSG.

```glsl
float mapCreature(vec3 p) {
    // Torso
    float body = sdSphere(p, 0.5);

    // Head — larger blend radius
    float head = sdSphere(p - vec3(0.0, 0.6, 0.3), 0.25);
    float d = smin(body, head, 0.15);

    // Limbs — medium blend radius
    float leg = sdCylinder(p - vec3(0.2, -0.5, 0.0), 0.3, 0.08);
    d = smin(d, leg, 0.08);

    // Eye sockets — small blend radius for smooth subtraction
    float eye = sdSphere(p - vec3(0.05, 0.75, 0.4), 0.05);
    d = smax(d, -eye, 0.02);

    return d;
}
```

### Step 8: Ray Marching Main Loop

**What**: Render the SDF scene using the sphere tracing algorithm.

**Why**: SDF scenes cannot be rendered with traditional rasterization. Ray Marching is needed: cast a ray from each pixel, advance by the current point's distance to the nearest surface (i.e., the SDF value)

 without surface penetration.

```glsl
float t = 0.0;
for (int i = 0; i < MAX_STEPS; i++) {
    vec3 p = ro + rd * t;
    float d = map(p);
    if (d < SURF_DIST) break;
    t += d;
}
```

### Step 9: Shading and Output

**What**: Compute normals and shade CSG hit; write `fragColor`.

```glsl
vec3 p = ro + rd * t;
vec3 n = calcNormal(p);
float diff = clamp(dot(n, normalize(vec3(0.5, 0.8, 0.3))), 0.0, 1.0);
fragColor = vec4(vec3(0.7) * diff + 0.1, 1.0);
```

## Gotchas

- Sharp `min`/`max` booleans create C1-discontinuous normals — add `smin`/`smax` or bevel for lit surfaces.
- Subtracting a large primitive from a small one can erase the entire field — verify operand scale before CSG.
- Nested booleans without intermediate grouping change evaluation order — parenthesize with helper SDF functions.

## Combine With

- [sdf-3d](sdf-3d.md)
- [domain-repetition](domain-repetition.md)
