# domain-repetition: Domain Repetition

## Guideline

The essence of domain repetition is **coordinate transformation**: before computing the SDF, fold/map point `p` into a finite "fundamental domain".

## Rationale


**Three fundamental operations:**

| Operation | Formula | Effect |
|-----------|---------|--------|
| **mod repetition** | `p = mod(p + c/2, c) - c/2` | Infinite translational repetition along an axis |
| **abs mirroring** | `p = abs(p)` | Mirror symmetry across an axis plane |
| **Rotational folding** | `angle = mod(atan(p.y,p.x), TAU/N)` | N-fold rotational symmetry |

Key math: `mod(x,c)` -> periodic mapping to `[0,c)`; `abs(x)` -> reflection symmetry; `fract(x)` = `mod(x,1.0)` -> normalized period.

## How to Apply

1. **Step 1: Cartesian Domain Repetition (mod repetition)** — Fold world position with `mod(p + c/2, c) - c/2` for infinite tiling along axes.
2. **Step 2: Symmetric Folding (abs-mod triangle wave)** — Mirror with `abs(p)` or triangle-wave folding for kaleidoscope symmetry.
3. **Step 3: Angular Domain Repetition (Polar Coordinate Folding)** — Fold angle with `mod(atan(p.y, p.x), TAU/N)` for N-fold symmetry.
4. **Step 4: fract Domain Folding (Fractal Iteration)** — Apply `fract` scaling iterations for self-similar lattice detail.
5. **Step 5: Iterative abs Folding (IFS / Kali-set)** — Repeat abs-offset-scale steps to build fractal distance fields.
6. **Step 6: Reflection Folding (Polyhedral Symmetry)** — Mirror across multiple planes for platonic or crystal symmetry.
7. **Step 7: Toroidal/Cylindrical Domain Warping** — Map Cartesian coords to torus/cylinder parameterization before repetition.
8. **Step 8: 1D Centered Domain Repetition (with Cell ID)** — Repeat along one axis while tracking cell index for per-cell variation.
## Example

```glsl
#define PI 3.14159265359
#define TAU 6.28318530718
#define MAX_STEPS 100
#define MAX_DIST 50.0
#define SURF_DIST 0.001
#define PERIOD 4.0
#define ANGULAR_COUNT 6.0
#define IFS_ITERS 5
#define IFS_OFFSET 1.2

mat2 rot(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, s, -s, c);
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

vec3 domainRepeat(vec3 p, vec3 period) {
    return mod(p + period * 0.5, period) - period * 0.5;
}

vec2 pmod(vec2 p, float count) {
    float a = atan(p.x, p.y) + PI / count;
    float n = TAU / count;
    a = floor(a / n) * n;
    return p * rot(-a);
}

float map(vec3 p) {
    vec3 q = domainRepeat(p, vec3(PERIOD));
    q.xz = pmod(q.xz, ANGULAR_COUNT);
    for (int i = 0; i < IFS_ITERS; i++) {
        q = abs(q) - IFS_OFFSET;
        q.xy *= rot(0.785);
        q.yz *= rot(0.471);
    }
    return sdBox(q, vec3(0.15, 0.4, 0.15));
}

vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

float raymarch(vec3 ro, vec3 rd) {
    float t = 0.0;
    for (int i = 0; i < MAX_STEPS; i++) {
        float d = map(ro + rd * t);
        if (d < SURF_DIST || t > MAX_DIST) break;
        t += d;
    }
    return t;
}

void main() {
    vec2 uv = (gl_FragCoord.xy * 2.0 - uResolution.xy) / uResolution.y;

    float time = uTime * 0.5;
    vec3 ro = vec3(sin(time) * 6.0, 3.0 + sin(time * 0.7) * 2.0, cos(time) * 6.0);
    vec3 ta = vec3(0.0);
    vec3 ww = normalize(ta - ro);
    vec3 uu = normalize(cross(ww, vec3(0.0, 1.0, 0.0)));
    vec3 vv = cross(uu, ww);
    vec3 rd = normalize(uv.x * uu + uv.y * vv + 1.8 * ww);

    float t = raymarch(ro, rd);

    vec3 col = vec3(0.0);
    if (t < MAX_DIST) {
        vec3 p = ro + rd * t;
        vec3 n = calcNormal(p);
        vec3 lightDir = normalize(vec3(0.5, 0.8, -0.6));
        float diff = clamp(dot(n, lightDir), 0.0, 1.0);
        float amb = 0.5 + 0.5 * n.y;
        vec3 baseColor = 0.5 + 0.5 * cos(p * 0.5 + vec3(0.0, 2.0, 4.0));
        col = baseColor * (0.2 * amb + 0.8 * diff);
        col *= exp(-0.03 * t * t);
    }

    col = pow(col, vec3(0.4545));
    fragColor = vec4(col, 1.0);
}
```

```glsl
// Infinite translational repetition along one or more axes
vec3 domainRepeat(vec3 p, vec3 period) {
    return mod(p + period * 0.5, period) - period * 0.5;
}

float map(vec3 p) {
    vec3 q = domainRepeat(p, vec3(4.0)); // repeat every 4 units
    return sdBox(q, vec3(0.5));
}
```

```glsl
// Boundary-continuous symmetric folding, coordinates oscillate 0->tile->0
vec3 symmetricFold(vec3 p, float tile) {
    return abs(vec3(tile) - mod(p, vec3(tile * 2.0)));
}

// Star Nest classic usage
p = abs(vec3(tile) - mod(p, vec3(tile * 2.0)));
```

## Advanced

- GLSL basic syntax, `vec2/vec3/mat2` operations
- Behavior of built-in functions like `mod()`, `fract()`, `abs()`, `atan()`
- Signed Distance Field (SDF) concept — a function returning the distance from a point to the nearest surface
- Basic principles of Ray Marching
- 2D rotation matrix `mat2(cos(a), sin(a), -sin(a), cos(a))`

## Gotchas

- Repeating without `mod` centering shifts the lattice phase — use `mod(p + 0.5 * period, period) - 0.5 * period`.
- Infinite repetition + finite march budget misses far-cell hits — limit repetition index or enlarge scene bounds.
- Cell seams appear when the repeated primitive crosses cell borders — design primitives to fit inside one cell.

## Combine With

- [sdf-3d](sdf-3d.md)
- [ray-marching](ray-marching.md)
