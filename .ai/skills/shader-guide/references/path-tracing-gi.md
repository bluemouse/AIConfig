# path-tracing-gi: Path Tracing and Global Illumination

## Guideline

Path tracing solves the rendering equation via Monte Carlo methods. For each pixel, a ray is cast from the camera and bounced through the scene; at each bounce: intersect -> shade -> sample next direction -> accumulate contribution.

## Rationale

Core formulas:
- **Rendering equation**: $L_o = L_e + \int f_r \cdot L_i \cdot \cos\theta \, d\omega$
- **MC estimate**: $L \approx \frac{1}{N} \sum \frac{f_r \cdot L_i \cdot \cos\theta}{p(\omega)}$
- **Schlick Fresnel**: $F = F_0 + (1 - F_0)(1 - \cos\theta)^5$
- **Cosine-weighted PDF**: $p(\omega) = \cos\theta / \pi$

Use iterative loops instead of recursion: `acc` (accumulated radiance) and `throughput` (path attenuation) track path contributions.

## How to Apply


1. **Step 1: Pseudorandom Number Generator** — Provide a different random number sequence per pixel per frame, driving all Monte Carlo sampling.
2. **Step 2: Ray-Scene Intersection** — Given a ray origin and direction, find the nearest intersection along with normal and material information at the intersection point.
3. **Step 3: Cosine-Weighted Hemisphere Sampling** — Generate a random direction distributed according to cosine weighting on the hemisphere above the surface normal, used for diffuse bounces.
4. **Step 4: Material System and BRDF Evaluation** — Based on the material type at the intersection (diffuse, specular, refractive), determine the ray's next direction and energy attenuation.

## Example

```glsl
// Integer hash (recommended, good quality)
int iSeed;
int irand() { iSeed = iSeed * 0x343fd + 0x269ec3; return (iSeed >> 16) & 32767; }
float frand() { return float(irand()) / 32767.0; }
void srand(ivec2 p, int frame) {
    int n = frame;
    n = (n << 13) ^ n; n = n * (n * n * 15731 + 789221) + 1376312589;
    n += p.y;
    n = (n << 13) ^ n; n = n * (n * n * 15731 + 789221) + 1376312589;
    n += p.x;
    n = (n << 13) ^ n; n = n * (n * n * 15731 + 789221) + 1376312589;
    iSeed = n;
}

// Alternative: sin-hash (simpler)
float seed;
float rand() { return fract(sin(seed++) * 43758.5453123); }
```

```glsl
// Analytic sphere intersection
struct Ray { vec3 o, d; };
struct Sphere { float r; vec3 p, e, c; int refl; };

float iSphere(Sphere s, Ray r) {
    vec3 op = s.p - r.o;
    float b = dot(op, r.d);
    float det = b * b - dot(op, op) + s.r * s.r;
    if (det < 0.) return 0.;
    det = sqrt(det);
    float t = b - det;
    if (t > 1e-3) return t;
    t = b + det;
    return t > 1e-3 ? t : 0.;
}

// SDF ray marching (complex geometry)
float map(vec3 p) { /* return distance to nearest surface */ }
float raymarch(vec3 ro, vec3 rd, float tmax) {
    float t = 0.01;
    for (int i = 0; i < 256; i++) {
        float h = map(ro + rd * t);
        if (abs(h) < 0.0001 || t > tmax) break;
        t += h;
    }
    return t;
}
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.0001, 0.);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)));
}
```

```glsl
// fizzer method (most concise)
vec3 cosineDirection(vec3 n) {
    float u = frand(), v = frand();
    float a = 6.2831853 * v;
    float b = 2.0 * u - 1.0;
    vec3 dir = vec3(sqrt(1.0 - b * b) * vec2(cos(a), sin(a)), b);
    return normalize(n + dir);
}

// ONB construction method (more intuitive)
vec3 cosineDirectionONB(vec3 n) {
    vec2 r = vec2(frand(), frand());
    vec3 u = normalize(cross(n, vec3(0., 1., 1.)));
    vec3 v = cross(u, n);
    float ra = sqrt(r.y);
    return normalize(ra * cos(6.2831853 * r.x) * u + ra * sin(6.2831853 * r.x) * v + sqrt(1.0 - r.y) * n);
}
```

## Advanced

### Step 1: Pseudorandom Number Generator

**What**: Provide a different random number sequence per pixel per frame, driving all Monte Carlo sampling.

**Why**: All random decisions in path tracing (direction sampling, Russian roulette, Fresnel selection) depend on random numbers. The seed must be sufficiently decorrelated between pixels and frames; otherwise structured noise will appear.

**Method 1: sin-hash (simple, good for getting started)**
```glsl
float seed;
float rand() { return fract(sin(seed++) * 43758.5453123); }
// Initialization: seed = uTime + uResolution.y * gl_FragCoord.xy.x / uResolution.x + gl_FragCoord.xy.y / uResolution.y;
```

**Method 2: Integer hash (better quality, recommended)**
```glsl
int iSeed;
int irand() { iSeed = iSeed * 0x343fd + 0x269ec3; return (iSeed >> 16) & 32767; }
float frand() { return float(irand()) / 32767.0; }
void srand(ivec2 p, int frame) {
    int n = frame;
    n = (n << 13) ^ n; n = n * (n * n * 15731 + 789221) + 1376312589;
    n += p.y;
    n = (n << 13) ^ n; n = n * (n * n * 15731 + 789221) + 1376312589;
    n += p.x;
    n = (n << 13) ^ n; n = n * (n * n * 15731 + 789221) + 1376312589;
    iSeed = n;
}
```

The sin-hash may produce periodic artifacts on some GPUs (due to inconsistent sin precision across hardware). The integer hash is more reliable and uniform. The Visual Studio LCG (`0x343fd`) is a commonly used linear congruential generator.

### Step 2: Ray-Scene Intersection

**What**: Given a ray origin and direction, find the nearest intersection along with normal and material information at the intersection point.

**Why**: This is the fundamental operation of path tracing. Either analytic geometry (spheres, planes) or SDF ray marching can be used.

**Analytic sphere intersection (classic smallpt approach)**
```glsl
struct Ray { vec3 o, d; };
struct Sphere { float r; vec3 p, e, c; int refl; };

float intersectSphere(Sphere s, Ray r) {
    vec3 op = s.p - r.o;
    float b = dot(op, r.d);
    float det = b * b - dot(op, op) + s.r * s.r;
    if (det < 0.) return 0.;
    det = sqrt(det);
    float t = b - det;
    if (t > 1e-3) return t;
    t = b + det;
    return t > 1e-3 ? t : 0.;
}
```

Derivation: Ray $r(t) = o + td$, sphere $|p - c|^2 = R^2$, substitution yields quadratic $t^2 - 2b \cdot t + c = 0$, where $b = (c - o) \cdot d$, discriminant $\Delta = b^2 - |c - o|^2 + R^2$. The epsilon of `1e-3` prevents self-intersection.

**SDF ray marching (for complex geometry)**
```glsl
float map(vec3 p) { /* returns distance to nearest surface */ }

float raymarch(vec3 ro, vec3 rd, float tmax) {
    float t = 0.01;
    for (int i = 0; i < 256; i++) {
        float h = map(ro + rd * t);
        if (abs(h) < 0.0001 || t > tmax) break;
        t += h;
    }
    return t;
}

vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.0001, 0.);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)));
}
```

The principle of SDF marching: each step safely advances by the "distance to the nearest surface," ensuring no surface is crossed. The step count (128-256) and threshold (0.0001) represent a tradeoff between accuracy and performance.

### Step 3: Cosine-Weighted Hemisphere Sampling

**What**: Generate a random direction distributed according to cosine weighting on the hemisphere above the surface normal, used for diffuse bounces.

**Why**: Cosine-weighted sampling (Malley's method) matches the Lambertian BRDF distribution with PDF $\cos\theta / \pi$, simplifying BRDF/PDF to just the albedo and greatly reducing variance.

With uniform hemisphere sampling (PDF = $1/2\pi$), each bounce would need an extra multiplication by $\cos\theta \cdot 2$, and variance would be higher since many sample directions contribute very little to the integral.

**Method 1: fizzer method (most concise)**
```glsl
vec3 cosineDirection(vec3 nor) {
    float u = frand();
    float v = frand();
    float a = 6.2831853 * v;
    float b = 2.0 * u - 1.0;
    vec3 dir = vec3(sqrt(1.0 - b * b) * vec2(cos(a), sin(a)), b);
    return normalize(nor + dir); // fizzer method
}
```

Principle: Uniformly sampling a point on the unit sphere and adding the normal direction, then normalizing, naturally produces a cosine distribution. This works because uniform points on the unit sphere, projected onto the hemisphere above the normal, naturally form a cosine distribution.

**Method 2: Classic ONB construction (more intuitive)**
```glsl
vec3 cosineDirectionONB(vec3 n) {
    vec2 r = vec2(frand(), frand());
    vec3 u = normalize(cross(n, vec3(0., 1., 1.)));
    vec3 v = cross(u, n);
    float ra = sqrt(r.y);
    float rx = ra * cos(6.2831853 * r.x);
    float ry = ra * sin(6.2831853 * r.x);
    float rz = sqrt(1.0 - r.y);
    return normalize(rx * u + ry * v + rz * n);
}
```

Principle: First build an orthonormal basis (ONB) with n as the z-axis, then sample in local coordinates using Malley's method: map uniform random numbers onto the unit disk ($r = \sqrt{\xi_2}$, $\phi = 2\pi\xi_1$), with z-component $\sqrt{1 - r^2}$.

### Step 4: Material System and BRDF Evaluation

**What**: Based on the material type at the intersection (diffuse, specular, refractive), determine the ray's next direction and energy attenuation.

**Why**: Different materials respond to light completely differently. Diffuse scatters randomly, specular reflects perfectly, and refractive materials follow Snell's law. The Fresnel effect determines the reflection/refraction ratio.

```glsl
#define MAT_DIFFUSE  0
#define MAT_SPECULAR 1
#define MAT_DIELECTRIC 2
```

**Diffuse**:
- New direction = `cosineDirection(normal)`
- `throughput *= albedo`
- Because cosine-weighted sampling is used, BRDF($1/\pi$) * $\cos\theta$ / PDF($\cos\theta/\pi$) = 1, so throughput only needs to be multiplied by albedo

**Specular**:
- New direction = `reflect(rd, normal)`
- `throughput *= albedo`
- A perfect mirror's BRDF is a delta function; only one direction is sampled.

**Russian roulette**: terminate path when `max(throughput) < threshold` with survival boost.

### Step 6: Output Radiance

**What**: Average per-pixel samples and tone-map accumulated radiance.

```glsl
vec3 col = radiance / float(SAMPLES);
fragColor = vec4(col / (col + 1.0), 1.0);
```

## Gotchas

- Russian roulette without throughput compensation biases brightness — divide surviving paths by survival probability.
- Next-event estimation omitted leaves interiors black — add explicit light sampling for direct illumination.
- Low sample count per pixel noise requires accumulation — write running average across frames with `uFrame`.

## Combine With

- [analytic-ray-tracing](analytic-ray-tracing.md)
- [multipass-buffer](multipass-buffer.md)
