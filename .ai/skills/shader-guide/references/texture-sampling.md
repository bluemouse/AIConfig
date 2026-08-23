# texture-sampling: Texture Sampling

## Guideline

| Function | Coordinate Type | Filtering | Typical Use |

## Rationale

|----------|----------------|-----------|-------------|
| `texture(sampler, uv)` | Float UV `[0,1]` | Hardware bilinear | General texture reading |
| `textureLod(sampler, uv, lod)` | Float UV + LOD | Specified mip level | Control blur level / avoid auto mip |
| `texelFetch(sampler, ivec2, lod)` | Integer pixel coordinates | No filtering | Exact pixel data reading |

Key mathematics:
1. **Hardware bilinear interpolation**: `texture()` automatically linearly blends between 4 adjacent texels
2. **Quintic Hermite smoothing**: `u = f^3(6f^2 - 15f + 10)`, C2 continuous (eliminates hardware linear interpolation seams)
3. **LOD control**: `textureLod` third parameter selects mipmap level, `lod=0` is original resolution, each +1 halves resolution
4. **Coordinate wrapping**: `fract(uv)` implements torus boundary, equivalent to `GL_REPEAT`

## How to Apply

1. **Step 1: Basic Sampling and UV Normalization** — Normalize `gl_FragCoord` to `[0,1]` UV and call `texture()`.
2. **Step 2: textureLod for Mipmap Control** — Force explicit LOD in ray marching to avoid shimmering.
3. **Step 3: texelFetch for Exact Pixel Reading** — Read integer texel addresses without interpolation for buffer data.
4. **Step 4: Manual Bilinear + Quintic Hermite Smoothing** — Hand-blend four texels with C2-smooth weights for seam-free sampling.
5. **Step 5: FBM Texture Noise** — Layer procedural noise octaves as a stand-in or modulation for texture detail.
6. **Step 6: Separable Gaussian Blur** — Run horizontal then vertical 1D Gaussian passes on a framebuffer texture.
7. **Step 7: Dispersion Sampling** — Offset R/G/B UVs radially to simulate chromatic dispersion in refraction.
8. **Step 8: IBL Environment Sampling** — Sample equirectangular or cubemap environment along reflection vector.
## Example

```glsl
vec2 uv = gl_FragCoord.xy / uResolution.xy;
vec4 col = texture(uChannel0, uv);
```

```glsl
// In ray marching: force LOD 0 to avoid artifacts
vec3 groundCol = textureLod(uChannel2, groundUv * 0.05, 0.0).rgb;

// Depth of field blur: LOD varies with distance
float focus = mix(maxBlur - coverage, minBlur, smoothstep(.1, .2, coverage));
vec3 col = textureLod(uChannel0, uv + normal, focus).rgb;

// Bloom: sample high mip levels
#define BLOOM_LOD_A 4.0  // adjustable: bloom first mip level
#define BLOOM_LOD_B 5.0
#define BLOOM_LOD_C 6.0
vec3 bloom = vec3(0.0);
bloom += textureLod(uChannel0, uv + off * exp2(BLOOM_LOD_A), BLOOM_LOD_A).rgb;
bloom += textureLod(uChannel0, uv + off * exp2(BLOOM_LOD_B), BLOOM_LOD_B).rgb;
bloom += textureLod(uChannel0, uv + off * exp2(BLOOM_LOD_C), BLOOM_LOD_C).rgb;
bloom /= 3.0;
```

```glsl
// Data storage addresses
const ivec2 txBallPosVel = ivec2(0, 0);
const ivec2 txPaddlePos  = ivec2(1, 0);
const ivec2 txPoints     = ivec2(2, 0);
const ivec2 txState      = ivec2(3, 0);

vec4 loadValue(in ivec2 addr) {
    return texelFetch(uChannel0, addr, 0);
}

void storeValue(in ivec2 addr, in vec4 val, inout vec4 fragColor, in ivec2 fragPos) {
    fragColor = (fragPos == addr) ? val : fragColor;
}

// Keyboard input
float key = texelFetch(uChannel1, ivec2(KEY_SPACE, 0), 0).x;
```

## Advanced

- **GLSL Basic Syntax**: `vec2`/`vec3`/`vec4`, `uniform sampler2D`, and other types and declarations
- **UV Coordinate System**: `gl_FragCoord.xy / uResolution.xy` normalizes to `[0,1]`, with origin at the bottom-left corner
- **Mipmap Concept**: A multi-resolution pyramid of the texture, with each level at half the resolution. The GPU automatically selects the appropriate level based on screen-space derivatives to avoid aliasing
- **Derivative-Based LOD**: `dFdx`/`dFdy` drive automatic mip selection in `texture()`.

## Gotchas

- Nearest filtering on minified textures moirés — enable mipmaps and `texture()` with LOD bias for distant surfaces.
- Repeating UVs without wrap mode clamp seam at edges — set repeat addressing or fract UVs explicitly.
- sRGB textures sampled as linear double-gamma — mark sRGB formats or apply `pow(color, 2.2)` on load.

## Combine With

- [texture-mapping-advanced](texture-mapping-advanced.md)
