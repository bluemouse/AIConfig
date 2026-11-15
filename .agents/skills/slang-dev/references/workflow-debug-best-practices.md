# Workflow, Testing, Debugging, and Performance Best Practices

Use when planning implementation, debugging, reviewing code, or optimizing Slang shaders for Vulkan and Metal.

## Implementation Process

1. Define the shader contract.
   - Entry points and stages.
   - Input/output semantics.
   - Resource groups and update frequency.
   - Host-visible struct layout and matrix convention.
   - Required Vulkan features and Metal platform level.
2. Write the smallest compiling module.
   - Use one module per feature area.
   - Keep entry points thin; move shared logic into functions/types.
   - Compile Vulkan and Metal before adding specialization.
3. Add resource bindings through policy.
   - Prefer reflection-generated layouts.
   - Use explicit bindings only when the engine requires stable ABI.
4. Add generics/interfaces only when they simplify variant structure.
   - Keep specialization count bounded.
   - Avoid replacing simple constants with type-level machinery.
5. Add backend-sensitive code last.
   - Isolate Vulkan-only and Metal-only differences with capabilities or `__target_switch`.
   - Document capabilities and fallbacks.

## Test Matrix

At minimum, test each changed entry point across:

- Vulkan SPIR-V binary emission.
- Vulkan SPIR-V assembly emission for review.
- SPIR-V validation/disassembly (`spirv-val`, `spirv-dis`).
- Metal MSL emission.
- Apple Metal compiler validation where available.
- C++ reflection layout (`ProgramLayout`) matches host descriptor/argument-buffer setup.
- Post-compile `IMetaData` binding usage matches bound resources.
- Engine pipeline creation with reflection-derived layout.
- A GPU capture for a representative workload.

For compute shaders, also test:
- dimensions not divisible by thread-group size;
- zero or tiny dispatches;
- maximum expected dispatch sizes;
- resource aliasing hazards;
- barriers/synchronization behavior;
- deterministic CPU reference output where feasible.

For raster shaders, also test:
- clip-space convention and Y direction;
- interpolation modifiers;
- depth/stencil interactions;
- MRT output locations;
- vertex input layout agreement;
- MSAA/sample-rate behavior if used.

## Debugging Decision Tree

**Compile-time error:**
- Re-run a single target and single entry point with explicit `-entry` and `-stage`.
- Reduce imported modules until the diagnostic points to one declaration.
- Check [language-grammar.md](language-grammar.md) before editing syntax.
- Inspect diagnostics even if output exists.
- Check capability requirements vs compile target (`[require]` mismatch).

**SPIR-V validation failure:**
- Emit `spirv-asm` or disassemble the `.spv`.
- Check capabilities/profile/device features.
- Verify resource types, image formats, atomics, pointer use, and stage-specific built-ins.

**Metal compile failure:**
- Emit MSL source and inspect the failing generated declaration.
- Check resource type mapping, argument buffers, buffer arrays, address spaces, matrix layout, and unsupported stage/features.
- Minimize the Slang source around the generated MSL failure before adding workarounds.

**Reflection/layout mismatch:**
- Compare `ProgramLayout` (and post-compile `IMetaData`) with host descriptor set/layout or Metal binding setup.
- Check implicit `ParameterBlock<>` wrapping of global-scope parameters.
- Verify auto-introduced uniform buffer at binding 0 inside `ParameterBlock<>` with ordinary data.
- Confirm matrix layout mode matches session `defaultMatrixLayoutMode`.

**Pipeline creation failure:**
- Compare reflection output with descriptor set/layout or Metal binding setup.
- Verify shader stage flags and entry-point names.
- Confirm specialization constants and push constants match pipeline layout.

**Wrong pixels/data:**
- Validate matrix convention and coordinate-space transforms first.
- Check resource binding order and descriptor/argument-buffer contents.
- Add simple debug outputs or sentinel colors/values.
- Use RenderDoc/Xcode GPU capture, not guesswork.

**Performance regression:**
- Identify the bottleneck: bandwidth, ALU, texture sampling, occupancy/registers, divergence, synchronization, descriptor churn, or pipeline count.
- Compare generated SPIR-V/MSL before and after.
- Measure one change at a time.

## Correctness Best Practices

- Make entry-point I/O structs explicit and stable.
- Use named constants for thread group sizes and validate dispatch bounds.
- Guard all buffer/texture indexing when dimensions can be arbitrary.
- Keep coordinate spaces named in variable names (`worldPos`, `viewDir`, `clipPos`).
- Prefer explicit conversions between `half`, `float`, and integer types.
- Ensure all code paths initialize outputs.
- Treat NaN/Inf paths explicitly in BRDF, normalize, reciprocal, and sqrt code.
- Keep CPU-side struct definitions generated from or validated against Slang reflection.

## Performance Best Practices

- Minimize global memory bandwidth; use packed formats only when precision and alignment are verified.
- Coalesce buffer access and avoid divergent resource indexing where target support is limited.
- Keep branch divergence predictable; prefer branchless math only when it reduces actual cost.
- Avoid unnecessary `normalize`, `sqrt`, `pow`, transcendental functions, and high precision in inner loops.
- Use `half` carefully on Metal/mobile when precision permits; validate Vulkan behavior separately.
- Keep compute group sizes tuned per workload; common starting points are 64, 128, or 256 threads total, then measure.
- Avoid excessive generic specialization that creates many pipelines and long compile times.
- Group parameters by update frequency to reduce descriptor/argument-buffer rebinding.
- Keep generated target code readable during development; enable obfuscation only in release pipelines that preserve debugging alternatives.

## Review Checklist

- Does every shader entry point compile for Vulkan and Metal, or is the unsupported backend explicitly documented?
- Are target-specific features isolated behind capabilities or build policy?
- Does the host use reflection (`ProgramLayout` + post-compile `IMetaData`) for layout, offsets, and bindings?
- Are matrix layout and coordinate conventions explicit?
- Are resource arrays/bindless/pointers/subgroups checked against Metal limitations?
- Are all buffers indexed safely?
- Is the specialization strategy bounded and cacheable?
- Is there a reproducible command/API path to regenerate artifacts?
