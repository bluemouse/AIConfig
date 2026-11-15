# fluid-simulation: Fluid Simulation

## Guideline

Incompressible Navier-Stokes equation discretization:

## Rationale

- Navier-Stokes split across advection, diffusion, pressure projection passes.
- Velocity/pressure/ink live in separate RGBA channels per texel.
- Requires [multipass-buffer](multipass-buffer.md) self-feedback each frame.

## How to Apply


1. **Step 1: Data Encoding and Buffer Layout** — Encode fluid physical quantities into the RGBA channels of a texture.
2. **Step 2: Discrete Differential Operators** — Compute gradient, Laplacian, divergence, and curl over a 3x3 pixel neighborhood.
3. **Step 3: Initial Frame and Noise** — Initialize the fluid state and inject a small amount of noise to avoid symmetry lock.
4. **Step 4: Semi-Lagrangian Advection** — Trace backward along the velocity field and sample from the upstream position to update the current pixel.
5. **Step 5: Viscous Diffusion** — Apply Laplacian diffusion to the velocity field to simulate viscosity.
6. **Step 6: Pressure Projection** — Compute the gradient of the pressure field and subtract it from the velocity field to enforce the incompressibility constraint.
7. **Step 7: External Forces and Mouse Interaction** — Inject velocity and ink into the fluid based on mouse input.
8. **Step 8: Boundary Conditions and Numerical Stability** — Handle boundary pixels, clamp numerical ranges, and apply dissipation.

## Example

```glsl
// Data layout: .xy=velocity, .z=pressure/density, .w=ink
#define T(p) texture(uChannel0, (p) / uResolution.xy)

vec4 c = T(p);                    // center
vec4 n = T(p + vec2(0, 1));       // north
vec4 e = T(p + vec2(1, 0));       // east
vec4 s = T(p - vec2(0, 1));       // south
vec4 w = T(p - vec2(1, 0));       // west
```

```glsl
// Laplacian (weighted 3x3 stencil)
const float _K0 = -20.0 / 6.0;
const float _K1 =   4.0 / 6.0;
const float _K2 =   1.0 / 6.0;
vec4 laplacian = _K0 * c
    + _K1 * (n + e + s + w)
    + _K2 * (T(p+vec2(1,1)) + T(p+vec2(-1,1)) + T(p+vec2(1,-1)) + T(p+vec2(-1,-1)));

// Gradient (central difference)
vec4 dx = (e - w) / 2.0;
vec4 dy = (n - s) / 2.0;

// Divergence & Curl
float div = dx.x + dy.y;
float curl = dx.y - dy.x;
```

```glsl
#define DT 0.15  // time step
// Backward trace: sample from upstream, unconditionally stable
vec4 advected = T(p - DT * c.xy);
c.xyw = advected.xyw;
```

## Advanced

### Step 1: Data Encoding and Buffer Layout

**What**: Encode fluid physical quantities into the RGBA channels of a texture.

**Why**: GPU textures serve as the storage medium for fluid state. Each pixel is a grid cell, with channels storing different physical quantities, enabling full fluid state persistence.

**Code**:
```glsl
// Data layout convention:
// .xy = velocity field
// .z  = pressure / density
// .w  = passive scalar, e.g., ink concentration

// Sampling macro — simplify neighborhood access
#define T(p) texture(uChannel0, (p) / uResolution.xy)

// Get current pixel and its four neighbors
vec4 c = T(p);                    // center
vec4 n = T(p + vec2(0, 1));       // north
vec4 e = T(p + vec2(1, 0));       // east
vec4 s = T(p - vec2(0, 1));       // south
vec4 w = T(p - vec2(1, 0));       // west
```

### Step 2: Discrete Differential Operators

**What**: Compute gradient, Laplacian, divergence, and curl over a 3x3 pixel neighborhood.

**Why**: These operators are the foundation for discretizing the Navier-Stokes equations. A 3x3 stencil is more isotropic than a simple cross stencil, reducing grid-direction artifacts.

**Code**:
```glsl
// ===== Laplacian =====
// Weighted 3x3 stencil: center weight _K0, edge weight _K1, corner weight _K2
const float _K0 = -20.0 / 6.0;  // adjustable: center weight
const float _K1 =   4.0 / 6.0;  // adjustable: edge weight
const float _K2 =   1.0 / 6.0;  // adjustable: corner weight

vec4 laplacian = _K0 * c
    + _K1 * (n + e + s + w)
    + _K2 * (T(p+vec2(1,1)) + T(p+vec2(-1,1)) + T(p+vec2(1,-1)) + T(p+vec2(-1,-1)));

// ===== Gradient =====
// Central difference with diagonal correction
vec4 dx = (e - w) / 2.0;
vec4 dy = (n - s) / 2.0;

// ===== Divergence =====
float div = dx.x + dy.y;  // ∂vx/∂x + ∂vy/∂y

// ===== Curl / Vorticity =====
float curl = dx.y - dy.x;  // ∂vy/∂x - ∂vx/∂y
```

### Step 3: Initial Frame and Noise

**What**: Initialize the fluid state and inject a small amount of noise to avoid symmetry lock.

**Why**: If the initial state is entirely zero (zero velocity), the fluid equations will maintain this symmetric state and never move. Adding a small amount of random noise breaks the symmetry, allowing turbulence to develop naturally.

**Code**:
```glsl
if (uFrame < 10) {
    vec2 uv = p / uResolution.xy;
    // Position-based pseudo-random noise
    float noise = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
    // velocity.xy = small noise, pressure.z = 1.0, ink.w = small amount
    fragColor = vec4(noise * 1e-4, noise * 1e-4, 1.0, noise * 0.1);
    return;
}
```

### Step 4: Semi-Lagrangian Advection

**What**: Trace backward along the velocity field and sample from the upstream position to update the current pixel.

**Why**: This is the standard method for handling the `-(v·∇)v` advection term. Direct forward advection on an Eulerian grid leads to instability, while the semi-Lagrangian method is unconditionally stable — it won't blow up regardless of time step size.

**Code**:
```glsl
#define DT 0.15  // adjustable: time step, larger = faster fluid motion but may reduce accuracy

// Core: backward tracing — find the "upstream" position by tracing backward along velocity
// Then sample from the upstream position, effectively "transporting" the upstream state here
vec4 advected = T(p - DT * c.xy);

// Only advect velocity and passive scalar (ink), preserve local pressure
c.xyw = advected.xyw;
```

### Step 5: Viscous Diffusion

**What**: Apply Laplacian diffusion to the velocity field to simulate viscosity.

**Why**: Corresponds to the `ν∇²v` term. Viscosity smooths the velocity field, dissipating small-scale vortices. The parameter `ν` controls whether the fluid behaves like "water" (low viscosity) or "honey" (high viscosity).

**Code**:
```glsl
#define NU 0.5     // adjustable: kinematic viscosity coefficient. 0.01=water, 1.0=syrup
#define KAPPA 0.1  // adjustable: passive scalar (ink) diffusion coefficient

c.xy  += DT * NU * laplacian.xy;     // velocity diffusion
c.w   += DT * KAPPA * laplacian.w;   // ink diffusion
```

### Step 6: Pressure Projection

**What**: Compute the gradient of the pressure field and subtract it from the velocity field to enforce the incompressibility constraint.

**Why**: This is the core of Helmholtz-Hodge decomposition — decomposing the velocity field into a divergence-free part (what we want) and a curl-free part. By projecting out the divergence component via `v = v - K·∇p`, we ensure `∇·v ≈ 0`. In 
**Code**:
```glsl
#define K 0.2  // adjustable: pressure correction strength. Too large causes oscillation, too small yields poor incompressibility

// Pressure is stored in the .z channel
// Use pressure gradient to correct velocity, eliminating divergence
c.xy -= K * vec2(dx.z, dy.z);

// Mass conservation: update density/pressure based on divergence (Euler method)
c.z -= DT * (dx.z * c.x + dy.z * c.y + div * c.z);
```

### Step 7: External Forces and Mouse Interaction

**What**: Inject velocity and ink into the fluid based on mouse input.

**Why**: The external force term `f` is the entry point for user interaction. The typical approach is to apply a Gaussian-decaying velocity impulse and ink injection near the mouse position.

**Code**:
```glsl
// Mouse interaction — drag to inject velocity and ink
if (uMouse.z > 0.0) {
    vec2 mousePos = uMouse.xy;
    vec2 mouseDelta = uMouse.xy - uMouse.zw;  // drag direction

    float dist = length(p - mousePos);
    float influence = exp(-dist * dist / 50.0);  // adjustable: 50.0 controls influence radius

    c.xy += DT * influence * mouseDelta;  // inject velocity
    c.w  += DT * influence;                // inject ink
}
```

### Step 8: Boundary Conditions and Numerical Stability

**What**: Handle boundary pixels, clamp numerical ranges, and apply dissipation.

**Why**: Without boundary conditions, the fluid "leaks" off-screen; without dissipation, fluid energy accumulates indefinitely, causing numerical explosion.

**Code**:
```

```glsl
// No-slip: zero velocity at domain edges
if (uv.x < texel.x || uv.x > 1.0 - texel.x) velocity = vec2(0.0);
// Dissipation
velocity *= 0.998;
```

### Step 10: Visualization Pass

**What**: Render ink/density with color mapping in a separate image pass.

```glsl
float ink = texture(uPass0, uv).w;
fragColor = vec4(vec3(ink), 1.0);
```

## Gotchas

- Semi-Lagrangian advection without divergence projection creates sources/sinks — run pressure solve each step.
- Velocity stored in low-precision buffers accumulates drift — use `RG32F` or clamp max velocity.
- CFL violation when `dt` too large for grid velocity blows up — scale `dt` by `min(cellSize / max|v|)`.

## Combine With

- [multipass-buffer](multipass-buffer.md)
- [procedural-noise](procedural-noise.md)
