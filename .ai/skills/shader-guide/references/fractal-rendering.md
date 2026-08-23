# fractal-rendering: Fractal Rendering

## Guideline

Fractal rendering is essentially **visualization of iterative systems**, falling into three categories:

## Rationale


### 1. Escape-Time Algorithm
Iterate `Z <- Z^2 + c`, count escape steps. Distance estimation by simultaneously tracking the derivative `Z'`:
```
Z  <- Z^2 + c
Z' <- 2*Z*Z' + 1
d(c) = |Z|*log|Z| / |Z'|
```

### 2. Iterated Function System (IFS / KIFS)
Fold-sort-scale-offset iteration produces self-similar structures:
```
p = abs(p)                          // fold
sort p.xyz descending               // sort
p = Scale * p - Offset * (Scale-1)  // scale and offset
```

### 3. Spherical Inversion Fractals
`fract()` space folding + spherical inversion `p *= s/dot(p,p)`:
```
p = -1.0 + 2.0 * fract(0.5*p + 0.5)
k = s / dot(p, p)
p *= k; scale *= k
```

All 3D fractals are rendered via **Sphere Tracing (Ray Marching)**.

## How to Apply


1. **Step 1: Coordinate Normalization** — Map pixel coordinates to standard coordinates centered on the screen with aspect ratio correction.
2. **Step 2: 2D Fractal — Mandelbrot Escape-Time Iteration** — For each pixel point as complex number `c`, iterate `Z <- Z^2 + c` while tracking the derivative.
3. **Step 3: 3D Fractal — Distance Field Function (Mandelbulb Example)** — Implement the Mandelbulb power-N iteration using spherical coordinates, returning a distance estimate.
4. **Step 4: 3D Fractal — IFS Distance Field (Menger Sponge Example)** — Construct a KIFS fractal distance field through fold-sort-scale-offset iteration.
5. **Step 5: 3D Fractal — Spherical Inversion Distance Field (Apollonian Type)** — Construct an Apollonian fractal using fract folding + spherical inversion iteration, while recording orbit traps.
6. **Step 6: Ray Marching (Sphere Tracing)** — Step along the ray direction, advancing by the distance field value at each step, until hitting the surface.
7. **Step 7: Normal Calculation (Finite Differences)** — Sample the distance field gradient around the hit point as the surface normal.
8. **Step 8: Shading and Lighting** — Compute Lambertian diffuse + ambient + AO for hit surfaces.

## Example

```glsl
vec2 p = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
```

```glsl
float distanceToMandelbrot(in vec2 c) {
    vec2 z  = vec2(0.0);
    vec2 dz = vec2(0.0);
    float m2 = 0.0;

    for (int i = 0; i < MAX_ITER; i++) {
        if (m2 > BAILOUT * BAILOUT) break;
        // Z' -> 2*Z*Z' + 1
        dz = 2.0 * vec2(z.x*dz.x - z.y*dz.y,
                         z.x*dz.y + z.y*dz.x) + vec2(1.0, 0.0);
        // Z -> Z^2 + c
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        m2 = dot(z, z);
    }
    return 0.5 * sqrt(dot(z,z) / dot(dz,dz)) * log(dot(z,z));
}
```

```glsl
float mandelbulb(vec3 p) {
    vec3 z = p;
    float dr = 1.0;
    float r;

    for (int i = 0; i < FRACTAL_ITER; i++) {
        r = length(z);
        if (r > BAILOUT) break;
        float theta = atan(z.y, z.x);
        float phi   = asin(z.z / r);
        dr = pow(r, POWER - 1.0) * dr * POWER + 1.0;
        r = pow(r, POWER);
        theta *= POWER;
        phi *= POWER;
        z = r * vec3(cos(theta)*cos(phi),
                      sin(theta)*cos(phi),
                      sin(phi)) + p;
    }
    return 0.5 * log(r) * r / dr;
}
```

## Advanced

### Step 1: Coordinate Normalization

**What**: Map pixel coordinates to standard coordinates centered on the screen with aspect ratio correction.

**Why**: All fractal calculations must be performed in mathematical space, independent of pixel resolution.

```glsl
vec2 p = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
// p now has y range [-1,1], x scaled by aspect ratio
```

### Step 2: 2D Fractal — Mandelbrot Escape-Time Iteration

**What**: For each pixel point as complex number `c`, iterate `Z <- Z^2 + c` while tracking the derivative.

**Why**: Escape time produces fractal structure; derivative tracking enables distance estimation coloring.

```glsl
float distanceToMandelbrot(in vec2 c) {
    vec2 z  = vec2(0.0);
    vec2 dz = vec2(0.0);  // Derivative
    float m2 = 0.0;

    for (int i = 0; i < MAX_ITER; i++) {
        if (m2 > BAILOUT * BAILOUT) break;

        // Z' -> 2*Z*Z' + 1 (complex derivative chain rule)
        dz = 2.0 * vec2(z.x*dz.x - z.y*dz.y,
                         z.x*dz.y + z.y*dz.x) + vec2(1.0, 0.0);

        // Z -> Z^2 + c (complex squaring)
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;

        m2 = dot(z, z);
    }

    // Distance estimation: d(c) = |Z|*log|Z| / |Z'|
    return 0.5 * sqrt(dot(z,z) / dot(dz,dz)) * log(dot(z,z));
}
```

### Step 3: 3D Fractal — Distance Field Function (Mandelbulb Example)

**What**: Implement the Mandelbulb power-N iteration using spherical coordinates, returning a distance estimate.

**Why**: 3D fractals cannot be directly colored via escape-time on pixels; they require distance fields for ray marching.

```glsl
float mandelbulb(vec3 p) {
    vec3 z = p;
    float dr = 1.0;  // Derivative (distance scaling factor)
    float r;

    for (int i = 0; i < FRACTAL_ITER; i++) {
        r = length(z);
        if (r > BAILOUT) break;

        // Convert to spherical coordinates
        float theta = atan(z.y, z.x);
        float phi   = asin(z.z / r);

        // Derivative: dr -> power * r^(power-1) * dr + 1
        dr = pow(r, POWER - 1.0) * dr * POWER + 1.0;

        // z -> z^power + p (spherical coordinate exponentiation)
        r = pow(r, POWER);
        theta *= POWER;
        phi *= POWER;
        z = r * vec3(cos(theta)*cos(phi),
                      sin(theta)*cos(phi),
                      sin(phi)) + p;
    }

    // Distance estimation
    return 0.5 * log(r) * r / dr;
}
```

### Step 4: 3D Fractal — IFS Distance Field (Menger Sponge Example)

**What**: Construct a KIFS fractal distance field through fold-sort-scale-offset iteration.

**Why**: IFS fractals produce self-similar structures through spatial transforms rather than numerical iteration; distance is tracked via `Scale^(-n)` scaling.

```glsl
float mengerDE(vec3 z) {
    z = abs(1.0 - mod(z, 2.0));  // Infinite tiling
    float d = 1000.0;

    for (int n = 0; n < IFS_ITER; n++) {
        z = abs(z);                              // Fold
        if (z.x < z.y) z.xy = z.yx;             // Sort
        if (z.x < z.z) z.xz = z.zx;
        if (z.y < z.z) z.yz = z.zy;
        z = SCALE * z - OFFSET * (SCALE - 1.0); // Scale + offset
        if (z.z < -0.5 * OFFSET.z * (SCALE - 1.0))
            z.z += OFFSET.z * (SCALE - 1.0);
        d = min(d, length(z) * pow(SCALE, float(-n) - 1.0));
    }

    return d - 0.001;
}
```

### Step 5: 3D Fractal — Spherical Inversion Distance Field (Apollonian Type)

**What**: Construct an Apollonian fractal using fract folding + spherical inversion iteration, while recording orbit traps.

**Why**: Spherical inversion `p *= s/dot(p,p)` produces sphere packing structures; orbit traps provide color and AO information.

```glsl
vec4 orb;  // Global orbit trap

float apollonianDE(vec3 p, float s) {
    float scale = 1.0;
    orb = vec4(1000.0);

    for (int i = 0; i < INVERSION_ITER; i++) {
        p = -1.0 + 2.0 * fract(0.5 * p + 0.5);  // Fold space to [-1,1]
        float r2 = dot(p, p);
        orb = min(orb, vec4(abs(p), r2));          // Record orbit trap
        float k = s / r2;                          // Inversion factor
        p *= k;
        scale *= k;
    }

    return 0.25 * abs(p.y) / scale;
}
```

### Step 6: Ray Marching (Sphere Tracing)

**What**: Step along the ray direction, advancing by the distance field value at each step, until hitting the surface.

**Why**: The distance field guarantees safe stepping (won't pass through the surface), and is the standard method for rendering implicit 3D fractals.

```glsl
float rayMarch(vec3 ro, vec3 rd) {
    float t = 0.01;
    for (int i = 0; i < MAX_STEPS; i++) {
        float precis = PRECISION * t;  // Relax precision with distance
        float h = map(ro + rd * t);
        if (h < precis || t > MAX_DIST) break;
        t += h * FUDGE_FACTOR;         // fudge < 1.0 improves safety
    }
    return (t > MAX_DIST) ? -1.0 : t;
}
```

### Step 7: Normal Calculation (Finite Differences)

**What**: Sample the distance field gradient around the hit point as the surface normal.

**Why**: Implicit surfaces have no analytical normals and require numerical approximation. Tetrahedral sampling (4-tap) saves 1/3 of the cost compared to central differences (6-tap).

```glsl
// 6-tap central difference method (more intuitive)
vec3 calcNormal_6tap(vec3 pos) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(pos + e.xyy) - map(pos - e.xyy),
        map(pos + e.yxy) - map(pos - e.yxy),
        map(pos + e.yyx) - map(pos - e.yyx)));
}

// 4-tap tetrahedral method (more efficient, recommended)
vec3 calcNormal_4tap(vec3 pos, float t) {
    float precis = 0.001 * t;
    vec2 e = vec2(1.0, -1.0) * precis;
    return normalize(
        e.xyy * map(pos + e.xyy) +
        e.yyx * map(pos + e.yyx) +
        e.yxy * map(pos + e.yxy) +
        e.xxx * map(pos + e.xxx));
}
```

### Step 8: Shading and Lighting

**What**: Compute Lambertian diffuse + ambient + AO for hit surfaces.

**Why**: Lighting gives 3D fractals depth and material quality. Orbit trap values also drive palette index for coloring.

```glsl
float ao = 0.5 + 0.5 * nor.y;
vec3 col = palette(trap) * diff * ao;
fragColor = vec4(col, 1.0);
```

## Gotchas

- Fixed max iterations for all rays is costly — bail out when distance estimate falls below threshold.
- Orbit trap coloring without normalization flickers on zoom — smooth trap magnitude across iteration bands.
- Julia constant changed per frame without temporal filter strobes — interpolate `c` or hold constant per shot.

## Combine With

- [color-palette](color-palette.md)
- [polar-uv-manipulation](polar-uv-manipulation.md)
