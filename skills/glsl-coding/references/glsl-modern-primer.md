# Modern GLSL Primer

## Table of contents

1. Mental model
2. Shader program shape
3. Data flow and resources
4. Core shader stages
5. Coordinate and interpolation basics
6. Teaching pattern for juniors

## 1. Mental model

A shader is a small program executed by the GPU for many independent invocations. Each stage transforms a specific kind of work item: a vertex, patch/control point, primitive, fragment, or compute work item — per the [GLSL overview](https://docs.vulkan.org/glsl/latest/chapters/overview.html). Shaders communicate through explicit inputs, outputs, built-in variables, and API-bound resources; they do not call each other directly.

Use this explanation for juniors:

- CPU code schedules rendering or dispatch work and binds resources.
- The graphics or compute pipeline creates many shader invocations.
- Each invocation runs the same shader code on different data.
- Outputs become the next stage's inputs, framebuffer writes, storage writes, or other side effects.
- Performance is usually dominated by data movement, texture/memory access, overdraw, and parallel execution behavior, not just arithmetic count.

## 2. Shader program shape

Modern GLSL code should start with a version directive, declare stage inputs and outputs, declare resources, define helper functions, then implement `main()`.

```glsl
#version 450 core

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec2 inTexCoord;

layout(location = 0) out vec2 vTexCoord;

void main()
{
    vTexCoord = inTexCoord;
    gl_Position = vec4(inPosition, 1.0);
}
```

Key teaching points:

- Use `in` and `out` for stage interfaces.
- Use `uniform` blocks, storage buffers, textures/samplers, images, push constants, or specialization constants for API-provided data.
- Use vector and matrix types deliberately. Swizzling is useful, but avoid clever swizzles that obscure meaning.
- Prefer explicit locations and bindings so shader and host code agree without fragile reflection-only assumptions.

## 3. Data flow and resources

Common GLSL data paths:

- Vertex attributes: per-vertex data fetched by the vertex stage.
- Varyings: outputs from one graphics stage interpolated or passed to a later stage.
- Uniform buffers: read-only structured data shared across many invocations.
- Push constants in Vulkan: very small, frequently changed values stored in a push-constant block.
- Specialization constants: compile/pipeline-creation-time constants that allow variants without source edits.
- Samplers/textures: filtered or unfiltered image reads.
- Images and storage buffers: read/write resources that need careful synchronization.
- Atomic counters/atomics: high-contention operations that should be used sparingly and measured.

## 4. Core shader stages

### Vertex shader

Runs once per input vertex. It usually transforms object-space attributes to clip space and passes varyings to later stages.

Use it for:

- Position transforms, skinning, morphing, per-vertex procedural attributes.
- Computing values that can be safely interpolated for fragments.

Watch for:

- Forgetting to write `gl_Position`.
- Doing work per vertex that actually needs per-fragment precision.
- Mismatched vertex attribute locations or formats.

### Tessellation control shader

Runs for each control point in a patch and collectively emits an output patch plus tessellation levels.

Use it for:

- Deciding tessellation density.
- Passing or modifying per-control-point and per-patch data.

Watch for:

- Missing or inconsistent `layout(vertices = N) out`.
- Reading values written by another invocation without a valid `barrier()` phase.
- Excessive tessellation factors that create too many primitives.

### Tessellation evaluation shader

Runs for each generated tessellated vertex. It evaluates a surface position and attributes from patch data and `gl_TessCoord`.

Use it for:

- Bezier/NURBS-like evaluation, terrain displacement, adaptive surface refinement.

Watch for:

- Inconsistent primitive mode, spacing, winding, or patch size with the control shader.
- Expensive displacement sampling at very high tessellation rates.

### Geometry shader

Runs per input primitive and can emit zero or more output primitives.

Use it carefully for:

- Lightweight primitive expansion, layered rendering, debug visualization.

Watch for:

- Heavy amplification. Geometry shaders often become a throughput bottleneck compared with instancing, compute preprocessing, or mesh shaders where available.
- Large outputs or complex branching per primitive.

### Fragment shader

Runs for rasterized fragments. It computes color, depth, coverage-related outputs, or storage side effects.

Use it for:

- Material evaluation, texture sampling, lighting, compositing, post-processing.

Watch for:

- Overdraw, expensive texture chains, divergent branches, `discard`, writing `gl_FragDepth`, and framebuffer feedback loops.
- Derivative-dependent functions inside non-uniform control flow. Use explicit gradients when needed.

### Compute shader

Runs outside the graphics pipeline in workgroups. It writes visible results through buffers, images, atomics, or other storage side effects.

Use it for:

- Tiled/clustered lighting, culling, particle simulation, image processing, reductions, prefix sums, GPU preprocessing.

Watch for:

- Bad local workgroup size, uncoalesced memory access, excessive barriers, shared-memory bank conflicts, atomics under high contention, missing API memory barriers after dispatch.

## 5. Coordinate and interpolation basics

- Clip-space output from vertex/tessellation/geometry reaches fixed-function clipping and perspective division.
- Interpolated varyings are generated for fragments based on primitive rasterization.
- Use interpolation qualifiers (`flat`, `smooth`, `noperspective`, `centroid`, `sample`) when default perspective-correct interpolation is not correct.
- OpenGL and Vulkan differ in coordinate conventions and defaults. Check clip-depth range, framebuffer Y orientation, viewport setup, and `gl_FragCoord` assumptions for the target API.

## 6. Teaching pattern for juniors

When explaining a shader concept, use this sequence:

1. State what stage owns the work.
2. Describe one invocation: what data it receives, what it outputs, and what it cannot see.
3. Show the minimal code.
4. Explain host-side bindings or pipeline state that must match the shader.
5. Name the main correctness pitfalls.
6. Name the first performance consideration and how to measure it.
