# volumetric-rendering: Volumetric Rendering

## Guideline

Advance along each view ray at fixed or adaptive step sizes (Ray Marching), querying medium density at each sample point, accumulating color and opacity.

## Rationale

- Beer-Lambert transmittance governs extinction along each march step.
- Front-to-back premultiplied compositing avoids double-blend errors.
- Combine with [procedural-noise](procedural-noise.md) for density and [atmospheric-scattering](atmospheric-scattering.md) for sky composite.

## How to Apply

1. **Step 1: Camera and Ray Construction** — Build aspect-correct UVs and world-space ray from camera position and look-at.
2. **Step 2: Volume Bounds Intersection** — Find ray entry/exit against cloud layers, AABB, or height shells.
3. **Step 3: Density Field Definition** — Sample procedural noise or 3D texture for extinction coefficient.
4. **Step 4: Ray Marching Main Loop** — March fixed or adaptive steps; accumulate premultiplied color and alpha.
5. **Step 5: Lighting Calculation** — Add directional in-scatter with phase function and shadow march.
6. **Step 6: Color Mapping** — Map density to color ramps (cloud white, fire orange, etc.).
7. **Step 7: Final Compositing and Post-Processing** — Composite over sky background; optional tone map.

## Example

```glsl
vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
vec3 ro = vec3(0.0, 1.0, -5.0);  // Camera position
vec3 ta = vec3(0.0, 0.0, 0.0);   // Look-at target
vec3 ww = normalize(ta - ro);
vec3 uu = normalize(cross(ww, vec3(0.0, 1.0, 0.0)));
vec3 vv = cross(uu, ww);
float fl = 1.5; // Focal length
vec3 rd = normalize(uv.x * uu + uv.y * vv + fl * ww);
```

```glsl
// Method A: Horizontal plane bounds (cloud layers)
float tmin = (yBottom - ro.y) / rd.y;
float tmax = (yTop    - ro.y) / rd.y;
if (tmin > tmax) { float tmp = tmin; tmin = tmax; tmax = tmp; }

// Method B: Sphere bounds (explosions, atmosphere)
vec2 intersectSphere(vec3 ro, vec3 rd, float r) {
    float b = dot(ro, rd);
    float c = dot(ro, ro) - r * r;
    float d = b * b - c;
    if (d < 0.0) return vec2(1e5, -1e5);
    d = sqrt(d);
    return vec2(-b - d, -b + d);
}
```

```glsl
// Helpers: use hashNoise/FBM from procedural-noise.md; GLSL builtin noise() is invalid for SPIR-V
// 3D Value Noise (texture-based)
float noise(vec3 x) {
    vec3 p = floor(x);
    vec3 f = fract(x);
    f = f * f * (3.0 - 2.0 * f);
    vec2 uv = (p.xy + vec2(37.0, 239.0) * p.z) + f.xy;
    vec2 rg = textureLod(uChannel0, (uv + 0.5) / 256.0, 0.0).yx;
    return mix(rg.x, rg.y, f.z);
}

// fBM
float fbm(vec3 p) {
    float f = 0.0;
    f += 0.50000 * hashNoise(p); p *= 2.02;
    f += 0.25000 * hashNoise(p); p *= 2.03;
    f += 0.12500 * hashNoise(p); p *= 2.01;
    f += 0.06250 * hashNoise(p); p *= 2.02;
    f += 0.03125 * hashNoise(p);
    return f;
}

// Cloud density
float cloudDensity(vec3 p) {
    vec3 q = p - vec3(0.0, 0.1, 1.0) * uTime;
    float f = fbm(q);
    return clamp(1.5 - p.y - 2.0 + 1.75 * f, 0.0, 1.0);
}
```

## Advanced

- **GLSL Fundamentals**: uniforms, varyings, built-in functions
- **Vector Math**: dot product, cross product, normalize
- **Ray Representation**: `P = ro + t * rd` (ray origin + t × ray direction)
- **Noise Function Basics**: value noise, Perlin noise, fBM (Fractal Brownian Motion)
- **Basic Optical Concepts**:
  - Transmittance: the fraction of light remaining after passing through a medium
  - Scattering: light changing direction within a medium
  - Absorption: light energy being converted to heat by the medium

## Gotchas

- Constant step fog ignores density peaks — adapt step size to local density or use empty-space skipping.
- Single-scattering without shadow map looks uniformly lit — multiply density by light transmittance per step.
- Alpha blending volumetrics before opaque surfaces shows through geometry — render volumes after depth resolve or use depth-aware composite.

## Combine With

- [procedural-noise](procedural-noise.md)
- [ray-marching](ray-marching.md)
