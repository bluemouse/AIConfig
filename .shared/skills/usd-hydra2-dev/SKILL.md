---
name: usd-hydra2-dev
description: "Source-grounded OpenUSD Hydra 2.0 development guidance for scene indices, data sources, schema authoring, filtering scene indices, dependency forwarding, retained scene indices, Hydra renderer and scene-index plugin integration, Hdx task-controller use, USD imaging pipelines, materials, transparency, instancing, dirty propagation, code review, API migration from Hydra 1.0, and compile-ready C++ snippets. Use when implementing, reviewing, debugging, designing, or documenting rendering functionality with OpenUSD Hydra 2.0, Hd, Hdx, USD imaging, plugInfo.json plugins, or Hydra renderer pipelines — even if the user does not say 'Hydra 2.0'. For API-agnostic renderer architecture (render graph, frames-in-flight, binding model), use gpu-rendering-guide. For Vulkan implementation details, use vulkan-dev."
---

# USD Hydra 2.0 Development

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Source-grounded coding assistant for OpenUSD Hydra 2.0. Default output: implementation plans, API-correct C++ snippets, review findings, dirtying rules, and source files to inspect next.

For API-agnostic renderer architecture (render graph, frames-in-flight, binding model, GPU memory strategy), use [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md). For concrete `Vk*` implementation work, use [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md).

## When to Use

- Implementing or reviewing `HdSceneIndexBase`, filtering scene indices, datasources, schemas, or dirty propagation
- Authoring mesh/material/instancer prim data for Hydra 2.0 consumers
- Integrating `HdRenderer`, scene-index plugins, USD imaging chains, or `HdxTaskControllerSceneIndex`
- Debugging transparency, material bindings, opacity, or Storm material-tag behavior
- Migrating from Hydra 1.0 (`HdRenderDelegate`, `HdSceneDelegate`) with compatibility adapters

## When NOT to Use

- API-agnostic renderer architecture without Hydra/OpenUSD APIs — [`../gpu-rendering-guide/SKILL.md`](../gpu-rendering-guide/SKILL.md)
- Vulkan/D3D12/Metal/WebGPU implementation — [`../vulkan-dev/SKILL.md`](../vulkan-dev/SKILL.md) or the matching API skill
- Raw USD stage authoring, composition, or schema design without Hydra scene-index consumption — USD docs and app-specific USD skills
- CMake/build wiring for OpenUSD — project build docs; this skill covers Hydra C++ APIs and scene-index graphs

## Operating standard

1. Prefer source verification over memory. For compile-ready code, verify class names, token names, signatures, and includes against the user's OpenUSD checkout when available. Otherwise verify against official OpenUSD docs and the matching GitHub branch.
2. Do not invent Hydra APIs. If a symbol cannot be verified, call it out and provide pseudocode or a verification checklist instead of compile-ready code.
3. Separate Hydra 2.0 scene-index work from Hydra 1.0 render-delegate work. Use legacy `HdRenderDelegate`, `HdSceneDelegate`, and `HdRenderIndex` only for compatibility or emulation.
4. Preserve incremental correctness. Every mutation path must explain the corresponding `PrimsAdded`, `PrimsRemoved`, `PrimsDirtied`, or `PrimsRenamed` notice and the locator set downstream consumers must repull.
5. Keep resource use proportional. For simple questions, answer from `SKILL.md` and one reference file. For code generation or review, load the relevant reference and run `scripts/hydra2_lint.py` when feasible.

## Workflow

1. Identify the task category:
   - scene-index producer, filter, or graph composition: [references/hydra2-core.md](references/hydra2-core.md)
   - mutable/runtime scene authoring: [references/hydra2-core.md](references/hydra2-core.md) (`HdRetainedSceneIndex`)
   - cross-prim dirty propagation: [references/hydra2-core.md](references/hydra2-core.md) (`HdDependencyForwardingSceneIndex`)
   - schema authoring, meshes, primvars, materials, instancing: [references/schemas-and-authoring.md](references/schemas-and-authoring.md)
   - renderer/app/plugin integration, `plugInfo.json`, `HdRenderer`, `HdxTaskControllerSceneIndex`, USD imaging: [references/rendering-plugins-and-usd-ecosystem.md](references/rendering-plugins-and-usd-ecosystem.md)
   - transparency, material opacity, alpha cutouts, Storm behavior: [references/transparency-materials.md](references/transparency-materials.md)
   - examples or starter code: [references/examples.md](references/examples.md)
   - compile-ready code, code review, or suspected hallucinated APIs: [references/source-verification.md](references/source-verification.md) and run [scripts/hydra2_lint.py](scripts/hydra2_lint.py)
2. Ask for the OpenUSD version or checkout path only when the answer depends on branch-specific APIs and the user has not provided enough context.
3. For design answers, produce a scene-index graph, data-source layout, dirtying plan, and API/source map.
4. For code answers, include only verified includes and symbols. Explain which containers and locators are authored and which notices must be emitted after runtime changes.
5. For reviews, prioritize: nonexistent APIs, invalid schema tokens, wrong datasource ownership/type, missing or overbroad dirtying, thread-safety violations, inconsistent `GetPrim`/`GetChildPrimPaths`, and unnecessary eager computation.

## Core mental model

Hydra 2.0 scene data is pulled. A scene index returns `HdSceneIndexPrim { primType, dataSource }` for a path and child paths for traversal. The prim's `dataSource` is a hierarchy of `HdDataSourceBase` objects, usually interpreted by generated `HdSchema` wrappers. Changes are pushed only as invalidation notices; consumers repull requested data.

A correct implementation needs all four pieces:

- a stable `SdfPath` tree (`GetChildPrimPaths` agrees with `GetPrim`),
- canonical prim types and schema tokens,
- thread-safe pull methods and datasource access,
- precise enough `HdDataSourceLocatorSet` dirtying.

## Common answer templates

Implementation plan:

```text
scene-index graph:
  app/source -> filtering scene index(es) -> renderer/plugin terminal scene index

prim/data layout:
  /Prim type=<hd prim type>
    schema/member = datasource type and value shape

runtime updates:
  change -> notice -> locator(s) -> expected repull

source files to verify:
  pxr/imaging/hd/...
```

C++ snippets:

```text
verified against: <branch/version or docs/source basis>
requires: <headers and libraries>
notes: <what is compile-ready vs pseudocode>
```

## Bundled resources

- [references/hydra2-core.md](references/hydra2-core.md): scene indices, observers, datasources, locators, filtering, retained scenes, dependency forwarding, dirtying, thread-safety
- [references/schemas-and-authoring.md](references/schemas-and-authoring.md): schema-token rules, mesh/primvar/material/instancing layouts, authoring practices
- [references/rendering-plugins-and-usd-ecosystem.md](references/rendering-plugins-and-usd-ecosystem.md): ecosystem libraries, plugin registry, renderer/app integration, USD imaging, Hdx
- [references/transparency-materials.md](references/transparency-materials.md): Storm transparency, `displayOpacity`, material opacity, cutouts, dirtying
- [references/examples.md](references/examples.md): source-checked patterns for scene indices, filters, retained scenes, dirtying helpers, material binding
- [references/source-verification.md](references/source-verification.md): full source map, official docs links, verification checklist
- [SOURCES.md](SOURCES.md): provenance and refresh workflow for this skill
- [scripts/hydra2_lint.py](scripts/hydra2_lint.py): lightweight static checks for common AI-generated Hydra 2.0 mistakes
