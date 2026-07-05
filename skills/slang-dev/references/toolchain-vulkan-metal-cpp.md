# Slang Toolchain for Vulkan, Metal, and C++ Integration

Use when giving compile commands, build-system advice, or C++ API/reflection guidance.

## Command-Line Compilation

Baseline Vulkan SPIR-V compile:

```bash
slangc shader.slang -entry computeMain -stage compute -target spirv -profile glsl_460 -o compute.spv
```

With `[shader("compute")]` on the entry point, Slang can infer stage for SPIR-V and Metal, but explicit `-entry` and `-stage` remain clearer in build scripts:

```bash
slangc shader.slang -entry vertexMain   -stage vertex   -target spirv -profile glsl_460 -o vertex.spv
slangc shader.slang -entry fragmentMain -stage fragment -target spirv -profile glsl_460 -o fragment.spv
```

Metal MSL compile:

```bash
slangc shader.slang -entry vertexMain   -stage vertex   -target metal -o vertex.metal
slangc shader.slang -entry fragmentMain -stage fragment -target metal -o fragment.metal
slangc shader.slang -entry computeMain  -stage compute  -target metal -o compute.metal
```

If `-target metal` spelling differs in the installed Slang version, check `slangc -help` and update build scripts consistently.

Debug and inspection:

```bash
slangc shader.slang -entry computeMain -stage compute -target spirv-asm -profile glsl_460 -g1 -o compute.spvasm
slangc shader.slang -entry computeMain -stage compute -target spirv     -profile glsl_460 -g1 -o compute.spv
```

Warnings and macros:

```bash
slangc shader.slang -entry main -stage compute -target spirv -profile glsl_460 -Wall -Wextra -Werror all -o main.spv
slangc shader.slang -entry main -stage compute -target spirv -DMY_FEATURE=1 -o main.spv
```

Choose `-profile glsl_450` or newer to match the engine's minimum Vulkan feature level.

### Multi-target and preprocessor rules

- Front-end (preprocess, parse, semantic check) runs **once** per compilation session and is shared across all `-target` backends.
- Slang does **not** automatically supply target-specific preprocessor `#define`s for multi-target passes.
- Compile Vulkan and Metal as separate targets when backend-specific macros are required.
- Prefer one output per entry point/backend in deterministic builds.

### Precompiled modules

Offline precompile + link workflow:

```bash
slangc lib.slang -o lib.slang-module                    # precompile module
slangc lib.slang-module entry.slang -target spirv -o program.spv  # link + emit
```

Hybrid: precompile stable modules to `.slang-module`; link entry points and specialize per backend at build or runtime; cache artifacts keyed by Slang version, source hash, target, profile, options, specialization values, and matrix layout.

## C++ Compiler API Model

Use the C++ API when the engine needs reflection, runtime specialization, custom search paths, file systems, precompiled modules, or control over composition/linking.

Recommended object lifetime:

1. Create one long-lived `slang::IGlobalSession` per compiler context when possible.
2. Create an `slang::ISession` per compilation configuration: targets, profiles, search paths, macros, matrix layout, file system.
3. Load modules via `ISession::loadModule()`.
4. Find entry points (`findEntryPointByName` requires `[shader(...)]`; otherwise `findAndCheckEntryPoint`).
5. Compose module(s) + entry point(s) into a component type.
6. Link/specialize.
7. Query reflection/layout (`getLayout(targetIndex)`).
8. Emit target code per entry point/backend.
9. Query post-compile metadata (`getTargetMetadata` / `getEntryPointMetadata`) after code generation.

C++ skeleton:

```cpp
#include <slang.h>
#include <slang-com-ptr.h>

using namespace slang;

Slang::ComPtr<IGlobalSession> globalSession;
SLANG_RETURN_ON_FAIL(createGlobalSession(globalSession.writeRef()));

TargetDesc target = {};
target.format = SLANG_SPIRV; // use SLANG_METAL for MSL builds
target.profile = globalSession->findProfile("glsl_460");

const char* searchPaths[] = { "shaders" };
SessionDesc sessionDesc = {};
sessionDesc.targets = &target;
sessionDesc.targetCount = 1;
sessionDesc.searchPaths = searchPaths;
sessionDesc.searchPathCount = 1;
sessionDesc.defaultMatrixLayoutMode = SLANG_MATRIX_LAYOUT_ROW_MAJOR;

Slang::ComPtr<ISession> session;
SLANG_RETURN_ON_FAIL(globalSession->createSession(sessionDesc, session.writeRef()));

Slang::ComPtr<IBlob> diagnostics;
IModule* module = session->loadModule("Renderer.Lighting", diagnostics.writeRef());
// Always print diagnostics if non-null, even on success.
```

Adjust enum names for the installed Slang headers. Treat `_Experimental` interfaces as unstable.

## Reflection

**`slangc` does not output reflection metadata.** Applications must use the C++ compilation API.

### Pre-compile layout (`ProgramLayout`)

After linking a component type:

```cpp
slang::IComponentType* program = /* linked program */;
slang::ProgramLayout* layout = program->getLayout(targetIndex);
```

- `ProgramLayout` lifetime is tied to the `IComponentType` that returned it — retain the component while using the layout.
- Layout includes global scope (`getGlobalParamsVarLayout()`) and entry points (`getEntryPointByIndex()`).
- Layout is target-dependent — pass the correct `targetIndex` when multiple targets are configured.
- Prefer walking `VariableLayoutReflection` from scopes rather than `getParameterCount()`/`getParameterByIndex()` alone (corner cases with implicit wrappers).

`ConstantBuffer<>` and `ParameterBlock<>` reflection includes auto-introduced constant buffers and descriptor-set/register-space assignments. For `ParameterBlock<>`, expect a descriptor set (`SubElementRegisterSpace`) plus binding slot for any auto-introduced uniform buffer at offset 0.

### Post-compile metadata (`IMetaData`)

After `getTargetCode()` or `getEntryPointCode()`:

```cpp
// Same targetIndex / entryPointIndex as used for code generation
IMetaData* meta = program->getEntryPointMetadata(entryPointIndex, targetIndex);
// or program->getTargetMetadata(targetIndex);
```

Use `isParameterLocationUsed()` to detect parameters eliminated or optimized out during target compilation.

## Threading Rules

- Protect shared Slang sessions and object graphs unless the API explicitly documents reentrancy.
- Use separate global/session objects for concurrent front-end compilation when in doubt.
- Parallelize backend emission only when the installed Slang API documents that workflow; otherwise serialize.

## Reflection-Driven Binding

Use reflection to answer:
- Which global and entry-point parameters are active (including post-optimization via `IMetaData`)?
- Which descriptor set/binding or Metal slot/argument-buffer location is assigned?
- What is the layout/offset/stride of ordinary data?
- Which stages use each parameter?
- Which specialization parameters affect the target output?

Host integration rule:
- Treat reflection as source of truth; generate or validate C++ descriptor/argument-buffer metadata from it.
- Keep a checked-in reflection snapshot for offline-compiled shaders when runtime reflection is unavailable.

## Vulkan Backend Notes

- Generate SPIR-V and validate with project tools: `spirv-val`, `spirv-dis`, Vulkan validation layers.
- Descriptor sets/bindings should come from reflection or an explicit binding policy aligned with reflection.
- Gate SPIR-V-only features (pointers, descriptor handles, subgroups, ray tracing, mesh/task stages, specialization constants) with capabilities and runtime device feature checks.
- Global-scope parameters without explicit space may be wrapped in an implicit `ParameterBlock<>` — check reflection rather than assuming flat globals.
- For Y inversion or binding shifts, prefer documented build/session options over shader-source hacks.

## Metal Backend Notes

- Slang emits MSL; validate with Apple tooling (`metal`, Xcode, or runtime library compile).
- Metal uses independent binding spaces for buffers/textures/samplers and argument buffers — not Vulkan descriptor sets. Confirm generated MSL and reflection; do not assume 1:1 mapping.
- Metal shares binding slots across stages and has platform/version limitations.
- Arrays of buffers, bindless patterns, pointers, and SPIR-V-specific behavior may need fallbacks.
- Prefer readable generated MSL during development.

## Offline vs Runtime Compilation

**Offline preferred when:**
- shader variants are known at build time;
- startup latency matters;
- pipeline cache artifacts must be reproducible;
- generated SPIR-V/MSL needs code review or static validation.

**Runtime useful when:**
- user-authored shaders or material graphs generate Slang;
- specialization choices are unknown at build time;
- reflection drives runtime pipeline layout generation.
