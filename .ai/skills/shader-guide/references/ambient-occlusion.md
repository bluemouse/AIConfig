# ambient-occlusion: Ambient Occlusion

## Guideline

Sample the SDF along the surface normal direction at multiple distances, comparing the "expected distance" with the "actual distance" to estimate occlusion.

## Rationale


For surface point P, normal N, and sampling distance h:
- Expected distance = h (SDF should equal h when surroundings are open)
- Actual distance = map(P + N * h)
- Occlusion contribution = h - map(P + N * h) (larger difference = stronger occlusion)

```
AO = 1 - k * sum(weight_i * max(0, h_i - map(P + N * h_i)))
```

Result: 1.0 = no occlusion, 0.0 = fully occluded. Weights decay exponentially (closer samples have higher weight).

## How to Apply


1. **Step 1: Build the Base SDF Scene** — Define a `map()` function that returns the signed distance value for any point in space.
2. **Step 2: Compute Surface Normal** — Compute the normal direction via finite difference approximation of the SDF gradient.
3. **Step 3: Implement Classic Normal-Direction AO (Additive Accumulation)** — Sample the SDF at 5 distances along the normal direction, accumulating occlusion.
4. **Step 4: Apply AO to Lighting** — Multiply the AO factor into ambient and indirect light components.
5. **Step 5: Raymarching Main Loop Integration** — Integrate AO into the complete raymarching pipeline.

## Example

```glsl
float map(vec3 p) {
    float d = p.y; // ground
    d = min(d, length(p - vec3(0.0, 1.0, 0.0)) - 1.0); // sphere
    d = min(d, length(vec2(length(p.xz) - 1.5, p.y - 0.5)) - 0.4); // torus
    return d;
}
```

```glsl
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}
```

```glsl
float calcAO(vec3 pos, vec3 nor) {
    float occ = 0.0;
    float sca = 1.0;
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.12 * float(i) / 4.0; // sampling distance 0.01~0.13
        float d = map(pos + h * nor);
        occ += (h - d) * sca; // (expected - actual) * weight
        sca *= 0.95;
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}
```

## Advanced

### Step 1: Build the Base SDF Scene

**What**: Define a `map()` function that returns the signed distance value for any point in space.

**Why**: AO computation relies entirely on SDF queries, so a working distance field is needed first.

```glsl
float map(vec3 p) {
    float d = p.y; // Ground plane
    d = min(d, length(p - vec3(0.0, 1.0, 0.0)) - 1.0); // Sphere
    d = min(d, length(vec2(length(p.xz) - 1.5, p.y - 0.5)) - 0.4); // Torus
    return d;
}
```

### Step 2: Compute Surface Normal

**What**: Compute the normal direction via finite difference approximation of the SDF gradient.

**Why**: AO sampling probes outward along the normal direction; the normal determines the sampling direction.

```glsl
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}
```

### Step 3: Implement Classic Normal-Direction AO (Additive Accumulation)

**What**: Sample the SDF at 5 distances along the normal direction, accumulating occlusion.

**Why**: This is a classic method — the most concise and efficient SDF-AO implementation. 5 samples strike an excellent balance between quality and performance. The weight decays at 0.95 exponentially, giving closer samples more influence (near-surface occlusion is more perceptually important).

```glsl
// Classic AO
float calcAO(vec3 pos, vec3 nor) {
    float occ = 0.0;
    float sca = 1.0; // Initial weight
    for (int i = 0; i < 5; i++) {
        float h = 0.01 + 0.12 * float(i) / 4.0; // Sample distance: 0.01 ~ 0.13
        float d = map(pos + h * nor);             // Actual SDF distance
        occ += (h - d) * sca;                     // Accumulate (expected - actual) × weight
        sca *= 0.95;                              // Weight decay
    }
    return clamp(1.0 - 3.0 * occ, 0.0, 1.0);
}
```

### Step 4: Apply AO to Lighting

**What**: Multiply the AO factor into ambient and indirect light components.

**Why**: AO simulates the degree to which indirect light is occluded. Physically, it should only affect ambient/indirect light, not the direct light source's diffuse and specular (direct light occlusion is handled by shadows). However, in practice AO is often multiplied into all lighting for a stronger visual effect.

```glsl
float ao = calcAO(pos, nor);

// Method A: Affect only ambient light (physically correct)
vec3 ambient = vec3(0.2, 0.3, 0.5) * ao;
vec3 color = diffuse * shadow + ambient;

// Method B: Affect all lighting (stronger visual effect)
vec3 color = (diffuse * shadow + ambient) * ao;

// Method C: Combined with sky visibility bias
float skyVis = 0.5 + 0.5 * nor.y; // Upward-facing surfaces are brighter
vec3 color = diffuse * shadow + ambient * ao * skyVis;
```

### Step 5: Raymarching Main Loop Integration

**What**: Integrate AO into the complete raymarching pipeline.

**Why**: AO is part of the lighting computation and needs to be calculated after hitting a surface but before final output.

```glsl
void main() {
    // ... camera setup, ray generation ...

    // Raymarching loop
    float t = 0.0;
    for (int i = 0; i < 128; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);
        if (d < 0.001) break;
        t += d;
        if (t > 100.0) break;
    }

    // Compute lighting on hit
    vec3 col = vec3(0.0);
    if (t < 100.0) {
        vec3 pos = ro + rd * t;
        vec3 nor = calcNormal(pos);
        float ao = calcAO(pos, nor);

        // Lighting
        vec3 lig = normalize(vec3(1.0, 0.8, -0.6));
        float dif = clamp(dot(nor, lig), 0.0, 1.0);
        float sky = 0.5 + 0.5 * nor.y;
        col = vec3(1.0) * dif + vec3(0.2, 0.3, 0.5) * sky * ao;
    }

    fragColor = vec4(col, 1.0);
}
```

## Gotchas

- AO sampled only along geometric normal misses concave cavities — bias samples toward cavity direction or use multi-tap hemisphere.
- Large AO radius on repeating SDFs bleeds across domain repetitions — limit AO march distance to local cell size.
- Dark AO multiplied twice (object + post) crushes midtones — apply AO once in the lighting composite.

## Combine With

- [lighting-model](lighting-model.md)
- [normal-estimation](normal-estimation.md)
