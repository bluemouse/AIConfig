# matrix-transform: Matrix Transforms

## Guideline

The essence of matrix transforms is coordinate system transformation. In a ray marching pipeline: camera rays are built from screen UVs, and object transforms warp sample points before SDF evaluation.

## Rationale


1. **Camera matrix**: Screen pixels → world-space ray direction (view-to-world)
2. **Object transform matrix**: World-space sample point → object local space (world-to-local, domain transform)

### Key Formulas

**2D Rotation** R(θ) = `[[cosθ, -sinθ], [sinθ, cosθ]]`

**3D Rotation Around Y-Axis** Ry(θ) = `[[cosθ, 0, sinθ], [0, 1, 0], [-sinθ, 0, cosθ]]`

**Rodrigues (Arbitrary Axis k, Angle θ)**: `R = cosθ·I + (1-cosθ)·k⊗k + sinθ·K`

**LookAt Camera**:
```
forward = normalize(target - eye)
right   = normalize(cross(forward, worldUp))
up      = cross(right, forward)
viewMatrix = mat3(right, up, forward)
```

**Perspective Ray**: `rd = normalize(camMatrix * vec3(uv, focalLength))`

## How to Apply

1. **Step 1: Screen Coordinate Normalization** — Map `gl_FragCoord` to aspect-correct `[-1,1]` UV or NDC.
2. **Step 2: Rotation Matrices** — Build `mat2`/`mat3` rotations for 2D patterns or 3D object orientation.
3. **Step 3: LookAt Camera** — Construct `mat3(right, up, forward)` from eye, target, and world up.
4. **Step 4: Perspective Ray Generation** — Transform normalized UV through camera matrix to world-space ray direction.
5. **Step 5: Mouse-Interactive Camera** — Orbit or pan camera from `uMouse` offsets while preserving look-at stability.
6. **Step 6: SDF Domain Transforms** — Apply inverse object transform to sample point before evaluating `map(p)`.
7. **Step 7: Quaternion Rotation** — Use unit quaternions for smooth interactive rotation without gimbal lock.
## Example

```glsl
// Range [-aspect, aspect] x [-1, 1]
vec2 uv = (2.0 * gl_FragCoord.xy - uResolution.xy) / uResolution.y;
```

```glsl
// 2D rotation (mat2)
mat2 rot2D(float a) {
    float c = cos(a), s = sin(a);
    return mat2(c, s, -s, c);
}

// 3D single-axis rotation (mat3)
mat3 rotX(float a) {
    float s = sin(a), c = cos(a);
    return mat3(1, 0, 0,  0, c, s,  0, -s, c);
}
mat3 rotY(float a) {
    float s = sin(a), c = cos(a);
    return mat3(c, 0, s,  0, 1, 0,  -s, 0, c);
}
mat3 rotZ(float a) {
    float s = sin(a), c = cos(a);
    return mat3(c, s, 0,  -s, c, 0,  0, 0, 1);
}

// Euler angles → mat3 (yaw/pitch/roll)
mat3 fromEuler(vec3 ang) {
    vec2 a1 = vec2(sin(ang.x), cos(ang.x));
    vec2 a2 = vec2(sin(ang.y), cos(ang.y));
    vec2 a3 = vec2(sin(ang.z), cos(ang.z));
    mat3 m;
    m[0] = vec3( a1.y*a3.y + a1.x*a2.x*a3.x,
                  a1.y*a2.x*a3.x + a3.y*a1.x,
                 -a2.y*a3.x);
    m[1] = vec3(-a2.y*a1.x, a1.y*a2.y, a2.x);
    m[2] = vec3( a3.y*a1.x*a2.x + a1.y*a3.x,
                  a1.x*a3.x - a1.y*a3.y*a2.x,
                  a2.y*a3.y);
    return m;
}

// Rodrigues arbitrary-axis rotation (mat3)
mat3 rotationMatrix(vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle), c = cos(angle), oc = 1.0 - c;
    return mat3(
        oc*axis.x*axis.x + c,          oc*axis.x*axis.y - axis.z*s, oc*axis.z*axis.x + axis.y*s,
        oc*axis.x*axis.y + axis.z*s,   oc*axis.y*axis.y + c,        oc*axis.y*axis.z - axis.x*s,
        oc*axis.z*axis.x - axis.y*s,   oc*axis.y*axis.z + axis.x*s, oc*axis.z*axis.z + c
    );
}
```

```glsl
// Classic setCamera, cr = camera roll
mat3 setCamera(in vec3 ro, in vec3 ta, float cr) {
    vec3 cw = normalize(ta - ro);
    vec3 cp = vec3(sin(cr), cos(cr), 0.0);
    vec3 cu = normalize(cross(cw, cp));
    vec3 cv = normalize(cross(cu, cw));
    return mat3(cu, cv, cw);
}

// mat4 LookAt (with translation, for homogeneous coordinate scenes)
mat4 LookAt(vec3 pos, vec3 target, vec3 up) {
    vec3 dir = normalize(target - pos);
    vec3 x = normalize(cross(dir, up));
    vec3 y = cross(x, dir);
    return mat4(vec4(x, 0), vec4(y, 0), vec4(dir, 0), vec4(pos, 1));
}
```

## Advanced

- **Vector Fundamentals**: Meaning of `vec2/vec3/vec4`, dot product `dot()`, cross product `cross()`, `normalize()`
- **Matrix Fundamentals**: Column-major storage of `mat2/mat3/mat4` in GLSL, semantics of matrix multiplication `m * v`
- **Coordinate Systems**: NDC (Normalized Device Coordinates), screen-space to world-space mapping, aspect ratio correction
- **Trigonometry**: Relationship between `sin()`/`cos()` and rotation
- **Quaternion Basics**: unit quaternion rotation avoids gimbal lock for interactive cameras.

## Gotchas

- Column-major vs row-major multiply order inverts transforms — match `p' = M * p` convention used in the rest of the shader.
- Euler rotation order changes gimbal lock axis — document XYZ vs ZYX or use axis-angle / quaternion.
- Non-uniform scale in inverse transpose normals corrupts lighting — use `transpose(inverse(mat3(model)))` for normals.

## Combine With

- [ray-marching](ray-marching.md)
- [camera-effects](camera-effects.md)
