# OpenGL and Vulkan GLSL Divergence Reference

OpenGL GLSL and Vulkan-target GLSL look similar but differ in resource declarations, interface rules, built-ins, coordinate defaults, and synchronization responsibilities. Infer the target API before writing or reviewing declarations; keep shared math/material functions separate from API-specific entrypoints and resource declarations.

## 1. Resource declarations

Uniform block — OpenGL adds `binding`, Vulkan adds `set`:

```glsl
layout(std140, binding = 0) uniform CameraBlock { mat4 viewProj; float exposure; } camera;        // OpenGL
layout(set = 0, binding = 0, std140) uniform CameraBlock { mat4 viewProj; float exposure; } camera; // Vulkan
```

Vulkan push constants (`std430` packing, tight byte budget; small per-draw/dispatch values only):

```glsl
layout(push_constant) uniform PushConstants { mat4 model; uint materialIndex; } pc;
```

Vulkan specialization constants (pipeline-creation-time variants only — not values that change per draw):

```glsl
layout(constant_id = 0) const int TILE_SIZE_X = 16;
```

Samplers and images:

```glsl
layout(binding = 2) uniform sampler2D albedoTex;                                      // OpenGL combined
layout(set = 1, binding = 2) uniform sampler2D albedoTex;                             // Vulkan combined
layout(set = 1, binding = 3, rgba16f) uniform image2D outputImage;                    // Vulkan storage image
```

Storage buffer (Vulkan; use `std430`; CPU-side struct layout must match GLSL alignment and padding):

```glsl
layout(set = 2, binding = 0, std430) readonly buffer InstanceData { mat4 model[]; } instances;
```

## 2. Layout and interface matching

- Explicit locations for every cross-stage varying; match type, component count, array-ness, and interpolation qualifiers across producer and consumer.
- Matrices consume one location slot per column unless using block layouts.
- Interface blocks for groups of related varyings between stages.
- Fragment outputs: `layout(location = N) out`, matching render target formats and blend state.
- Vulkan `set`/`binding` declarations must match the `VkDescriptorSetLayout` and `VkPipelineLayout` — host `Vk*` setup is [`../../vulkan-dev/SKILL.md`](../../vulkan-dev/SKILL.md).

## 3. Synchronization and memory visibility

Inside shaders:

- `barrier()` synchronizes invocations in a workgroup or tessellation-control patch phase where defined.
- Memory barriers (`memoryBarrier()`, `groupMemoryBarrier()`, image/storage variants) order shader memory operations; they do not replace API command-buffer barriers.
- Do not add `coherent`/`volatile`/atomics unless the algorithm needs them.

Host counterparts (pointer only): Vulkan needs explicit pipeline barriers between compute writes and later reads; descriptor updates, push constants, and specialization constants have different lifetimes. OpenGL needs memory barriers after shader image/SSBO/atomic-counter/compute writes before later reads.

## 4. Coordinate and built-in differences

- Vulkan GLSL uses `gl_VertexIndex`/`gl_InstanceIndex`; OpenGL uses `gl_VertexID`/`gl_InstanceID`.
- Vulkan's default fragment origin is upper-left; OpenGL's historical default is lower-left. Centralize projection/viewport correction rather than scattering sign flips through shaders.
- `gl_FragCoord.z` and depth output must match the engine's projection convention and depth range.

## 5. SPIR-V constraints (Vulkan GLSL)

Per the [Non-Normative SPIR-V Mappings](https://docs.vulkan.org/glsl/latest/chapters/spirvmappings.html):

**Removed:** default non-opaque uniforms (use blocks/push constants/descriptors), subroutines, `noise()`, deprecated texturing builtins, `shared`/`packed` block layouts, compatibility-profile features.

**Added:** `layout(push_constant)` blocks; `layout(set = M, binding = N)` (array resources take one binding for the whole array); `layout(constant_id = K) const` specialization constants (scalar int/uint/float/bool only); input attachments (`layout(input_attachment_index = N)`); separate `texture2D` + `sampler` in addition to combined `sampler2D`.

**Changed:** fragment origin `origin_upper_left`; `mediump`/`lowp` honored (desktop default stays `highp`); no implicit `gl_FragColor` broadcast — declare explicit `layout(location = 0) out` targets.

**Toolchain:** SPIR-V generation is requested from the offline compiler (`glslangValidator -V`), not an in-shader switch. Exceeding built-in constants is a compile-time error. After SPIR-V emission, `spirv-val` and Vulkan validation layers are the next correctness gates.

Extension stages — task/mesh (`VK_EXT_mesh_shader`), ray tracing (`VK_KHR_ray_tracing_pipeline`), subpass shading/cluster culling — are not baseline OpenGL 4.6 or Vulkan 1.3; state the required extension/feature first.
