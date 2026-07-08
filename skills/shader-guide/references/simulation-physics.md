# simulation-physics: GPU Physics Simulation

## Guideline

The core paradigm of GPU physics simulation is **Buffer Feedback**: physical state is stored in texture buffers, each frame reads the previous frame's state → computes → writes back, with each pixel processed independently in parallel.

## Rationale

- Buffer feedback stores position, velocity, and force fields in texture channels.
- Semi-Lagrangian advection and discrete Laplacian stencils drive wave/cloth solvers.
- Pair with [multipass-buffer](multipass-buffer.md) for ping-pong state.

## How to Apply


1. **Step 1: Ping-Pong Double Buffer Structure** — Create two Buffers (A and B) that alternate read/write to achieve state persistence.
2. **Step 2: Interaction-Driven (External Force Injection)** — Inject energy into the simulation through mouse clicks or programmatic generation.
3. **Step 3: Rendering Layer (Height Field Visualization)** — Read simulation results in the Image Pass, compute normals via gradient calculation, and render lighting effects.
4. **Step 4: Chained Multi-Buffer Iteration (Improving Accuracy)** — Chain multiple Buffers together to execute the same solver multiple times per frame.

## Example

```glsl
// // IMPORTANT: Only uChannel0 (reads currentBuf), writes to nextBuf (must be different!)
// IMPORTANT: encode/decode ensures signed values aren't truncated under RGBA8 (no float textures)

uniform int useFloatTex;
float decode(float v) { return useFloatTex == 1 ? v : v * 2.0 - 1.0; }
float encode(float v) { return useFloatTex == 1 ? v : v * 0.5 + 0.5; }

void main() {
    vec2 uv = vUv;
    vec2 texel = 1.0 / uResolution;

    vec2 raw = texture(uChannel0, uv).xy;
    float current = decode(raw.x);
    float previous = decode(raw.y);

    float left  = decode(texture(uChannel0, uv - vec2(texel.x, 0.0)).x);
    float right = decode(texture(uChannel0, uv + vec2(texel.x, 0.0)).x);
    float down  = decode(texture(uChannel0, uv - vec2(0.0, texel.y)).x);
    float up    = decode(texture(uChannel0, uv + vec2(0.0, texel.y)).x);

    float laplacian = left + right + down + up - 4.0 * current;
    float next = 2.0 * current - previous + 0.25 * laplacian;
    next *= 0.995;
    next *= min(1.0, float(uFrame));

    fragColor = vec4(encode(next), encode(current), 0.0, 1.0);
}
```

```glsl
// Insert external forces before the wave equation computation (add to next)
float force = 0.0;
if (uMouse.z > 0.0)
{
    vec2 gl_FragCoord.xy = vUv * uResolution;
    force = smoothstep(4.5, 0.5, length(uMouse.xy - gl_FragCoord.xy));
}
else
{
    // Procedural raindrops
    vec2 gl_FragCoord.xy = vUv * uResolution;
    float t = uTime * 2.0;
    vec2 pos = fract(floor(t) * vec2(0.456665, 0.708618)) * uResolution;
    float amp = 1.0 - step(0.05, fract(t));
    force = -amp * smoothstep(2.5, 0.5, length(pos - gl_FragCoord.xy));
}

// Add external force after wave equation
next += force;
```

```glsl
// IMPORTANT: Image Pass also needs decode
uniform int useFloatTex;
float decode(float v) { return useFloatTex == 1 ? v : v * 2.0 - 1.0; }

void main()
{
    vec2 uv = vUv;
    vec2 texel = 1.0 / uResolution;

    float left  = decode(texture(uChannel0, uv - vec2(texel.x, 0.0)).x);
    float right = decode(texture(uChannel0, uv + vec2(texel.x, 0.0)).x);
    float down  = decode(texture(uChannel0, uv - vec2(0.0, texel.y)).x);
    float up    = decode(texture(uChannel0, uv + vec2(0.0, texel.y)).x);

    vec3 normal = normalize(vec3((right - left) * 8.0, (up - down) * 8.0, 1.0));

    vec3 light = normalize(vec3(0.2, -0.5, 0.7));
    float diffuse = max(dot(normal, light), 0.0);
    float spec = pow(max(-reflect(light, normal).z, 0.0), 32.0);

    vec3 waterTint = vec3(0.05, 0.15, 0.3);
    vec3 color = waterTint * (0.6 + 0.5 * diffuse) + vec3(1.0) * spec * 0.6;

    fragColor = vec4(color, 1.0);
}
```

## Advanced

### Step 1: Ping-Pong Double Buffer Structure

**What**: Create two Buffers (A and B) that alternate read/write to achieve state persistence.

**Why**: GPU shaders cannot simultaneously read and write the same buffer. The ping-pong strategy reads from one buffer (previous frame's data) and writes to the other each frame, then swaps on the next frame.

**IMPORTANT: Key Difference Between 
**Code** (
```glsl
// IMPORTANT: Only use uChannel0 (read currentBuf), write to nextBuf (must be different!)
// IMPORTANT: encode/decode ensure signed values aren't clipped on RGBA8 (no float textures/SwiftShader)
uniform int useFloatTex;
float decode(float v) { return useFloatTex == 1 ? v : v * 2.0 - 1.0; }
float encode(float v) { return useFloatTex == 1 ? v : v * 0.5 + 0.5; }

void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;
    vec2 texel = 1.0 / uResolution.xy;

    float current = decode(texture(uChannel0, uv).x);
    float previous = decode(texture(uChannel0, uv).y);

    float left  = decode(texture(uChannel0, uv - vec2(texel.x, 0.0)).x);
    float right = decode(texture(uChannel0, uv + vec2(texel.x, 0.0)).x);
    float down  = decode(texture(uChannel0, uv - vec2(0.0, texel.y)).x);
    float up    = decode(texture(uChannel0, uv + vec2(0.0, texel.y)).x);

    float laplacian = left + right + down + up - 4.0 * current;
    float next = 2.0 * current - previous + 0.25 * laplacian;

    next *= 0.995; // damping decay
    next *= min(1.0, float(uFrame)); // zero on frame 0

    fragColor = vec4(encode(next), encode(current), 0.0, 0.0);
}
```

### Step 2: Interaction-Driven (External Force Injection)

**What**: Inject energy into the simulation through mouse clicks or programmatic generation.

**Why**: Physics simulations need external excitation to start and sustain. Mouse interaction is the most intuitive driving method; programmatic methods can simulate raindrops, explosions, etc.

**Code** (insert before wave equation computation):
```glsl
float d = 0.0;

if (uMouse.z > 0.0)
{
    // Mouse click: create ripple at mouse position
    d = smoothstep(4.5, 0.5, length(uMouse.xy - gl_FragCoord.xy));
}
else
{
    // Programmatic raindrop: pseudo-random position + impulse
    float t = uTime * 2.0;
    vec2 pos = fract(floor(t) * vec2(0.456665, 0.708618)) * uResolution.xy;
    float amp = 1.0 - step(0.05, fract(t));
    d = -amp * smoothstep(2.5, 0.5, length(pos - gl_FragCoord.xy));
}
```

### Step 3: Rendering Layer (Height Field Visualization)

**What**: Read simulation results in the Image Pass, compute normals via gradient calculation, and render lighting effects.

**Why**: The simulation result is a height field texture that needs to be transformed into a visible surface effect. Computing gradients via finite differences as normals enables refraction, diffuse reflection, specular highlights, and other water surface effects.

**Code** (Image Pass):
```glsl
void main() {
    vec2 uv = gl_FragCoord.xy / uResolution.xy;
    vec3 e = vec3(vec2(1.0) / uResolution.xy, 0.0);

    // Read four-neighbor height values from passA
    float left  = texture(uChannel0, uv - e.xz).x;
    float right = texture(uChannel0, uv + e.xz).x;
    float down  = texture(uChannel0, uv - e.zy).x;
    float up    = texture(uChannel0, uv + e.zy).x;

    // Construct normal from gradient
    vec3 normal = normalize(vec3(right - left, up - down, 1.0));

    // Lighting computation
    vec3 light = normalize(vec3(0.2, -0.5, 0.7));
    float diffuse = max(dot(normal, light), 0.0);
    float spec = pow(max(-reflect(light, normal).z, 0.0), 32.0);

    // Refraction-offset background texture sampling
    vec4 bg = texture(uChannel1, uv + normal.xy * 0.35);
    vec3 waterTint = vec3(0.7, 0.8, 1.0);

    fragColor = mix(bg, vec4(waterTint, 1.0), 0.25) * diffuse + spec;
}
```

### Step 4: Chained Multi-Buffer Iteration (Improving Accuracy)

**What**: Chain multiple Buffers together to execute the same solver multiple times per frame.

**Why**: Many physics solvers (fluid pressure projection, constraint solving) require multiple iterations to converge. In 
**Full Euler fluid solver code** (passA/B/C share Common pass):
```glsl
// === Common Pass ===
#define dt 0.15                        // adjustable: time step
#define viscosityThreshold 0.64        // adjustable: viscosity coefficient (larger = thinner)
#define vorticityThreshold 0.25        // adjustable: vorticity confinement strength

vec4 fluidSolver(sampler2D field, vec2 uv, vec2 step,
                 vec4 mouse, vec4 prevMouse)
{
    float k = 0.2, s = k / dt;

    // Sample center and four neighbors
    vec4 c  = textureLod(field, uv, 0.0);
    vec4 fr = textureLod(field, uv + vec2(step.x, 0.0), 0.0);
    vec4 fl = textureLod(field, uv - vec2(step.x, 0.0), 0.0);
    vec4 ft = textureLod(field, uv + vec2(0.0, step.y), 0.0);
    vec4 fd = textureLod(field, uv - vec2(0.0, step.y), 0.0);

    // Divergence and density gradient
    vec3 ddx = (fr - fl).xyz * 0.5;
    vec3 ddy = (ft - fd).xyz * 0.5;
    float divergence = ddx.x + ddy.y;
    vec2 densityDiff = vec2(ddx.z, ddy.z);

    // Density solve
    c.z -= dt * dot(vec3(densityDiff, divergence), c.xyz);

    // Viscous force (Laplacian)
    vec2 laplacian = fr.xy + fl.xy + ft.xy + fd.xy - 4.0 * c.xy;
    vec2 viscosity = viscosityThreshold * laplacian;

    // Semi-Lagrangian advection
    vec2 densityInv = s * densityDiff;
    vec2 uvHistory = uv - dt * c.xy * step;
    c.xyw = textureLod(field, uvHistory, 0.0).xyw;

    // Mouse external force
    vec2 extForce = vec2(0.0);
    if (mouse.z > 1.0 && prevMouse.z > 1.0)
    {
        vec2 drag = clamp((mouse.xy - prevMouse.xy) * step * 600.0,
                          -10.0, 10.0);
        vec2 p = uv - mouse.xy * step;
        extForce += 0.001 / dot(p, p) * drag;
    }

    c.xy += dt * (viscosity - densityInv + extForce);

    // Velocity decay
    c.xy = max(vec2(0.0), abs(c.xy) - 5e-6) * sign(c.xy);

    // Vorticity confinement
    c.w = (fd.x - ft.x + fr.y - fl.y);

    c.xy += dt * curlForce;
    fragColor = encode(c);
}
```

### Step 9: Image Pass Visualization

**What**: Read simulation texture in display pass; shade height field or vector field.

```glsl
float h = decode(texture(uChannel0, uv).x);
vec3 nor = normalize(vec3(dHdx, 1.0, dHdz));
fragColor = vec4(shade(nor), 1.0);
```

## Gotchas

- Explicit Euler integration explodes on stiff springs — reduce `dt` or switch to Verlet / implicit step.
- Collision response without restitution tuning sticks objects — separate tangential friction from normal impulse.
- Feedback loops reading and writing the same buffer in one pass race — split update and integrate passes.

## Combine With

- [multipass-buffer](multipass-buffer.md)
