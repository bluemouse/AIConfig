---
name: slang-dev
description: "Develop, review, compile, and debug Slang shaders (`.slang`) and C++ host integration for Vulkan SPIR-V and Metal MSL: modules, capabilities, `ParameterBlock`, generics/interfaces, `slangc`, `IGlobalSession`/`ProgramLayout` reflection, and cross-backend layout portability."
---

# Slang Development

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

> Verified against Slang source docs last reviewed **2026-07-05**; no pinned release — confirm version-specific syntax against the installed `slangc`/C++ API before relying on it.

Covers Slang shader authoring and C++ host integration through SPIR-V/MSL emission, reflection-driven layout, and cross-backend portability; D3D12, CUDA, CPU, and WebGPU are comparison context only. Do not invent syntax — verify against the installed Slang version with `slangc` or the C++ API (grammar disputes: [Slang spec](https://github.com/shader-slang/spec) → user guide → compiler diagnostics).

## Operating Principles

- **Reflection-first:** `slangc` does not output reflection; use the C++ API (`getLayout()`, post-compile `IMetaData`) as layout source of truth.
- **Compile early for both backends:** SPIR-V + `spirv-val`/disassembly; MSL + Apple-side compile when available.
- **Three-way modularity:** `import` (separate module), `__include`/`implementing` (multi-file single module), `#include` (legacy textual — avoid inside modules).
- **Capabilities over macros:** `[require(...)]`, `__target_switch`, and `__stage_switch` instead of target `#ifdef` hacks.
- **ParameterBlock by update frequency:** each block → independent descriptor set / argument buffer; ordinary data in `T` auto-introduces a uniform buffer at binding 0 of that set.
- **Correctness before performance:** validate both backends and reflection layout before tuning divergence, bandwidth, or specialization count.

## Core Workflow

1. Design the interface (entry-point I/O, `ParameterBlock` boundaries, push constants, host-visible structs), then write minimal valid Slang: `[shader(...)]`, stage semantics, `[numthreads]` for compute.
2. Compile early for both backends — keep explicit `-entry`/`-stage` in build scripts — and derive descriptor/argument-buffer layout from C++ reflection, not hand-mirroring.
3. Debug in layers (Slang diagnostics → generated target code → target validation → pipeline creation → binding → GPU capture); optimize only after correctness.

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

## Gotchas

- `ParameterBlock<T>` with ordinary data in `T` auto-introduces a uniform buffer at **binding 0**; resource bindings offset after it.
- Global-scope ordinary uniforms → default constant buffer; entry-point `uniform` ordinary params → push constants in SPIR-V unless `[vk::push_constant]`.
- Front-end runs once per session across targets — preprocessor state does not isolate per backend.
- `internal` is module-wide visibility; only `public` crosses module boundaries.
- Metal may reject descriptor arrays, bindless patterns, or SPIR-V-specific behavior Vulkan accepts — verify generated MSL and reflection.
- Global-scope parameters without explicit space may be wrapped in an implicit `ParameterBlock<>` — check reflection, do not assume flat globals.

## Routing

Read only the row matching the task.

| Task | Read |
|------|------|
| Slang authoring or build integration: modules, `import`/`__include`, access control, entry points, generics, capabilities, ParameterBlock layout, `slangc`, C++ API, reflection, backend notes | [references/language-grammar.md](references/language-grammar.md), [references/toolchain-vulkan-metal-cpp.md](references/toolchain-vulkan-metal-cpp.md) |
| Review / test plan / debug / perf: test matrix, debug tree, review checklist, perf guidance | [references/workflow-debug-best-practices.md](references/workflow-debug-best-practices.md) |
| Many entry points × backends: repeatable SPIR-V + MSL compile matrix from a JSON manifest | [scripts/slang_compile_matrix.py](scripts/slang_compile_matrix.py) |
| Raw `Vk*` pipeline/descriptor/swapchain setup | [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md) |
| API-agnostic renderer architecture (render graph, binding model, frames-in-flight) | [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md) |
| Raw GLSL source/layouts/compile issues; creative effect authoring (SDF, ray marching, procedural post) | [`../glsl-coding/SKILL.md`](../glsl-coding/SKILL.md) / [`../shader-guide/SKILL.md`](../shader-guide/SKILL.md) |
| General C++20 style or CPU allocator design | [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md) |

## Response Contract

- New code ships with compile commands/API steps for both backends and reflection-backed host binding; reviews go correctness → portability → layout → performance.
- Every entry point has `[shader(...)]`, stage semantics, and `[numthreads]` for compute; syntax is valid or labeled pseudocode.
- Debugging gathers Slang version, targets, diagnostics, generated code, failure phase; perf advice names bottleneck and tradeoff.

## Compile Matrix

Run the bundled script for repeatable SPIR-V/MSL builds across entry points:

```bash
python <SKILL_ROOT>/scripts/slang_compile_matrix.py manifest.json [--print-only]
```

`--print-only` emits commands without executing; `--allow-missing-slangc` exits `0` when `slangc` is not on `PATH`; invalid manifests exit `2`.

## Tool notes

### Claude Code

- Reload the session after installing or editing the skill so updated frontmatter and relative cross-links are rediscovered.

### Cursor

- Reload the window after installing or editing the skill so the skill catalog refreshes.

### GitHub Copilot

- Reload VS Code or start a new chat session after installing or editing the skill so the updated skill is rediscovered.
