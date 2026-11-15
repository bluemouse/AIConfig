# Source verification reference

## Table of contents

1. Required verification behavior
2. Official docs and source URLs
3. Source map
4. API checks before code generation
5. Common false APIs and traps
6. Review prompt pattern

## 1. Required verification behavior

For compile-ready Hydra 2.0 code, verify against source in this order:

1. User-provided local OpenUSD checkout or vendored source.
2. The user's stated OpenUSD version/branch.
3. Official OpenUSD dev API docs and the corresponding OpenUSD GitHub branch.
4. If none is available, mark code as pseudocode or version-sensitive.

Never present a class, function, token, schema member, or plugin metadata field as real unless it is verified in headers/docs/source.

## 2. Official docs and source URLs

Official docs requested for this skill:

```text
https://openusd.org/dev/api/_page__hydra__getting__started__guide.html
https://openusd.org/dev/api/arch_page_front.html
https://openusd.org/dev/api/plug_page_front.html
https://openusd.org/dev/api/tf_page_front.html
https://openusd.org/dev/api/vt_page_front.html
https://openusd.org/dev/api/sdf_page_front.html
https://openusd.org/dev/api/hd_page_front.html
https://openusd.org/dev/api/hdx_page_front.html
```

Source repository:

```text
https://github.com/PixarAnimationStudios/OpenUSD
```

When browsing source, prefer branch/version-specific URLs. The default branch may move and OpenUSD dev APIs can change.

## 3. Source map

Inspect these files for exact signatures:

```text
core scene index:
  pxr/imaging/hd/sceneIndex.h
  pxr/imaging/hd/sceneIndex.cpp
  pxr/imaging/hd/sceneIndexObserver.h
  pxr/imaging/hd/sceneIndexObserver.cpp

datasource and locators:
  pxr/imaging/hd/dataSource.h
  pxr/imaging/hd/dataSource.cpp
  pxr/imaging/hd/dataSourceTypeDefs.h
  pxr/imaging/hd/dataSourceLocator.h
  pxr/imaging/hd/dataSourceLocator.cpp
  pxr/imaging/hd/retainedDataSource.h
  pxr/imaging/hd/retainedDataSource.cpp
  pxr/imaging/hd/overlayContainerDataSource.h
  pxr/imaging/hd/containerDataSourceEditor.h

mutable and dependency scene indices:
  pxr/imaging/hd/retainedSceneIndex.h
  pxr/imaging/hd/retainedSceneIndex.cpp
  pxr/imaging/hd/dependencyForwardingSceneIndex.h
  pxr/imaging/hd/dependencyForwardingSceneIndex.cpp
  pxr/imaging/hd/dependencySchema.h

filters and scene-index graph:
  pxr/imaging/hd/filteringSceneIndex.h
  pxr/imaging/hd/filteringSceneIndex.cpp
  pxr/imaging/hd/mergingSceneIndex.h
  pxr/imaging/hd/prefixingSceneIndex.h
  pxr/imaging/hd/flatteningSceneIndex.h
  pxr/imaging/hd/cachingSceneIndex.h
  pxr/imaging/hd/noticeBatchingSceneIndex.h

schemas:
  pxr/imaging/hd/schema.h
  pxr/imaging/hd/*Schema.h
  pxr/imaging/hd/tokens.h
  pxr/imaging/hd/tokens.cpp

materials/transparency/storm:
  pxr/imaging/hd/materialSchema.h
  pxr/imaging/hd/materialNetworkSchema.h
  pxr/imaging/hd/materialNodeSchema.h
  pxr/imaging/hd/materialNodeParameterSchema.h
  pxr/imaging/hd/materialConnectionSchema.h
  pxr/imaging/hd/materialBindingsSchema.h
  pxr/imaging/hd/materialBindingSchema.h
  pxr/imaging/hdSt/materialNetwork.cpp
  pxr/imaging/hdSt/primUtils.cpp
  pxr/imaging/hdSt/tokens.h
  pxr/imaging/hdx/oitRenderTask.cpp
  pxr/imaging/hdx/oitResolveTask.cpp

instancing:
  pxr/imaging/hd/instancerTopologySchema.h
  pxr/imaging/hd/instancer.h
  pxr/imaging/hd/instancer.cpp

plugins/renderers:
  pxr/imaging/hd/sceneIndexPlugin.h
  pxr/imaging/hd/sceneIndexPluginRegistry.h
  pxr/imaging/hd/renderer.h
  pxr/imaging/hd/rendererPlugin.h
  pxr/imaging/hd/rendererPluginRegistry.h
  pxr/imaging/hd/legacyRenderControlInterface.h
  pxr/imaging/hd/renderDelegateAdapterRenderer.h
  pxr/imaging/hd/sceneIndexAdapterSceneDelegate.h
  pxr/imaging/hd/renderIndexAdapterSceneIndex.h
  pxr/imaging/hd/dirtyBitsTranslator.h

usd imaging, gl engine, and hdx:
  pxr/usdImaging/usdImaging/stageSceneIndex.h
  pxr/usdImaging/usdImaging/sceneIndices.h
  pxr/usdImaging/usdImaging/primAdapter.h
  pxr/usdImaging/usdImaging/apiSchemaAdapter.h
  pxr/usdImaging/usdImagingGL/engine.h
  pxr/imaging/hdx/taskControllerSceneIndex.h
```

## 4. API checks before code generation

Before returning C++ snippets, check:

- All headers match classes used.
- Every `::New(...)` call is on a concrete class.
- Generated schema `BuildRetained(...)` parameter order matches the target source.
- Token sets exist and names match source.
- `HdPrimTypeTokens` contains the prim type used.
- Locator helper names exist on the schema. If a helper is not verified, construct locators from schema tokens instead and label as version-sensitive.
- `HdSingleInputFilteringSceneIndexBase` hooks match exact signatures.
- Plugin methods and `plugInfo.json` metadata match target source.
- `HdMaterialSchemaTokens->universalRenderContext` is the empty token `""`.

## 5. Common false APIs and traps

<!-- hydra2-lint: ignore-start -->

Documented traps (intentional warnings, not code to copy):

- `HdTokenDataSource::New(...)`: usually wrong because this is commonly an abstract typed datasource alias. Use `HdRetainedTypedSampledDataSource<TfToken>::New(...)` unless source proves otherwise.
- `HdDataSourceSentinelTokens->container`: legacy name in some comments; use `HdDataSourceLocatorSentinelTokens->container`.
- Dirtying only a leaf after replacing a parent container: insufficient if downstream cached the parent handle. Use editor-computed dirty locators.
- Treating `PrimsDirtied` as hierarchical on prim path: wrong. It is hierarchical on locators, not on prim paths.
- Assuming `displayOpacity` means true blending in Storm: version/renderer-specific; material opacity is the safer path for semitransparency.
- Mixing Hydra 1.0 dirty bits with Hydra 2.0 locators without `HdDirtyBitsTranslator` or compatibility context.

<!-- hydra2-lint: ignore-end -->

## 6. Review prompt pattern

For code review, use this structure:

```text
correctness findings:
  1. <issue> - <source/API basis> - <fix>

missing dirtying:
  - change: <state mutation>
  - expected notice: <notice>
  - locator: <locator set>

thread-safety:
  - pull path:
  - mutation path:

source files to inspect next:
  - <file>
```
