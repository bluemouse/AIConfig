# polar-uv-manipulation: Polar UV Manipulation

## Guideline

Polar coordinates convert (x, y) to (r, θ):

## Rationale

- **r = length(p)** — distance to origin
- **θ = atan(y, x)** — angle from positive x-axis, range [-π, π]

Inverse transform: x = r·cos(θ), y = r·sin(θ)

Manipulation effects:
- Modifying θ → rotation, warping, kaleidoscope
- Modifying r → scaling, radial ripples
- θ += f(r) → spiral effect

| Spiral Type | Equation | Code |
|------------|----------|------|
| Archimedean spiral | r = a + bθ | `theta += radius` |
| Logarithmic spiral | r = ae^(bθ) | `theta += log(radius)` |
| Rose curve | r = cos(nθ) | `r - A*sin(n*theta)` |

## How to Apply

1. **Step 1: UV Normalization and Centering** — Center and scale UVs so the origin lies at the pattern focal point.
2. **Step 2: Cartesian → Polar Coordinates** — Compute `r = length(p)` and `theta = atan(p.y, p.x)`.
3. **Step 3: Polar Space Operations** — Rotate, scale, or warp `r`/`theta` for spirals, kaleidoscope, or ripples.
4. **Step 4: Polar → Cartesian Reconstruction** — Convert back with `p = vec2(r*cos(theta), r*sin(theta))`.
5. **Step 5: Polar Coordinate Shape SDF** — Define distance functions in polar space (rose curves, rings, sectors).
6. **Step 6: Coloring and Anti-Aliasing** — Map polar parameters to palette and apply `fwidth`-based edge smoothing.
## Example

```glsl
// Range [-1, 1], most commonly used
vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / min(uResolution.x, uResolution.y);

// Range [-aspect, aspect] x [-1, 1]
vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;

// Pixelated style (Balatro style)
float pixel_size = length(uResolution.xy) / PIXEL_FILTER;
vec2 uv = (floor(gl_FragCoord.xy * (1.0/pixel_size)) * pixel_size - 0.5*uResolution.xy) / length(uResolution.xy);
```

```glsl
float r = length(uv);
float theta = atan(uv.y, uv.x); // [-PI, PI]

// Reusable function
vec2 toPolar(vec2 p) { return vec2(length(p), atan(p.y, p.x)); }

// Normalized angle to [0, 1]
vec2 polar = vec2(atan(uv.y, uv.x) / 6.283 + 0.5, length(uv));
```

```glsl
float spin_amount = 0.25;
float new_theta = theta - spin_amount * 20.0 * r;
```

## Advanced

### GLSL Fundamentals
- **uniform / varying**: Global variable passing mechanisms
- **Built-in functions**: `sin`, `cos`, `atan`, `length`, `fract`, `mod`, `smoothstep`, `mix`, `clamp`, `pow`, `exp`, `log`, `abs`, `max`, `min`, `floor`, `ceil`, `dot`
- **Vector types**: `vec2`, `vec3`, `vec4`, with swizzle support (e.g., `.xy`, `.rgb`)
- **Matrix types**: `mat2` for 2D rotation

### Vector Math
- 2D vector operations: addition, subtraction, multiplication, division, length (`length`), normalization (`normalize`)
- Dot product (`dot`): projection and angle relationships
- 2D rotation matrix:
```glsl
mat2 rotate(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, s, -s, c);
}
```

### Coordinate Systems
- Cartesian coordinates (x, y): standard rectangular coordinate system
- Screen coordinates: bottom-left (0,0), top-right (uResolution.x, uResolution.y)
- Normalized coordinates: typically mapped to [-1, 1] or [0, 1] range

### Fragment entry and uniforms
- `gl_FragCoord.xy`: current pixel's screen coordinates
- `uResolution`: viewport resolution (pixels)
- `uTime`: time since launch (seconds)
- `uMouse`: mouse position

## Gotchas

- Angle from `atan` jumps at ±π seam — use `atan(y, x)` and unwrap or avoid seam in visible region.
- Spirals without log-polar remap compress inner turns — use `log(r)` for even angular spacing.
- Rotating polar UVs without compensating aspect skews rings — multiply angle or radius by aspect ratio.

## Combine With

- [procedural-2d-pattern](procedural-2d-pattern.md)
- [fractal-rendering](fractal-rendering.md)
