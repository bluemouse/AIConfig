# ray-marching: Ray Marching

## Guideline


Advance rays with sphere tracing: step by the SDF value at each sample until distance falls below epsilon or max distance/steps is reached.

## Rationale

Cast a ray from the camera along each pixel direction, advancing step by step using a **Signed Distance Function (SDF)** (Sphere Tracing). Each step advances by the SDF value at the current point, guaranteeing no surface penetration.

- Ray equation: `P(t) = ro + t * rd`
- Stepping logic: `t += SDF(P(t))`
- Hit test: `SDF(P) < epsilon`
- Normal estimation: `N = normalize(gradient of SDF(P))` (direction of the SDF gradient)
- Volumetric rendering: advance at fixed step size, accumulating density and color per step (front-to-back compositing)

## How to Apply


1. **Step 1: UV Coordinate Normalization and Ray Direction Computation** — Convert pixel coordinates to normalized coordinates in the [-1,1] range, and compute the ray direction from the camera.
2. **Step 2: Building the Camera Matrix (Look-At)** — Construct a view matrix from the camera position, target point, and up direction, then transform the view-space ray direction into world space.
3. **Step 3: Defining the Scene SDF** — Write a function that returns the signed distance from any point in space to the nearest surface.
4. **Step 4: Core Ray Marching Loop** — Iteratively step along the ray direction, using the SDF value at each step to determine the advance distance, and check whether the ray has hit a surface or exceeded the maximum range.
5. **Step 5: Normal Estimation** — Compute the surface normal at the hit point using the numerical gradient of the SDF.
6. **Step 6: Lighting and Shading** — Compute Phong lighting (ambient + diffuse + specular) at the hit point.

## Example

```glsl
// ============================================================
// Stage: fragment | Version: 450 | Uniforms: uResolution, uTime, uFrame, uMouse
// ============================================================

#define MAX_STEPS 128
#define MAX_DIST 100.0
#define SURF_DIST 0.001
#define SHADOW_STEPS 24
#define AO_STEPS 5
#define FOCAL_LENGTH 2.5
#define SHININESS 16.0

// --- SDF Primitives ---
float sdSphere(vec3 p, float r) { return length(p) - r; }

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

float sdTorus(vec3 p, vec2 t) {
    return length(vec2(length(p.xz) - t.x, p.y)) - t.y;
}

// --- Boolean Operations ---
float opUnion(float a, float b) { return min(a, b); }
float opSubtraction(float a, float b) { return max(a, -b); }
float opIntersection(float a, float b) { return max(a, b); }

float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;
}

mat2 rot2D(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, -s, s, c);
}

// --- Scene Definition ---
float map(vec3 p) {
    float ground = p.y;
    vec3 q = p - vec3(0.0, 0.8, 0.0);
    q.xz *= rot2D(uTime * 0.5);
    float body = smin(sdSphere(q, 0.5), sdTorus(q, vec2(0.8, 0.15)), 0.3);
    return opUnion(ground, body);
}

// --- Normal (Tetrahedral Trick) ---
vec3 calcNormal(vec3 pos) {
    vec3 n = vec3(0.0);
    for (int i = min(uFrame,0); i < 4; i++) {
        vec3 e = 0.5773 * (2.0 * vec3((((i+3)>>1)&1), ((i>>1)&1), (i&1)) - 1.0);
        n += e * map(pos + 0.001 * e);
    }
    return normalize(n);
}

// --- Soft Shadows ---
float calcSoftShadow(vec3 ro, vec3 rd, float tmin, float tmax) {
    float res = 1.0, t = tmin;
    for (int i = 0; i < SHADOW_STEPS; i++) {
        float h = map(ro + rd * t);
        float s = clamp(8.0 * h / t, 0.0, 1.0);
        res = min(res, s);
        t += clamp(h, 0.01, 0.2);
        if (res < 0.004 || t > tmax) break;
    }
    res = clamp(res, 0.0, 1.0);
    return res * res * (3.0 - 2.0 * res);
}

// --- Ambient Occlusion ---
float calcAO(vec3 pos, vec3 nor) {
    float occ = 0.0, sca = 1.0;
    for (int i = 0; i < AO_STEPS; i++) {
        float h = 0.01 + 0.12 * float(i) / float(AO_STEPS - 1);
        float d = map(pos + h * nor);
        occ += (h - d) * sca;
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}

// --- Ray March ---
float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + t * rd;
        float d = map(p);
        if (abs(d) < SURF_DIST * (1.0 + t * 0.1)) return t;
        t += d;
        if (t > MAX_DIST) break;
    }
    return -1.0;
}

// --- Camera ---
mat3 setCamera(vec3 ro, vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = cross(cu, cw);
    return mat3(cu, cv, cw);
}

// --- Rendering ---
vec3 render(vec3 ro, vec3 rd) {
    vec3 col = vec3(0.7, 0.7, 0.9) - max(rd.y, 0.0) * 0.3; // sky

    float t = rayMarch(ro, rd);
    if (t > 0.0) {
        vec3 pos = ro + t * rd;
        vec3 nor = calcNormal(pos);

        // Material
        vec3 mate = vec3(0.18);
        if (pos.y < 0.001) {
            float f = mod(floor(pos.x) + floor(pos.z), 2.0);
            mate = vec3(0.1 + 0.05 * f);
        } else {
            mate = 0.2 + 0.2 * sin(vec3(0.0, 1.0, 2.0));
        }

        // Lighting
        vec3 lightDir = normalize(vec3(-0.5, 0.4, -0.6));
        float occ = calcAO(pos, nor);
        float dif = clamp(dot(nor, lightDir), 0.0, 1.0);
        dif *= calcSoftShadow(pos + nor * 0.01, lightDir, 0.02, 2.5);
        vec3 hal = normalize(lightDir - rd);
        float spe = pow(clamp(dot(nor, hal), 0.0, 1.0), SHININESS) * dif;
        float sky = sqrt(clamp(0.5 + 0.5 * nor.y, 0.0, 1.0));

        vec3 lin = vec3(0.0);
        lin += dif * vec3(1.3, 1.0, 0.7) * 2.2;
        lin += sky * vec3(0.4, 0.6, 1.15) * 0.6 * occ;
        lin += vec3(0.25) * 0.55 * occ;
        col = mate * lin;
        col += spe * vec3(1.3, 1.0, 0.7) * 5.0;

        col = mix(col, vec3(0.7, 0.7, 0.9), 1.0 - exp(-0.0001 * t * t * t)); // distance fog
    }
    return clamp(col, 0.0, 1.0);
}

void main() {
    float time = 32.0 + uTime * 1.5;
    vec2 mo = uMouse.xy / uResolution.xy;
    vec3 ta = vec3(0.0, 0.5, 0.0);
    vec3 ro = ta + vec3(4.0*cos(0.1*time+7.0*mo.x), 1.5, 4.0*sin(0.1*time+7.0*mo.x));
    mat3 ca = setCamera(ro, ta, 0.0);

    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    vec3 rd = ca * normalize(vec3(uv, FOCAL_LENGTH));

    vec3 col = render(ro, rd);
    col = pow(col, vec3(0.4545));

    vec2 q = gl_FragCoord.xy / uResolution.xy;
    col *= 0.5 + 0.5 * pow(16.0 * q.x * q.y * (1.0 - q.x) * (1.0 - q.y), 0.25);

    fragColor = vec4(col, 1.0);
}
```

```glsl
// Concise version
vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
vec3 ro = vec3(0.0, 0.0, -3.0);
vec3 rd = normalize(vec3(uv, 1.0));          // z=1.0 ~ 90 deg FOV

// Precise FOV control
vec2 xy = gl_FragCoord.xy - uResolution.xy / 2.0;
float z = uResolution.y / tan(radians(FOV) / 2.0);
vec3 rd = normalize(vec3(xy, -z));
```

```glsl
mat3 setCamera(vec3 ro, vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = cross(cu, cw);
    return mat3(cu, cv, cw);
}

mat3 ca = setCamera(ro, ta, 0.0);
vec3 rd = ca * normalize(vec3(uv, FOCAL_LENGTH)); // 1.0~3.0, larger = narrower FOV
```

## Advanced

### Step 1: UV Coordinate Normalization and Ray Direction Computation

**What**: Convert pixel coordinates to normalized coordinates in the [-1,1] range, and compute the ray direction from the camera.

**Why**: This establishes the mapping from screen pixels to the 3D world. Dividing by `uResolution.y` preserves the aspect ratio; the z component controls the field of view.

```glsl
// Method A: Concise version (common for quick prototyping)
vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
vec3 ro = vec3(0.0, 0.0, -3.0);             // Ray origin (camera position)
vec3 rd = normalize(vec3(uv, 1.0));          // Ray direction, z=1.0 gives ~90° FOV

// Method B: Precise FOV control
vec2 xy = gl_FragCoord.xy - uResolution.xy / 2.0;
float z = uResolution.y / tan(radians(FOV) / 2.0); // FOV is adjustable: field of view in degrees
vec3 rd = normalize(vec3(xy, -z));
```

### Step 2: Building the Camera Matrix (Look-At)

**What**: Construct a view matrix from the camera position, target point, and up direction, then transform the view-space ray direction into world space.

**Why**: Without a camera matrix, the ray direction is fixed along -Z. With a Look-At matrix, the camera can be freely positioned and rotated.

```glsl
mat3 setCamera(vec3 ro, vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);                     // Forward direction
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);            // Up reference (cr controls roll)
    vec3 cu = normalize(cross(cw, cp));                // Right direction
    vec3 cv = cross(cu, cw);                           // Up direction
    return mat3(cu, cv, cw);
}

// Usage:
mat3 ca = setCamera(ro, ta, 0.0);
vec3 rd = ca * normalize(vec3(uv, FOCAL_LENGTH)); // FOCAL_LENGTH adjustable: 1.0~3.0, larger = narrower FOV
```

### Step 3: Defining the Scene SDF

**What**: Write a function that returns the signed distance from any point in space to the nearest surface.

**Why**: The SDF is the core of Ray Marching — it simultaneously defines geometry and step distance.

```glsl
// --- Basic SDF Primitives ---
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}

float sdTorus(vec3 p, vec2 t) {
    return length(vec2(length(p.xz) - t.x, p.y)) - t.y;
}

// --- CSG Boolean Operations ---
float opUnion(float a, float b)        { return min(a, b); }
float opSubtraction(float a, float b)  { return max(a, -b); }
float opIntersection(float a, float b) { return max(a, b); }

// --- Smooth Boolean Operations (organic blending) ---
float smin(float a, float b, float k) {
    float h = max(k - abs(a - b), 0.0);
    return min(a, b) - h * h * 0.25 / k;  // k adjustable: blend radius, 0.1~0.5
}

// --- Spatial Transforms ---
// Translation: apply inverse translation to the sample point
// Rotation: multiply the sample point by a rotation matrix
// Scaling: p /= s, result *= s

// --- Scene Composition Example ---
float map(vec3 p) {
    float d = sdSphere(p - vec3(0.0, 0.5, 0.0), 0.5);   // Sphere
    d = opUnion(d, p.y);                                    // Add ground plane
    d = smin(d, sdBox(p - vec3(1.0, 0.3, 0.0), vec3(0.3)), 0.2); // Smooth blend with box
    return d;
}
```

### Step 4: Core Ray Marching Loop

**What**: Iteratively step along the ray direction, using the SDF value at each step to determine the advance distance, and check whether the ray has hit a surface or exceeded the maximum range.

**Why**: Sphere Tracing guarantees that each step advances the maximum safe distance (without penetrating surfaces), taking large steps in open areas and automatically slowing down near surfaces.

```glsl
#define MAX_STEPS 128   // Adjustable: max step count, 64~256, more = more precise but slower
#define MAX_DIST 100.0  // Adjustable: max travel distance
#define SURF_DIST 0.001 // Adjustable: surface hit threshold, 0.0001~0.01

float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + t * rd;
        float d = map(p);
        if (d < SURF_DIST) return t;   // Surface hit
        t += d;
        if (t > MAX_DIST) break;        // Out of range
    }
    return -1.0; // No hit
}
```

### Step 5: Normal Estimation

**What**: Compute the surface normal at the hit point using the numerical gradient of the SDF.

**Why**: Normals are the foundation of lighting calculations. The gradient direction of the SDF is the surface normal direction.

```glsl
// Method A: Central differences (6 SDF calls, straightforward)
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);  // e.x adjustable: differentiation step size
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

// Method B: Tetrahedron trick (4 SDF calls, prevents compiler inline bloat, recommended)
vec3 calcNormal(vec3 pos) {
    vec3 n = vec3(0.0);
    for (int i = 0; i < 4; i++) {
        vec3 e = 0.5773 * (2.0 * vec3((((i+3)>>1)&1), ((i>>1)&1), (i&1)) - 1.0);
        n += e * map(pos + 0.001 * e);
    }
    return normalize(n);
}
```

### Step 6: Lighting and Shading

**What**: Compute Phong lighting (ambient + diffuse + specular) at the hit point.

**Why**: Give SDF surfaces realistic shading with highlights and shadow gradients.

```glsl
vec3 shade(vec3 p, vec3 rd) {
    vec3 nor = calcNormal(p);
    vec3 lightDir = normalize(vec3(0.6, 0.35, 0.5));   // Light direction (adjustable)
    vec3 viewDir = -rd;
    vec3 halfDir = normalize(lightDir + viewDir);

    // Diffuse
    float diff = clamp(dot(nor, lightDir), 0.0, 1.0);
    // Specular
    float spec = pow(clamp(dot(nor, halfDir), 0.0, 1.0), SHININESS); // SHININESS adjustable: 8~64
    // Ambient + sky light
    float sky = sqrt(clamp(0.5 + 0.5 * nor.y, 0.0, 1.0));

    vec3 col = vec3(0.2, 0.2, 0.25);             // Material base color (adjustable)

    col += diff * lightColor + spec * vec3(1.0) + sky * vec3(0.1, 0.15, 0.25);
    return col;
}
```

### Step 7: Post-Processing

**What**: Apply gamma correction, vignette, and tone mapping to the final shaded color.

**Why**: Linear march output must be display-referred; small post steps sell the final look.

```glsl
col = pow(col, vec3(0.4545));  // gamma ~2.2
col *= 1.0 - 0.3 * dot(uv, uv); // vignette
fragColor = vec4(col, 1.0);
```

### Step 8: main() Assembly

**What**: Wire UV → ray → march → shade → post in `void main()`.

```glsl
void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    vec3 ro = vec3(0.0, 1.0, -3.0);
    vec3 rd = normalize(vec3(uv, 1.5));
    float t = rayMarch(ro, rd);
    vec3 col = (t > 0.0) ? shade(ro + rd * t, rd) : vec3(0.1, 0.15, 0.2);
    fragColor = vec4(col, 1.0);
}
```

## Gotchas

- Fixed step sizes miss thin geometry — always scale steps by `max(d * k, minStep)` from the SDF.
- No early exit on miss wastes fill rate — return sky color once `t` exceeds max distance or `d < epsilon`.
- Camera inside the surface needs negative starting `t` or inverted normals — guard with interior distance sign.

## Combine With

- [sdf-3d](sdf-3d.md)
- [normal-estimation](normal-estimation.md)
- [lighting-model](lighting-model.md)
