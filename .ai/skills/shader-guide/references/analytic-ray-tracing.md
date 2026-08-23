# analytic-ray-tracing: Analytic Ray Tracing

## Guideline

Substitute the ray equation `P(t) = O + tD` into the geometric body's implicit equation to obtain an algebraic equation in `t`, then solve it in closed form.

## Rationale


**Unified intersection workflow**: Build equation -> Simplify to standard form -> Discriminant test -> Take smallest positive root -> Compute gradient at intersection for normal

**Key formulas**:
- **Sphere** `|P-C|^2 = r^2` -> Quadratic equation
- **Plane** `N·P + d = 0` -> Linear equation
- **Box** Intersection of three pairs of parallel planes -> Slab Method
- **Ellipsoid** `|P/R|^2 = 1` -> Sphere intersection in scaled space
- **Torus** `(|P_xy| - R)^2 + P_z^2 = r^2` -> Quartic equation

## How to Apply


1. **Step 1: Ray Generation** — Generate a ray from the camera position through each pixel.
2. **Step 2: Ray-Sphere Intersection** — Compute the exact intersection of a ray with a sphere. This is the most fundamental and commonly used intersection function.
3. **Step 3: Ray-Plane Intersection** — Compute the intersection of a ray with an infinite plane.
4. **Step 4: Ray-Box Intersection (Slab Method)** — Compute the intersection of a ray with an axis-aligned bounding box (AABB).
5. **Step 5: Ray-Ellipsoid Intersection** — Compute the intersection of a ray with an ellipsoid.

## Example

```glsl
vec3 generateRay(vec2 gl_FragCoord.xy, vec2 resolution, vec3 ro, vec3 ta) {
    vec2 p = (2.0 * gl_FragCoord.xy - resolution) / resolution.y;
    vec3 cw = normalize(ta - ro);
    vec3 cu = normalize(cross(cw, vec3(0, 1, 0)));
    vec3 cv = cross(cu, cw);
    float fov = 1.5;
    return normalize(p.x * cu + p.y * cv + fov * cw);
}
```

```glsl
// Optimized version with sphere center at origin
float iSphere(vec3 ro, vec3 rd, vec2 distBound, inout vec3 normal, float r) {
    float b = dot(ro, rd);
    float c = dot(ro, ro) - r * r;
    float h = b * b - c;
    if (h < 0.0) return MAX_DIST;
    h = sqrt(h);
    float d1 = -b - h;
    float d2 = -b + h;
    if (d1 >= distBound.x && d1 <= distBound.y) {
        normal = normalize(ro + rd * d1);
        return d1;
    } else if (d2 >= distBound.x && d2 <= distBound.y) {
        normal = normalize(ro + rd * d2);
        return d2;
    }
    return MAX_DIST;
}
```

```glsl
// General version, supports arbitrary sphere center (sph = vec4(center.xyz, radius))
float sphIntersect(vec3 ro, vec3 rd, vec4 sph) {
    vec3 oc = ro - sph.xyz;
    float b = dot(oc, rd);
    float c = dot(oc, oc) - sph.w * sph.w;
    float h = b * b - c;
    if (h < 0.0) return -1.0;
    return -b - sqrt(h);
}
```

## Advanced

### Step 1: Ray Generation

**What**: Generate a ray from the camera position through each pixel.

**Why**: This is the starting point of ray tracing. Each pixel corresponds to a ray from the camera through the near plane. The standard approach is to construct a camera coordinate system (right, up, forward) and map normalized screen coordinates to world-space directions.

```glsl
// Construct camera ray
vec3 generateRay(vec2 gl_FragCoord.xy, vec2 resolution, vec3 ro, vec3 ta) {
    vec2 p = (2.0 * gl_FragCoord.xy - resolution) / resolution.y;

    // Build camera coordinate system
    vec3 cw = normalize(ta - ro);               // forward
    vec3 cu = normalize(cross(cw, vec3(0, 1, 0))); // right
    vec3 cv = cross(cu, cw);                    // up

    float fov = 1.5; // Adjustable: field of view control (larger = narrower angle)
    vec3 rd = normalize(p.x * cu + p.y * cv + fov * cw);
    return rd;
}
```

### Step 2: Ray-Sphere Intersection

**What**: Compute the exact intersection of a ray with a sphere. This is the most fundamental and commonly used intersection function.

**Why**: Substituting the ray `P = O + tD` into the sphere equation `|P - C|² = r²` and expanding yields a quadratic equation in `t`. The discriminant `h = b² - c` determines the number of intersections (0, 1, or 2); the smallest positive root is the nearest intersection.

This is a ubiquitous technique, with two common variants:

**Code (optimized version, assumes sphere centered at origin)**:
```glsl
// Ray-sphere intersection (optimized version for sphere at origin)
// ro: ray origin (sphere center offset already subtracted)
// rd: ray direction (must be normalized)
// r:  sphere radius
// Returns: intersection distance, MAX_DIST if no intersection
float iSphere(vec3 ro, vec3 rd, vec2 distBound, inout vec3 normal, float r) {
    float b = dot(ro, rd);
    float c = dot(ro, ro) - r * r;
    float h = b * b - c;       // Discriminant (optimized: 4a factor omitted)
    if (h < 0.0) return MAX_DIST; // No intersection

    h = sqrt(h);
    float d1 = -b - h;        // Near intersection
    float d2 = -b + h;        // Far intersection

    // Select the nearest intersection within valid range
    if (d1 >= distBound.x && d1 <= distBound.y) {
        normal = normalize(ro + rd * d1);
        return d1;
    } else if (d2 >= distBound.x && d2 <= distBound.y) {
        normal = normalize(ro + rd * d2);
        return d2;
    }
    return MAX_DIST;
}
```

**Code (general version, arbitrary sphere center)**:
```glsl
// Ray-sphere intersection (general version, supports arbitrary sphere center)
// sph: vec4(center.xyz, radius)
float sphIntersect(vec3 ro, vec3 rd, vec4 sph) {
    vec3 oc = ro - sph.xyz;
    float b = dot(oc, rd);
    float c = dot(oc, oc) - sph.w * sph.w;
    float h = b * b - c;
    if (h < 0.0) return -1.0;
    return -b - sqrt(h);  // Returns only the near intersection
}
```

### Step 3: Ray-Plane Intersection

**What**: Compute the intersection of a ray with an infinite plane.

**Why**: The plane equation `N·P + d = 0` substituted with the ray yields a linear equation, solved directly by division. This is the simplest intersection primitive, commonly used for floors, walls, Cornell Boxes, etc. Note: when `N·D ≈ 0`, the ray is parallel to the plane.

```glsl
// Ray-plane intersection
// planeNormal: plane normal (must be normalized)
// planeDist:   distance from plane to origin (N·P + planeDist = 0)
float iPlane(vec3 ro, vec3 rd, vec2 distBound, inout vec3 normal,
             vec3 planeNormal, float planeDist) {
    float denom = dot(rd, planeNormal);
    // Only intersects when ray hits the front face of the plane
    if (denom > 0.0) return MAX_DIST;

    float d = -(dot(ro, planeNormal) + planeDist) / denom;

    if (d < distBound.x || d > distBound.y) return MAX_DIST;

    normal = planeNormal;
    return d;
}

// Quick version: horizontal ground plane (y-axis aligned)
float iGroundPlane(vec3 ro, vec3 rd, float height) {
    return -(ro.y - height) / rd.y;
}
```

### Step 4: Ray-Box Intersection (Slab Method)

**What**: Compute the intersection of a ray with an axis-aligned bounding box (AABB).

**Why**: The Slab Method treats the box as the intersection of three pairs of parallel planes. It computes the ray's intersection with each pair of planes `(tmin, tmax)`, then takes the maximum of all `tmin` values and the minimum of all `tmax` values. If `tN > tF` or `tF < 0`, there is no intersection. The normal is determined by which face was hit first.

```glsl
// Ray-box intersection (Slab Method, optimized version)
// boxSize: box half-size vec3(halfW, halfH, halfD)
float iBox(vec3 ro, vec3 rd, vec2 distBound, inout vec3 normal, vec3 boxSize) {
    vec3 m = sign(rd) / max(abs(rd), 1e-8); // Avoid division by zero
    vec3 n = m * ro;
    vec3 k = abs(m) * boxSize;

    vec3 t1 = -n - k;  // Near plane intersections
    vec3 t2 = -n + k;  // Far plane intersections

    float tN = max(max(t1.x, t1.y), t1.z); // Entry distance into the box
    float tF = min(min(t2.x, t2.y), t2.z); // Exit distance from the box

    if (tN > tF || tF <= 0.0) return MAX_DIST; // No intersection

    if (tN >= distBound.x && tN <= distBound.y) {
        // Normal: determine which face was hit
        normal = -sign(rd) * step(t1.yzx, t1.xyz) * step(t1.zxy, t1.xyz);
        return tN;
    } else if (tF >= distBound.x && tF <= distBound.y) {
        normal = -sign(rd) * step(t1.yzx, t1.xyz) * step(t1.zxy, t1.xyz);
        return tF;
    }
    return MAX_DIST;
}
```

### Step 5: Ray-Ellipsoid Intersection

**What**: Compute the intersection of a ray with an ellipsoid.

**Why**: An ellipsoid can be viewed as a sphere scaled differently along each axis. By dividing both the ray origin and direction by the ellipsoid radii `R`, a sphere intersection is performed in scaled space, then the normal is transformed back to the original space. This "space transformation" technique is one of the core ideas of analytic intersection.

```glsl
float rayEllipsoid(vec3 ro, vec3 rd, vec3 R) {
    vec3 o = ro / R;
    vec3 d = normalize(rd / R);
    float b = dot(o, d);
    float c = dot(o, o) - 1.0;
    float h = b * b - c;
    if (h < 0.0) return -1.0;
    return -b - sqrt(h);
}
```

### Step 6: Scene Loop and Shading

**What**: Test analytic primitives per ray; shade closest hit.

```glsl
void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    vec3 ro = vec3(0.0, 0.0, -3.0);
    vec3 rd = normalize(vec3(uv, 1.5));
    float t = raySphere(ro, rd, 1.0);
    vec3 col = t > 0.0 ? vec3(0.8) : vec3(0.1);
    fragColor = vec4(col, 1.0);
}
```

## Gotchas

- Solving quadratics without `b` half-value form loses precision on grazing hits — use `q = -0.5 * (b + sign(b)*sqrt(disc))`.
- Discriminant near zero produces flicker between zero and two roots — clamp with epsilon and pick nearest positive `t`.
- Plane/sphere ordering matters for transparency — sort hits or march remaining distance after each intersection.

## Combine With

- [lighting-model](lighting-model.md)
