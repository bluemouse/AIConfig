# Transparency and materials reference

## Table of contents

1. Choosing a transparency path
2. `displayOpacity` primvar
3. Material opacity
4. Cutout opacity threshold
5. Material binding layout
6. Dirtying rules
7. Review checklist

## 1. Choosing a transparency path

Hydra scene-index data can express alpha through either geometry primvars or material networks.

Use `primvars/displayOpacity` when:

- no material is required,
- preview behavior is acceptable,
- opacity varies per vertex/face/point,
- hard discard of fully transparent fragments is sufficient in Storm.

Use material `opacity < 1` when:

- true semitransparent blending is needed,
- opacity is a material property or texture-driven,
- Storm order-independent transparency is desired.

Use material `opacityThreshold > 0` when:

- hard cutout behavior is needed,
- fragments below a threshold should be discarded,
- depth-writing opaque/cutout rendering is preferred over OIT.

## 2. `displayOpacity` primvar

Datasource layout:

```text
primvars/
  displayOpacity/
    primvarValue = float or VtArray<float>
    interpolation = constant, vertex, faceVarying, etc.
```

Author constant opacity with:

```cpp
HdRetainedContainerDataSource::New(
    HdTokens->displayOpacity,
    HdPrimvarSchema::BuildRetained(
        HdRetainedTypedSampledDataSource<float>::New(opacity),
        nullptr,
        nullptr,
        HdPrimvarSchema::BuildInterpolationDataSource(HdPrimvarSchemaTokens->constant),
        nullptr,
        nullptr,
        nullptr));
```

Storm-specific behavior to remember:

- With no bound material, presence of `displayOpacity` can put the draw item in a masked/cutout path rather than true translucent blending.
- A value below or equal to the effective alpha discard threshold may disappear; values above the threshold can still write depth like opaque geometry.
- For smooth transparency, prefer material opacity.

## 3. Material opacity

For a UsdPreviewSurface-like material, author `opacity` as a material node parameter and bind the material to geometry.

Simplified layout:

```text
/material prim type = material
  material/
    "" /  # HdMaterialSchemaTokens->universalRenderContext (empty token)
      nodes/
        Surface/
          nodeIdentifier = UsdPreviewSurface
          parameters/
            diffuseColor/value = GfVec3f
            opacity/value = float less than 1
      terminals/
        surface/
          upstreamNodePath = Surface
          upstreamNodeOutputName = surface

/mesh prim type = mesh
  materialBindings/
    <all-purpose>/path = /Materials/Transparent
```

Storm material tag behavior, to be verified against target source when exact behavior matters:

- material metadata can force a material tag,
- `opacityThreshold > 0` makes a masked/cutout material,
- connected opacity or authored opacity below 1 can make a translucent material,
- otherwise material is opaque/default.

## 4. Cutout opacity threshold

For alpha cutouts, author `opacityThreshold` on the material surface node. This is different from semitransparent blending.

Use cases:

- fences,
- foliage,
- decals,
- binary show/hide masks.

Implementation notes:

- `opacityThreshold > 0` usually selects a masked material tag in Storm.
- Fragments below threshold are discarded; fragments above threshold render as opaque/cutout.
- If opacity is texture-connected, verify the exact input connection schema for the target branch.

## 5. Material binding layout

Geometry material bindings are stored on the geometry prim, not the material prim.

Common structure:

```cpp
HdRetainedContainerDataSource::New(
    HdMaterialBindingsSchemaTokens->materialBindings,
    HdRetainedContainerDataSource::New(
        HdMaterialBindingsSchemaTokens->allPurpose,
        HdMaterialBindingSchema::BuildRetained(
            HdRetainedTypedSampledDataSource<SdfPath>::New(materialPath)))); // HdPathDataSourceHandle
```

Verify binding-purpose token names against the target OpenUSD source before returning compile-ready code.

## 6. Dirtying rules

| runtime change | prim to dirty | recommended notice/locator |
|---|---|---|
| `displayOpacity` value changes | geometry prim | dirty `HdDataSourceLocator(primvars, displayOpacity)` or the primvar record |
| `displayOpacity` added or removed | geometry prim | resync or dirty `primvars` container for re-enumeration |
| bound material path changes | geometry prim | dirty `HdMaterialBindingsSchema::GetDefaultLocator()` |
| material `opacity` parameter changes | material prim | dirty `HdMaterialSchema::GetDefaultLocator()` or precise material network locator |
| material terminal/node structure changes | material prim | resync material prim or dirty material container broadly |
| opacity threshold changes | material prim | dirty material parameter/network locator |

If using `HdContainerDataSourceEditor` to replace a material or binding container, include the editor-computed container dirty locators.

## 7. Review checklist

When reviewing transparency code, check:

- Is the desired visual effect cutout or blended transparency?
- Is alpha authored on geometry (`displayOpacity`) or material (`opacity`) intentionally?
- Does geometry bind to the intended material path?
- Are material nodes, terminals, and parameter names in the right containers?
- Are value types correct (`float` for scalar opacity, `VtArray<float>` for varying opacity)?
- Are material prim changes dirtied on the material prim, not only the geometry prim?
- Does the renderer support the selected material tag/transparent path?
