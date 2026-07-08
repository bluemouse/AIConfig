# normal-estimation: Normal Estimation

## Guideline

The gradient of an SDF `nabla f(p)` points in the direction of fastest distance increase, which is the outward surface normal. Numerical differentiation approximates the gradient:

## Rationale

$$\vec{n} = \text{normalize}\left(\nabla f(p)\right)$$

Three main strategies:

| Method | Samples | Accuracy | Recommendation |
|--------|---------|----------|----------------|
| Forward difference | 4 | O(epsilon) | Simple scenes |
| Central difference | 6 | O(epsilon^2) | When symmetry is needed |
| **Tetrahedron method** | **4** | **Between the two** | **Preferred** |

Key parameter epsilon: commonly `0.0005 ~ 0.001`; for advanced scenes, multiply by ray distance `t` for adaptive scaling.

## How to Apply


1. **Step 1: Define the SDF Scene Function** — Create a `map(vec3 p) -> float` function that returns the signed distance from any point in space to the scene surface.
2. **Step 2: Choose a Difference Method and Implement the Normal Function** — Sample the SDF along the 4 vertices of a regular tetrahedron, computing the weighted sum to obtain the gradient.
3. **Step 3: Normalize and Apply to Lighting** — Call `normalize()` on the gradient vector to obtain the unit normal for subsequent lighting calculations.

## Example

```glsl
float map(vec3 p) {
    float d = length(p) - 1.0; // unit sphere
    return d;
}
```

```glsl
const float EPSILON = 1e-3;

vec3 getNormal(vec3 p) {
    vec3 n;
    n.x = map(vec3(p.x + EPSILON, p.y, p.z));
    n.y = map(vec3(p.x, p.y + EPSILON, p.z));
    n.z = map(vec3(p.x, p.y, p.z + EPSILON));
    return normalize(n - map(p));
}
```

```glsl
vec3 getNormal(vec3 p) {
    vec2 o = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + o.xyy) - map(p - o.xyy),
        map(p + o.yxy) - map(p - o.yxy),
        map(p + o.yyx) - map(p - o.yyx)
    ));
}
```

## Advanced

### Step 1: Define the SDF Scene Function

**What**: Create a `map(vec3 p) -> float` function that returns the signed distance from any point in space to the scene surface.

**Why**: All normal estimation methods need to repeatedly call this function to sample the distance field. The normal function itself does not care about the SDF shape — it only needs to query distance values at different positions in space.

```glsl
float map(vec3 p) {
    float d = length(p) - 1.0; // Unit sphere
    // Can compose more SDF primitives
    return d;
}
```

### Step 2: Choose a Difference Method and Implement the Normal Function

#### Method A: Forward Differences — 4 Samples

**What**: Sample the SDF at point `p` and at three axis-aligned offsets, using the differences to build the gradient.

**Why**: The simplest and most intuitive approach. Requires 4 samples (`map(p)` once + three offsets once each), suitable for beginners and performance-sensitive scenarios with lower accuracy requirements.

**Mathematical derivation**:
- `∂f/∂x ≈ (f(x+ε, y, z) - f(x, y, z)) / ε`
- Since we `normalize()` at the end, the constant denominator `ε` can be omitted
- Thus `n = normalize(map(p+εx̂) - map(p), map(p+εŷ) - map(p), map(p+εẑ) - map(p))`

```glsl
// Classic forward difference
const float EPSILON = 1e-3;

vec3 getNormal(vec3 p) {
    vec3 n;
    n.x = map(vec3(p.x + EPSILON, p.y, p.z));
    n.y = map(vec3(p.x, p.y + EPSILON, p.z));
    n.z = map(vec3(p.x, p.y, p.z + EPSILON));
    return normalize(n - map(p));
}
```

#### Method B: Central Differences — 6 Samples

**What**: Sample once in each positive and negative direction per axis, taking the difference.

**Why**: Symmetric sampling eliminates the first-order error term, improving accuracy from O(ε) to O(ε²). The cost is 6 SDF calls.

**Mathematical derivation**:
- Taylor expansion: `f(x+ε) = f(x) + εf'(x) + ε²f''(x)/2 + ...`
- `f(x-ε) = f(x) - εf'(x) + ε²f''(x)/2 - ...`
- Subtraction: `f(x+ε) - f(x-ε) = 2εf'(x) + O(ε³)`
- The first-order error term is eliminated, improving accuracy by one order

```glsl
// Compact swizzle notation
vec3 getNormal(vec3 p) {
    vec2 o = vec2(0.001, 0.0);
    return normalize(vec3(
        map(p + o.xyy) - map(p - o.xyy),
        map(p + o.yxy) - map(p - o.yxy),
        map(p + o.yyx) - map(p - o.yyx)
    ));
}
```

#### Method C: Tetrahedron Technique — 4 Samples (Recommended)

**What**: Sample the SDF along the 4 vertices of a regular tetrahedron, computing the weighted sum to obtain the gradient.

**Why**: Requires only 4 samples (2 fewer than central difference), yet is more accurate and symmetric than forward difference.

**Mathematical derivation**:
- The 4 vertices of a regular tetrahedron: `(+,+,+)`, `(+,-,-)`, `(-,+,-)`, `(-,-,+)`
- The coefficient `0.5773 ≈ 1/√3` normalizes the vertices onto the unit sphere
- The weighted sum `Σ eᵢ·map(p + eᵢ·ε)` is equivalent to a gradient estimate in 4 symmetric directions
- Due to the perfect symmetry of the tetrahedron, error distribution is more uniform than forward difference
- Actual accuracy falls between forward and central difference, but only requires 4 samples

```glsl
// Classic tetrahedron technique
vec3 calcNormal(vec3 pos) {
    float eps = 0.0005; // Adjustable: sample offset
    vec2 e = vec2(1.0, -1.0) * 0.5773;
    return normalize(
        e.xyy * map(pos + e.xyy * eps) +
        e.yyx * map(pos + e.yyx * eps) +
        e.yxy * map(pos + e.yxy * eps) +
        e.xxx * map(pos + e.xxx * eps)
    );
}
```

### Step 3: Normalize and Apply to Lighting

**What**: Call `normalize()` on the gradient vector to obtain the unit normal for subsequent lighting calculations.

**Why**: The gradient length obtained from finite differences depends on the local gradient magnitude of the SDF. Lighting calculations require unit vectors. For an ideal SDF (gradient magnitude of 1), normalize barely changes the direction, but for SDFs that have undergone boolean operations or deformations, the gradient magnitude may deviate from 1, and normalize ensures correct results.

```glsl
// After a raymarching hit
vec3 pos = ro + rd * t;        // Hit point
vec3 nor = calcNormal(pos);    // Surface normal

// Basic Lambertian diffuse
vec3 lightDir = normalize(vec3(1.0, 4.0, -4.0));
float diff = max(dot(nor, lightDir), 0.0);
vec3 col = vec3(0.8) * diff;
```

---

## Gotchas

- Central differences on noisy SDFs amplify high-frequency error — increase epsilon or smooth the field first.
- Epsilon too large on curved surfaces rounds corners — scale epsilon to scene units and distance at hit.
- Normals from 2D SDF gradients differ from 3D surface normals — use tetrahedral or six-tap 3D gradient for lighting.

## Combine With

- [ray-marching](ray-marching.md)
- [lighting-model](lighting-model.md)
