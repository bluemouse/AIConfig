# water-ocean: Water and Ocean

## Guideline

Water rendering solves three problems: **water surface shape generation**, **light-water surface interaction**, and **water body color compositing**.

## Rationale

### Wave Generation: Exponential Sine Stacking + Derivative Domain Warping

`wave(x) = exp(sin(x) - 1)` — sharp wave crests (`exp(0)=1`), broad flat troughs (`exp(-2)≈0.135`), similar to a trochoidal profile but at much lower computational cost than Gerstner waves.

When stacking multiple waves, use **derivative domain warping (Drag)**:
```
position += direction * derivative * weight * DRAG_MULT
```
Small ripples cluster on the crests of large waves, simulating capillary waves riding on gravity waves.

### Lighting: Schlick Fresnel + Subsurface Scattering

- **Schlick Fresnel**: `F = F0 + (1-F0) * (1-dot(N,V))^5`, water F0 ≈ 0.04
- **SSS approximation**: thicker water layer at troughs → stronger blue-green scattering; thinner layer at crests → weaker scattering

### Water Surface Intersection: Bounded Height Field Marching

The water surface is constrained within a `[0, -WATER_DEPTH]` bounding box, with adaptive step size: `step = ray_y - wave_height`.

## How to Apply

1. **Step 1: Exponential Sine Wave Function** — Layer Gerstner or exp-sin waves for sharp crests and broad troughs.
2. **Step 2: Multi-Octave Wave Stacking with Domain Warping** — Stack octaves and warp position by wave derivatives for capillary detail.
3. **Step 3: Bounded Bounding Box Ray Marching** — March rays against height field constrained to `[0, -WATER_DEPTH]`.
4. **Step 4: Normal Calculation and Distance Smoothing** — Derive surface normal from wave height gradient; smooth hit distance.
5. **Step 5: Fresnel Reflection and Subsurface Scattering** — Apply Schlick Fresnel and depth-tinted SSS at troughs vs crests.
6. **Step 6: Atmosphere and Tone Mapping** — Composite sky reflection and tone-map HDR water color for display.
## Example

```glsl
// Single wave: exp(sin(x)-1) produces sharp peaks and broad troughs, returns (value, negative derivative)
vec2 wavedx(vec2 position, vec2 direction, float frequency, float timeshift) {
    float x = dot(direction, position) * frequency + timeshift;
    float wave = exp(sin(x) - 1.0);
    float dx = wave * cos(x);
    return vec2(wave, -dx);
}
```

```glsl
#define DRAG_MULT 0.38  // Domain warp strength, 0=none, 0.5=strong clustering

float getwaves(vec2 position, int iterations) {
    float wavePhaseShift = length(position) * 0.1;
    float iter = 0.0;
    float frequency = 1.0;
    float timeMultiplier = 2.0;
    float weight = 1.0;
    float sumOfValues = 0.0;
    float sumOfWeights = 0.0;
    for (int i = 0; i < iterations; i++) {
        vec2 p = vec2(sin(iter), cos(iter));  // Pseudo-random wave direction
        vec2 res = wavedx(position, p, frequency, uTime * timeMultiplier + wavePhaseShift);
        position += p * res.y * weight * DRAG_MULT; // Derivative domain warp
        sumOfValues += res.x * weight;
        sumOfWeights += weight;
        weight = mix(weight, 0.0, 0.2);      // Weight decay
        frequency *= 1.18;                     // Frequency growth rate
        timeMultiplier *= 1.07;                // Dispersion
        iter += 1232.399963;                   // Uniform direction distribution
    }
    return sumOfValues / sumOfWeights;
}
```

```glsl
#define WATER_DEPTH 1.0

float intersectPlane(vec3 origin, vec3 direction, vec3 point, vec3 normal) {
    return clamp(dot(point - origin, normal) / dot(direction, normal), -1.0, 9991999.0);
}

float raymarchwater(vec3 camera, vec3 start, vec3 end, float depth) {
    vec3 pos = start;
    vec3 dir = normalize(end - start);
    for (int i = 0; i < 64; i++) {
        float height = getwaves(pos.xz, ITERATIONS_RAYMARCH) * depth - depth;
        if (height + 0.01 > pos.y) {
            return distance(pos, camera);
        }
        pos += dir * (pos.y - height);      // Adaptive step size
    }
    return distance(start, camera);
}
```

## Advanced

- **GLSL Fundamentals**: uniforms, varyings, built-in functions
- **Vector Math**: dot product, cross product, reflection/refraction vectors
- **Basic Raymarching Concepts**
- **FBM (Fractal Brownian Motion) / Multi-octave Noise Layering Basics**
- **Physical Intuition of the Fresnel Effect**: strong reflection at grazing angles, strong transmission at normal incidence

## Gotchas

- Gerstner waves without choppiness look sinusoidal and flat — add horizontal displacement tied to wave steepness.
- Specular sun glint without Fresnel looks painted on — modulate glint by `pow(1 - NdotV, 5)`.
- Deep and shallow colors lerped by constant depth ignore bathymetry — drive depth from floor distance or heightmap.

## Combine With

- [atmospheric-scattering](atmospheric-scattering.md)
- [lighting-model](lighting-model.md)
