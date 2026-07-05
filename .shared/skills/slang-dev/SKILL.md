---
name: slang-dev
description: "Develop, review, port, compile, test, debug, and optimize Slang shaders and C++ host integration for Vulkan SPIR-V and Metal MSL renderers: modules, import/__include, capabilities, ParameterBlock, generics/interfaces, slangc, IGlobalSession/ISession, ProgramLayout reflection, descriptor/argument-buffer layout, and cross-backend portability. Use for .slang files, slang compiler API, SPIR-V/MSL emission, shader entry points, or shader correctness/performance — even when the user does not say 'Slang'."
---

# Slang Development

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

This skill covers **Slang shader authoring and C++ host integration** through SPIR-V and MSL emission, reflection-driven layout, and cross-backend portability. API-agnostic binding and shader-system architecture live in [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md); `Vk*` pipeline and descriptor setup after SPIR-V exists live in [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md).

Prioritize correctness, reflection-validated layout, and measurable performance. Do not invent syntax or target behavior — verify with `slangc` or the C++ API against the installed Slang version. For grammar disputes: [Slang spec](https://github.com/shader-slang/spec) → user guide → compiler diagnostics.

## When to Use

- Writing, reviewing, or porting `.slang` modules, entry points, `ParameterBlock` groupings, capabilities, generics, or interfaces
- `slangc`, C++ compilation API (`IGlobalSession`, `ISession`, linking, specialization), or reflection (`ProgramLayout`, `IMetaData`)
- SPIR-V/MSL emission, validation, and descriptor-set or Metal argument-buffer layout from Slang reflection
- Debugging compile failures, SPIR-V validation, Metal compiler errors, layout/binding mismatches, or shader perf regressions

## When NOT to Use

- Raw `Vk*` pipeline/descriptor/swapchain setup — [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md)
- API-agnostic renderer architecture (render graph, binding model, frames-in-flight) — [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md)
- GLSL ShaderToy-style visual effects (SDF, ray marching, post) — out of scope
- D3D12, CUDA, CPU, or WebGPU as primary targets — mention only for comparison or capability context
- General C++20 style or CPU allocator design — [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md)

## Operating Principles

- **Reflection-first:** `slangc` does not output reflection; use the C++ API (`getLayout()`, post-compile `IMetaData`) as layout source of truth.
- **Compile early for both backends:** SPIR-V + `spirv-val`/disassembly; MSL + Apple-side compile when available.
- **Three-way modularity:** `import` (separate module), `__include`/`implementing` (multi-file single module), `#include` (legacy textual — avoid inside modules).
- **Capabilities over macros:** `[require(...)]`, `__target_switch`, and `__stage_switch` instead of target `#ifdef` hacks.
- **ParameterBlock by update frequency:** each block → independent descriptor set / argument buffer; ordinary data in `T` auto-introduces a uniform buffer at binding 0 of that set.
- **Correctness before performance:** validate both backends and reflection layout before tuning divergence, bandwidth, or specialization count.

## Default Development Workflow

1. Establish constraints: Vulkan feature level, Metal platform/version, stages, entry points, matrix convention, resource model, offline vs runtime compilation.
2. Design the shader interface: entry-point I/O, `ParameterBlock` boundaries, push constants, specialization constants, host-visible structs.
3. Write minimal valid Slang: `[shader(...)]`, stage semantics, `[numthreads]` for compute, clear module boundaries.
4. Compile early for both backends; keep explicit `-entry`/`-stage` in build scripts even when SPIR-V/Metal infer from attributes.
5. Derive descriptor/argument-buffer layout from C++ reflection — do not ask the user to mirror layout manually unless unavoidable.
6. Debug in layers: Slang diagnostics → generated target code → target validation → pipeline creation → binding → GPU capture.
7. Optimize only after correctness.

## Hard Rules

- Keep `import`, `__include`, and `#include` separate; avoid `#include` inside importable modules.
- Never rely on automatic target-specific preprocessor `#define`s in multi-target passes; compile targets separately when per-target macros differ.
- Default visibility in new modules is `internal`; use `public` for cross-module API. Legacy modules without `module`/`__include`/visibility are all `public` (deprecated).
- Public and interface methods must declare capability requirements explicitly — omitting `[require]` means no specific capability is required; internal/private infer from the body.
- Use `let` for immutable locals; keep host-visible layouts explicit — do not rely on defaults for matrices, packing, or opaque resource layout.
- `[shader("...")]` on entry points is required for `IModule::findEntryPointByName`; otherwise use `findAndCheckEntryPoint`.
- Retain `IComponentType` while using `ProgramLayout`; query post-compile `IMetaData` after code generation for optimized binding info.
- Mark Vulkan-only and Metal-only paths at the call site; do not assume descriptor sets map 1:1 to Metal slots or argument buffers.

## Anti-patterns

- Hard-coding set/binding/register layout without reflection
- Mixing `#include` into modular Slang code (duplicate declarations, broken preprocessor isolation)
- Single multi-target `slangc` pass with conflicting per-target `#define`s
- Assuming `slangc` output includes reflection metadata
- Unbounded generic specialization creating pipeline/compile explosions
- SPIR-V-only features (pointers, bindless, subgroups) without capability gating and Metal fallback

## Workflow Decision Tree

- **New shader / module** → [references/language-grammar.md](references/language-grammar.md), then [references/toolchain-vulkan-metal-cpp.md](references/toolchain-vulkan-metal-cpp.md)
- **Build integration / reflection / C++ API** → [references/toolchain-vulkan-metal-cpp.md](references/toolchain-vulkan-metal-cpp.md)
- **Review / test plan / debug / perf** → [references/workflow-debug-best-practices.md](references/workflow-debug-best-practices.md)
- **Many entry points × backends** → [scripts/slang_compile_matrix.py](scripts/slang_compile_matrix.py) with a JSON manifest
- **VkDescriptorSetLayout / pipeline after SPIR-V** → [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md)

## Reference Routing

| Task | Read |
|------|------|
| Modules, `import`/`__include`, access control, entry points, generics, capabilities, ParameterBlock layout | [references/language-grammar.md](references/language-grammar.md) |
| `slangc`, C++ API lifecycle, reflection, precompiled modules, Vulkan/Metal backend notes | [references/toolchain-vulkan-metal-cpp.md](references/toolchain-vulkan-metal-cpp.md) |
| Test matrix, debug tree, review checklist, perf guidance | [references/workflow-debug-best-practices.md](references/workflow-debug-best-practices.md) |
| Repeatable SPIR-V + MSL compile matrix | [scripts/slang_compile_matrix.py](scripts/slang_compile_matrix.py) |

## Answer Patterns

**New code:** `.slang` with entry points and resources; compile commands or C++ API steps for Vulkan and Metal; host binding/reflection assumptions; backend-sensitive parts called out.

**Reviews (in order):** correctness → Vulkan/Metal portability → layout/reflection → performance → revised code → compile/test commands.

**Debugging:** infer or ask for Slang version, target descriptors, diagnostics, generated SPIR-V/MSL, validation output, pipeline state, and failure phase (compile, link, pipeline, runtime, perf).

## Gotchas

- `ParameterBlock<T>` with ordinary data in `T` auto-introduces a uniform buffer at **binding 0**; resource bindings offset after it.
- Global-scope ordinary uniforms → default constant buffer; entry-point `uniform` ordinary params → push constants in SPIR-V unless `[vk::push_constant]`.
- Front-end runs once per session across targets — preprocessor state does not isolate per backend.
- `internal` is module-wide visibility; only `public` crosses module boundaries.
- Metal may reject descriptor arrays, bindless patterns, or SPIR-V-specific behavior Vulkan accepts — verify generated MSL and reflection.
- Global-scope parameters without explicit space may be wrapped in an implicit `ParameterBlock<>` — check reflection, do not assume flat globals.

## Final Response Checklist

- Slang syntax is valid or labeled pseudocode
- Every entry point has `[shader(...)]` and stage semantics; compute has `[numthreads]` and dispatch assumptions
- Resources have a reflection-backed host binding strategy
- Vulkan and Metal consequences addressed or excluded with reason
- Suggested commands/API calls target the same entry points the code declares
- Performance advice names bottleneck and tradeoff

## Progressive Disclosure

- [references/language-grammar.md](references/language-grammar.md) — load for modules, syntax, capabilities, ParameterBlock, entry points
- [references/toolchain-vulkan-metal-cpp.md](references/toolchain-vulkan-metal-cpp.md) — load for `slangc`, C++ API, reflection, backend layout
- [references/workflow-debug-best-practices.md](references/workflow-debug-best-practices.md) — load for test matrix, debug tree, review checklist
- [scripts/slang_compile_matrix.py](scripts/slang_compile_matrix.py) — run for repeatable SPIR-V/MSL compile matrix from JSON manifest

## Companion Skills

| Task | Path |
|------|------|
| Vk* pipeline, descriptors, swapchain after SPIR-V exists | [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md) |
| API-agnostic binding model, render graph, shader-system architecture | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| C++20 style and build verification | [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md) |

Relative paths resolve from `skills/slang-dev/` in bootstrap layout (or `.shared/skills/slang-dev/` when installed).
