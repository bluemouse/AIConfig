# Hydra 2.0 examples and patterns

These examples are intentionally compact. Before using them as compile-ready code, verify generated schema signatures against the target OpenUSD branch.

## 1. Minimal scene index shape

```cpp
#include "pxr/pxr.h"
#include "pxr/base/tf/token.h"
#include "pxr/usd/sdf/path.h"
#include "pxr/imaging/hd/sceneIndex.h"
#include "pxr/imaging/hd/retainedDataSource.h"
#include "pxr/imaging/hd/tokens.h"

PXR_NAMESPACE_OPEN_SCOPE

class MinimalSceneIndex final : public HdSceneIndexBase
{
public:
    HdSceneIndexPrim GetPrim(const SdfPath &primPath) const override
    {
        if (primPath == SdfPath("/World")) {
            return { TfToken(), HdRetainedContainerDataSource::New() };
        }
        if (primPath == SdfPath("/World/EmptyMesh")) {
            return { HdPrimTypeTokens->mesh, HdRetainedContainerDataSource::New() };
        }
        return { TfToken(), nullptr };
    }

    SdfPathVector GetChildPrimPaths(const SdfPath &primPath) const override
    {
        if (primPath == SdfPath::AbsoluteRootPath()) {
            return { SdfPath("/World") };
        }
        if (primPath == SdfPath("/World")) {
            return { SdfPath("/World/EmptyMesh") };
        }
        return {};
    }
};

PXR_NAMESPACE_CLOSE_SCOPE
```

This is a structural example only. A real mesh needs mesh topology and `points` primvar data.

## 2. Retained scene index for runtime updates

```cpp
#include "pxr/imaging/hd/retainedSceneIndex.h"
#include "pxr/imaging/hd/meshSchema.h"

HdRetainedSceneIndexRefPtr scene = HdRetainedSceneIndex::New();

scene->AddPrims({
    { SdfPath("/World"), TfToken(), HdRetainedContainerDataSource::New() },
    { SdfPath("/World/Mesh"), HdPrimTypeTokens->mesh, BuildMeshDataSource() }
});

scene->DirtyPrims({
    { SdfPath("/World/Mesh"),
      HdDataSourceLocatorSet{ HdMeshSchema::GetTopologyLocator() } }
});
```

Use `HdRetainedSceneIndex` when you own the scene table and want built-in notice emission. Pair with immutable retained child datasources when possible.

## 3. Mesh datasource pattern

```cpp
HdRetainedContainerDataSource::New(
    HdMeshSchemaTokens->mesh,
    HdMeshSchema::BuildRetained(
        HdMeshTopologySchema::BuildRetained(
            HdRetainedTypedSampledDataSource<VtArray<int>>::New(faceVertexCounts),
            HdRetainedTypedSampledDataSource<VtArray<int>>::New(faceVertexIndices),
            nullptr,
            HdRetainedTypedSampledDataSource<TfToken>::New(HdTokens->rightHanded)),
        HdRetainedTypedSampledDataSource<TfToken>::New(PxOsdOpenSubdivTokens->none),
        nullptr,
        HdRetainedTypedSampledDataSource<bool>::New(true)),
    HdPrimvarsSchemaTokens->primvars,
    HdRetainedContainerDataSource::New(
        HdTokens->points,
        HdPrimvarSchema::BuildRetained(
            HdRetainedTypedSampledDataSource<VtArray<GfVec3f>>::New(points),
            nullptr,
            nullptr,
            HdPrimvarSchema::BuildInterpolationDataSource(HdPrimvarSchemaTokens->vertex),
            HdPrimvarSchema::BuildRoleDataSource(HdPrimvarSchemaTokens->point),
            nullptr,
            nullptr)))
```

Required headers usually include:

```cpp
#include "pxr/base/gf/vec3f.h"
#include "pxr/base/vt/array.h"
#include "pxr/imaging/hd/meshSchema.h"
#include "pxr/imaging/hd/meshTopologySchema.h"
#include "pxr/imaging/hd/primvarSchema.h"
#include "pxr/imaging/hd/primvarsSchema.h"
#include "pxr/imaging/hd/retainedDataSource.h"
#include "pxr/imaging/hd/tokens.h"
#include "pxr/imaging/pxOsd/tokens.h"
```

## 4. Overlaying a derived displayColor in a filter

```cpp
HdSceneIndexPrim GetPrim(const SdfPath &primPath) const override
{
    HdSceneIndexPrim prim = _GetInputSceneIndex()->GetPrim(primPath);

    if (HdPrimTypeIsGprim(prim.primType) && prim.dataSource) {
        HdContainerDataSourceEditor editor(prim.dataSource);
        editor.Set(
            HdDataSourceLocator(HdPrimvarsSchemaTokens->primvars, HdTokens->displayColor),
            HdPrimvarSchema::BuildRetained(
                HdRetainedTypedSampledDataSource<GfVec3f>::New(GfVec3f(0.0f, 1.0f, 0.0f)),
                nullptr,
                nullptr,
                HdPrimvarSchema::BuildInterpolationDataSource(HdPrimvarSchemaTokens->constant),
                HdPrimvarSchema::BuildRoleDataSource(HdPrimvarSchemaTokens->color),
                nullptr,
                nullptr));
        prim.dataSource = editor.Finish();
    }

    return prim;
}
```

For runtime changes in the data that drives this overlay, dirty the output `primvars/displayColor` locator. If the editor is used to create replacement containers, use `HdContainerDataSourceEditor::ComputeDirtyLocators` for exact container dirtying.

## 5. Dirty locator helper for editor operations

```cpp
static HdDataSourceLocatorSet
ComputeDirtyingForEditedLocator(const HdDataSourceLocator &locator)
{
    const HdDataSourceLocatorSet authoredLocators(locator);
    return HdContainerDataSourceEditor::ComputeDirtyLocators(authoredLocators);
}
```

Use this when `HdContainerDataSourceEditor::Finish()` replaces container handles and downstream caches must refetch intermediate containers.

## 6. Shared retained datasource pattern

```cpp
static HdContainerDataSourceHandle GetSharedMeshDataSource()
{
    static const HdContainerDataSourceHandle meshDs = BuildMeshDataSourceOnce();
    return meshDs;
}

HdSceneIndexPrim GetPrim(const SdfPath &path) const override
{
    if (!IsInstancePath(path)) {
        return { TfToken(), nullptr };
    }

    HdContainerDataSourceHandle perPrim = HdRetainedContainerDataSource::New(
        HdXformSchemaTokens->xform,
        HdXformSchema::BuildRetained(
            HdRetainedTypedSampledDataSource<GfMatrix4d>::New(ComputeXform(path)),
            HdRetainedTypedSampledDataSource<bool>::New(false)));

    return {
        HdPrimTypeTokens->mesh,
        HdOverlayContainerDataSource::New(perPrim, GetSharedMeshDataSource())
    };
}
```

This is instances-by-sharing, not true Hydra instancing. Use real instancer schemas when the renderer should see an instancer prim.

## 7. Dependency forwarding wrapper

```cpp
#include "pxr/imaging/hd/dependencyForwardingSceneIndex.h"

HdSceneIndexBaseRefPtr BuildSceneWithDependencies(
    const HdRetainedSceneIndexRefPtr &source)
{
    return HdDependencyForwardingSceneIndex::New(source);
}
```

Author `HdDependencySchema` on depended-on prims so dirties on materials, bindings, or other upstream fields reach affected geometry. Verify exact builder fields against `dependencySchema.h` for the target branch.

## 8. Output format for code answers

When generating code, include:

```text
verified basis:
  - official docs/source path(s)
  - branch/version if known

compile status:
  - compile-ready except for application-specific <...>
  - or pseudocode where source was not verified

dirtying:
  - change -> prim path -> locator set -> notice
```
