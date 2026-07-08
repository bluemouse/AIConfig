# particle-system: Particle Systems

## Guideline

Particle systems manage collections of many independent entities, each with position, velocity, lifetime, and other attributes.

## Rationale

**Stateless paradigm**: All attributes are recomputed each frame from particle ID and time, no Buffer needed.
```
position_i = trajectory(id_i, time) + randomOffset(hash(id_i))
lifetime_i = fract((time - spawnTime_i) / lifeDuration_i)
```

**Stateful paradigm**: Particle state is stored in Buffer texture pixels, each frame reading → computing → writing back.
```
// Euler method
velocity += acceleration * dt
position += velocity * dt

// Verlet integration (no explicit velocity, more stable)
newPos = 2 * currentPos - previousPos + acceleration * dt²
```

**Rendering**: Distance-based falloff `intensity = brightness / (dist² + epsilon)`, with multi-particle superposition creating metaball fusion effects.

## How to Apply


1. **Step 1: Hash Random Functions** — Define a function that generates pseudo-random numbers from a float (particle ID). This is the foundational infrastructure for all particle systems.
2. **Step 2: Particle Lifecycle Management** — Compute birth time, lifespan, current age for each particle, and auto-respawn after death.
3. **Step 3: Stateless Particle Position Computation** — Compute 2D/3D position solely from particle ID and time, without relying on any Buffer.
4. **Step 4: Buffer-Stored Particle State (Stateful System)** — Use one row of pixels in a Buffer texture to store all particles, with each pixel = one particle's (pos.x, pos.y, vel.x, vel.y).

## Example

```glsl
// 1D -> 1D hash, returns [0, 1)
float hash11(float p) {
    return fract(sin(p * 127.1) * 43758.5453);
}

// 1D -> 2D hash
vec2 hash12(float p) {
    vec3 p3 = fract(vec3(p) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx + p3.yz) * p3.zy);
}

// 3D -> 3D hash
vec3 hash33(vec3 p) {
    p = fract(p * vec3(443.897, 397.297, 491.187));
    p += dot(p.zxy, p.yxz + 19.19);
    return fract(vec3(p.x * p.y, p.z * p.x, p.y * p.z)) - 0.5;
}
```

```glsl
#define NUM_PARTICLES 100
#define LIFETIME_MIN 1.0
#define LIFETIME_MAX 3.0
#define START_TIME 2.0

// Returns: x = normalized age [0,1], y = life cycle number
vec2 particleAge(int id, float time) {
    float spawnTime = START_TIME * hash11(float(id) * 2.0);
    float lifetime = mix(LIFETIME_MIN, LIFETIME_MAX, hash11(float(id) * 3.0 - 35.0));
    float age = mod(time - spawnTime, lifetime);
    float run = floor((time - spawnTime) / lifetime);
    return vec2(age / lifetime, run);
}
```

```glsl
#define GRAVITY vec2(0.0, -4.5)
#define DRIFT_MAX vec2(0.28, 0.28)

// Harmonic superposition for smooth main trajectory
float harmonics(vec3 freq, vec3 amp, vec3 phase, float t) {
    float val = 0.0;
    for (int h = 0; h < 3; h++)
        val += amp[h] * cos(t * freq[h] * 6.2832 + phase[h] / 360.0 * 6.2832);
    return (1.0 + val) / 2.0;
}

vec2 particlePosition(int id, float time) {
    vec2 ageInfo = particleAge(id, time);
    float age = ageInfo.x;
    float run = ageInfo.y;

    float slowTime = time * 0.1;
    vec2 mainPos = vec2(
        harmonics(vec3(0.4, 0.66, 0.78), vec3(0.8, 0.24, 0.18), vec3(0.0, 45.0, 55.0), slowTime),
        harmonics(vec3(0.415, 0.61, 0.82), vec3(0.72, 0.28, 0.15), vec3(90.0, 120.0, 10.0), slowTime)
    );

    vec2 drift = DRIFT_MAX * (vec2(hash11(float(id) * 3.0 + run * 4.0),
                                    hash11(float(id) * 7.0 - run * 2.5)) - 0.5) * age;
    vec2 grav = GRAVITY * age * age * 0.5;

    return mainPos + drift + grav;
}
```

## Advanced

### Step 1: Hash Random Functions

**What**: Define a function that generates pseudo-random numbers from a float (particle ID). This is the foundational infrastructure for all particle systems.

**Why**: Each particle needs unique but deterministic attributes (color, size, initial direction, etc.); hash functions provide repeatable "randomness".

Three hash function dimensions are provided:
- `hash11`: 1D → 1D, for scalar randomness (lifetime, brightness, etc.)
- `hash12`: 1D → 2D, for 2D randomness (initial position, etc.)
- `hash33`: 3D → 3D, for 3D velocity perturbation

```glsl
// Standard 1D -> 1D hash, returns [0, 1)
float hash11(float p) {
    return fract(sin(p * 127.1) * 43758.5453);
}

// 1D -> 2D hash, for 2D randomness
vec2 hash12(float p) {
    vec3 p3 = fract(vec3(p) * vec3(0.1031, 0.1030, 0.0973));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xx + p3.yz) * p3.zy);
}

// 3D -> 3D hash, for 3D velocity perturbation
vec3 hash33(vec3 p) {
    p = fract(p * vec3(443.897, 397.297, 491.187));
    p += dot(p.zxy, p.yxz + 19.19);
    return fract(vec3(p.x * p.y, p.z * p.x, p.y * p.z)) - 0.5;
}
```

### Step 2: Particle Lifecycle Management

**What**: Compute birth time, lifespan, current age for each particle, and auto-respawn after death.

**Why**: Lifecycle is the core mechanism of particle systems — the cycle of birth, motion, fade-out, death, and respawn. `fract` or `mod` implements infinite cycling without additional state.

Key design:
- `spawnTime`: Each particle's birth time differs, generated by `hash11` from the ID, spread across the `[0, START_TIME]` interval
- `lifetime`: Each particle's lifespan differs, random within the `[LIFETIME_MIN, LIFETIME_MAX]` interval
- `mod(time - spawnTime, lifetime)`: Automatic cycling; the particle respawns immediately after death
- `floor(...)` computes the current life cycle number, used to generate different random attributes each cycle

```glsl
#define NUM_PARTICLES 100   // adjustable: particle count
#define LIFETIME_MIN 1.0    // adjustable: minimum lifespan (seconds)
#define LIFETIME_MAX 3.0    // adjustable: maximum lifespan (seconds)
#define START_TIME 2.0      // adjustable: time for all particles to be born

// Returns: x = current normalized age [0,1], y = current life cycle number
vec2 particleAge(int id, float time) {
    float spawnTime = START_TIME * hash11(float(id) * 2.0);
    float lifetime = mix(LIFETIME_MIN, LIFETIME_MAX, hash11(float(id) * 3.0 - 35.0));
    float age = mod(time - spawnTime, lifetime);
    float run = floor((time - spawnTime) / lifetime);
    return vec2(age / lifetime, run);
}
```

### Step 3: Stateless Particle Position Computation

**What**: Compute 2D/3D position solely from particle ID and time, without relying on any Buffer.

**Why**: For decorative effects (starfields, fireworks, orbiting light points), the stateless approach is simplest and most efficient. Define the main trajectory via parametric curves (e.g., Lissajous curves), then add random offset and gravity.

Position is composed of three components:
1. **Main trajectory** (harmonic oscillator): Multiple cosine waves superimposed to form smooth Lissajous curves, controlling the overall motion path of the particle group
2. **Random drift**: Each particle linearly diffuses from the main trajectory position over time; `DRIFT_MAX` controls the diffusion range
3. **Gravity**: Parabolic descent via `0.5 * g * t²`; `age²` is the normalized form of time

```glsl
#define GRAVITY vec2(0.0, -4.5)     // adjustable: gravity direction and strength
#define DRIFT_MAX vec2(0.28, 0.28)  // adjustable: maximum random drift amplitude

// Harmonic superposition for smooth main trajectory
float harmonics(vec3 freq, vec3 amp, vec3 phase, float t) {
    float val = 0.0;
    for (int h = 0; h < 3; h++)
        val += amp[h] * cos(t * freq[h] * 6.2832 + phase[h] / 360.0 * 6.2832);
    return (1.0 + val) / 2.0;
}

vec2 particlePosition(int id, float time) {
    vec2 ageInfo = particleAge(id, time);
    float age = ageInfo.x;
    float run = ageInfo.y;

    // Main trajectory (harmonic oscillator)
    float slowTime = time * 0.1; // time along main trajectory
    vec2 mainPos = vec2(
        harmonics(vec3(0.4, 0.66, 0.78), vec3(0.8, 0.24, 0.18), vec3(0.0, 45.0, 55.0), slowTime),
        harmonics(vec3(0.415, 0.61, 0.82), vec3(0.72, 0.28, 0.15), vec3(90.0, 120.0, 10.0), slowTime)
    );

    // Random drift (grows linearly with time)
    vec2 drift = DRIFT_MAX * (vec2(hash11(float(id) * 3.0 + run * 4.0),
                                    hash11(float(id) * 7.0 - run * 2.5)) - 0.5) * age;
    // Gravity effect
    vec2 grav = GRAVITY * age * age * 0.5;

    return mainPos + drift + grav;
}
```

### Step 4: Buffer-Stored Particle State (Stateful System)

**What**: Use one row of pixels in a Buffer texture to store all particles, with each pixel = one particle's (pos.x, pos.y, vel.x, vel.y).

**Why**: When inter-frame persistent state is needed (physics collisions, force field interactions, N-body simulations), particle data must be written to a Buffer and read back the next frame.

Design points:
- `gl_FragCoord.xy.y > 0.5`: Only the first row of pixels stores particles; remaining pixels are discarded
- `gl_FragCoord.xy.x` corresponds to particle ID; each pixel's RGBA stores (pos.x, pos.y, vel.x, vel.y)
- `uFrame < 5`: First few frames are initialization, randomly distributing particle positions
- Force accumulation: boundary repulsion + inter-particle attraction/repulsion + friction
- Clamp velocity and acceleration after integration to prevent numerical explosion

```glsl
// === passA: Particle physics update ===
#define NUM_PARTICLES 40    // adjustable: particle count
#define MAX_VEL 0.5         // adjustable: maximum velocity
#define MAX_ACC 3.0         // adjustable: maximum acceleration
#define RESIST 0.2          // adjustable: drag coefficient
#define DT 0.03             // adjustable: time step

vec4 loadParticle(int i) {
    return texelFetch(uChannel0, ivec2(i, 0), 0);
}
```

### Step 5: Integrate and Write Back

**What**: Update position/velocity with drag and acceleration; write next state to ping-pong buffer.

```glsl
vec2 vel = p.xy + acc * DT;
p.xy += vel * DT;
fragColor = vec4(p.xyz, life);
```

## Gotchas

- Stateless particles cannot remember velocity across frames — use buffer row or transform feedback for persistence.
- Random seed from `gl_FragCoord` alone repeats per frame — mix `uFrame` or `uTime` into hash inputs.
- Thousands of overdrawn quads saturate fill rate — cap alive count per `performance-budget.md` particle limits.

## Combine With

- [procedural-noise](procedural-noise.md)
- [color-palette](color-palette.md)
