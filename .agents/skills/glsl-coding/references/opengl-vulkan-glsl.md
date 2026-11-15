# OpenGL and Vulkan GLSL Reference

## Table of contents

1. Target selection
2. Core stage matrix
3. OpenGL 4.x GLSL rules of thumb
4. Vulkan 1.3 GLSL-to-SPIR-V rules of thumb
5. Resource declarations
6. Layout and interface matching
7. Synchronization and memory visibility
8. Coordinate and built-in differences
9. Optional Vulkan extension stages

## 1. Target selection

Ask or infer the target API early because OpenGL GLSL and Vulkan GLSL look similar but differ in resource layout, compilation path, built-ins, coordinate defaults, and synchronization responsibilities.

Default assumptions:

- OpenGL 4.x: source GLSL compiled and linked by the OpenGL driver unless the user says SPIR-V.
- Vulkan 1.3: GLSL is compiled offline or at build time to SPIR-V, then used in pipeline creation.
- Cross-API: keep shared math/material functions separate from API-specific entrypoints and resource declarations.

## 2. Core stage matrix

| Stage | OpenGL 4.x | Vulkan 1.3 | Notes |
|---|---|---|---|
| Vertex | Core graphics stage | Core graphics stage | Produces clip-space position. |
| Tessellation control | OpenGL 4.0+ | API stage, device feature dependent | Operates on patches/control points. |
| Tessellation evaluation | OpenGL 4.0+ | API stage, device feature dependent | Evaluates generated vertices. |
| Geometry | OpenGL 3.2+/4.x | API stage, device feature dependent | Often expensive; avoid heavy amplification. |
| Fragment | Core graphics stage | Core graphics stage | Computes framebuffer outputs or side effects. |
| Compute | OpenGL 4.3+ | Core compute pipeline stage | Runs in workgroups outside graphics pipeline. |

Do not present mesh, task, ray tracing, subpass shading, or cluster culling stages as baseline OpenGL 4.x stages. In Vulkan, treat them as extension or feature-specific stages unless the user explicitly names enabled support.

## 3. OpenGL 4.x GLSL rules of thumb

- Use modern core-profile syntax: `#version 410 core`, `#version 430 core`, `#version 450 core`, or `#version 460 core` as needed.
- Prefer explicit `layout(location = N)` for vertex attributes, stage varyings, and fragment outputs.
- Use uniform blocks for structured state. Default uniforms are legal in OpenGL but can become hard to manage at scale.
- Use `layout(binding = N)` for samplers, images, uniform blocks, and shader storage blocks when available, while still matching host-side binding calls.
- Always check shader compile logs and program link logs.
- A uniform optimized out by the compiler may return location `-1`; distinguish this from misspelling or failing to bind/use the correct program.
- `glUniform*` updates the current program unless using direct-state-style `glProgramUniform*` functionality.
- Never sample from and render to the same texture region in the same draw unless using a valid texture-barrier pattern. Treat framebuffer feedback loops as undefined behavior.

## 4. Vulkan 1.3 GLSL-to-SPIR-V rules of thumb

- Vulkan consumes SPIR-V modules. GLSL must be compiled to SPIR-V with Vulkan semantics.
- Prefer `#version 450` for Vulkan GLSL unless a newer GLSL feature is required and supported by the toolchain.
- Put non-opaque uniforms in blocks; do not use OpenGL-style loose default uniforms for portable Vulkan GLSL.
- Use explicit descriptor sets and bindings: `layout(set = M, binding = N)`.
- Use `layout(push_constant)` uniform blocks for small frequently changed values.
- Use specialization constants for pipeline-creation-time variants, not for values that change every draw or dispatch.
- Match shader resource declarations to `VkDescriptorSetLayout`, `VkPipelineLayout`, and descriptor updates.
- Validate generated SPIR-V and run with Vulkan validation layers during development.
- Host-side synchronization is explicit. Shader writes to storage buffers/images are not automatically visible to later draws/dispatches without appropriate pipeline barriers and access masks.

## 5. Resource declarations

### OpenGL-style uniform block

```glsl
layout(std140, binding = 0) uniform CameraBlock
{
    mat4 viewProj;
    vec3 cameraWorldPos;
    float exposure;
} camera;
```

### Vulkan uniform buffer

```glsl
layout(set = 0, binding = 0, std140) uniform CameraBlock
{
    mat4 viewProj;
    vec3 cameraWorldPos;
    float exposure;
} camera;
```

### Vulkan push constants

```glsl
layout(push_constant) uniform PushConstants
{
    mat4 model;
    uint materialIndex;
} pc;
```

Use push constants for small per-draw or per-dispatch values. Do not put large arrays or frequently reinterpreted layouts there.

### Vulkan specialization constants

```glsl
layout(constant_id = 0) const int TILE_SIZE_X = 16;
layout(constant_id = 1) const int TILE_SIZE_Y = 16;
```

Use specialization constants for branch removal, array sizes, local sizes, and feature variants decided at pipeline creation time.

### Samplers, textures, and images

OpenGL combined sampler:

```glsl
layout(binding = 2) uniform sampler2D albedoTex;
```

Vulkan combined image sampler:

```glsl
layout(set = 1, binding = 2) uniform sampler2D albedoTex;
```

Vulkan storage image:

```glsl
layout(set = 1, binding = 3, rgba16f) uniform image2D outputImage;
```

### Storage buffers

```glsl
layout(set = 2, binding = 0, std430) readonly buffer InstanceData
{
    mat4 model[];
} instances;
```

Use `std430` for storage buffers when possible. Ensure CPU-side struct layout matches GLSL alignment and padding.

## 6. Layout and interface matching

- Use explicit locations for every cross-stage varying in complete examples.
- Match type, component count, array-ness, and interpolation qualifiers across producer and consumer stages.
- For matrices, remember that each column consumes a location slot unless using block layouts or explicit packing.
- Use interface blocks for groups of related varyings, especially between vertex/tessellation/geometry/fragment stages.
- For fragment outputs, use `layout(location = N) out` and match render target formats and blend state.
- For Vulkan descriptors, the shader's set/binding declarations must match the descriptor set layout used by the pipeline layout.

## 7. Synchronization and memory visibility

Inside shaders:

- `barrier()` synchronizes invocations in a workgroup or tessellation-control patch phase where defined.
- Memory barriers such as `memoryBarrier()`, `groupMemoryBarrier()`, and image/storage-specific barriers order shader memory operations for the relevant scope; they do not replace Vulkan command-buffer barriers.
- `coherent`, `volatile`, and atomics have specific costs and semantics. Do not add them unless the algorithm needs them.

In Vulkan host code:

- Use pipeline barriers between compute writes and graphics reads, graphics writes and compute reads, image layout transitions, and storage image/buffer hazards.
- Descriptor updates, push constants, and specialization constants have different lifetimes. Do not treat them interchangeably.

In OpenGL host code:

- Use the appropriate OpenGL memory barriers after shader image, SSBO, atomic counter, or compute writes before later reads.
- Bind the correct program and resources before draw or dispatch.

## 8. Coordinate and built-in differences

- OpenGL and Vulkan differ in default framebuffer coordinate conventions and clip-depth expectations. A portable engine should centralize projection/viewport correction rather than scattering sign flips through shaders.
- Vulkan GLSL uses `gl_VertexIndex` and `gl_InstanceIndex`; OpenGL uses `gl_VertexID` and `gl_InstanceID`.
- Vulkan's default fragment coordinate origin is upper-left in its GLSL/SPIR-V environment, while OpenGL's historical default is lower-left.
- `gl_FragCoord.z` and depth output must match the projection convention and depth range configured by the engine.

## 9. Optional Vulkan extension stages

When users ask about these stages, start by asking or stating which extension/feature is required:

- Task and mesh shaders: `VK_EXT_mesh_shader` or vendor-specific mesh shader support.
- Ray generation, closest-hit, any-hit, miss, intersection, callable: ray tracing pipeline support such as `VK_KHR_ray_tracing_pipeline` and related acceleration-structure support.
- Subpass shading or cluster culling: vendor-specific extensions.

For OpenGL 4.x, do not claim native support for these stages. Suggest equivalent techniques such as compute preprocessing, instancing, multi-draw, transform feedback, or conventional vertex/tessellation/geometry/fragment paths when appropriate.

## 10. SPIR-V constraints (Vulkan GLSL)

Per [Non-Normative SPIR-V Mappings](https://docs.vulkan.org/glsl/latest/chapters/spirvmappings.html), the following differ when targeting Vulkan SPIR-V:

### Removed for Vulkan (still present in OpenGL SPIR-V path where noted)

- **Default uniforms** for non-opaque types — put data in uniform blocks, push constants, or descriptors.
- **Subroutines** — not available in SPIR-V.
- **`noise()` and deprecated texturing builtins** — `texture2D()`, `textureCube()`, etc. are already deprecated; `noise()` is invalid for SPIR-V.
- **`shared` and `packed` block layouts** — use `std140` or `std430`.
- **Compatibility-profile features** — not supported.

### Added for Vulkan

- **`layout(push_constant) uniform` blocks** — small per-draw/dispatch data; `std430` packing; tight byte budget.
- **`layout(set = M, binding = N)`** — descriptor set assignment; array resources take one binding for the whole array.
- **`layout(constant_id = K) const`** — specialization constants (scalar int/uint/float/bool only).
- **`gl_VertexIndex` / `gl_InstanceIndex`** — replace OpenGL `gl_VertexID` / `gl_InstanceID` in Vulkan shaders.
- **Input attachments** — `layout(input_attachment_index = N)` for subpass inputs.
- **Separate texture + sampler** — `texture2D` + `sampler` types in addition to combined `sampler2D`.

### Changed for Vulkan

- **Default fragment coordinate origin** — `origin_upper_left` instead of OpenGL's historical lower-left default.
- **Precision qualifiers** — `mediump`/`lowp` are honored (desktop defaults remain `highp`).
- **`gl_FragColor` broadcast** — no implicit broadcast; declare explicit `layout(location = 0) out` targets.

### Toolchain notes

- SPIR-V generation is requested from the **offline compiler** (`glslangValidator -V`, build-time shader compile, etc.), not from an in-shader `#version` or `#extension` switch.
- Front ends should be given legal SPIR-V capabilities and limits; exceeding built-in constants is a compile-time error.
- After SPIR-V emission, **`spirv-val`** and Vulkan validation layers are the next correctness gates — host `Vk*` setup is [`../../vulkan-dev/SKILL.md`](../../vulkan-dev/SKILL.md).
