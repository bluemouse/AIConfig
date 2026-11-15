# voxel-rendering: Voxel Rendering

## Guideline

The core of voxel rendering is the **DDA (Digital Differential Analyzer) ray traversal algorithm**: cast a ray from the camera through each pixel, stepping through the 3D grid cell by cell along the ray direction until hitting an occupied voxel.

## Rationale

For ray `P(t) = rayPos + t * rayDir`, DDA maintains:
- **`mapPos`** = `floor(rayPos)`: current grid coordinate (integer)
- **`deltaDist`** = `abs(1.0 / rayDir)`: t cost to cross one cell
- **`sideDist`** = `(sign(rayDir) * (mapPos - rayPos) + sign(rayDir) * 0.5 + 0.5) * deltaDist`: t distance to the next boundary on each axis

Each step advances along the axis with the smallest `sideDist`, updating `sideDist += deltaDist` and `mapPos += rayStep`.

Normal on hit: `normal = -mask * rayStep`

Face UV is obtained by projecting the hit point onto the two tangent axes of the hit face.

## How to Apply

1. **Step 1: Camera Ray Construction** — Build per-pixel ray origin and direction from screen UVs and camera basis vectors.
2. **Step 2: DDA Initialization** — Set `mapPos = ivec3(floor(rayPos))`, `deltaDist`, and `sideDist` for the first grid crossing.
3. **Step 3: DDA Traversal Loop (Branchless Version)** — Advance along the axis with smallest `sideDist` until a voxel hit or max steps.
4. **Step 4: Voxel Occupancy Function** — Return whether `mapPos` contains solid material (texture lookup or procedural rule).
5. **Step 5: Face Shading (Normal + Base Color)** — Shade hit face using `normal = -mask * rayStep` and per-voxel color.
6. **Step 6: Precise Hit Position and Face UV** — Refine hit `t` and project onto face tangent axes for texturing.
7. **Step 7: Neighbor Voxel AO** — Darken faces occluded by adjacent occupied voxels.
8. **Step 8: DDA Shadow Ray** — Cast a short DDA shadow ray toward the light to attenuate direct lighting.
## Example

```glsl
vec2 screenPos = (gl_FragCoord.xy / uResolution.xy) * 2.0 - 1.0;
vec3 cameraDir = vec3(0.0, 0.0, 0.8);  // Focal length; larger = narrower FOV
vec3 cameraPlaneU = vec3(1.0, 0.0, 0.0);
vec3 cameraPlaneV = vec3(0.0, 1.0, 0.0) * uResolution.y / uResolution.x;
vec3 rayDir = cameraDir + screenPos.x * cameraPlaneU + screenPos.y * cameraPlaneV;
vec3 rayPos = vec3(0.0, 2.0, -12.0);
```

```glsl
ivec3 mapPos = ivec3(floor(rayPos));
vec3 rayStep = sign(rayDir);
vec3 deltaDist = abs(1.0 / rayDir);  // When ray is normalized, equivalent to abs(1.0/rd), no length() needed
vec3 sideDist = (sign(rayDir) * (vec3(mapPos) - rayPos) + (sign(rayDir) * 0.5) + 0.5) * deltaDist;
```

```glsl
#define MAX_RAY_STEPS 64

bvec3 mask;
for (int i = 0; i < MAX_RAY_STEPS; i++) {
    if (getVoxel(mapPos)) break;
    // Branchless axis selection
    mask = lessThanEqual(sideDist.xyz, min(sideDist.yzx, sideDist.zxy));
    sideDist += vec3(mask) * deltaDist;
    mapPos += ivec3(vec3(mask)) * ivec3(rayStep);
}
```

## Advanced

### GLSL Fundamentals
- GLSL basic syntax (uniforms, varyings, built-in functions)
- Vector math: dot product, cross product, normalize, reflect
- Understanding of step functions like `floor()`, `sign()`, `step()`

### Ray-AABB Intersection (Ray-Box Intersection)
The foundation of voxel rendering is ray tracing. You need to understand how a ray `P(t) = O + t * D` intersects with an axis-aligned bounding box (AABB). The DDA algorithm is essentially an extension of this test to the entire grid space.

### Basic Lighting Models
- Lambert diffuse: `diffuse = max(dot(normal, lightDir), 0.0)`
- Phong specular: `specular = pow(max(dot(reflect(-lightDir, normal), viewDir), 0.0), shininess)`

### SDF (Signed Distance Field) Basics
An SDF function returns the signed distance from a point to the nearest surface (negative inside, positive outside). In voxel rendering, SDF is commonly used to define voxel occupancy: `d < 0.0` means occupied.

Common SDF primitives:
```glsl
float sdSphere(vec3 p, float r) { return length(p) - r; }
float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return min(max(d.x, max(d.y, d.z)), 0.0) + length(max(d, 0.0));
}
```

SDF boolean operations:
- Union: `min(d1, d2)`
- Intersection: `max(d1, d2)`
- Subtraction: `max(d1, -d2)`

## Gotchas

- DDA without boundary checks walks past grid limits — clamp voxel indices and return miss outside volume.
- Minecraft-style ambient on face normals alone flattens caves — combine face AO with neighbor occupancy.
- Large voxel worlds without chunk LOD stall the march loop — cap steps per ray and stream chunks near camera.

## Combine With

- [lighting-model](lighting-model.md)
- [shadow-techniques](shadow-techniques.md)
