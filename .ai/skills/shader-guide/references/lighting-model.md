# lighting-model: Lighting Models

## Guideline

Lighting = Diffuse + Specular Reflection: combine Lambert diffuse with specular highlights (Blinn-Phong or Cook-Torrance) using surface normal **N**, light **L**, and view **V**.

## Rationale


- **Diffuse**: Lambert's law `I = max(0, N·L)`
- **Specular**: Empirical model uses Blinn-Phong `pow(max(0, N·H), shininess)`; physically-based model uses Cook-Torrance BRDF

### Key Formulas

```
Lambert:        L_diffuse  = albedo * lightColor * max(0, N·L)
Blinn-Phong:    H = normalize(V + L); L_specular = lightColor * pow(max(0, N·H), shininess)
Cook-Torrance:  f_specular = D(h) * F(v,h) * G(l,v,h) / (4 * (N·L) * (N·V))
Fresnel:        F = F0 + (1 - F0) * (1 - V·H)^5
```

- **D** = GGX/Trowbridge-Reitz normal distribution
- **F** = Schlick Fresnel approximation
- **G** = Smith geometric shadowing
- F0: dielectric ~0.04, metals use baseColor

## How to Apply


1. **Step 1: Scene Foundation (UV, Camera, Raymarching)** — Establish the standard UV normalization, camera matrix, ray march, and normal estimation foundation before applying any lighting model.
2. **Step 2: Lambert Diffuse** — Compute basic diffuse lighting — the foundation of all lighting models.
3. **Step 3: Blinn-Phong Specular** — Add specular highlights based on the half vector.
4. **Step 4: Fresnel-Schlick Approximation** — Compute reflectance based on viewing angle — reflectance increases at grazing angles ("edge brightening" effect).

## Example

```glsl
// SDF normal (finite difference method)
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

vec3 N = calcNormal(pos);           // surface normal
vec3 V = -rd;                        // view direction
vec3 L = normalize(lightPos - pos);  // light direction (point light)
// directional light: vec3 L = normalize(vec3(0.6, 0.8, -0.5));
```

```glsl
float NdotL = max(0.0, dot(N, L));
vec3 diffuse = albedo * lightColor * NdotL;

// energy-conserving version
vec3 diffuse_conserved = albedo / PI * lightColor * NdotL;

// Half-Lambert (reduces over-darkening on backlit faces, commonly used for SSS approximation)
float halfLambert = NdotL * 0.5 + 0.5;
vec3 diffuse_wrapped = albedo * lightColor * halfLambert;
```

```glsl
vec3 H = normalize(V + L);
float NdotH = max(0.0, dot(N, H));
float SHININESS = 32.0;  // 4.0 (rough) ~ 256.0 (smooth)

// with normalization factor for energy conservation
float normFactor = (SHININESS + 8.0) / (8.0 * PI);
float spec = normFactor * pow(NdotH, SHININESS);
vec3 specular = lightColor * spec;
```

## Advanced

### Step 1: Scene Foundation (UV, Camera, Raymarching)

**What**: Establish the standard UV normalization, camera matrix, ray march, and normal estimation foundation before applying any lighting model.
**Why**: Lighting calculations require normal N, view direction V, and light direction L as inputs, all of which depend on scene geometry. Without correct normals and direction vectors, no lighting model can work.

**Details**:
- UV coordinates are typically normalized as `(2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y` to ensure correct aspect ratio
- The camera uses a look-at matrix: forward direction `ww`, right direction `uu`, up direction `vv`
- SDF normals use six-point central difference, which is more accurate than forward difference
- The epsilon value in `e = vec2(0.001, 0.0)` affects normal accuracy: too large blurs details, too small introduces noise

**Code**:
```glsl
// Compute normal from SDF scene (finite differences) — standard technique
vec3 calcNormal(vec3 p) {
    vec2 e = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + e.xyy) - map(p - e.xyy),
        map(p + e.yxy) - map(p - e.yxy),
        map(p + e.yyx) - map(p - e.yyx)
    ));
}

// Prepare basic vectors needed for lighting
vec3 N = calcNormal(pos);           // Surface normal
vec3 V = -rd;                        // View direction (reverse of ray)
vec3 L = normalize(lightPos - pos);  // Light direction (point light)
// Or directional light: vec3 L = normalize(vec3(0.6, 0.8, -0.5));
```

### Step 2: Lambert Diffuse

**What**: Compute basic diffuse lighting — the foundation of all lighting models.

**Why**: Lambert's law describes the ideal diffuse behavior of rough surfaces — brightness is proportional to cos(angle of incidence). This is the most fundamental physically-based lighting model, assuming light enters the surface and is scattered uniformly.

**Details**:
- `max(0.0, dot(N, L))` uses `max(0,...)` to avoid negative values (backface lighting)
- Energy-conserving Lambertian diffuse requires dividing by PI, since Lambert BRDF = albedo/PI and the integrated irradiance = PI * L_incoming
- Half-Lambert (`NdotL * 0.5 + 0.5`) is a technique invented by Valve that maps [-1,1] to [0,1], giving backlit areas some brightness; commonly used for character rendering and SSS approximation
- Many ocean shaders use a similar wrapped diffuse pattern

**Code**:
```glsl
// Basic Lambert diffuse
float NdotL = max(0.0, dot(N, L));
vec3 diffuse = albedo * lightColor * NdotL;

// Energy-conserving version (albedo/PI)
vec3 diffuse_conserved = albedo / PI * lightColor * NdotL;

// Half-Lambert variant (wrapped dot product)
// Reduces over-darkening on backlit faces, commonly used for SSS approximation
float halfLambert = NdotL * 0.5 + 0.5;
vec3 diffuse_wrapped = albedo * lightColor * halfLambert;
```

### Step 3: Blinn-Phong Specular

**What**: Add specular highlights based on the half vector.

**Why**: Blinn-Phong is more computationally efficient and physically plausible than classic Phong. The half vector H is the average direction of V and L; the highlight is brightest when H aligns with N. Blinn-Phong also behaves more realistically at grazing angles compared to Phong.

**Details**:
- Half vector H = normalize(V + L), which avoids the reflect computation needed by Phong's reflect(-L, N)
- Shininess controls highlight concentration: 4.0 gives a very rough surface feel, 256.0 approaches a mirror
- The normalization factor `(shininess + 8.0) / (8.0 * PI)` ensures total reflected energy remains constant when changing shininess (energy conservation)
- Based on the standard half vector method used in many raymarching shaders

**Code**:
```glsl
// Blinn-Phong specular (standard half vector method)
vec3 H = normalize(V + L);
float NdotH = max(0.0, dot(N, H));

// Empirical model: directly use shininess exponent
float SHININESS = 32.0;  // Adjustable: 4.0 (rough) ~ 256.0 (mirror-like)
float spec = pow(NdotH, SHININESS);

// With energy-conserving normalization factor
// Normalization factor (s+8)/(8*PI) ensures total energy is preserved when changing shininess
float normFactor = (SHININESS + 8.0) / (8.0 * PI);
float spec_normalized = normFactor * pow(NdotH, SHININESS);

vec3 specular = lightColor * spec_normalized;
```

### Step 4: Fresnel-Schlick Approximation

**What**: Compute reflectance based on viewing angle — reflectance increases at grazing angles ("edge brightening" effect).

**Why**: All real materials approach 100% reflectance at grazing angles. This is a fundamental physical phenomenon (Fresnel effect). The Schlick approximation uses a fifth-power curve to simulate this, and is a core component of all PBR pipelines. This is a ubiquitous formula in real-time rendering.

**Details**:
- F0 is the reflectance at normal incidence (looking straight at the surface)
- Dielectrics (plastic, water, etc.): F0 is approximately 0.02~0.04; most light is scattered (diffuse)
- Metals: F0 uses the material's baseColor, since metals have virtually no diffuse reflection
- `mix(vec3(0.04), baseColor, metallic)` is the unified metallic workflow, interpolating between dielectrics and metals
- Using V·H for the Cook-Torrance BRDF specular term
- Using N·V for environment reflections, rim lighting, etc.
- A widely used approximation in both real-time and offline rendering pipelines.

**Code**:
```glsl
// Fresnel-Schlick approximation (standard formulation)
vec3 fresnelSchlick(vec3 F0, float cosTheta) {
    return F0 + (1.0 - F0) * pow(1.0 - cosTheta, 5.0);
}

// Dielectrics (plastic, water, etc.): F0 approximately 0.02~0.04
vec3 F0_dielectric = vec3(0.04);

// Metals: F0 uses the material's baseColor
vec3 F0_metal = baseColor;

// Unified metallic workflow
vec3 F0 = mix(vec3(0.04), baseColor, metallic);

// Compute Fresnel using V·H (for specular BRDF)
float VdotH = max(0.0, dot(V, H));
vec3 F = fresnelSchlick(F0, VdotH);

// Alternatively, compute Fresnel using N·V (for environment reflections, rim light)
// Optional: pow(fGloss, 20.0) factor for gloss adjustment
float NdotV = max(0.0, dot(N, V));
vec3 F_env = F0 + (1.0 - F0) * pow(1.0 - NdotV, 5.0);
```

### Step 6: Ambient and Final Composite

**What**: Add ambient/sky term and combine diffuse + specular per model (Phong, PBR, toon).

```glsl
vec3 ambient = 0.03 * albedo;
vec3 Lo = (kD * albedo / PI + spec) * radiance * NdotL;
return ambient + Lo;
```

## Gotchas

- Specular without energy conservation blows out highlights — clamp Fresnel or use physically based `F * G * D / (4 * NdotL * NdotV)`.
- Diffuse plus specular can exceed 1.0 on white dielectrics — divide by `(1 + F)` or use metallic workflow separation.
- N·L clamped to 0 on backfaces kills rim lighting — add ambient or separate view-dependent Fresnel term.

## Combine With

- [shadow-techniques](shadow-techniques.md)
- [ambient-occlusion](ambient-occlusion.md)
