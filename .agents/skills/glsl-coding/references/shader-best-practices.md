# Shader Best Practices

## Table of contents

1. Maintainable structure
2. Efficiency hierarchy
3. Stage-specific performance guidance
4. Common correctness mistakes
5. Review checklist
6. Debugging and validation workflow

## 1. Maintainable structure

Prefer this order in real shaders:

1. `#version` and required extensions.
2. A short header comment naming stage, target API, and resource contract.
3. Constants and specialization constants.
4. Inputs and outputs.
5. Resource declarations grouped by descriptor set/binding or OpenGL binding.
6. Small helper functions with single responsibility.
7. `main()` as a readable orchestration step.

Naming conventions:

- `inPosition`, `inNormal`, `inTexCoord` for vertex attributes.
- `vWorldPos`, `vNormal`, `vTexCoord` for varyings.
- `uCamera`, `uMaterial`, `uLights` for uniform block instances when the codebase uses prefixes.
- `pc` for a push-constant block is acceptable in compact Vulkan examples.
- Avoid one-letter names except for local math where the domain is obvious.

Refactoring principles:

- Isolate BRDF/material math from API-specific resource declarations so it can be unit-tested or shared across stages/APIs.
- Replace magic constants with named constants or specialization constants.
- Avoid macros for ordinary functions. Use macros only for compile-time platform switches that cannot be represented otherwise.
- Keep coordinate-space names explicit: `objectPos`, `worldPos`, `viewDir`, `clipPos`.
- Make color-space expectations explicit: linear vs sRGB, HDR range, premultiplied alpha.

## 2. Efficiency hierarchy

When optimizing, check in this order:

1. Algorithm and stage placement: avoid doing per-fragment work that can be done per-vertex, per-tile, per-object, or on the CPU without visible loss.
2. Data movement: reduce texture fetches, SSBO reads/writes, framebuffer bandwidth, and overdraw.
3. Work granularity: choose compute workgroup sizes and draw batching that keep the GPU occupied without excessive synchronization.
4. Divergence and control flow: coherent branches can be beneficial; highly divergent branches and variable loops are risky.
5. Arithmetic: after the above, simplify math, remove redundant normalizations, replace repeated divisions with reciprocals where compilers do not already do it, and precompute invariants.
6. Precision: use `float` by default, avoid `double` unless necessary, and use lower precision only when the target GPU/compiler benefits and quality is verified.

Avoid absolute claims such as "branchless is always faster" or "texture fetches are always slower than ALU." Modern GPUs vary. Recommend measurement for performance-critical code.

## 3. Stage-specific performance guidance

### Vertex

- Move invariant object/material work out of the vertex shader if it repeats for every vertex.
- Keep vertex formats compact and aligned. Bandwidth can dominate.
- Skinning and morphing can be expensive; limit bone influences and consider compute preprocessing for heavy workloads.

### Tessellation

- Clamp tessellation levels and base them on screen-space need.
- Avoid displacement sampling at unnecessarily high tessellation rates.
- Ensure tessellation control and evaluation shaders agree on patch size, winding, spacing, and output semantics.

### Geometry

- Avoid heavy geometry amplification. Prefer instancing, compute-generated draws, or mesh shaders if available.
- Use geometry shaders for small, clear use cases such as layered rendering or debug visualization.

### Fragment

- Reduce overdraw and bandwidth before micro-optimizing math.
- Be cautious with `discard` and `gl_FragDepth`; they can reduce early-depth optimization opportunities.
- Minimize dependent texture chains in hot paths.
- Use derivatives only where they are valid. In divergent control flow, consider `textureGrad` or restructuring.
- Keep framebuffer format and blending costs in mind.

### Compute

- Pick local sizes based on algorithm, memory access pattern, subgroup/wave size expectations, and occupancy.
- Prefer coalesced memory access and shared-memory tiling when reuse justifies synchronization.
- Minimize atomics and barriers. Use them where correctness requires them, not as a default.
- Separate algorithmic barriers inside the shader from API pipeline barriers after dispatch.

## 4. Common correctness mistakes

OpenGL GLSL:

- Calling `glUniform*` before binding the intended program with `glUseProgram`, unless using direct program uniform APIs.
- Passing the wrong `count` to vector uniform setters. The count is the number of vectors/matrices, not the scalar component count.
- Treating `glGetUniformLocation == -1` as always fatal. It can mean the uniform was optimized out, but also check spelling and program linkage.
- Forgetting to check shader compile logs and program link logs.
- Relying on legacy names such as `gl_FragColor`, `varying`, `attribute`, `texture2D`, or fixed-function varyings in modern core shaders.
- Using `noise()` when compiling for Vulkan SPIR-V — invalid per SPIR-V mappings.
- Using default non-opaque uniforms in Vulkan GLSL — use uniform blocks or push constants.
- Sampling from a texture while rendering to the same texture region without a valid feedback-loop avoidance strategy.

Vulkan GLSL:

- Missing descriptor `set`/`binding` layout qualifiers or mismatching the pipeline layout.
- Using default uniforms instead of uniform blocks, push constants, specialization constants, or descriptors.
- Confusing `gl_VertexID`/`gl_InstanceID` with Vulkan `gl_VertexIndex`/`gl_InstanceIndex`.
- Forgetting host-side pipeline barriers for storage buffer/image writes.
- Assuming OpenGL framebuffer origin/depth conventions without checking Vulkan viewport/projection setup.
- Using specialization constants for values that must change after pipeline creation.

Cross-stage:

- Producer/consumer varying type or location mismatches.
- Missing interpolation qualifiers for integer or flat data.
- Writing outputs that no later stage consumes and mistaking optimized-away code for runtime failure.
- Assuming neighboring fragments or invocations are visible without explicit stage/resource mechanisms.

## 5. Review checklist

Use this checklist when reviewing shader code:

- Target: API, GLSL version, stage, enabled extensions/features.
- Compilation: valid `#version`, no legacy identifiers, required extensions declared.
- Interfaces: explicit locations, matching types, interpolation qualifiers, fragment outputs.
- Resources: descriptor set/binding or OpenGL binding, block layout, CPU struct compatibility, sampler/image formats.
- Correctness: initialized values, `gl_Position`, output writes, bounds checks, coordinate spaces, color spaces.
- Synchronization: workgroup barriers, memory barriers, API pipeline barriers, image layouts.
- Performance: stage placement, texture/memory bandwidth, overdraw, divergence, loops, atomics, tessellation/geometry amplification.
- Maintainability: names, helper functions, constants, comments describing non-obvious math, minimal macro use.
- Validation: compile/link logs, SPIR-V validation, validation layers, GPU capture/profiling.

## 6. Debugging and validation workflow

For **creative effect visual debugging** (SDF bands, normal colors, march step heatmaps), use [`../../shader-guide/SKILL.md`](../../shader-guide/SKILL.md) — this skill owns compile/link and layout validation only.

OpenGL:

1. Compile each shader and inspect `GL_COMPILE_STATUS` plus the shader info log.
2. Link the program and inspect `GL_LINK_STATUS` plus the program info log.
3. Verify attribute locations, fragment output locations, uniform block bindings, sampler bindings, and buffer/image bindings.
4. Use debug output and GPU captures to confirm state and resource binding.
5. Reduce the shader to a minimal visual output, then reintroduce features one at a time.

Vulkan:

1. Compile GLSL to SPIR-V with Vulkan semantics.
2. Run SPIR-V validation where available.
3. Check descriptor set layouts, push constant ranges, specialization constants, render-pass/dynamic-rendering formats, and pipeline layout compatibility.
4. Enable validation layers and inspect messages.
5. Use GPU capture/profiling to inspect bound descriptors, pipeline state, and shader performance.
6. Confirm memory/image barriers between producing and consuming passes.
