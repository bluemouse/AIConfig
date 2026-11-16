---
name: glsl-coding
description: "Teach, write, review, debug, and optimize modern GLSL for OpenGL 4.6 core and Vulkan 1.3 SPIR-V: shader stages, layouts, descriptors, push constants, specialization constants, interface matching, precision, and compile/link validation. Use for GLSL syntax, stage I/O, resource bindings, GLSL-to-SPIR-V layout questions, maintainability refactors, and diagnosing shader mistakes — even when the user does not say 'GLSL' or 'SPIR-V'."
---

# GLSL Coding (OpenGL 4.6 / Vulkan SPIR-V)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. This skill owns GLSL language and stage/resource contracts. Review order: target assumptions → correctness blockers (compile, interface, layout/binding, sync) → performance risks → maintainability → smallest patch → validation evidence.

## When to Use

- Teaching or explaining GLSL: what each stage does, its inputs/outputs, and what it can see
- Writing, reviewing, or debugging GLSL for vertex/tessellation/geometry/fragment/compute stages
- OpenGL compile/link failures, binding mismatches, varying interface errors
- Vulkan GLSL layout: `layout(set, binding)`, push constants, specialization constants, `std140`/`std430`, GLSL-to-SPIR-V validation, descriptor/pipeline-layout compatibility

## When NOT to Use

- Creative effects (SDF, ray marching, generative art, visual debug colors) — [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md)
- Slang modules, slangc, reflection — [`../slang-dev/SKILL.md`](../slang-dev/SKILL.md)
- Renderer architecture (render graph, binding model) — [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md)
- `Vk*` objects, swapchain, command recording, host-side barriers — [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md)
- Host/runtime glue only, with no GLSL source to inspect

## Version Standard

| Target | Default `#version` | Notes |
|--------|-------------------|-------|
| OpenGL 4.6 core | `#version 460 core` | Lower only when a feature requires; avoid compatibility profile |
| Vulkan SPIR-V | `#version 450` | No profile keyword; SPIR-V emission is chosen by the offline compiler |
| OpenGL ES | `#version 300 es`/`310 es` | Not a strict subset of desktop GLSL — precision and interfaces differ |

Authority: GLSL spec → SPIR-V mappings appendix → toolchain docs → validation layers. Extension stages (task, mesh, ray tracing, subpass shading) are not baseline OpenGL 4.6 or Vulkan 1.3 — explain only with explicit extension caveats.

## Reference routing

| Load condition | Read |
|------|------|
| Resource declarations (UBO/SSBO/push-constant/sampler/image), interface matching, shader-side synchronization, coordinate/built-in differences, Vulkan SPIR-V constraints | [references/opengl-vulkan-glsl.md](references/opengl-vulkan-glsl.md) |

Never validate by inspection alone: compile with `glslangValidator` (`-V` for Vulkan semantics) or OpenGL compile/link logs, then `spirv-val` / validation layers for SPIR-V. Measure performance claims with a GPU capture — no folklore. Shader structure: `#version` → constants → stage in/out with explicit locations → resources → helpers (callees before callers) → `main()`; fragment outputs are `layout(location = 0) out vec4 outColor;`, not `gl_FragColor`.

## Gotchas

- **Vulkan SPIR-V removes** default non-opaque uniforms, subroutines, `noise()`, deprecated texturing builtins, `shared`/`packed` layouts, and compatibility-profile features — put data in uniform blocks, push constants, or descriptors.
- **Built-in indices** — Vulkan `gl_VertexIndex`/`gl_InstanceIndex`; OpenGL `gl_VertexID`/`gl_InstanceID`.
- **Fragment origin** — Vulkan defaults to `origin_upper_left`, OpenGL to lower-left. Centralize the Y-flip in projection/viewport setup, not per-shader.
- **Push constants** — `std430` packing, tight byte budget; watch `mat3`/array alignment. Specialization constants are for pipeline-creation-time variants only.
- **Descriptor arrays** — an array of samplers/UBOs consumes **one** `binding` for the whole array in Vulkan SPIR-V.
- **Legacy names** — `gl_FragColor`, `varying`, `attribute`, `texture2D()` are invalid in modern core shaders.
- **Uniform setter count** — the `count` in `glUniform*` vector/matrix setters is the number of vectors/matrices, not scalar components.
- **Location `-1`** — `glGetUniformLocation == -1` can mean the uniform was optimized out; also check spelling and linkage.
- **Feedback loops** — sampling from and rendering to the same texture region in one draw is undefined without a valid texture-barrier pattern.
- **Integer varyings** need `flat` on both producer and consumer.
- **Derivatives in divergent control flow** are invalid — restructure or use explicit-gradient variants (`textureGrad`).
- **Function order** — callees before callers unless prototypes are supported. **Dead code is still checked** — ill-formed statements inside `if (false)` must compile.
- **Reserved identifiers** — avoid `patch`, `sample`, `filter`, `input`, `output`, `common`, `partition`, `active` as variable names.

## Spec pointers

[GLSL 4.60 spec](https://docs.vulkan.org/glsl/latest/index.html) · [SPIR-V mappings](https://docs.vulkan.org/glsl/latest/chapters/spirvmappings.html) · [Vulkan shaders chapter](https://docs.vulkan.org/spec/latest/chapters/shaders.html) · [Khronos GLSL wiki](https://wikis.khronos.org/opengl/OpenGL_Shading_Language)
