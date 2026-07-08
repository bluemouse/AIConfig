# sdf-3d: 3D Signed Distance Functions

## Guideline


Model 3D surfaces with signed distance functions — positive outside, negative inside, zero on the surface — then combine primitives with CSG and smooth blends.

## Rationale

An SDF returns the **signed distance** from any point in space to the nearest surface: positive = outside, negative = inside, zero = surface.

**Sphere Tracing**: advance along a ray, stepping by the current SDF value (the safe marching distance) at each step. The SDF guarantees no surface exists within that radius. A hit is registered when the distance falls below epsilon.

Key math:
- Sphere: `f(p) = |p| - r`
- Box: `f(p) = |max(|p|-b, 0)| + min(max(|p-b|), 0)`
- Union: `min(d1, d2)` / Subtraction: `max(d1, -d2)`
- Smooth union: `min(d1,d2) - h^2/4k`, `h = max(k-|d1-d2|, 0)`
- Normal = SDF gradient: `n = normalize(gradient of f(p))` (finite difference approximation)

## How to Apply


1. **Step 1: SDF Primitive Library** — Define basic geometric distance functions.
2. **Step 2: Boolean Operations and Smooth Blending** — Define combination operations between primitives — union, subtraction, intersection, and their smooth variants.
3. **Step 3: Scene Definition (map Function)** — Write the `map()` function that combines the above primitives and operations into a complete 3D scene.
4. **Step 4: Raymarching** — Implement the sphere tracing loop — cast a ray from the camera and step along the ray direction until hitting a surface or exceeding the maximum distance.
5. **Step 5: Normal Computation** — Compute the surface normal at the hit point by taking the finite-difference gradient of the SDF.

## Example

```glsl
// Stage: fragment | Version: 450 | Uniforms: uResolution, uTime, uFrame, uMouse
#define AA 1                // Anti-aliasing (1=off, 2=4xAA, 3=9xAA)
#define MAX_STEPS 128
#define MAX_DIST 40.0
#define SURF_DIST 0.0001
#define SHADOW_STEPS 24
#define SHADOW_SOFTNESS 8.0
#define SMOOTH_K 0.3
#define ZERO (min(uFrame, 0))

// === SDF Primitives ===
float sdSphere(vec3 p, float r) { return length(p) - r; }
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}
float sdEllipsoid(vec3 p, vec3 r) {
    float k0 = length(p / r); float k1 = length(p / (r * r));
    return k0 * (k0 - 1.0) / k1;
}
float sdTorus(vec3 p, vec2 t) {
    return length(vec2(length(p.xz) - t.x, p.y)) - t.y;
}
float sdCapsule(vec3 p, vec3 a, vec3 b, float r) {
    vec3 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}
float sdCylinder(vec3 p, vec2 h) {
    vec2 d = abs(vec2(length(p.xz), p.y)) - h;
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}

// === Extended SDF Primitives ===
float sdRoundBox(vec3 p, vec3 b, float r) {
    vec3 q = abs(p) - b + r;
    return length(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0) - r;
}

float sdBoxFrame(vec3 p, vec3 b, float e) {
    p = abs(p) - b;
    vec3 q = abs(p + e) - e;
    return min(min(
        length(max(vec3(p.x, q.y, q.z), 0.0)) + min(max(p.x, max(q.y, q.z)), 0.0),
        length(max(vec3(q.x, p.y, q.z), 0.0)) + min(max(q.x, max(p.y, q.z)), 0.0)),
        length(max(vec3(q.x, q.y, p.z), 0.0)) + min(max(q.x, max(q.y, p.z)), 0.0));
}

float sdCone(vec3 p, vec2 c, float h) {
    vec2 q = h * vec2(c.x / c.y, -1.0);
    vec2 w = vec2(length(p.xz), p.y);
    vec2 a = w - q * clamp(dot(w, q) / dot(q, q), 0.0, 1.0);
    vec2 b = w - q * vec2(clamp(w.x / q.x, 0.0, 1.0), 1.0);
    float k = sign(q.y);
    float d = min(dot(a, a), dot(b, b));
    float s = max(k * (w.x * q.y - w.y * q.x), k * (w.y - q.y));
    return sqrt(d) * sign(s);
}

float sdCappedCone(vec3 p, float h, float r1, float r2) {
    vec2 q = vec2(length(p.xz), p.y);
    vec2 k1 = vec2(r2, h);
    vec2 k2 = vec2(r2 - r1, 2.0 * h);
    vec2 ca = vec2(q.x - min(q.x, (q.y < 0.0) ? r1 : r2), abs(q.y) - h);
    vec2 cb = q - k1 + k2 * clamp(dot(k1 - q, k2) / dot(k2, k2), 0.0, 1.0);
    float s = (cb.x < 0.0 && ca.y < 0.0) ? -1.0 : 1.0;
    return s * sqrt(min(dot(ca, ca), dot(cb, cb)));
}

float sdRoundCone(vec3 p, float r1, float r2, float h) {
    float b = (r1 - r2) / h;
    float a = sqrt(1.0 - b * b);
    vec2 q = vec2(length(p.xz), p.y);
    float k = dot(q, vec2(-b, a));
    if (k < 0.0) return length(q) - r1;
    if (k > a * h) return length(q - vec2(0.0, h)) - r2;
    return dot(q, vec2(a, b)) - r1;
}

float sdSolidAngle(vec3 p, vec2 c, float ra) {
    vec2 q = vec2(length(p.xz), p.y);
    float l = length(q) - ra;
    float m = length(q - c * clamp(dot(q, c), 0.0, ra));
    return max(l, m * sign(c.y * q.x - c.x * q.y));
}

float sdOctahedron(vec3 p, float s) {
    p = abs(p);
    float m = p.x + p.y + p.z - s;
    vec3 q;
    if (3.0 * p.x < m) q = p.xyz;
    else if (3.0 * p.y < m) q = p.yzx;
    else if (3.0 * p.z < m) q = p.zxy;
    else return m * 0.57735027;
    float k = clamp(0.5 * (q.z - q.y + s), 0.0, s);
    return length(vec3(q.x, q.y - s + k, q.z - k));
}

float sdPyramid(vec3 p, float h) {
    float m2 = h * h + 0.25;
    p.xz = abs(p.xz);
    p.xz = (p.z > p.x) ? p.zx : p.xz;
    p.xz -= 0.5;
    vec3 q = vec3(p.z, h * p.y - 0.5 * p.x, h * p.x + 0.5 * p.y);
    float s = max(-q.x, 0.0);
    float t = clamp((q.y - 0.5 * p.z) / (m2 + 0.25), 0.0, 1.0);
    float a = m2 * (q.x + s) * (q.x + s) + q.y * q.y;
    float b = m2 * (q.x + 0.5 * t) * (q.x + 0.5 * t) + (q.y - m2 * t) * (q.y - m2 * t);
    float d2 = min(q.y, -q.x * m2 - q.y * 0.5) > 0.0 ? 0.0 : min(a, b);
    return sqrt((d2 + q.z * q.z) / m2) * sign(max(q.z, -p.y));
}

float sdHexPrism(vec3 p, vec2 h) {
    const vec3 k = vec3(-0.8660254, 0.5, 0.57735);
    p = abs(p);
    p.xy -= 2.0 * min(dot(k.xy, p.xy), 0.0) * k.xy;
    vec2 d = vec2(length(p.xy - vec2(clamp(p.x, -k.z * h.x, k.z * h.x), h.x)) * sign(p.y - h.x), p.z - h.y);
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}

float sdCutSphere(vec3 p, float r, float h) {
    float w = sqrt(r * r - h * h);
    vec2 q = vec2(length(p.xz), p.y);
    float s = max((h - r) * q.x * q.x + w * w * (h + r - 2.0 * q.y), h * q.x - w * q.y);
    return (s < 0.0) ? length(q) - r : (q.x < w) ? h - q.y : length(q - vec2(w, h));
}

float sdCappedTorus(vec3 p, vec2 sc, float ra, float rb) {
    p.x = abs(p.x);
    float k = (sc.y * p.x > sc.x * p.y) ? dot(p.xy, sc) : length(p.xy);
    return sqrt(dot(p, p) + ra * ra - 2.0 * ra * k) - rb;
}

float sdLink(vec3 p, float le, float r1, float r2) {
    vec3 q = vec3(p.x, max(abs(p.y) - le, 0.0), p.z);
    return length(vec2(length(q.xy) - r1, q.z)) - r2;
}

float sdPlane(vec3 p, vec3 n, float h) {
    return dot(p, n) + h;
}

float sdRhombus(vec3 p, float la, float lb, float h, float ra) {
    p = abs(p);
    vec2 b = vec2(la, lb);
    float f = clamp((dot(b, b - 2.0 * p.xz)) / dot(b, b), -1.0, 1.0);
    vec2 q = vec2(length(p.xz - 0.5 * b * vec2(1.0 - f, 1.0 + f)) * sign(p.x * b.y + p.z * b.x - b.x * b.y) - ra, p.y - h);
    return min(max(q.x, q.y), 0.0) + length(max(q, 0.0));
}

// Unsigned distance (exact)
float udTriangle(vec3 p, vec3 a, vec3 b, vec3 c) {
    vec3 ba = b - a; vec3 pa = p - a;
    vec3 cb = c - b; vec3 pb = p - b;
    vec3 ac = a - c; vec3 pc = p - c;
    vec3 nor = cross(ba, ac);
    return sqrt(
        (sign(dot(cross(ba, nor), pa)) +
         sign(dot(cross(cb, nor), pb)) +
         sign(dot(cross(ac, nor), pc)) < 2.0)
        ? min(min(
            dot(ba * clamp(dot(ba, pa) / dot(ba, ba), 0.0, 1.0) - pa,
                ba * clamp(dot(ba, pa) / dot(ba, ba), 0.0, 1.0) - pa),
            dot(cb * clamp(dot(cb, pb) / dot(cb, cb), 0.0, 1.0) - pb,
                cb * clamp(dot(cb, pb) / dot(cb, cb), 0.0, 1.0) - pb)),
            dot(ac * clamp(dot(ac, pc) / dot(ac, ac), 0.0, 1.0) - pc,
                ac * clamp(dot(ac, pc) / dot(ac, ac), 0.0, 1.0) - pc))
        : dot(nor, pa) * dot(nor, pa) / dot(nor, nor));
}

// === Boolean Operations ===
vec2 opU(vec2 d1, vec2 d2) { return (d1.x < d2.x) ? d1 : d2; }
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}
vec2 smin(vec2 a, vec2 b, float k) {
    // vec2 smin: x=distance (smooth blend), y=materialID (take material of closer distance)
    float h = max(k - abs(a.x - b.x), 0.0);
    float d = min(a.x, b.x) - h * h * 0.25 / k;
    float m = (a.x < b.x) ? a.y : b.y;
    return vec2(d, m);
}
float smax(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return max(a, b) + h * h * 0.25 / k;
}

// === Deformation Operators ===

// Round: soften edges of any SDF
// Usage: sdRound(sdBox(p, vec3(1.0)), 0.1)
float opRound(float d, float r) { return d - r; }

// Onion: hollow out any SDF into a shell
// Usage: opOnion(sdSphere(p, 1.0), 0.1) — sphere shell of thickness 0.1
float opOnion(float d, float t) { return abs(d) - t; }

// Elongate: stretch a shape along axes
// Usage: elongate a sphere into a capsule-like shape
float opElongate(in vec3 p, in vec3 h, in vec3 center, in vec3 size) {
    // Generic elongation: subtract h from abs(p), clamp to 0
    vec3 q = abs(p) - h;
    // Then evaluate original SDF with max(q, 0.0)
    // Return: sdOriginal(max(q, 0.0)) + min(max(q.x, max(q.y, q.z)), 0.0)
    return sdBox(max(q, 0.0), size) + min(max(q.x, max(q.y, q.z)), 0.0); // example with box
}

// Twist: rotate around Y axis based on height
vec3 opTwist(vec3 p, float k) {
    float c = cos(k * p.y);
    float s = sin(k * p.y);
    mat2 m = mat2(c, -s, s, c);
    return vec3(m * p.xz, p.y);
}

// Cheap Bend: bend along X axis based on X position
vec3 opCheapBend(vec3 p, float k) {
    float c = cos(k * p.x);
    float s = sin(k * p.x);
    mat2 m = mat2(c, -s, s, c);
    vec2 q = m * p.xy;
    return vec3(q, p.z);
}

// Displacement: add procedural detail to surface
float opDisplace(float d, vec3 p) {
    float displacement = sin(20.0 * p.x) * sin(20.0 * p.y) * sin(20.0 * p.z);
    return d + displacement * 0.02;
}

// === 2D-to-3D Constructors ===

// Revolution: rotate a 2D SDF around the Y axis to create a 3D solid of revolution
// sdf2d: any 2D SDF function, o: offset from axis
float opRevolution(vec3 p, float sdf2d_result, float o) {
    vec2 q = vec2(length(p.xz) - o, p.y);
    // Example: revolve a 2D circle to make a torus
    // float d2d = length(q) - 0.3;  // 2D circle as cross-section
    // return d2d;
    return sdf2d_result; // pass pre-computed 2D SDF of vec2(length(p.xz)-o, p.y)
}

// Extrusion: extend a 2D SDF along the Z axis with finite height
float opExtrusion(vec3 p, float d2d, float h) {
    vec2 w = vec2(d2d, abs(p.z) - h);
    return min(max(w.x, w.y), 0.0) + length(max(w, 0.0));
}

// Usage example: extruded 2D star
// float d2d = sdStar2D(p.xy, 0.5, 5, 2.0);  // any 2D SDF
// float d3d = opExtrusion(p, d2d, 0.2);       // extrude 0.2 units

// === Symmetry Operators ===

// Mirror across X axis (most common — bilateral symmetry)
// Place this at the beginning of map() to model only one half
vec3 opSymX(vec3 p) { p.x = abs(p.x); return p; }

// Mirror across X and Z (four-fold symmetry)
vec3 opSymXZ(vec3 p) { p.xz = abs(p.xz); return p; }

// Mirror across arbitrary direction
vec3 opMirror(vec3 p, vec3 dir) {
    return p - 2.0 * dir * max(dot(p, dir), 0.0);
}

// === Scene ===
vec2 map(vec3 pos) {
    vec2 res = vec2(pos.y, 0.0);
    // Animated blob cluster
    float dBlob = 2.0;
    for (int i = 0; i < 8; i++) {
        float fi = float(i);
        float t = uTime * (fract(fi * 412.531 + 0.513) - 0.5) * 2.0;
        vec3 offset = sin(t + fi * vec3(52.5126, 64.627, 632.25)) * vec3(2.0, 2.0, 0.8);
        float radius = mix(0.3, 0.6, fract(fi * 412.531 + 0.5124));
        dBlob = smin(dBlob, sdSphere(pos + offset, radius), SMOOTH_K);
    }
    res = opU(res, vec2(dBlob, 1.0));
    float dBox = sdBox(pos - vec3(3.0, 0.4, 0.0), vec3(0.3, 0.4, 0.3));
    res = opU(res, vec2(dBox, 2.0));
    float dTorus = sdTorus((pos - vec3(-3.0, 0.5, 0.0)).xzy, vec2(0.4, 0.1));
    res = opU(res, vec2(dTorus, 3.0));
    // CSG subtraction: sphere minus box
    float dCSG = sdSphere(pos - vec3(0.0, 0.5, 3.0), 0.5);
    dCSG = max(dCSG, -sdBox(pos - vec3(0.0, 0.5, 3.0), vec3(0.3)));
    res = opU(res, vec2(dCSG, 4.0));
    return res;
}

// === Normals ===
vec3 calcNormal(vec3 pos) {
    vec3 n = vec3(0.0);
    for (int i = ZERO; i < 4; i++) {
        vec3 e = 0.5773 * (2.0 * vec3((((i+3)>>1)&1), ((i>>1)&1), (i&1)) - 1.0);
        n += e * map(pos + 0.0005 * e).x;
    }
    return normalize(n);
}

// === Shadows ===
float calcSoftshadow(vec3 ro, vec3 rd, float mint, float tmax) {
    float res = 1.0, t = mint;
    for (int i = ZERO; i < SHADOW_STEPS; i++) {
        float h = map(ro + rd * t).x;
        float s = clamp(SHADOW_SOFTNESS * h / t, 0.0, 1.0);
        res = min(res, s);
        t += clamp(h, 0.01, 0.2);
        if (res < 0.004 || t > tmax) break;
    }
    res = clamp(res, 0.0, 1.0);
    return res * res * (3.0 - 2.0 * res);
}

// === AO ===
float calcAO(vec3 pos, vec3 nor) {
    float occ = 0.0, sca = 1.0;
    for (int i = ZERO; i < 5; i++) {
        float h = 0.01 + 0.12 * float(i) / 4.0;
        float d = map(pos + h * nor).x;
        occ += (h - d) * sca;
        sca *= 0.95;
        if (occ > 0.35) break;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0) * (0.5 + 0.5 * nor.y);
}

// === Ray Marching ===
vec2 raycast(vec3 ro, vec3 rd) {
    vec2 res = vec2(-1.0);
    float t = 0.01;
    for (int i = 0; i < MAX_STEPS && t < MAX_DIST; i++) {
        vec2 h = map(ro + rd * t);
        if (abs(h.x) < SURF_DIST * t) { res = vec2(t, h.y); break; }
        t += h.x;
    }
    return res;
}

// === Camera ===
mat3 setCamera(vec3 ro, vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = cross(cu, cw);
    return mat3(cu, cv, cw);
}

// === Rendering ===
vec3 render(vec3 ro, vec3 rd) {
    vec3 col = vec3(0.7, 0.7, 0.9) - max(rd.y, 0.0) * 0.3;
    vec2 res = raycast(ro, rd);
    float t = res.x, m = res.y;
    if (m > -0.5) {
        vec3 pos = ro + t * rd;
        vec3 nor = (m < 0.5) ? vec3(0.0, 1.0, 0.0) : calcNormal(pos);
        vec3 ref = reflect(rd, nor);
        vec3 mate = 0.2 + 0.2 * sin(m * 2.0 + vec3(0.0, 1.0, 2.0));
        if (m < 0.5) mate = vec3(0.15);
        float occ = calcAO(pos, nor);
        vec3 lin = vec3(0.0);
        // Key light
        {
            vec3 lig = normalize(vec3(-0.5, 0.4, -0.6));
            vec3 hal = normalize(lig - rd);
            float dif = clamp(dot(nor, lig), 0.0, 1.0);
            dif *= calcSoftshadow(pos, lig, 0.02, 2.5);
            float spe = pow(clamp(dot(nor, hal), 0.0, 1.0), 16.0);
            spe *= dif * (0.04 + 0.96 * pow(clamp(1.0 - dot(hal, lig), 0.0, 1.0), 5.0));
            lin += mate * 2.20 * dif * vec3(1.30, 1.00, 0.70);
            lin += 5.00 * spe * vec3(1.30, 1.00, 0.70);
        }
        // Sky light
        {
            float dif = sqrt(clamp(0.5 + 0.5 * nor.y, 0.0, 1.0)) * occ;
            lin += mate * 0.60 * dif * vec3(0.40, 0.60, 1.15);
        }
        // Subsurface scattering approximation
        {
            float dif = pow(clamp(1.0 + dot(nor, rd), 0.0, 1.0), 2.0) * occ;
            lin += mate * 0.25 * dif;
        }
        col = lin;
        col = mix(col, vec3(0.7, 0.7, 0.9), 1.0 - exp(-0.0001 * t * t * t));
    }
    return clamp(col, 0.0, 1.0);
}

// === Main Function ===
void main() {
    vec2 mo = uMouse.xy / uResolution.xy;
    float time = 32.0 + uTime * 1.5;
    vec3 ta = vec3(0.0, 0.0, 0.0);
    vec3 ro = ta + vec3(4.5 * cos(0.1 * time + 7.0 * mo.x), 2.2,
                        4.5 * sin(0.1 * time + 7.0 * mo.x));
    mat3 ca = setCamera(ro, ta, 0.0);
    vec3 tot = vec3(0.0);
#if AA > 1
    for (int m = ZERO; m < AA; m++)
    for (int n = ZERO; n < AA; n++) {
        vec2 o = vec2(float(m), float(n)) / float(AA) - 0.5;
        vec2 p = (2.0 * (gl_FragCoord.xy + o) - uResolution.xy) / uResolution.y;
#else
        vec2 p = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
#endif
        vec3 rd = ca * normalize(vec3(p, 2.5));
        vec3 col = render(ro, rd);
        col = pow(col, vec3(0.4545));
        tot += col;
#if AA > 1
    }
    tot /= float(AA * AA);
#endif
    fragColor = vec4(tot, 1.0);
}
```

## Advanced

### Step 1: SDF Primitive Library

**What**: Define basic geometric distance functions.

**Why**: All SDF scenes are composed of basic primitives. Each primitive is a pure function that takes a point in space and returns the shortest distance to that primitive's surface. The accuracy of these primitives directly determines the efficiency of sphere tracing — accurate SDFs allow larger step sizes.

**Code**:

```glsl
// Sphere: p=sample point, r=radius
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

// Box: p=sample point, b=half-size (xyz dimensions)
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

// Ellipsoid (approximate): p=sample point, r=three-axis radii
float sdEllipsoid(vec3 p, vec3 r) {
    float k0 = length(p / r);
    float k1 = length(p / (r * r));
    return k0 * (k0 - 1.0) / k1;
}

// Torus: p=sample point, t.x=major radius, t.y=tube radius
float sdTorus(vec3 p, vec2 t) {
    return length(vec2(length(p.xz) - t.x, p.y)) - t.y;
}

// Capsule (two endpoints + radius): useful for skeleton/limb modeling
float sdCapsule(vec3 p, vec3 a, vec3 b, float r) {
    vec3 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

// Cylinder (vertical): h.x=radius, h.y=half-height
float sdCylinder(vec3 p, vec2 h) {
    vec2 d = abs(vec2(length(p.xz), p.y)) - h;
    return min(max(d.x, d.y), 0.0) + length(max(d, 0.0));
}

// Plane (y=0)
float sdPlane(vec3 p) {
    return p.y;
}
```

### Step 2: Boolean Operations and Smooth Blending

**What**: Define combination operations between primitives — union, subtraction, intersection, and their smooth variants.

**Why**: Union merges multiple primitives into one scene; subtraction carves one object out of another; intersection keeps the overlapping region. Smooth variants (`smin`/`smax`) use a control parameter `k` to produce smooth blend transitions — one of SDF's most powerful capabilities over traditional modeling, achieving organic forms without additional geometry.

**Code**:

```glsl
// === Hard Boolean Operations ===

// Union: take the nearer surface
float opUnion(float d1, float d2) { return min(d1, d2); }

// Subtraction: subtract d2 from d1
float opSubtraction(float d1, float d2) { return max(d1, -d2); }

// Intersection: keep the overlapping region
float opIntersection(float d1, float d2) { return max(d1, d2); }

// Union with material ID (vec2.x stores distance, vec2.y stores material ID)
vec2 opU(vec2 d1, vec2 d2) { return (d1.x < d2.x) ? d1 : d2; }

// === Smooth Boolean Operations ===

// Smooth union: k=blend radius (larger = smoother, typical values 0.1~0.5)
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}
// vec2 version of smin: for smooth blending of vec2(distance, materialID)
vec2 smin(vec2 a, vec2 b, float k) {
    float h = max(k - abs(a.x - b.x), 0.0);
    float d = min(a.x, b.x) - h * h * 0.25 / k;
    float m = (a.x < b.x) ? a.y : b.y;
    return vec2(d, m);
}

// Smooth subtraction / smooth max
float smax(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return max(a, b) + h * h * 0.25 / k;
}
```

### Step 3: Scene Definition (map Function)

**What**: Write the `map()` function that combines the above primitives and operations into a complete 3D scene.

**Why**: `map(p)` is the core of the SDF rendering pipeline — it returns the distance from any point p in space to the nearest scene surface (plus optional material information). Ray marching, normal computation, shadows, and AO all depend on this function. All geometric complexity of the scene is encapsulated here.

**Code**:

```glsl
// Returns vec2(distance, materialID)
vec2 map(vec3 p) {
    // Ground
    vec2 res = vec2(p.y, 0.0); // Material 0: ground

    // Sphere (displaced to y=0.5)
    float d1 = sdSphere(p - vec3(0.0, 0.5, 0.0), 0.4);
    res = opU(res, vec2(d1, 1.0)); // Material 1: sphere

    // Box
    float d2 = sdBox(p - vec3(1.5, 0.4, 0.0), vec3(0.3, 0.4, 0.3));
    res = opU(res, vec2(d2, 2.0)); // Material 2: box

    // Blend two spheres with smin for organic blob effect
    float d3 = sdSphere(p - vec3(-1.2, 0.5, 0.0), 0.3);
    float d4 = sdSphere(p - vec3(-1.5, 0.8, 0.2), 0.25);
    float dBlob = smin(d3, d4, 0.3);
    res = opU(res, vec2(dBlob, 3.0)); // Material 3: blob

    return res;
}
```

### Step 4: Raymarching

**What**: Implement the sphere tracing loop — cast a ray from the camera and step along the ray direction until hitting a surface or exceeding the maximum distance.

**Why**: Sphere tracing exploits the "safe distance" property of SDFs — the current SDF value tells us there is absolutely no surface within that radius, so we can safely advance that far. This is much more efficient than fixed-step volumetric ray marching, typically achieving precise results in 64-128 steps.

**Code**:

```glsl
#define MAX_STEPS 128      // Adjustable: step count, 64=fast/coarse, 256=precise/slow
#define MAX_DIST 40.0       // Adjustable: max trace distance
#define SURF_DIST 0.0001    // Adjustable: surface detection threshold

vec2 raycast(vec3 ro, vec3 rd) {
    vec2 res = vec2(-1.0, -1.0);
    float t = 0.01;

    for (int i = 0; i < MAX_STEPS && t < MAX_DIST; i++) {
        vec2 h = map(ro + rd * t);
        if (abs(h.x) < SURF_DIST * t) {
            res = vec2(t, h.y);
            break;
        }
        t += h.x; // Key: step distance = SDF value
    }
    return res; // .x=hit distance, .y=materialID; -1 means no hit
}
```

### Step 5: Normal Computation

**What**: Compute the surface normal at the hit point by taking the finite-difference gradient of the SDF.

**Why**: The gradient direction of the SDF is the surface normal direction. We use the tetrahedron trick (4 `map` calls) instead of central differences (6 calls), saving performance and avoiding compiler inline bloat from inlining `map()`

```glsl
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy).x - map(p - e.xyy).x,
        map(p + e.yxy).x - map(p - e.yxy).x,
        map(p + e.yyx).x - map(p - e.yyx).x
    ));
}
```

### Step 6: Lighting and main()

**What**: Shade hit point with diffuse/specular; assemble `main()` entry.

```glsl
vec3 shade(vec3 p, vec3 rd, float matId) {
    vec3 n = calcNormal(p);
    vec3 l = normalize(vec3(0.6, 0.7, 0.3));
    float diff = clamp(dot(n, l), 0.0, 1.0);
    return vec3(0.8) * diff + vec3(0.05);
}

void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    vec3 ro = vec3(0.0, 1.0, -3.0);
    vec3 rd = normalize(vec3(uv, 1.5));
    vec2 hit = raycast(ro, rd);
    vec3 col = hit.x > 0.0 ? shade(ro + rd * hit.x, rd, hit.y) : vec3(0.1);
    fragColor = vec4(col, 1.0);
}
```

## Gotchas

- Under-stepping in ray marching causes surface acne — tie step size to distance field magnitude and add epsilon at hit.
- Domain repetition without limiting iterations can march through infinite lattice copies — clamp loop bounds.
- Smooth CSG radii that exceed primitive size invert blends — keep blend radius smaller than the smaller operand.

## Combine With

- [csg-boolean-operations](csg-boolean-operations.md)
- [ray-marching](ray-marching.md)
- [sdf-tricks](sdf-tricks.md)
