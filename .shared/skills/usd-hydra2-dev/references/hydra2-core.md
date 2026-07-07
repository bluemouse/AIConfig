# Hydra 2.0 core reference

## Table of contents

1. Scene-index contract
2. Observer notices
3. Datasource taxonomy
4. Locators and dirtying
5. Filtering scene indices
6. Mutable authoring (`HdRetainedSceneIndex`)
7. Dependency forwarding
8. Scene-index graph composition
9. Thread-safety rules
10. Correctness checklist

## 1. Scene-index contract

`HdSceneIndexBase` is the central Hydra 2.0 scene abstraction.

Core virtuals:

```cpp
virtual HdSceneIndexPrim GetPrim(const SdfPath &primPath) const = 0;
virtual SdfPathVector GetChildPrimPaths(const SdfPath &primPath) const = 0;
```

`HdSceneIndexPrim` is a pair:

```cpp
struct HdSceneIndexPrim {
    TfToken primType;
    HdContainerDataSourceHandle dataSource;
};
```

Key invariants:

- A prim exists at a path when `dataSource` is non-null. The `primType` may be empty for scope-like structural prims.
- Except for the absolute root path, `GetPrim(path)` existence must agree with membership in `GetChildPrimPaths(path.GetParentPath())`.
- Traversal from `SdfPath::AbsoluteRootPath()` must produce the same logical set of prims as applying add/remove notices over time.
- Return `{TfToken(), nullptr}` for a nonexistent prim.

Practical authoring patterns:

- Use immutable retained datasources for static data.
- Publish shared retained mesh/material containers once and overlay per-prim deltas with `HdOverlayContainerDataSource`.
- Keep path generation deterministic. Map external ids to stable `SdfPath` values early and centralize escaping/sanitization.

## 2. Observer notices

Scene indices notify downstream observers via protected helpers:

```cpp
_SendPrimsAdded(entries);
_SendPrimsRemoved(entries);
_SendPrimsDirtied(entries);
_SendPrimsRenamed(entries);
```

Notice semantics:

- `PrimsAdded`: path and prim type. If the path already exists, observers treat this as a resync and refetch all data. Use this when the prim type changes or a structural schema membership change cannot be represented safely as dirty locators.
- `PrimsRemoved`: path is a subtree root. Removing `/A` removes `/A` and all descendants.
- `PrimsDirtied`: path is not hierarchical, but locators are hierarchical. Dirtying `/A` does not dirty `/A/B`; dirtying `primvars` on `/A` also dirties `primvars/displayColor` on `/A`.
- `PrimsRenamed`: old and new paths are subtree roots. Use only when the subtree identity is preserved enough for downstream optimization; remove+add is always simpler.

For `HdSingleInputFilteringSceneIndexBase`, `_PrimsRenamed` has a default implementation that converts rename notices into remove+add and then calls your `_PrimsRemoved` / `_PrimsAdded` overrides. Simple pass-through filters therefore do not need a rename override unless they preserve rename semantics explicitly.

## 3. Datasource taxonomy

Hydra prim data is a tree of datasource handles.

- `HdDataSourceBase`: abstract base.
- `HdContainerDataSource`: named children; use for schema containers and nested records.
- `HdVectorDataSource`: indexed list of datasource elements; use for arrays of datasource records, not for regular numeric arrays.
- `HdSampledDataSource`: value over time; `GetValue(shutterOffset)` returns a `VtValue`.
- `HdTypedSampledDataSource<T>`: typed sampled datasource interface.
- `HdRetainedTypedSampledDataSource<T>`: concrete constant sampled datasource; use `::New(value)` for immutable authored values.
- `HdRetainedContainerDataSource`: concrete retained container; use `::New(token0, child0, token1, child1, ...)` or empty `::New()`.
- `HdBlockDataSource`: explicit block/absence opinion for composition.

Important distinction:

<!-- hydra2-lint: ignore-start -->
Many names in `dataSourceTypeDefs.h`, such as `HdTokenDataSource`, `HdIntArrayDataSource`, or `HdMatrixDataSource`, are aliases for abstract typed sampled datasource interfaces. Do not write `HdTokenDataSource::New(...)` unless source proves that concrete class exists.
<!-- hydra2-lint: ignore-end -->

Prefer:

```cpp
HdRetainedTypedSampledDataSource<TfToken>::New(HdTokens->rightHanded);
HdRetainedTypedSampledDataSource<VtArray<GfVec3f>>::New(points);
```

## 4. Locators and dirtying

`HdDataSourceLocator` addresses nested datasource fields by token path. Example:

```cpp
HdDataSourceLocator(HdPrimvarsSchemaTokens->primvars, HdTokens->displayColor)
```

`HdDataSourceLocatorSet` is closed under descendancy. If the set contains `primvars`, it implicitly contains `primvars/points`, `primvars/displayColor`, and all other children.

Dirtying guidance:

- Prefer schema locator helpers such as `HdMeshSchema::GetTopologyLocator()` when available.
- Dirty the smallest locator that fully covers what changed.
- Reserve the universal locator set (`HdDataSourceLocatorSet` resync helper) only when the whole prim must be repulled; avoid broad invalidation for routine value edits.
- Adding/removing a primvar, material binding purpose, topology membership, or any schema child name often changes `GetNames()` membership. If a consumer may need to re-enumerate a container, dirty the parent container or resync the prim.

Container replacement trap:

`HdContainerDataSourceEditor::Finish()` returns a new composed container handle. Downstream caches that hold handles at intermediate container levels must be invalidated. When using the editor for set/overlay operations, compute dirty locators with:

```cpp
HdContainerDataSourceEditor::ComputeDirtyLocators(locatorSet)
```

Use the public sentinel token set `HdDataSourceLocatorSentinelTokens->container`, not the legacy name `HdDataSourceSentinelTokens` shown in some older header comments.

## 5. Filtering scene indices

Use `HdSingleInputFilteringSceneIndexBase` for the common case of one input scene index.

Implementation pattern:

```cpp
class MyFilter final : public HdSingleInputFilteringSceneIndexBase {
public:
    static HdSceneIndexBaseRefPtr New(const HdSceneIndexBaseRefPtr &input) {
        return TfCreateRefPtr(new MyFilter(input));
    }

    HdSceneIndexPrim GetPrim(const SdfPath &path) const override {
        HdSceneIndexPrim prim = _GetInputSceneIndex()->GetPrim(path);
        // Return prim unchanged, overlay datasource fields, or block fields.
        return prim;
    }

    SdfPathVector GetChildPrimPaths(const SdfPath &path) const override {
        return _GetInputSceneIndex()->GetChildPrimPaths(path);
    }

protected:
    explicit MyFilter(const HdSceneIndexBaseRefPtr &input)
        : HdSingleInputFilteringSceneIndexBase(input) {}

    void _PrimsAdded(const HdSceneIndexBase &, const HdSceneIndexObserver::AddedPrimEntries &e) override {
        _SendPrimsAdded(e);
    }
    void _PrimsRemoved(const HdSceneIndexBase &, const HdSceneIndexObserver::RemovedPrimEntries &e) override {
        _SendPrimsRemoved(e);
    }
    void _PrimsDirtied(const HdSceneIndexBase &, const HdSceneIndexObserver::DirtiedPrimEntries &e) override {
        _SendPrimsDirtied(e);
    }
    // _PrimsRenamed: optional; base converts rename -> remove+add then calls the hooks above
};
```

Filter notification rules:

- If `GetPrim` transforms data lazily, upstream dirties must usually be forwarded or augmented so downstream repulls the transformed result.
- If a filter output depends on an upstream field not equal to the output field, translate dirty locators. Example: if output `primvars/displayColor` is derived from an upstream material parameter, dirty `primvars/displayColor` when that material parameter changes.
- If a filter adds/removes prims, it must maintain child path traversal and added/removed notices for its output scene, not just pass through upstream notices.

## 6. Mutable authoring (`HdRetainedSceneIndex`)

For runtime-populated scenes (tests, procedural generators, editor overlays), prefer `HdRetainedSceneIndex` over hand-rolling notice emission.

Key API (`pxr/imaging/hd/retainedSceneIndex.h`):

```cpp
HdRetainedSceneIndexRefPtr scene = HdRetainedSceneIndex::New();

scene->AddPrims({
    { SdfPath("/World"), TfToken(), HdRetainedContainerDataSource::New() },
    { SdfPath("/World/Mesh"), HdPrimTypeTokens->mesh, meshDataSource }
});

scene->DirtyPrims({
    { SdfPath("/World/Mesh"),
      HdDataSourceLocatorSet{ HdMeshSchema::GetTopologyLocator() } }
});

scene->RemovePrims({ SdfPath("/World/Mesh") });
```

Rules:

- `AddPrims` owns the provided datasources and emits `PrimsAdded` when applicable.
- `DirtyPrims` does not mutate retained data itself; it emits `PrimsDirtied` for downstream repull. Subclasses may override to invalidate internal caches.
- `RemovePrims` emits hierarchical `PrimsRemoved`.
- After `AddPrims`, new observers are not back-filled; callers must sync observer state separately.

Use a custom `HdSceneIndexBase` subclass when you need lazy computation, cross-prim derivation, or filter-like transformation without retaining a full scene table.

## 7. Dependency forwarding

When prim A's displayed data depends on prim B's data, dirtying B must also dirty A. Author dependencies with `HdDependencySchema` and insert `HdDependencyForwardingSceneIndex` into the graph.

Typical pattern:

```cpp
HdRetainedSceneIndexRefPtr source = HdRetainedSceneIndex::New();
source->AddPrims({ /* mesh + material prims */ });

HdSceneIndexBaseRefPtr withDeps =
    HdDependencyForwardingSceneIndex::New(source);
```

On the depended-on prim, author a dependency record naming the affected prim and the locator mapping:

```cpp
HdDependencySchema::Builder()
    .SetDependedOnPrimPath(HdRetainedTypedSampledDataSource<SdfPath>::New(meshPath))
    .SetDependedOnDataSourceLocator(
        HdRetainedTypedSampledDataSource<HdDataSourceLocator>::New(
            HdMaterialSchema::GetDefaultLocator()))
    .SetAffectedDataSourceLocator(
        HdRetainedTypedSampledDataSource<HdDataSourceLocator>::New(
            HdMaterialBindingsSchema::GetDefaultLocator()))
    .Build()
```

`HdDependencyForwardingSceneIndex` observes upstream dirties, consults dependency schemas, and emits additional `PrimsDirtied` notices on affected prims. Inspect `pxr/imaging/hd/dependencyForwardingSceneIndex.h` and `testHdSceneIndex.cpp` dependency tests before returning compile-ready dependency wiring.

## 8. Scene-index graph composition

Common built-in scene indices beyond filters:

| Class | Role |
| --- | --- |
| `HdMergingSceneIndex` | Overlay multiple input scenes; stronger opinions win per path |
| `HdPrefixingSceneIndex` | Prefix all paths (namespace isolation) |
| `HdFlatteningSceneIndex` | Flatten nested containers for consumers expecting a flat layout |
| `HdCachingSceneIndex` | Cache `GetPrim` results; requires correct dirty forwarding |
| `HdNoticeBatchingSceneIndex` | Coalesce notices for performance |
| `HdDependencyForwardingSceneIndex` | Propagate dirties across authored dependencies |

`HdEncapsulatingSceneIndexBase` marks scene indices that build internal subgraphs. Use it when tooling needs to display nested scene-index topology.

Typical app graph:

```text
UsdStage -> UsdImagingStageSceneIndex
  -> usdImaging filters (instancing, draw mode, materials, ...)
  -> app filters (selection, overrides)
  -> HdDependencyForwardingSceneIndex (optional)
  -> renderer terminal observer
```

## 9. Thread-safety rules

Hydra pull APIs are expected to be thread-safe:

- `HdSceneIndexBase::GetPrim`
- `HdSceneIndexBase::GetChildPrimPaths`
- `HdContainerDataSource::GetNames` and `Get`
- `HdVectorDataSource::GetNumElements` and `GetElement`
- `HdSampledDataSource::GetValue` and sample-time discovery

Notice dispatch and observer callbacks are not expected to be thread-safe. Send `_SendPrims*` from a single agreed thread or serialize notice emission. `AddObserver` and `RemoveObserver` are also not thread-safe.

Cache safely:

- Immutable retained handles published once are preferred.
- Mutable caches used by `GetPrim` must use locks, atomics, copy-on-write snapshots, or another safe publication scheme.
- Do not hold a mutex while calling observer callbacks or upstream scene-index APIs unless the code is proven reentrancy-safe.

## 10. Correctness checklist

Before returning or approving code, check:

- `GetPrim` and `GetChildPrimPaths` agree for every authored path.
- All schema container tokens come from generated schema token sets or `HdTokens`.
- Concrete retained datasource classes are used for `::New(...)` values.
- `GetPrim` and datasource methods can run concurrently.
- Mutations emit notices after state publication.
- Dirty locators match the data changed and include container identity dirtying if container handles were replaced.
- Filtering scene indices translate or augment upstream dirties for derived outputs.
- Cross-prim dependencies use `HdDependencySchema` + forwarding scene index when needed.
- Legacy Hydra 1.0 APIs are isolated to compatibility/adaptation code.
