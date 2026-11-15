# terrain-rendering: Terrain Rendering

## Guideline

Rendering pipeline: height field definition → ray marching intersection → normals & materials → lighting → atmospheric effects

## Rationale

- **FBM**: `f(p) = Σ (aⁿ × noise(2ⁿ × R × p))`, a=0.5, R=rotation matrix, 2ⁿ=frequency doubling
- **Derivative erosion**: `f(p) = Σ (aⁿ × noise(p) / (1 + dot(d,d)))`, d=accumulated gradient, suppresses detail on steep slopes
- **Adaptive step size**: `step = factor × (ray.y - terrain_height)`

## How to Apply

1. **FBM height field** — Stack rotated noise octaves: `f(p) = Σ a^n × noise(2^n × R × p)`.
2. **Derivative erosion** — Divide by `(1 + dot(d,d))` to suppress detail on steep slopes.
3. **Ray-height intersection** — Sphere-trace or binary-search ray against `terrainM(p.xz)`.
4. **Adaptive step size** — Scale march step by `(ray.y - terrain_height)` for efficient hits.
5. **Shade and atmosphere** — Gradient normals, biplanar textures, sky per [atmospheric-scattering](atmospheric-scattering.md).

## Example

```glsl
// Helpers: use hashNoise/FBM from procedural-noise.md; GLSL builtin noise() is invalid for SPIR-V
// =====================================================
// Heightfield Terrain Rendering - Complete Template
// =====================================================
#define TERRAIN_OCTAVES 9     // FBM octave count (3~16)
#define TERRAIN_SCALE 0.003   // Terrain spatial frequency
#define TERRAIN_HEIGHT 120.0  // Terrain elevation scale
#define MAX_STEPS 300         // Ray march step count (80~400)
#define MAX_DIST 5000.0       // Maximum render distance
#define STEP_FACTOR 0.4       // March conservative factor (0.3~0.8)
#define SHADOW_STEPS 80       // Shadow step count (32~128)
#define SHADOW_K 16.0         // Penumbra softness (8~64)
#define FOG_DENSITY 0.00025   // Fog density
#define SNOW_HEIGHT 80.0      // Snow line height
#define CAM_ALTITUDE 20.0     // Camera height above ground
#define SUN_DIR normalize(vec3(0.8, 0.4, -0.6))
#define SUN_COL vec3(8.0, 5.0, 3.0)
#define SKY_COL vec3(0.5, 0.7, 1.0)

// ---- Hash & Noise ----
float hash(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 19.19);
    return fract((p3.x + p3.y) * p3.z);
}

vec3 noised(in vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u  = f * f * (3.0 - 2.0 * f);
    vec2 du = 6.0 * f * (1.0 - f);
    float a = hash(i + vec2(0.0, 0.0));
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    float v = a + (b - a) * u.x + (c - a) * u.y + (a - b - c + d) * u.x * u.y;
    vec2  g = du * (vec2(b - a, c - a) + (a - b - c + d) * u.yx);
    return vec3(v, g);
}

float noise(in vec2 p) { return noised(p).x; }

// ---- FBM Terrain (derivative erosion) + LOD ----
const mat2 m2 = mat2(0.8, -0.6, 0.6, 0.8);

float terrainFBM(in vec2 p, int octaves) {
    p *= TERRAIN_SCALE;
    float a = 0.0, b = 1.0;
    vec2  d = vec2(0.0);
    for (int i = 0; i < 16; i++) {
        if (i >= octaves) break;
        vec3 n = noised(p);
        d += n.yz;
        a += b * n.x / (1.0 + dot(d, d));
        b *= 0.5;
        p = m2 * p * 2.0;
    }
    return a * TERRAIN_HEIGHT;
}

float terrainL(vec2 p) { return terrainFBM(p, 3); }
float terrainM(vec2 p) { return terrainFBM(p, TERRAIN_OCTAVES); }
float terrainH(vec2 p) { return terrainFBM(p, 16); }

// ---- Ray Marching ----
float raymarch(in vec3 ro, in vec3 rd) {
    float t = 0.0;
    if (ro.y > TERRAIN_HEIGHT && rd.y >= 0.0) return -1.0;
    if (ro.y > TERRAIN_HEIGHT) t = (ro.y - TERRAIN_HEIGHT) / (-rd.y);
    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 pos = ro + t * rd;
        float h = pos.y - terrainM(pos.xz);
        if (abs(h) < 0.0015 * t) break;
        if (t > MAX_DIST) return -1.0;
        t += STEP_FACTOR * h;
    }
    return t;
}

// ---- Normals ----
vec3 calcNormal(in vec3 pos, float t) {
    float eps = 0.02 + 0.00005 * t * t;
    float hC = terrainH(pos.xz);
    float hR = terrainH(pos.xz + vec2(eps, 0.0));
    float hU = terrainH(pos.xz + vec2(0.0, eps));
    return normalize(vec3(hC - hR, eps, hC - hU));
}

// ---- Soft Shadows ----
float calcShadow(in vec3 pos, in vec3 sunDir) {
    float res = 1.0, t = 1.0;
    for (int i = 0; i < SHADOW_STEPS; i++) {
        vec3 p = pos + t * sunDir;
        float h = p.y - terrainM(p.xz);
        if (h < 0.001) return 0.0;
        res = min(res, SHADOW_K * h / t);
        t += clamp(h, 2.0, 100.0);
    }
    return clamp(res, 0.0, 1.0);
}

// ---- Materials ----
vec3 getMaterial(in vec3 pos, in vec3 nor) {
    float slope = nor.y, h = pos.y;
    float nz = hashNoise(pos.xz * 0.04) * hashNoise(pos.xz * 0.005);
    vec3 rock  = vec3(0.10, 0.09, 0.08);
    vec3 grass = mix(vec3(0.10, 0.08, 0.04), vec3(0.05, 0.09, 0.02), nz);
    vec3 snow  = vec3(0.62, 0.65, 0.70);
    vec3 sand  = vec3(0.50, 0.45, 0.35);
    vec3 col = rock;
    col = mix(col, grass, smoothstep(0.5, 0.8, slope));
    float snowMask = smoothstep(SNOW_HEIGHT - 20.0 * nz, SNOW_HEIGHT + 10.0, h)
                   * smoothstep(0.3, 0.7, slope);
    col = mix(col, snow, snowMask);
    float beachMask = smoothstep(2.5, 0.0, h) * smoothstep(0.5, 0.9, slope);
    col = mix(col, sand, beachMask);
    return col;
}

// ---- Lighting ----
vec3 calcLighting(in vec3 pos, in vec3 nor, in vec3 rd, float shadow) {
    float dif = clamp(dot(nor, SUN_DIR), 0.0, 1.0);
    float amb = 0.5 + 0.5 * nor.y;
    vec3 backDir = normalize(vec3(-SUN_DIR.x, 0.0, -SUN_DIR.z));
    float bac = clamp(0.2 + 0.8 * dot(nor, backDir), 0.0, 1.0);
    float fre = pow(clamp(1.0 + dot(rd, nor), 0.0, 1.0), 2.0);
    vec3 hal = normalize(SUN_DIR - rd);
    float spe = pow(clamp(dot(nor, hal), 0.0, 1.0), 16.0)
              * (0.04 + 0.96 * pow(1.0 + dot(hal, rd), 5.0));
    vec3 lin = vec3(0.0);
    lin += dif * shadow * SUN_COL * 0.1;
    lin += amb * SKY_COL * 0.2;
    lin += bac * vec3(0.15, 0.05, 0.04);
    lin += fre * SKY_COL * 0.3;
    lin += spe * shadow * SUN_COL * 0.05;
    return lin;
}

// ---- Atmosphere ----
vec3 applyFog(in vec3 col, float t, in vec3 rd) {
    vec3 ext = exp(-t * FOG_DENSITY * vec3(1.0, 1.5, 4.0));
    float sundot = clamp(dot(rd, SUN_DIR), 0.0, 1.0);
    vec3 fogCol = mix(vec3(0.55, 0.55, 0.58), vec3(1.0, 0.7, 0.3), 0.3 * pow(sundot, 8.0));
    return col * ext + fogCol * (1.0 - ext);
}

// ---- Sky ----
vec3 getSky(in vec3 rd) {
    vec3 col = vec3(0.3, 0.5, 0.85) - rd.y * vec3(0.2, 0.15, 0.0);
    float horizon = pow(1.0 - max(rd.y, 0.0), 4.0);
    col = mix(col, vec3(0.8, 0.75, 0.7), 0.5 * horizon);
    float sundot = clamp(dot(rd, SUN_DIR), 0.0, 1.0);
    col += vec3(1.0, 0.7, 0.3) * 0.3 * pow(sundot, 8.0);
    col += vec3(1.0, 0.9, 0.7) * 0.5 * pow(sundot, 64.0);
    col += vec3(1.0, 1.0, 0.9) * min(pow(sundot, 1150.0), 0.3);
    return col;
}

// ---- Camera ----
vec3 cameraPath(float t) {
    return vec3(100.0 * sin(0.2 * t), 0.0, -100.0 * t);
}

mat3 setCamera(in vec3 ro, in vec3 ta) {
    vec3 cw = normalize(ta - ro);
    vec3 cu = normalize(cross(cw, vec3(0.0, 1.0, 0.0)));
    vec3 cv = cross(cu, cw);
    return mat3(cu, cv, cw);
}

// ======== Main Function ========
void main() {
    vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
    float time = uTime * 0.5;
    vec3 ro = cameraPath(time);
    ro.y = terrainL(ro.xz) + CAM_ALTITUDE;
    vec3 ta = cameraPath(time + 2.0);
    ta.y = terrainL(ta.xz) + CAM_ALTITUDE * 0.5;
    mat3 cam = setCamera(ro, ta);
    vec3 rd = cam * normalize(vec3(uv, 1.5));

    float t = raymarch(ro, rd);
    vec3 col;
    if (t > 0.0) {
        vec3 pos = ro + t * rd;
        vec3 nor = calcNormal(pos, t);
        vec3 mate = getMaterial(pos, nor);
        float sha = calcShadow(pos + nor * 0.5, SUN_DIR);
        vec3 lin = calcLighting(pos, nor, rd, sha);
        col = mate * lin;
        col = applyFog(col, t, rd);
    } else {
        col = getSky(rd);
    }
    col = 1.0 - exp(-col * 2.0);
    col = pow(col, vec3(1.0 / 2.2));
    fragColor = vec4(col, 1.0);
}
```

```glsl
float bisect(in vec3 ro, in vec3 rd, float tNear, float tFar) {
    for (int i = 0; i < 5; i++) {
        float tMid = 0.5 * (tNear + tFar);
        vec3 pos = ro + tMid * rd;
        float h = pos.y - terrainM(pos.xz);
        if (h > 0.0) tNear = tMid; else tFar = tMid;
    }
    return 0.5 * (tNear + tFar);
}
```

```glsl
float raymarchRelax(in vec3 ro, in vec3 rd) {
    float t = 0.0;
    float d = (ro + rd * t).y - terrainM((ro + rd * t).xz);
    for (int i = 0; i < 90; i++) {
        if (abs(d) < t * 0.0001 || t > 400.0) break;
        float rl = max(t * 0.02, 1.0);
        t += d * rl;
        vec3 pos = ro + t * rd;
        d = (pos.y - terrainM(pos.xz)) * 0.7;
    }
    return t;
}
```

## Advanced

- **GLSL Fundamentals**: uniforms, varyings, built-in functions (mix, smoothstep, clamp, fract, floor)
- **Vector Math**: dot product, cross product, matrix transforms, normal calculation
- **Basic Ray Marching Concepts**: casting rays from the camera, advancing along rays, detecting intersections
- **Noise Functions**: basic principles of Value Noise / Gradient Noise (grid sampling + interpolation)
- **FBM (Fractal Brownian Motion)**: layering multiple noise octaves to build fractal detail

## Gotchas

- Height-only displacement without normal update looks flat-lit — derive normals from height gradient or neighbor samples.
- Low-frequency noise terrains alias at distance — blend to coarser octaves with distance-based LOD.
- Ray march through heightfield without binary search overshoots peaks — refine hit with secant or bisection step.

## Combine With

- [procedural-noise](procedural-noise.md)
- [atmospheric-scattering](atmospheric-scattering.md)
