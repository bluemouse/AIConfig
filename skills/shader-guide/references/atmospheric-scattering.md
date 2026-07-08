# atmospheric-scattering: Atmospheric Scattering

## Guideline

Three physical mechanisms: Rayleigh (wavelength-dependent), Mie (aerosol forward scatter), and Beer-Lambert extinction along the view ray.

## Rationale


**Rayleigh scattering** — molecular-scale particles, β_R(λ) ∝ 1/λ⁴, shorter wavelengths scatter more strongly (blue sky / red sunset).
Sea-level values: `vec3(5.5e-6, 13.0e-6, 22.4e-6)` m⁻¹.
Phase function: `P_R(θ) = 3/(16π) × (1 + cos²θ)`, symmetric forward-backward.

**Mie scattering** — aerosol particles, wavelength-independent, strong forward scattering (sun halo).
Sea-level value: `vec3(21e-6)` m⁻¹.
Phase function: Henyey-Greenstein, `g ≈ 0.76~0.88`.

**Beer-Lambert attenuation** — `T(A→B) = exp(-∫ σ_e(s) ds)`, exponential decay of light through a medium.

**Algorithm flow**: ray march along the view ray; at each sample point: compute density → compute optical depth toward the sun → Beer-Lambert attenuation → phase function weighting → accumulate.

## How to Apply

1. **Step 1: Ray-Sphere Intersection** — Intersect view rays with atmosphere shell spheres to get optical-path entry and exit distances.
2. **Step 2: Atmospheric Physical Constants** — Define Rayleigh/Mie coefficients, scale heights, and sun direction.
3. **Step 3: Phase Functions** — Evaluate Rayleigh and Henyey-Greenstein Mie phase for in-scatter direction weighting.
4. **Step 4: Atmospheric Density Sampling** — Sample exponential density falloff with altitude along the view ray.
5. **Step 5: Light Direction Optical Depth** — March toward the sun at each sample to compute Beer-Lambert transmittance.
6. **Step 6: Primary Scattering Integration** — Accumulate in-scattered radiance weighted by phase and transmittance.
7. **Step 7: Tone Mapping** — Map HDR accumulated sky radiance to display range after scattering composite.
## Example

```glsl
// Returns (t_near, t_far); no intersection when t_near > t_far
vec2 raySphereIntersect(vec3 p, vec3 dir, float r) {
    float b = dot(p, dir);
    float c = dot(p, p) - r * r;
    float d = b * b - c;
    if (d < 0.0) return vec2(1e5, -1e5);
    d = sqrt(d);
    return vec2(-b - d, -b + d);
}
```

```glsl
#define PLANET_RADIUS 6371e3
#define ATMOS_RADIUS  6471e3
#define PLANET_CENTER vec3(0.0)

#define BETA_RAY vec3(5.5e-6, 13.0e-6, 22.4e-6)  // Rayleigh scattering coefficients
#define BETA_MIE vec3(21e-6)                        // Mie scattering coefficients
#define BETA_OZONE vec3(2.04e-5, 4.97e-5, 1.95e-6) // Ozone absorption

#define MIE_G 0.76          // Anisotropy parameter 0.76~0.88
#define MIE_EXTINCTION 1.1  // Extinction/scattering ratio

#define H_RAY 8000.0        // Rayleigh scale height
#define H_MIE 1200.0        // Mie scale height
#define H_OZONE 30e3        // Ozone peak altitude
#define OZONE_FALLOFF 4e3   // Ozone decay width

#define PRIMARY_STEPS 32    // Primary ray steps 8(mobile)~64(high quality)
#define LIGHT_STEPS 8       // Light direction steps 4~16
```

```glsl
float phaseRayleigh(float cosTheta) {
    return 3.0 / (16.0 * 3.14159265) * (1.0 + cosTheta * cosTheta);
}

// Henyey-Greenstein phase function
float phaseMie(float cosTheta, float g) {
    float gg = g * g;
    float num = (1.0 - gg) * (1.0 + cosTheta * cosTheta);
    float denom = (2.0 + gg) * pow(1.0 + gg - 2.0 * g * cosTheta, 1.5);
    return 3.0 / (8.0 * 3.14159265) * num / denom;
}
```

## Advanced

Foundational concepts required before using this Skill:

- **GLSL Fundamentals**: uniforms, varyings, built-in functions
- **Vector Math**: dot product, cross product, vector normalization
- **Ray-Sphere Intersection**: given a ray origin and direction, find the intersection distances with a sphere surface
- **Physical Meaning of Exponential Functions** (Beer-Lambert Law): light attenuates exponentially through a medium, `I = I₀ × e^(-σ×d)`, where σ is the extinction coefficient and d is the distance
- **Basic Ray Marching Concepts**: advancing step by step along a ray direction, accumulating information at each sample point

## Gotchas

- Phase function without optical depth integration looks like a fog tint — march along view ray and accumulate density.
- Sun disk size hard-coded in screen space scales wrong on resize — derive angular radius from sun direction and elevation.
- Ignoring earth curvature on horizon views over-brightens haze — add height falloff or density scale with altitude.

## Combine With

- [volumetric-rendering](volumetric-rendering.md)
- [lighting-model](lighting-model.md)
