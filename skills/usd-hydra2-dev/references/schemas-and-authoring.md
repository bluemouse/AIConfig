# Schemas and authoring reference

## Table of contents

1. Schema wrappers and tokens
2. Minimal gprim schema set
3. Mesh and primvars
4. Materials and bindings
5. Instancing
6. Authoring and dirtying checklist

## 1. Schema wrappers and tokens

Hydra schemas are typed facades over `HdContainerDataSourceHandle`. Generated schemas usually provide:

- `GetFromParent(parentContainer)`
- member accessors such as `GetTopology()` or `GetVisibility()`
- `BuildRetained(...)`
- optional `Builder`
- `GetSchemaToken()` and `GetDefaultLocator()`
- schema-specific member locator helpers

Use generated token sets for container names:

```cpp
HdMeshSchemaTokens->mesh
HdPrimvarsSchemaTokens->primvars
HdXformSchemaTokens->xform
HdVisibilitySchemaTokens->visibility
HdMaterialSchemaTokens->material
HdMaterialBindingsSchemaTokens->materialBindings
```

Avoid ad-hoc string tokens for standard schema fields. Ad-hoc `TfToken("...")` is appropriate for user/authored names such as a material node name (`TfToken("Surface")`) or custom primvar name only after checking naming rules.

## 2. Minimal gprim schema set

For a mesh/gprim that should render predictably, consider authoring:

- `HdMeshSchema`: mesh topology, subdivision scheme, double-sided state.
- `HdPrimvarsSchema`: `points`, normals, display color, opacity, custom primvars.
- `HdXformSchema`: local transform and reset flag.
- `HdVisibilitySchema`: visibility.
- `HdPurposeSchema`: render tag/purpose when the pipeline filters by purpose.
- `HdExtentSchema`: bounds when consumers expect provided extents.
- `HdMaterialBindingsSchema`: material path(s) when using material networks.

Do not over-author. Missing schemas can be valid if downstream has fallbacks, but renderer-facing code should know which fallbacks it depends on.

## 3. Mesh and primvars

Common mesh data layout:

```text
mesh/
  topology/
    faceVertexCounts = int[]
    faceVertexIndices = int[]
    holeIndices = int[] or null
    orientation = token, often HdTokens->rightHanded
  subdivisionScheme = token, often PxOsdOpenSubdivTokens->none for polygonal preview
  subdivisionTags = null or schema
  doubleSided = bool
primvars/
  points/
    primvarValue = VtArray<GfVec3f>
    interpolation = vertex
    role = point
  displayColor/
    primvarValue = GfVec3f or VtArray<GfVec3f>
    interpolation = constant, vertex, faceVarying, etc.
    role = color
  displayOpacity/
    primvarValue = float or VtArray<float>
    interpolation = constant, vertex, faceVarying, etc.
```

Use retained values like:

```cpp
HdRetainedTypedSampledDataSource<VtArray<int>>::New(faceVertexCounts);
HdRetainedTypedSampledDataSource<VtArray<GfVec3f>>::New(points);
HdPrimvarSchema::BuildInterpolationDataSource(HdPrimvarSchemaTokens->vertex);
HdPrimvarSchema::BuildRoleDataSource(HdPrimvarSchemaTokens->point);
```

Dirtying examples:

- Point values changed: dirty `HdDataSourceLocator(HdPrimvarsSchemaTokens->primvars, HdTokens->points)` or a schema helper if available.
- Mesh topology changed: dirty `HdMeshSchema::GetTopologyLocator()` if available; otherwise dirty the mesh topology locator from schema tokens.
- Primvar added/removed: resync the prim or dirty the `primvars` container so consumers re-enumerate `GetNames()`.
- Interpolation or role changed: dirty the primvar record, not just the value child.

## 4. Materials and bindings

Material prims use `HdPrimTypeTokens->material` and the material schema under `HdMaterialSchemaTokens->material`.

**Universal render context:** `HdMaterialSchemaTokens->universalRenderContext` is the empty token `""`. In datasource trees it is the default cross-renderer material network container. Use the token constant in compile-ready code; do not invent a visible string name.

Common material network layout for a universal UsdPreviewSurface material:

```text
material/
  "" /  # HdMaterialSchemaTokens->universalRenderContext
    nodes/
      Surface/
        nodeIdentifier = UsdPreviewSurface
        parameters/
          diffuseColor/value = GfVec3f
          opacity/value = float
          opacityThreshold/value = float optional
    terminals/
      surface/
        upstreamNodePath = Surface
        upstreamNodeOutputName = surface
```

Renderer-specific contexts (for example Storm `glslfx`) are sibling containers under `material/`; verify names against `HdMaterialSchemaTokens` for the target branch.

Geometry binds materials through:

```text
materialBindings/
  allPurpose /  # HdMaterialBindingsSchemaTokens->allPurpose
    path = /Materials/MyMaterial
```

Typical all-purpose binding uses `HdMaterialBindingsSchemaTokens->allPurpose`. Verify binding-purpose token names against the target OpenUSD version because material binding helper tokens have changed across development history.

For the binding path child, prefer `HdPathDataSourceHandle` / `HdRetainedTypedSampledDataSource<SdfPath>::New(path)` with `HdMaterialBindingSchema::BuildRetained(...)`.

Dirtying examples:

- Bound material path changed on a mesh: dirty `HdMaterialBindingsSchema::GetDefaultLocator()` on the mesh prim.
- Material parameter changed: dirty `HdMaterialSchema::GetDefaultLocator()` or a precise material network locator on the material prim, not only the bound geometry prim.
- Material binding added/removed: resync the geometry prim or dirty `materialBindings` so binding purposes are re-enumerated.

## 5. Instancing

Two different techniques are often confused.

### Shared retained datasources

For many repeated simple meshes, reuse the same retained mesh container for many prim paths and overlay per-instance `xform`. This is memory-efficient and simple, but it is not Hydra instancing semantics. The renderer still sees many mesh prim paths.

Use this when:

- instance count is modest,
- geometry library is small,
- selection/path identity per repeated object matters,
- renderer instancer support is uncertain.

### True Hydra instancing

True Hydra instancing publishes prototype prims and an instancer prim, typically with:

- `HdPrimTypeTokens->instancer`
- `HdInstancerTopologySchema` under `HdInstancerTopologySchemaTokens->instancerTopology`
- `prototypes = VtArray<SdfPath>`
- `instanceIndices = HdVectorDataSource` with one int array per prototype
- optional `mask` and `instanceLocations` (verify need against target consumers)
- instance-rate primvars with interpolation `HdPrimvarSchemaTokens->instance`

Common instance-rate transform primvars (`HdInstancerTokens`):

- `instanceTransforms` — full `GfMatrix4d` per instance
- `instanceTranslations`, `instanceRotations`, `instanceScales` — decomposed TRS path (see `instancer.h`)

Use true instancing when:

- high instance counts require renderer-side instancing,
- prototype identity and instance-rate data fit Hydra instancer semantics,
- downstream renderer supports the necessary instancing path.

Dirtying examples:

- Instance transforms changed: dirty the instance transform primvar on the instancer prim.
- Prototype list, instance indices, mask, or instance locations changed: dirty `HdInstancerTopologySchema::GetDefaultLocator()` or resync the instancer if membership changed drastically.
- Prototype geometry changed: dirty the prototype prim's data; do not dirty every instance unless a downstream compatibility layer requires it.

## 6. Authoring and dirtying checklist

For each authored feature, define:

```text
prim path:
prim type:
schema container path:
value type:
concrete datasource class:
consumer fallback if absent:
mutation source:
dirty locator:
resync needed? yes/no and why:
```

Prefer this decision rule:

- value-only update: dirty the value or closest schema member locator.
- metadata/role/interpolation update: dirty the primvar/schema record.
- child membership update: dirty the parent container or resync.
- prim type or existence update: send added/resync or removed notices.
- path identity update: send renamed only if preserving identity is correct; otherwise remove+add.
- cross-prim dependency update: dirty the depended-on locator and ensure dependency forwarding will dirty affected prims.
