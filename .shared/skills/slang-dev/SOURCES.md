# Sources

## Slang Language Reference (normative spec)

- **URL:** https://github.com/shader-slang/spec
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Hard Rules, grammar disputes
  - Authoritative language grammar when user guide and compiler disagree
- **Aspects extracted:**
  - Module/import declaration semantics → `references/language-grammar.md`
  - Declaration and visibility rules → `references/language-grammar.md`

## Slang User's Guide — Modules and Access Control

- **URL:** https://docs.shader-slang.org/en/latest/external/slang/docs/user-guide/04-modules-and-access-control.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Operating Principles, Hard Rules
  - `import` vs `__include`/`implementing`, access control defaults, legacy modules
- **Aspects extracted:**
  - Multi-file module structure, `internal` default visibility → `references/language-grammar.md`
  - Preprocessor isolation across modules → `references/language-grammar.md`, `references/toolchain-vulkan-metal-cpp.md`

## Slang User's Guide — Capabilities

- **URL:** https://docs.shader-slang.org/en/latest/external/slang/docs/user-guide/05-capabilities.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Hard Rules, Anti-patterns
  - Capability atoms, `[require]`, inference rules, target/stage exclusivity
- **Aspects extracted:**
  - Public vs internal capability declaration requirements → `references/language-grammar.md`
  - `__target_switch` / `__stage_switch` guidance → `references/language-grammar.md`, `references/workflow-debug-best-practices.md`

## Slang User's Guide — Compiling Code with Slang

- **URL:** https://docs.shader-slang.org/en/latest/external/slang/docs/user-guide/08-compiling.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Default Development Workflow, Gotchas
  - `slangc` flags, multi-target front-end/back-end split, precompiled modules
- **Aspects extracted:**
  - Command-line examples, stage inference limits → `references/toolchain-vulkan-metal-cpp.md`
  - No reflection from `slangc` → `references/toolchain-vulkan-metal-cpp.md`
  - `.slang-module` offline workflow → `references/toolchain-vulkan-metal-cpp.md`

## Slang User's Guide — Reflection API

- **URL:** https://docs.shader-slang.org/en/latest/external/slang/docs/user-guide/09-reflection.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Operating Principles, Reflection-first binding
  - `ProgramLayout`, `VariableLayoutReflection`, `ParameterBlock<>` layout model
- **Aspects extracted:**
  - `getLayout(targetIndex)` lifecycle → `references/toolchain-vulkan-metal-cpp.md`
  - Implicit constant buffers in parameter blocks → `references/language-grammar.md`, `references/toolchain-vulkan-metal-cpp.md`

## Slang Compilation API

- **URL:** https://docs.shader-slang.org/en/latest/compilation-api.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Workflow Decision Tree (C++ API path)
  - `IGlobalSession`, `ISession`, entry-point discovery, post-compile `IMetaData`
- **Aspects extracted:**
  - API object lifetime and entry-point lookup rules → `references/toolchain-vulkan-metal-cpp.md`
  - `getEntryPointMetadata` / `isParameterLocationUsed` → `references/toolchain-vulkan-metal-cpp.md`, `references/workflow-debug-best-practices.md`

## Using Slang Parameter Blocks

- **URL:** https://docs.shader-slang.org/en/latest/parameter-blocks.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Gotchas (binding 0 uniform buffer)
  - Descriptor set / argument buffer grouping by update frequency
- **Aspects extracted:**
  - Auto-introduced uniform buffer at binding 0 → `references/language-grammar.md`
  - Nested blocks and CPU/CUDA flattening behavior → `references/language-grammar.md`

## SPIR-V-Specific Functionalities (Slang user guide appendix)

- **URL:** https://docs.shader-slang.org/en/latest/external/slang/docs/user-guide/a2-01-spirv-target-specific.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Gotchas (push constants, struct layout)
  - Vulkan-specific ParameterBlock and uniform mapping
- **Aspects extracted:**
  - Push constant vs default constant buffer rules → `references/language-grammar.md`
  - C/C++ layout for buffers and pointers on SPIR-V → `references/language-grammar.md`

## Slang language reference — declarations (compiler repo)

- **URL:** https://github.com/shader-slang/slang/blob/master/docs/language-reference/declarations.md
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `import` module resolution, `__exported import` (experimental)
  - Mixing `import` and `#include` hazards
- **Aspects extracted:**
  - Three-way modularity guidance → `references/language-grammar.md`, `SKILL.md`

## Source weighting

When sources disagree: (1) normative spec and compiler diagnostics for grammar; (2) user guide and compilation API for workflows and reflection; (3) SPIR-V/ParameterBlock appendices for backend layout; (4) project-specific binding policy only after reflection validation.

## Refresh Workflow

1. Re-read the upstream sources above (spec repo, user-guide chapters, parameter-blocks doc, compilation/reflection API)
2. Diff against the prior pull (or scan for newly added sections / API revisions)
3. For each changed area, update the corresponding `references/<topic>.md` and `SKILL.md` routing if needed
4. Bump **Last reviewed** date above
