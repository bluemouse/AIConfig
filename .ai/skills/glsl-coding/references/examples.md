# GLSL Examples and Output Patterns

## Table of contents

1. Minimal OpenGL vertex/fragment pair
2. Minimal Vulkan vertex/fragment pair
3. Tessellation skeleton
4. Geometry shader skeleton
5. Compute shader skeleton
6. Code review example style

## 1. Minimal OpenGL vertex/fragment pair

Vertex shader:

```glsl
#version 450 core

// Stage: vertex
// Target: OpenGL 4.5 core

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inNormal;
layout(location = 2) in vec2 inTexCoord;

layout(std140, binding = 0) uniform CameraBlock
{
    mat4 viewProj;
} camera;

layout(std140, binding = 1) uniform ObjectBlock
{
    mat4 model;
    mat3 normalFromObjectToWorld;
} objectData;

layout(location = 0) out vec3 vWorldNormal;
layout(location = 1) out vec2 vTexCoord;

void main()
{
    vec4 worldPos = objectData.model * vec4(inPosition, 1.0);
    vWorldNormal = normalize(objectData.normalFromObjectToWorld * inNormal);
    vTexCoord = inTexCoord;
    gl_Position = camera.viewProj * worldPos;
}
```

Fragment shader:

```glsl
#version 450 core

// Stage: fragment
// Target: OpenGL 4.5 core

layout(location = 0) in vec3 vWorldNormal;
layout(location = 1) in vec2 vTexCoord;

layout(binding = 2) uniform sampler2D albedoTex;

layout(location = 0) out vec4 outColor;

void main()
{
    vec3 n = normalize(vWorldNormal);
    float ndotl = max(dot(n, normalize(vec3(0.4, 0.7, 0.2))), 0.0);
    vec3 albedo = texture(albedoTex, vTexCoord).rgb;
    outColor = vec4(albedo * (0.05 + 0.95 * ndotl), 1.0);
}
```

Host assumptions: bind camera UBO at binding 0, object UBO at binding 1, and texture sampler at binding 2. Vertex attribute formats must match locations 0, 1, and 2.

## 2. Minimal Vulkan vertex/fragment pair

Vertex shader:

```glsl
#version 450

// Stage: vertex
// Target: Vulkan 1.3 GLSL compiled to SPIR-V

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inNormal;
layout(location = 2) in vec2 inTexCoord;

layout(set = 0, binding = 0, std140) uniform CameraBlock
{
    mat4 viewProj;
} camera;

layout(push_constant) uniform PushConstants
{
    mat4 model;
    mat4 normalFromObjectToWorld; // prefer mat4 over mat3 for std430 alignment in push constants
} pc;

layout(location = 0) out vec3 vWorldNormal;
layout(location = 1) out vec2 vTexCoord;

void main()
{
    vec4 worldPos = pc.model * vec4(inPosition, 1.0);
    vWorldNormal = normalize(mat3(pc.normalFromObjectToWorld) * inNormal);
    vTexCoord = inTexCoord;
    gl_Position = camera.viewProj * worldPos;
}
```

Fragment shader:

```glsl
#version 450

// Stage: fragment
// Target: Vulkan 1.3 GLSL compiled to SPIR-V

layout(location = 0) in vec3 vWorldNormal;
layout(location = 1) in vec2 vTexCoord;

layout(set = 1, binding = 0) uniform sampler2D albedoTex;

layout(location = 0) out vec4 outColor;

void main()
{
    vec3 n = normalize(vWorldNormal);
    float ndotl = max(dot(n, normalize(vec3(0.4, 0.7, 0.2))), 0.0);
    vec3 albedo = texture(albedoTex, vTexCoord).rgb;
    outColor = vec4(albedo * (0.05 + 0.95 * ndotl), 1.0);
}
```

Host assumptions: descriptor set 0 binding 0 is a camera UBO, descriptor set 1 binding 0 is a combined image sampler, and the pipeline layout includes the push constant range used by the vertex stage.

## 3. Tessellation skeleton

Tessellation control shader:

```glsl
#version 450 core

// Stage: tessellation control
// Target: OpenGL 4.5 core; for Vulkan add descriptor set qualifiers as needed.

layout(vertices = 3) out;

layout(location = 0) in vec3 vInWorldPos[];
layout(location = 0) out vec3 tcWorldPos[];

void main()
{
    tcWorldPos[gl_InvocationID] = vInWorldPos[gl_InvocationID];

    if (gl_InvocationID == 0) {
        gl_TessLevelOuter[0] = 4.0;
        gl_TessLevelOuter[1] = 4.0;
        gl_TessLevelOuter[2] = 4.0;
        gl_TessLevelInner[0] = 4.0;
    }
}
```

Tessellation evaluation shader:

```glsl
#version 450 core

// Stage: tessellation evaluation
// Target: OpenGL 4.5 core; for Vulkan add descriptor set qualifiers as needed.

layout(triangles, equal_spacing, ccw) in;

layout(location = 0) in vec3 tcWorldPos[];
layout(location = 0) out vec3 teWorldPos;

layout(std140, binding = 0) uniform CameraBlock
{
    mat4 viewProj;
} camera;

void main()
{
    vec3 p0 = tcWorldPos[0];
    vec3 p1 = tcWorldPos[1];
    vec3 p2 = tcWorldPos[2];
    teWorldPos = p0 * gl_TessCoord.x + p1 * gl_TessCoord.y + p2 * gl_TessCoord.z;
    gl_Position = camera.viewProj * vec4(teWorldPos, 1.0);
}
```

## 4. Geometry shader skeleton

```glsl
#version 450 core

// Stage: geometry
// Target: OpenGL 4.5 core; for Vulkan add descriptor set qualifiers as needed.

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

layout(location = 0) in vec3 vNormal[];
layout(location = 0) out vec3 gNormal;

void main()
{
    for (int i = 0; i < 3; ++i) {
        gNormal = vNormal[i];
        gl_Position = gl_in[i].gl_Position;
        EmitVertex();
    }
    EndPrimitive();
}
```

## 5. Compute shader skeleton

```glsl
#version 450

// Stage: compute
// Target: Vulkan 1.3 GLSL compiled to SPIR-V

layout(local_size_x = 16, local_size_y = 16, local_size_z = 1) in;

layout(set = 0, binding = 0, rgba16f) readonly uniform image2D inputImage;
layout(set = 0, binding = 1, rgba16f) writeonly uniform image2D outputImage;

void main()
{
    ivec2 pixel = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(outputImage);

    if (pixel.x >= size.x || pixel.y >= size.y) {
        return;
    }

    vec4 c = imageLoad(inputImage, pixel);
    imageStore(outputImage, pixel, vec4(c.rgb, 1.0));
}
```

Host assumptions: dispatch enough workgroups to cover the image and add a Vulkan pipeline barrier before later shader reads or presentation if the output image is consumed afterward.

## 6. Code review example style

Use this style for concise reviews:

```text
Target assumptions: Vulkan 1.3 fragment shader, GLSL compiled to SPIR-V.

Correctness blockers:
- `uniform mat4 viewProj;` is a default uniform. Use a uniform block or push constants in Vulkan.
- `gl_FragColor` is legacy. Declare `layout(location = 0) out vec4 outColor;`.

Performance risks:
- The shader samples four textures after `discard`; this may reduce early-depth benefits. Consider alpha testing before expensive samples if visual requirements allow it.

Maintainability:
- Rename `x`, `y`, and `z` to color-space or material terms; the current names hide intent.

Patch:
[small corrected shader]

Validation:
- Compile with Vulkan semantics, run SPIR-V validation, and confirm descriptor set layout matches set/binding declarations.
```
