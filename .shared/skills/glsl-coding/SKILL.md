---
name: glsl-coding
description: "Teach, write, review, debug, and optimize modern GLSL for OpenGL 4.6 core and Vulkan 1.3 SPIR-V: shader stages, layouts, descriptors, push constants, specialization constants, interface matching, precision, and compile/link validation. Use for GLSL syntax, stage I/O, resource bindings, GLSL-to-SPIR-V layout questions, maintainability refactors, and diagnosing shader mistakes — even when the user does not say 'GLSL' or 'SPIR-V'."
---

# GLSL Coding (OpenGL 4.6 / Vulkan SPIR-V)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

This skill owns **GLSL language and stage/resource contracts** for OpenGL 4.6 core-profile GLSL and Vulkan-target GLSL compiled to SPIR-V. Normative language rules: [GLSL 4.60 specification](https://docs.vulkan.org/glsl/latest/index.html) (Vulkan Documentation Project); SPIR-V mapping notes: [Non-Normative SPIR-V Mappings](https://docs.vulkan.org/glsl/latest/chapters/spirvmappings.html). For creative effect techniques (SDF, ray marching, procedural post), link to [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md). For `Vk*` pipeline/descriptor setup after SPIR-V exists, link to [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md).

## When to Use

- Writing, teaching, reviewing, or debugging GLSL for vertex/tessellation/geometry/fragment/compute stages
- OpenGL compile/link failures, uniform/block binding mismatches, varying interface errors
- Vulkan GLSL layout: `layout(set, binding)`, push constants, specialization constants, `std140`/`std430`, separate texture/sampler vs combined `sampler2D`
- GLSL-to-SPIR-V compilation, SPIR-V validation, descriptor/pipeline-layout compatibility
- Stage placement, maintainability refactors, precision choices, and shader performance triage

## When NOT to Use

- Creative fragment-shader effects (SDF scenes, ray marching, generative art recipes) — [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md)
- Slang modules, slangc, reflection, cross-backend `.slang` authoring — [`../slang-dev/SKILL.md`](../slang-dev/SKILL.md)
- Renderer architecture (render graph, bindless model, frames-in-flight) — [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md)
- Concrete `Vk*` objects, swapchain, command recording, pipeline barriers in host code — [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md)
- Host/runtime glue only (canvas setup, JavaScript loaders) with no GLSL source to inspect

## Version Standard

| Target | Default `#version` | Notes |
|--------|-------------------|-------|
| OpenGL 4.6 core | `#version 460 core` | Use lower versions only when a feature requires it; avoid compatibility profile |
| Vulkan SPIR-V | `#version 450` | No `core`/`compatibility` profile keyword; SPIR-V emission is toolchain-driven |
| OpenGL ES / GLES | `#version 300 es` / `310 es` | Not a strict subset of desktop GLSL — check precision and interface rules separately |
| Shared math headers | `#version 450` or `460` | Keep API-specific I/O and resource declarations in stage entry files |

Authority order for disputes: GLSL spec → SPIR-V mappings appendix → toolchain docs (`glslangValidator`, driver compile logs) → validation layers.

## Operating Principles

- **Name the contract** — every complete shader states stage, target API, GLSL version, and resource layout assumptions.
- **Explicit layouts** — `layout(location = N)` for stage I/O; Vulkan descriptors use `layout(set = M, binding = N)`.
- **Vulkan ≠ OpenGL** — do not paste OpenGL default uniforms or `binding = N` alone into Vulkan GLSL; use blocks, sets, and SPIR-V rules.
- **Correctness before micro-opts** — compile/link or SPIR-V-validate first; then stage placement and bandwidth; then arithmetic tweaks.
- **No folklore** — branchless is not always faster; measure with GPU capture when performance matters.
- **Progressive disclosure** — load one reference file per task; do not dump all references unless the task spans APIs and stages.

## Workflow Decision Tree

- **Teaching / concept explanation** → [references/glsl-modern-primer.md](references/glsl-modern-primer.md)
- **Writing stage examples** → [references/examples.md](references/examples.md); add API rules from [references/opengl-vulkan-glsl.md](references/opengl-vulkan-glsl.md) when bindings differ
- **Review / debug / optimize** → [references/shader-best-practices.md](references/shader-best-practices.md); optionally run [scripts/glsl_lint.py](scripts/glsl_lint.py)
- **OpenGL vs Vulkan layout, coordinates, SPIR-V constraints** → [references/opengl-vulkan-glsl.md](references/opengl-vulkan-glsl.md)
- **Creative effect pipeline or visual SDF debug colors** → [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md) (not duplicated here)

## Stage Coverage

Core stages (default): vertex, tessellation control, tessellation evaluation, geometry, fragment, compute — per [GLSL overview](https://docs.vulkan.org/glsl/latest/chapters/overview.html).

Extension stages (task, mesh, ray tracing, subpass shading, cluster culling): explain only with explicit extension/feature caveats; not baseline OpenGL 4.6 or Vulkan 1.3 core.

## Code Output Standard

Unless the user requests otherwise, structure complete shaders as:

```glsl
#version 450

// Stage: fragment
// Target: Vulkan 1.3 GLSL → SPIR-V (or OpenGL 4.6 core — adjust layouts)

// 1. Extensions (OpenGL only when required)
// 2. Constants / specialization constants
// 3. Stage inputs and outputs
// 4. Resources: UBOs, SSBOs, textures, images, push constants
// 5. Helper functions (callees before callers unless prototypes available)
// 6. main()
```

Vulkan fragment output example: `layout(location = 0) out vec4 outColor;` — not `gl_FragColor`.

## Review Output Template

1. **Target assumptions** — API, stage, GLSL version, inferred resources
2. **Correctness blockers** — compile errors, UB, interface mismatches, layout/binding, synchronization
3. **Performance risks** — stage placement, bandwidth, divergence, loops, atomics, amplification
4. **Maintainability** — naming, structure, magic numbers, hidden API assumptions
5. **Patch** — smallest useful corrected shader
6. **Validation** — compile/link logs, SPIR-V validation, descriptor layout check, GPU capture if perf claims matter

## Reference Routing

| Task | Read |
|------|------|
| Stage mental models, data flow, teaching juniors | [references/glsl-modern-primer.md](references/glsl-modern-primer.md) |
| OpenGL vs Vulkan bindings, coordinates, SPIR-V removals | [references/opengl-vulkan-glsl.md](references/opengl-vulkan-glsl.md) |
| Maintainability, efficiency, review checklist, debug workflow | [references/shader-best-practices.md](references/shader-best-practices.md) |
| Minimal stage skeletons and review example style | [references/examples.md](references/examples.md) |
| Spec provenance and design notes | [references/source-notes.md](references/source-notes.md) |
| Static first-pass lint on provided `.glsl` files | [scripts/glsl_lint.py](scripts/glsl_lint.py) |

## Gotchas

- **Vulkan SPIR-V removes** default non-opaque uniforms, subroutines, `noise()`, compatibility-profile features, and `shared`/`packed` block layouts — see SPIR-V mappings.
- **`#version 450` for Vulkan** — profile keywords are not used; SPIR-V targeting is selected by the offline compiler, not an in-shader `#extension`.
- **Fragment origin** — Vulkan GLSL defaults to `origin_upper_left`; OpenGL historically used lower-left. Centralize Y-flip in projection/viewport setup.
- **Built-in indices** — Vulkan uses `gl_VertexIndex` / `gl_InstanceIndex`; OpenGL uses `gl_VertexID` / `gl_InstanceID`.
- **Push constant packing** — push-constant blocks follow `std430` rules; watch `mat3`/array alignment and the small byte budget.
- **Descriptor arrays** — an array of samplers/UBOs consumes **one** `binding` for the whole array in Vulkan SPIR-V.
- **Function order** — GLSL requires callees before callers unless prototypes are supported.
- **Dead code is still checked** — ill-formed statements inside `if (false)` must still compile.
- **Reserved identifiers** — avoid `patch`, `sample`, `filter`, `input`, `output`, `common`, `partition`, `active` as variable names.

## Progressive Disclosure

- Read [references/glsl-modern-primer.md](references/glsl-modern-primer.md) — Load when explaining stages, resources, or teaching shader fundamentals
- Read [references/opengl-vulkan-glsl.md](references/opengl-vulkan-glsl.md) — Load when choosing OpenGL vs Vulkan layouts, coordinates, or SPIR-V constraints
- Read [references/shader-best-practices.md](references/shader-best-practices.md) — Load when reviewing, refactoring, optimizing, or triaging compile failures
- Read [references/examples.md](references/examples.md) — Load when generating stage skeletons or demonstrating review format
- Run [scripts/glsl_lint.py](scripts/glsl_lint.py) — Optional first-pass structural checklist on user-provided shader files

## Companion Skills

| Task | Path |
|------|------|
| Creative GLSL effects (SDF, ray marching, procedural post) | [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md) |
| Slang shader modules and slangc / reflection | [`../slang-dev/SKILL.md`](../slang-dev/SKILL.md) |
| Renderer architecture (render graph, binding model) | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| `Vk*` pipelines, descriptors, barriers, swapchain | [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md) |

Relative paths resolve from `.shared/skills/glsl-coding/` when installed (or `skills/glsl-coding/` in bootstrap layout).
