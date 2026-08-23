# Core classes and contracts

## Tool and stroke strategy classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisToolFreehandHelper` | turn pointer/tablet input into stroke jobs | creates `KisResourcesSnapshot`, `KisDistanceInformation`, stroke painters, smoothing/stabilizer state, airbrush/async timers, and `FreehandStrokeStrategy` |
| `FreehandStrokeStrategy` | execute freehand job data | dispatches point/line/curve/polyline/shape jobs to masked freehand painters |
| `KisPainterBasedStrokeStrategy` | initialize painter-backed strokes | selects target device, handles selection/indirect painting/masking brush, creates undo transaction, calls snapshot setup on painters |
| `KisResourcesSnapshot` | freeze resource and canvas state for a stroke | copies preset, colors, pattern, gradient, channel locks, mirror state, composite op, opacity, node context, and related resources |
| `KisStrokesFacade` | tool-facing stroke submission facade | start/add/end/cancel stroke jobs without exposing scheduler internals |

Important contract: input tools should not reach into paintop internals. They provide geometry and stroke lifecycle. Paintops decide brush behavior.

## Image scheduling classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisImage` | document coordinator | owns image dimensions, root layer, scheduler, dirty/projection coordination, undo adapters, wrap/mirror image state |
| `KisUpdateScheduler` | coordinate strokes and projection updates | arbitrates between stroke jobs, updates, LOD sync, spontaneous jobs, and undo/progress behavior |
| `KisStrokesQueue` | manage active strokes | queues jobs, can create LOD buddy strokes, handles stroke lifecycle |
| `KisStrokeStrategy` | stroke behavior abstraction | defines callbacks for init, do, finish, cancel, and job-data semantics |
| `KisRunnableStrokeJobData` | runnable job wrapper | lets paintops and strategies enqueue concurrent/sequential work |

Important contract: painting and projection are scheduled together. Do not make a brush implementation depend on immediate synchronous UI repaint.

## Paintop classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisPaintOpPreset` | user-facing brush preset | stores paintop id, settings, linked/embedded resources, and optional masking preset data |
| `KisPaintOpSettings` | engine-specific settings object | owns serialization/settings lookup for one paintop family |
| `KisPaintOpConfigWidget` | settings UI | exposes artist-facing controls and writes settings |
| `KisPaintOpFactory` | paintop factory | creates runtime paintops and declares linked/embedded resources |
| `KisPaintOpRegistry` | runtime paintop registry | maps paintop id to factory |
| `KisPaintOp` | abstract runtime engine | defines `paintAt`, spacing/timing, line/curve helpers, and optional async update hooks |
| `KisBrushBasedPaintOp` | base for brush-tip engines | provides shared brush resource and dab-generation support |
| `KisBrushOp` | default pixel brush engine | option-driven dab stamping with async dab generation and batched blitting |

### `KisPaintOp` contract

The protected pure virtual `paintAt(const KisPaintInformation&)` returns `KisSpacingInformation`. The public framework-facing `paintAt(info, currentDistance)` handles distance/timing registration around the engine implementation.

Do not casually bypass this chain. Spacing, drawing angle, timing, and airbrush behavior depend on it.

Minimum custom engine methods:

- implement `paintAt(const KisPaintInformation&)`
- implement `updateSpacingImpl(const KisPaintInformation&)`
- implement `updateTimingImpl(const KisPaintInformation&)` only if the engine emits timed/airbrush updates
- override `paintLine()` or `paintBezierCurve()` only when the default interpolation path is unsuitable
- override `doAsynchronousUpdate()` only when the engine schedules deferred rendering work

## Paint sample and spacing classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisPaintInformation` | per-sample input state | position, pressure, tilt, rotation, tangential pressure, perspective, time, speed, canvas rotation/mirror, random sources |
| `KisDistanceInformation` | stroke-local emission state | last positions, accumulated distance, timing, drawing angle, spacing/timing updates |
| `KisPaintOpUtils` | interpolation and geometry helpers | default line/curve dab placement, split dabs into rects, spacing/timing utilities |

Important contract: the paintop computes what a dab means now; the framework records how that affects stroke-local emission state.

## Dab and brush resource classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisBrush` | brush tip resource interface | creates masks or dab images for size, ratio, rotation, subpixel offset, and brush application mode |
| `KisPngBrush`, `KisSvgBrush`, `KisGbrBrush`, `KisImagePipeBrush` | concrete brush resources | normalize different asset formats into the common brush/dab interface |
| `KisDabCacheUtils` | turn logical dab request into `KisFixedPaintDevice` | creates image stamps, colorized masks, solid-color masked dabs, and postprocesses sharpness/texture |
| `KisDabRenderingExecutor` | async dab execution facade | submits render requests and provides prepared dabs to async update logic |
| `KisDabRenderingQueue` | dab render queue/cache | tracks sequence numbers and can generate, postprocess, or copy/reuse dabs |
| `KisRenderedDab` | prepared dab plus geometry | carries fixed device, offset, bounds, opacity/flow metadata |

Important contract: `KisBrush` is not the whole engine. It creates tip pixels/masks; the paintop decides placement, sensor response, timing, opacity, flow, texture, and compositing.

## Painter, device, and compositing classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisPainter` | rendering context | binds target device, paint color, composite op, opacity, selection, channel locks, mirror state, and runtime paintop |
| `KisPaintDevice` | paintable pixel device facade | owns color space, default bounds, offset, frame/LOD data, caches, and tiled data manager |
| `KisFixedPaintDevice` | fixed-position dab/device buffer | commonly used for generated dabs before blitting into tiled storage |
| `KoColorSpace` | color model/depth behavior | supplies color conversion and `bitBlt` implementation |
| `KoCompositeOp` | blend/composite operation | receives parameter blocks during blit/composite |
| `KisSelection` / masks | selection constraints | selection may be fixed or device-backed and must align with mirrored/wrapped dabs |

Important contract: final pixels appear when painter/compositor merges source dab/device data into the target `KisPaintDevice`, not when the paintop decides to emit a dab.

## Tiled storage classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisTiledDataManager` | tile storage policy | sparse tile hash, extent manager, memento/undo, accessors, bitBlt/bitBltRough, clear/purge/load/save |
| `KisTile` | positioned tile handle | row/column identity and extent |
| `KisTileData` | actual pixel bytes and lifetime state | 64x64 tile buffer, copy-on-write sharing, pooled/compressed/swapped states |
| `KisRandomAccessor2` | efficient random/tile-local access | caches tile locks and exposes contiguous columns/rows and row stride |
| `KisWrappedRandomAccessor` | wrap-around coordinate remapping | remaps requested coordinates before delegating to tiled access |

Important contract: storage policy is not brush semantics. Brush code decides what to paint; tiled storage decides how bytes are shared, cloned, swapped, and accessed.

## Layer and projection classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisNode` | graph node base | layer/mask/filter nodes participate in image tree and dirty propagation |
| `KisLayer` / `KisPaintLayer` | layer behavior and raster paint target | painting usually targets a node paint device and marks the node dirty |
| projection leaves/planes | projection recomputation | combine node data into composited image representation |
| `KisCanvas2` | UI canvas controller | chooses QPainter/OpenGL canvas, manages projection update scheduling, input managers, color display conversion |
| `KisOpenGLCanvas2` | OpenGL canvas widget | displays projection through GL-backed texture/tile infrastructure |
| `KisPrescaledProjection` | CPU/QPainter display helper | stores prescaled projection data for non-OpenGL canvas paths |

Important contract: canvas/GPU display should be treated as a consumer of projection updates unless the specific task is explicitly about moving paint computation to GPU.

## Resource and preset classes

| class | primary responsibility | implementation notes |
|---|---|---|
| `KisPaintOpPreset` | preset serialization and resource graph | includes paintop id, settings, linked/embedded resources, and masking preset data |
| `KisPaintOpFactory::prepareLinkedResources` | resource dependency declaration | must report external brushes/patterns/gradients/etc. used during painting |
| `KisPaintOpFactory::prepareEmbeddedResources` | self-contained preset support | must report resources to embed for portability |
| `KisBrushOptionProperties` | brush-tip option/resource binding | reads brush XML and resolves brush resource through resource interface |
| `KisTextureOption` / `KisTextureMaskInfo` | paper/texture processing | resolves pattern resource, computes/caches texture masks, applies them in dab postprocess |

Important contract: if a new engine feature uses a resource during painting, declare it through the factory/resource path and ensure stroke-local snapshot availability.
