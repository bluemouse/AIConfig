# Rendering, plugins, and OpenUSD ecosystem reference

## Table of contents

1. Ecosystem libraries used with Hydra 2.0
2. Hydra 2.0 application pipeline
3. Scene-index plugins
4. Renderer plugins and legacy bridge
5. UsdImaging scene-index chain
6. Hdx task-controller notes
7. Source files to inspect

## 1. Ecosystem libraries used with Hydra 2.0

Use these modules intentionally:

- `arch`: architecture-dependent/platform code, symbol visibility, multithreading, and low-level portability utilities.
- `tf`: foundation utilities such as `TfToken`, ref/weak pointers, diagnostics, runtime typing, registry initialization, debug flags, and plugin type metadata.
- `vt`: value containers, especially `VtValue` and `VtArray<T>`, used by Hydra sampled datasources.
- `sdf`: scene description foundations such as `SdfPath`, layers, prim specs, attribute specs, relationships, asset paths, and value type names.
- `plug`: plugin discovery and metadata through `plugInfo.json`, `PlugRegistry`, and `TfType` discovery.
- `hd`: core Hydra framework, including scene indices, datasources, schemas, renderers, renderer plugins, and scene-index plugins.
- `hdx`: Hydra extensions and tasks useful to applications, including task controllers and selection/render task support.
- `usdImaging` / `usdImagingGL`: USD stage to Hydra scene-index translation and GL engine entry points.

## 2. Hydra 2.0 application pipeline

A typical app integration should be described as a scene-index graph, not as a single monolithic delegate:

```text
source scene index
  -> app filters (selection, draw modes, overrides, custom attributes)
  -> renderer filters (capability adaptation, pruning, material filtering)
  -> terminal renderer observer
```

Hydra 2.0 replaces or wraps older concepts:

- `HdSceneDelegate` becomes scene indices.
- `UsdImagingDelegate` becomes a chain created by usd imaging scene-index APIs, starting from a stage scene index.
- `HdxTaskController` has a Hydra 2.0 analogue in `HdxTaskControllerSceneIndex`.
- `HdRenderDelegate` is replaced by `HdRenderer`; Hydra 1.0 render delegates can still be wrapped through compatibility adapters.

**Common app entry point:** `UsdImagingGLEngine` (`pxr/usdImaging/usdImagingGL/engine.h`) wires a USD stage, scene-index chain, renderer plugin, and task controller for interactive viewing. Inspect it when the user is building or debugging a USD viewport rather than a custom scene index from scratch.

When designing renderer-facing code, specify:

- where the terminal scene index comes from,
- which filters are app-owned versus renderer-owned,
- when plugins are inserted,
- what render settings/AOV/task controls still use legacy compatibility APIs,
- how updates are serialized to observer callbacks.

## 3. Scene-index plugins

Scene-index plugins insert filtering scene indices into a renderer/application pipeline through the plugin registry.

Use scene-index plugins for:

- renderer-specific pruning or adaptation,
- app-wide overlays such as selection, display mode, and visibility filters,
- capability-driven transformations such as expanding unsupported prim types,
- debug, validation, or instrumentation filters.

### C++ plugin surface

Subclass `HdSceneIndexPlugin` (`pxr/imaging/hd/sceneIndexPlugin.h`):

```cpp
class MySceneIndexPlugin : public HdSceneIndexPlugin {
protected:
    HdSceneIndexBaseRefPtr _AppendSceneIndex(
        const HdSceneIndexBaseRefPtr &inputScene,
        const HdContainerDataSourceHandle &inputArgs) override
    {
        return MyFilterSceneIndex::New(inputScene);
    }

    bool _IsEnabled(const HdContainerDataSourceHandle &inputArgs) const override {
        return true; // or gate on inputArgs / app settings
    }
};

TF_REGISTRY_FUNCTION(TfType) {
    HdSceneIndexPluginRegistry::Define<MySceneIndexPlugin>();
}
```

Public entry: `AppendSceneIndex(renderInstanceId, inputScene, inputArgs)` delegates to `_AppendSceneIndex`. Override only one of the two `_AppendSceneIndex` overloads.

### Registry registration

Register before render-index / renderer construction when using Hydra scene-index emulation:

```cpp
TF_REGISTRY_FUNCTION(HdSceneIndexPluginRegistry) {
    HdSceneIndexPluginRegistry::GetInstance()
        .RegisterSceneIndexForRenderer(
            /* rendererDisplayName */ "GL",
            /* sceneIndexPluginId */ TfToken("MySceneIndexPlugin"),
            /* inputArgs */ HdRetainedContainerDataSource::New(),
            HdSceneIndexPluginRegistry::InsertionPhase::PostFiltering,
            HdSceneIndexPluginRegistry::InsertionOrder::Default);
}
```

`RegisterSceneIndexForRenderer` parameters: renderer display name (empty string means all renderers), plugin typename token, `inputArgs` datasource passed to `_AppendSceneIndex`, insertion phase, and insertion order. Phases and JSON tag-based ordering can vary by branch — verify against `sceneIndexPluginRegistry.h`.

For app-owned filters without a `plugInfo.json` plugin, use `RegisterSceneIndexForRenderer` with a `SceneIndexAppendCallback` lambda instead of a plugin subclass.

### plugInfo.json metadata

Scene-index plugins also need a `plugInfo.json` entry (structure documented in `sceneIndexPlugin.h`): `bases: ["HdSceneIndexPlugin"]`, mandatory `loadWithRenderer`, optional `loadWithApps`, `tags`, and `ordering` constraints. Keep filter construction cheap; defer expensive traversal until needed.

## 4. Renderer plugins and legacy bridge

Hydra 2.0 renderer-side abstraction is `HdRenderer`, discovered through `HdRendererPlugin` and `HdRendererPluginRegistry`.

Renderer implementation tasks usually include:

- create or configure renderer plugin metadata,
- observe a terminal scene index,
- translate datasource changes into renderer-native resources,
- handle render settings/AOV/task controls through the current `HdRenderer` surface or the legacy control interface when required,
- report capabilities that influence upstream filters.

Legacy bridge concepts:

- `HdRenderDelegateAdapterRenderer` wraps a Hydra 1.0 render delegate as a Hydra 2.0 renderer.
- `HdSceneIndexAdapterSceneDelegate` exposes a scene index to legacy render delegates.
- `HdRenderIndexAdapterSceneIndex` can populate a scene index from legacy scene delegate machinery.
- `HdDirtyBitsTranslator` maps Hydra 1.0 dirty bits to Hydra 2.0 locator sets.

Use these only when the user is migrating or bridging. For new Hydra 2.0 code, design around scene indices and datasources first.

## 5. UsdImaging scene-index chain

For a USD stage source, start by looking at:

```text
pxr/usdImaging/usdImaging/stageSceneIndex.h
pxr/usdImaging/usdImaging/sceneIndices.h
pxr/usdImaging/usdImaging/sceneIndices.cpp
```

Important filters often present in the standard chain include instancing propagation, draw-mode replacement, selection overlays, root overrides, material binding resolution, and render setting flattening. Do not duplicate these behaviors in an app filter unless you know where it sits relative to the usd imaging chain.

When debugging a USD-to-Hydra issue:

1. Check if the authored USD data is present on the `UsdStage`.
2. Inspect the stage scene index output.
3. Inspect each downstream filtering scene index after the stage scene index.
4. Determine whether the renderer sees the expected terminal datasource layout.

## 6. Hdx task-controller notes

`Hdx` contains application-facing rendering tasks and task-controller utilities. In Hydra 2.0, prefer `HdxTaskControllerSceneIndex` when building scene-index-based application rendering pipelines. Legacy `HdxTaskController` remains relevant when the app is still using Hydra 1.0 task/delegate paths or compatibility mode.

When answering Hdx questions, verify:

- whether the user is using a Hydra 1.0 or 2.0 app pipeline,
- whether tasks are represented through scene-index prims or legacy task controller APIs,
- which render task collections and material tags are relevant,
- how free camera, selection, lighting, and render settings enter the scene-index graph.

## 7. Source files to inspect

Use this short map for ecosystem questions. For the full verification map, see [source-verification.md](source-verification.md).

```text
app entry:
  pxr/usdImaging/usdImagingGL/engine.h
  pxr/usdImaging/usdImagingGL/engine.cpp

scene index core + filters:
  pxr/imaging/hd/sceneIndex.h
  pxr/imaging/hd/filteringSceneIndex.h
  pxr/imaging/hd/retainedSceneIndex.h
  pxr/imaging/hd/dependencyForwardingSceneIndex.h

plugins and renderers:
  pxr/imaging/hd/sceneIndexPlugin.h
  pxr/imaging/hd/sceneIndexPluginRegistry.h
  pxr/imaging/hd/renderer.h
  pxr/imaging/hd/rendererPlugin.h

usd imaging + hdx:
  pxr/usdImaging/usdImaging/stageSceneIndex.h
  pxr/usdImaging/usdImaging/sceneIndices.h
  pxr/imaging/hdx/taskControllerSceneIndex.h
```
