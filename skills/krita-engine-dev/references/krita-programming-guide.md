# Krita Programming Guide

This guide is for junior software engineers who need a practical mental model of Krita's architecture, especially the raster stroke and brush engine. It complements `HACKING`, the online build instructions, and the user-facing manual. The manual is useful because it tells you which artist features matter; this guide tells you where those features live in code and how they are rendered.

Useful companion references:

- `HACKING`
- `README.md`
- [Krita User Manual](https://docs.krita.org/en/user_manual.html)
- [Build Instructions](https://docs.krita.org/en/untranslatable_pages/building_krita.html)
- [Krita API Docs](https://api.kde.org/extragear-api/graphics-apidocs/krita/html/index.html)

The mental model, the core painting objects, and the full raster stroke path
from stylus sample to pixels are covered by the focused references: read
[architecture-map.md](architecture-map.md) for the mental model, the subsystem
map, and the standard freehand stroke flow, and
[core-classes-and-contracts.md](core-classes-and-contracts.md) for the class
responsibility tables and contracts. This guide continues with the capability
map and the deeper implementation material.

## 1. What the Stroke and Brush Engine Can Do

The user manual describes these features from the artist's point of view. Here is where they come from in code.

### Pressure, tilt, rotation, and other tablet dynamics

These arrive through `KisPaintInformation`. A paintop or option object can derive size, opacity, scatter, or rotation from them. If a new input sensor or brush response is added, check this class and the option evaluators first.

### Spacing and airbrush timing

Spacing is handled through `KisDistanceInformation` plus `updateSpacingImpl()`. Airbrush-style temporal behavior is handled through `updateTimingImpl()`. In the default brush engine, `KisBrushOp::updateTimingImpl()` calls `effectiveTiming(...)`.

If spacing feels wrong, do not start at compositing. Start at:

- `KisPaintInformation`
- `KisDistanceInformation`
- `KisPaintOpUtils::paintLine()`
- the paintop's spacing/timing implementation

### Brush-tip transformation

The default engine computes scale, ratio, rotation, subpixel offsets, and scattering before requesting the dab. The brush resource then renders the appropriate tip image from its brush pyramid.

### Opacity, flow, sharpness, and texture

These are applied partly in the engine and partly in the dab postprocessing path:

- opacity and flow are evaluated before queuing the dab
- sharpness and texture are applied in `postProcessDab()`
- final opacity also participates in `KoCompositeOp::ParameterInfo`

### Mirroring and wrap-around mode

Mirror state is injected through `KisResourcesSnapshot::setupPainter()`. `KisBrushOp::doAsynchronousUpdate()` and related painter code duplicate or transform the final rendered dab data as needed. Wrap-around mode is handled during rect normalization and dab duplication before blitting.

These features are easy to break if you only test "paint a stroke on the center of a normal canvas".

### Masking brush and indirect painting

Some presets require painting into a temporary target and then compositing later. `KisPainterBasedStrokeStrategy::initStrokeCallback()` and `initPainters()` contain the logic for indirect painting and masking brush support.

This is a critical maintenance rule:

- masking brush rendering depends on indirect painting support
- if you change painter initialization, verify that masked brushes still behave correctly

### Asynchronous rendering

Some presets declare that they need asynchronous updates. In that case, the stroke strategy periodically asks the paintop for runnable jobs through `doAsynchronousUpdate()`, then issues dirty signals after those jobs complete.

This is a major reason why Krita can keep freehand painting responsive under heavy dab workloads.

### Level-of-detail painting

`KisStrokesQueue` can create LOD buddy strokes and clone stroke jobs for them. Paintops also need to respect LOD scaling where appropriate. The default brush engine multiplies size by `KisLodTransform::lodToScale(...)`.

If a change only works at full resolution, it is not finished.

### Multiple brush engines

Krita supports many paint engines under `plugins/paintops/`, not just the default pixel brush. The plugin registry and factory system are what turn an engine implementation into something users can choose in the preset editor.

## 2. Resource and Preset Architecture

This area matters much more than it first appears.

### Presets are resource graphs, not just parameter structs

`KisPaintOpPreset` stores:

- the selected paintop id
- engine settings
- linked resources
- embedded resources
- optional masking brush preset data

When a stroke begins, Krita clones the preset with a local resources snapshot using `cloneWithResourcesSnapshot(...)`.

Why this exists:

- worker-thread painting cannot safely query the GUI-thread global resource database
- a stroke should keep using a stable snapshot even if the user changes resources in the UI mid-stroke

### Linked and embedded resources must be declared correctly

`KisPaintOpFactory` exposes:

- `prepareLinkedResources(...)`
- `prepareEmbeddedResources(...)`

If you add a new engine feature that depends on a resource and you do not report it correctly, the engine may work in the GUI thread and fail during real painting, especially in worker-thread or serialization scenarios.

For the deeper design background, read `libs/resources/ResourcesDesignNotes.md`.

### Canvas resources are separate from the global resource database

Some resources depend on canvas state, such as foreground and background color. `KisPaintOpPreset::cloneWithResourcesSnapshot(...)` can bake required canvas resources into a local storage object. This is how gradients and similar resources stay consistent during a stroke.

## 3. How to Extend the Brush Engine

There are two common extension paths: modify an existing engine, or add a new one.

### Option A: Extend an existing engine

This is the right choice when the feature is specific to one engine, such as:

- a new brush option for `KisBrushOp`
- a new dab postprocess
- a new interpolation rule
- better async scheduling for an existing engine

Typical workflow:

1. Add or extend the option/settings object.
2. Update the settings widget.
3. Thread the setting into `paintAt()`, spacing, timing, or async update logic.
4. Verify linked resources and serialization if the feature depends on resources.
5. Test mirrored, wrapped, indirect, and LOD scenarios.

### Option B: Add a new paint engine

Most engines follow the same broad recipe.

1. Choose a base.

- derive directly from `KisPaintOp` if the engine is fundamentally custom
- derive from `KisBrushBasedPaintOp` if you still want brush-tip and dab-cache infrastructure

2. Implement the runtime behavior.

At minimum, implement:

- `paintAt(const KisPaintInformation&)`
- `updateSpacingImpl(const KisPaintInformation&)`

Implement `updateTimingImpl()` if the engine supports airbrushing or other temporal emission.

3. Implement settings and configuration UI.

You usually need:

- a `KisPaintOpSettings` subclass
- a `KisPaintOpConfigWidget` subclass

4. Register the engine.

Most paintops use `KisSimplePaintOpFactory<Op, Settings, Widget>`. Registration typically happens in a plugin source file using `K_PLUGIN_FACTORY_WITH_JSON(...)` and then `KisPaintOpRegistry::instance()->add(new KisSimplePaintOpFactory<...>(...))`.

5. Declare resource dependencies.

If the engine uses patterns, gradients, images, or other resources, make sure the factory reports them correctly.

6. Decide whether the engine is synchronous or asynchronous.

Not every engine needs async updates. If the engine generates heavy dabs or benefits from batched updates, study `KisBrushOp` closely before designing your own update path.

### Practical advice for first-time contributors

If you are adding your first new paint engine, copy the registration pattern from a small existing paintop plugin such as:

- `plugins/paintops/experiment/experiment_paintop_plugin.cpp`
- `plugins/paintops/spray/spray_paintop_plugin.cpp`

If you are adding your first raster brush feature, start with the default pixel brush path:

- `plugins/paintops/defaultpaintops/`
- `plugins/paintops/libpaintop/`
- `libs/brush/`

The performance and correctness rules — the spacing/timing contract,
worker-thread resource access, per-dab allocation, mirror/wrap/selection/
indirect/LOD coverage, and dirty rectangles — live in the skill's Core
invariants and Gotchas sections and in
[pixel-layer-gpu-performance.md](pixel-layer-gpu-performance.md).

## 4. A Good Code-Reading Order

If you are new to Krita, do not read the repository randomly. Read in this order:

1. `libs/ui/tool/kis_tool_freehand_helper.cpp`
2. `libs/ui/tool/strokes/freehand_stroke.h`
3. `libs/ui/tool/strokes/freehand_stroke.cpp`
4. `libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp`
5. `libs/ui/tool/kis_resources_snapshot.cpp`
6. `libs/image/kis_image.cc`
7. `libs/image/kis_update_scheduler.cpp`
8. `libs/image/kis_strokes_queue.cpp`
9. `libs/image/kis_painter.cc`
10. `libs/image/kis_painter_blt_multi_fixed.cpp`
11. `libs/image/brushengine/kis_paintop.h`
12. `libs/image/brushengine/kis_paint_information.h`
13. `libs/image/brushengine/kis_paintop_utils.h`
14. `libs/image/brushengine/kis_paintop_factory.h`
15. `libs/image/brushengine/kis_paintop_registry.cc`
16. `libs/image/brushengine/kis_paintop_preset.cpp`
17. `plugins/paintops/defaultpaintops/brush/kis_brushop.cpp`
18. `plugins/paintops/defaultpaintops/brush/KisDabRenderingExecutor.cpp`
19. `plugins/paintops/defaultpaintops/brush/KisDabRenderingQueue.cpp`
20. `plugins/paintops/libpaintop/KisDabCacheUtils.cpp`
21. `libs/brush/kis_brush.cpp`

After that, read one alternate engine under `plugins/paintops/` to see how Krita supports very different brush behavior on top of the same stroke framework.

## 5. Advanced Implementation: Tiled Painting

The stroke engine only makes sense if you understand what it is painting into. Krita's raster storage is not a single flat image buffer. `KisPaintDevice` is the public painting object, but the actual sparse pixel storage is usually delegated to `KisTiledDataManager`.

### 5.1 `KisPaintDevice` is a facade over tiled storage

`KisPaintDevice` owns:

- color-space information
- offset and default bounds
- caches such as exact bounds
- frame and LOD data
- a data manager that actually stores pixels

For normal raster layers, the backing store is tile-based. This is why `KisPaintDevice::extent()` is only approximate: the device extent is aligned to tile boundaries, while `exactBounds()` does a slower scanline-based calculation and caches the result.

This distinction matters when you maintain painting code:

- use `extent()` when you want the rough working region or tile-aligned storage shape
- use `exactBounds()` when correctness depends on the real painted pixels

### 5.2 Tiles are 64x64, sparse, and copy-on-write

At the lowest storage layer, `KisTileData::WIDTH` and `KisTileData::HEIGHT` are both 64. Krita therefore stores raster content in 64x64 chunks.

That design gives Krita several important properties:

- sparse images are cheap because untouched tiles do not need real storage
- large canvases stay manageable because only touched areas allocate tiles
- operations can share or duplicate tile data at tile granularity
- undo and temporary devices can reuse existing tiles through copy-on-write instead of eagerly cloning full images

The separation between `KisTile` and `KisTileData` is important:

- `KisTile` stores tile identity and position such as row, column, and extent
- `KisTileData` stores the actual pixel buffer and lifetime state

Because those are separate objects, multiple tiles or historical revisions can share a `KisTileData` instance until somebody writes to it.

### 5.3 `KisTiledDataManager` is where storage policy lives

`KisTiledDataManager` is responsible for:

- the tile hash table
- tracking the sparse extent through `KisTiledExtentManager`
- undo/redo state through the memento manager
- iterators and random accessors
- cloning and bit-block transfers
- clearing, purging, and loading/saving tile data

The manager knows nothing about painting semantics. It only knows pixel size and the default pixel value. This is a crucial architectural boundary: brush engines decide what to paint, while the tiled data manager decides how bytes are stored, cloned, or swapped.

Two methods are especially important for performance-sensitive code:

- `bitBlt(...)`: clones the requested rectangle as precisely as possible and shares tile data with copy-on-write where possible
- `bitBltRough(...)`: shares every tile touched by the rectangle, even if that copies more than the requested area

Krita uses the rough form for temporary devices and LOD transfers because it is much faster and because extra copied pixels are acceptable in those contexts.

### 5.4 Undo is tile-native, not layered on top

Undo is deeply integrated into tile storage through `KisMementoManager`. `KisTiledDataManager::getTilesPair()` can fetch both the current tile and the committed tile together, which lets iterators work against the live state and the undo baseline without extra hash-table traffic.

That is why tiled painting code often talks about:

- current tiles
- old tiles
- committed tiles
- mementos

This is not an afterthought. It is how Krita keeps painting, undo, and projection history coherent under heavy editing.

### 5.5 Random accessors are optimized around tiles

Many core painting loops do not iterate pixel-by-pixel in a naive way. `KisRandomAccessor2` caches tile info, locks tiles for read or write, and exposes:

- `rawData()`
- `numContiguousColumns()`
- `numContiguousRows()`
- `rowStride()`

That is exactly why `KisPainter::Private::applyDevice()` can walk large spans efficiently when blitting a dab: it asks how many contiguous pixels or rows are available before crossing a tile boundary, then hands those spans to the color-space compositing code.

In other words, the tile system directly shapes the structure of the brush engine's inner loops.

### 5.6 Wrap-around mode is implemented as accessor remapping

`KisWrappedRandomAccessor` is a useful example of Krita's storage design. It does not duplicate the whole image. Instead, it remaps requested coordinates into the wrap rectangle before delegating to the normal tiled accessor.

That means wrap-around mode is not a separate storage engine. It is a coordinate transformation layered over the same tiled device model.

This is why wrap-around logic shows up in both:

- low-level accessors and wrapped rect normalization
- high-level paintops such as `KisBrushOp::doAsynchronousUpdate()`

### 5.7 Tile data can be pooled, compressed, and swapped

`KisTileData` has storage states such as `NORMAL`, `COMPRESSED`, and `SWAPPED`, and it can use pooled memory for common pixel sizes. If tile data is swapped out, it is reloaded on demand through the data store.

This matters to brush-engine maintainers for two reasons:

1. A dab or temporary device may touch storage that is not currently resident in its hot form.
2. Adding extra passes over the image is expensive not only because of CPU work, but because it may force tile loads, decompression, or copy-on-write churn.

When a painting change causes mysterious performance regressions on large canvases, the culprit is often the interaction between the brush engine and the tiled backing store.

### 5.8 Why paintops create temporary composition devices

Many paintops do not stamp straight into the target device. They first build a temporary device with `createCompositionSourceDevice()` or `createCompositionSourceDeviceFixed()`.

That is not just convenience. Those helpers preserve:

- the composition source color space
- default bounds
- wrap-around capability

So when a paintop later blits or mirrors a dab, it is doing so in a temporary device that still matches the destination device's storage and coordinate rules.

## 6. Paintop Through Three Presets

The most important thing to understand about a Krita brush preset is that the preset file is not the engine. A `.kpp` stores embedded preset data, including a `paintopid`, and that `paintopid` determines which factory and runtime class the brush engine will use.

The framework path is always the same:

1. The preset provides `paintopid` plus engine parameters and linked resources.
2. `KisResourcesSnapshot` clones it into a stroke-local resource snapshot.
3. `KisPainter::setPaintOpPreset()` asks `KisPaintOpRegistry` for a runtime engine.
4. A `KisPaintOpFactory` or `KisSimplePaintOpFactory` constructs the concrete `KisPaintOp`.
5. The stroke framework calls `paintAt()`, `paintLine()`, spacing, timing, and optional async update hooks through the shared `KisPaintOp` contract.

The most important lesson is that preset names can be misleading. A preset that sounds like a "spray" or "bristle" brush may still be implemented by the default `paintbrush` engine if its `paintopid` says so. The engine id, not the marketing name, defines the code path.

### 6.1 Preset 1: `b)_Airbrush_Soft.kpp` (`paintopid="paintbrush"`)

This preset is a good first example because it uses the default raster paint engine while also exercising one of the engine's most important timing features. Its embedded preset data includes:

- `paintopid="paintbrush"`
- `AirbrushOption/isAirbrushing=true`
- an explicit airbrush rate

At runtime, this preset becomes `KisBrushOp`, the same engine used by many default pixel brushes. That matters because it shows that huge behavior differences can come from preset parameters without switching engines at all.

The registration path for this engine starts in `plugins/paintops/defaultpaintops/defaultpaintops_plugin.cc`, where `paintbrush` is added to `KisPaintOpRegistry` through `KisSimplePaintOpFactory`.

What this preset teaches about the framework:

- the preset stays inside the standard `KisBrushOp` path
- timing behavior comes from `updateTimingImpl()`, not from a special tool
- the freehand helper reacts to preset capabilities before painting even begins
- the brush tip, spacing, opacity, softness, scatter, rotation, and airbrush timing are all option-layer behavior on top of one paintop implementation

Why this is architecturally important:

- if you are asked to "make airbrush smoother", you are usually debugging preset options, timing, or `KisBrushOp`, not inventing a new engine
- if two presets feel completely different but share `paintopid="paintbrush"`, the right place to compare them is often the option evaluation path, not the registry or tool layer

### 6.2 Preset 2: `v)_Texture_Pointillism.kpp` (`paintopid="spraybrush"`)

This preset is a better example of a truly different engine. Its preset data declares `paintopid="spraybrush"` and includes spray-specific color and precision options such as per-particle color variation.

At runtime, the registry instantiates `KisSprayPaintOp`.

The registration path for this engine starts in `plugins/paintops/spray/spray_paintop_plugin.cpp`, where `spraybrush` is registered with its own factory, settings type, and settings widget.

The important difference from `KisBrushOp` is structural:

- `KisSprayPaintOp::paintAt()` creates or clears a temporary composition-source `KisPaintDevice`
- it delegates the particle generation to `SprayBrush::paint(...)`
- it blits the whole generated result with `painter()->bitBlt(...)`
- it applies mirroring with `renderMirrorMask(...)`

So the spray engine is not "one brush dab with different spacing". It is a mini particle system that renders many micro-elements into a temporary device during one `paintAt()` call.

What this preset teaches about the framework:

- not every paintop uses `KisBrushBasedPaintOp`
- not every paintop uses the async dab queue used by `KisBrushOp`
- some engines generate many internal particles, then commit them as one composed region
- spacing is still a first-class concept, but its meaning is engine-specific

Why this is architecturally important:

- the paintop framework is intentionally broad enough to support both classic dab-stamping engines and engines that synthesize richer local geometry
- if you add a new paint engine, you should not assume the default brush engine's async dab executor is mandatory

### 6.3 Preset 3: `k)_Blender_Basic.kpp` (`paintopid="colorsmudge"`)

This preset is an excellent example of a paintop that is still brush-based, but is semantically much closer to a local compositing system than a plain stamping engine.

Its preset data declares `paintopid="colorsmudge"` and includes parameters such as:

- color rate
- smudge rate
- gradient-related options
- precision and mirror settings

At runtime, the registry instantiates `KisColorSmudgeOp`, which derives from `KisBrushBasedPaintOp` but immediately becomes more complex than `KisBrushOp`.

The registration path for this engine starts in `plugins/paintops/colorsmudge/colorsmudge_paintop_plugin.cpp`, where `colorsmudge` is connected to its runtime class, settings object, and configuration widget.

Key implementation details:

- it chooses one of several strategy classes depending on brush application mode, overlay mode, and smudge settings
- it may use `KisColorSmudgeStrategyLightness`, `KisColorSmudgeStrategyMask`, `KisColorSmudgeStrategyStamp`, or legacy paths
- it computes both a destination dab rect and a source dab rect
- after the first run, it samples from previous paint state rather than only applying the current foreground color
- it can request `KisInterstrokeDataFactory` support so state persists coherently across stroke updates

The most interesting line of thinking is this: the smudge engine does not merely ask "where should I stamp the next dab?" It also asks "what local image state should this dab sample, smear, dull, or blend against?"

What this preset teaches about the framework:

- a paintop can still be brush-based and yet need its own strategy layer
- interstroke data is a real engine-extension point, not a rare corner case
- some paintops need multiple temporary devices and different precise color spaces to produce correct results
- the shared `KisPaintOp` API is flexible enough to host engines that behave more like localized filter/compositing pipelines

Why this is architecturally important:

- if you only study `KisBrushOp`, you may underestimate how much state a paintop is allowed to own
- if you are extending smudge-like behavior, you need to think about sampling history, strategy selection, and dirty-rect generation, not just tip shape and spacing

### 6.4 What these three presets show together

Taken together, these presets show three very different uses of the same framework:

- `paintbrush`: option-driven dab generation, potentially asynchronous, tuned by preset curves and sensors
- `spraybrush`: engine-specific particle synthesis into a temporary device
- `colorsmudge`: brush-based painting with local sampling, strategy dispatch, and interstroke state

That is the real design lesson of Krita paintops: the framework standardizes lifecycle and integration points, but it deliberately does not force every engine into the same rendering algorithm.

## 7. Advanced Implementation: Mirroring

The earlier sections treated mirroring as a user-facing feature. Internally, mirroring is a cross-cutting rendering concern that touches resource snapshots, painters, LOD transforms, dirty-rect handling, and paintop-specific execution strategies.

### 7.1 Mirror state is injected before paintop creation

Mirroring enters the paint path through `KisResourcesSnapshot::setupPainter()`, which calls `KisPainter::setMirrorInformation(...)`.

That means mirror state is part of the painter context before the concrete paintop is constructed. This is important because some engines inspect painter state during initialization and some engines need mirror-aware auxiliary devices from the start.

### 7.2 Mirroring is evaluated in effective LOD coordinates

`KisPainter::renderMirrorMask(...)` first maps the axes center through `KisLodTransform` before computing mirrored target positions.

This is a subtle but important implementation detail:

- mirror axes live in image-space semantics
- painting may happen on an LOD device
- mirrored placement must therefore use the effective axes center for the active device

If you ever see mirroring bugs that appear only during low-detail interactive painting, this is one of the first places to inspect.

### 7.3 There are two major mirroring paths

Krita does not mirror every paintop in the same way.

#### Path A: generic painter mirroring via `renderMirrorMask()`

Paintops such as `KisSprayPaintOp` and `KisHairyPaintOp` often:

1. paint into a temporary `KisPaintDevice`
2. blit the primary result once
3. call `renderMirrorMask(...)` to stamp the mirrored copies

`renderMirrorMask(QRect, KisFixedPaintDeviceSP)` works by:

- computing `mirrorX` and `mirrorY` from the dab bounds and effective axes center
- flipping the dab in-place with `dab->mirror(...)`
- calling `bltFixed(...)` one or three more times depending on horizontal and vertical mirror flags

There are overloads for:

- fixed dabs
- fixed dabs plus fixed selection masks
- regular paint devices, which are first copied into a fixed device for mirrored reuse

This path is simple and convenient, which makes it attractive for engines that already build one temporary local result per `paintAt()`.

#### Path B: async dab mirroring inside `KisBrushOp`

The default pixel brush engine takes a more specialized route. `KisBrushOp::doAsynchronousUpdate()` does not simply render a main dab and then call the generic helper. Instead, it:

- collects ready `KisRenderedDab` objects from `KisDabRenderingExecutor`
- splits dirty space into non-overlapping rectangles
- schedules concurrent `bltFixed()` jobs for the primary dabs
- appends mirroring jobs through `addMirroringJobs(...)`

This design exists for good reasons:

- the async dab pipeline already tracks dirty rects and batching
- mirrored output should participate in the same update-period calculation
- some rendered dabs may share the same underlying `KisFixedPaintDevice`

The last point is especially important. `addMirroringJobs(...)` inserts sequential barriers and tracks the previous dab device so Krita does not mirror shared pixel data twice. That is what the `skipMirrorPixels` flag is protecting against.

In other words, the pixel brush engine does not treat mirroring as a cosmetic post-step. It treats it as part of its scheduling and memory-sharing model.

### 7.4 Geometry helpers separate coordinate mirroring from pixel mirroring

`KritaUtils` provides utilities such as:

- `mirrorDab(...)`
- `mirrorRect(...)`
- `mirrorPoint(...)`

These helpers do not all perform the same work:

- `mirrorRect(...)` moves a rectangle to its mirrored position
- `mirrorDab(...)` can update a rendered dab's offset and optionally mirror its pixels
- `mirrorPoint(...)` mirrors coordinates only

This separation matters because sometimes Krita needs to move geometry without immediately touching pixel buffers, and sometimes it needs to mirror actual dab contents.

### 7.5 Selection masks and mirrored dabs must stay aligned

The fixed-dab overload `renderMirrorMask(QRect, KisFixedPaintDeviceSP, KisFixedPaintDeviceSP)` mirrors both:

- the dab
- the mask

before calling `bltFixedWithFixedSelection(...)`.

That is an easy place to introduce bugs when changing selection-aware painting or mirrored mask rendering. If the mask and dab are mirrored with different assumptions, the mirrored result will look offset or clipped even though the primary dab is correct.

### 7.6 Non-incremental mirroring has an overlap problem

`renderDabWithMirroringNonIncremental()` shows another subtlety: mirrored target rectangles can intersect each other. When that happens, the order of clearing and recompositing matters.

The implementation:

- builds all mirrored rects
- clears them
- checks whether the mirrored destinations intersect
- falls back to a safer recompositing path when needed

This is a reminder that mirroring is not just "paint the same dab three more times". When mirrored copies overlap, Krita has to avoid cyclic self-recompositing artifacts.

### 7.7 Mirroring interacts with wrap-around and temporary devices

Mirroring is layered on top of the same storage and access rules described in the tiled-painting section:

- temporary composition devices inherit default bounds and wrap-around support
- wrap-around-aware normalization may duplicate dabs before or after mirroring, depending on the engine path
- dirty rects must describe the mirrored results accurately or projection updates will be wrong

This is why mirror bugs can sometimes be storage bugs or scheduling bugs in disguise.

### 7.8 Maintainer checklist for mirror-related changes

If you change anything around dab generation, dirty-rect calculation, or temporary-device blitting, verify all of these:

- horizontal mirror only
- vertical mirror only
- both mirrors enabled
- mirrored painting in LOD mode
- mirrored painting near wrap-around boundaries
- mirrored painting with selections or masking brushes
- mirrored painting in engines that use `renderMirrorMask(...)`
- mirrored painting in `KisBrushOp`'s async update path

If one of those paths fails, the bug is usually not "just in the UI". It is usually a mismatch between painter state, dab geometry, or tiled-device updates.

## 8. Asset-Backed Brush Tips and Paper Textures

Many of Krita's most interesting presets are not defined only by numeric sliders. They depend on external image assets:

- a brush tip resource, such as a `.png`, `.gbr`, `.gih`, or `.svg`
- a texture or "paper" resource, usually a `KoPattern`

From the user's point of view, these are just preset ingredients. From the engine's point of view, they are linked resources that must be resolved, cloned into the stroke snapshot, interpreted correctly, and then fed through the same dab pipeline as any other brush.

### 8.1 Where these assets live in a preset

In the serialized preset data, the two key places are:

- `brush_definition`: XML describing the brush tip resource and how it should be used
- `Texture/Pattern/*`: metadata identifying the linked paper/texture pattern and its processing parameters

For a brush-based paintop, resource discovery happens through the factory layer:

1. `KisPaintOpPreset::linkedResources()` asks the paintop factory for linked resources.
2. `KisBrushBasedPaintOp::prepareLinkedResources()` adds both:
   - the linked `KisBrush` resource via `KisBrushOptionProperties`
   - the linked pattern resource via `KisTextureOption::prepareLinkedResources()`
3. `cloneWithResourcesSnapshot()` moves those resources into a local stroke snapshot so worker-thread painting does not need to query the global database.

This is why an asset-backed preset can keep painting correctly even when the stroke is running asynchronously.

There is also an important portability detail for paper textures. `KisEmbeddedTextureData` stores the pattern signature fields such as md5, filename, and name, and can also carry the pattern bytes as base64. At runtime `loadLinkedPattern()` first tries to resolve the pattern from the resource database and then falls back to the embedded payload if the external resource is missing. That is how textured presets can remain self-contained enough to survive resource moves or bundle export/import.

### 8.2 Example A: `g)_Dry_Brushing.kpp`

This preset is a very good example because it combines both asset types in a single `paintbrush` preset:

- `paintopid="paintbrush"`
- `brush_definition` uses `type="png_brush"` with `filename="random_particles.png"`
- `Texture/Pattern/Enabled=true`
- `Texture/Pattern/PatternFileName=.../4-paper-soft-grain_testtweak2.png.pat`
- `Texture/Pattern/TexturingMode=1`, which maps to `SUBTRACT`

So this preset is not just "a paintbrush with some roughness". It is:

1. a linked PNG brush tip
2. rendered by the default pixel brush engine
3. postprocessed against a tiled paper texture pattern

#### Step A1: The brush tip is loaded as a `KisBrush` resource

The `brush_definition` XML is parsed by `KisBrushOptionProperties::readOptionSettingResourceImpl()`, which calls `KisBrush::fromXML(...)`.

From there:

- `KisBrushRegistry` chooses a brush factory based on the XML `type`
- for this preset, the registry routes to `KisPredefinedBrushFactory("png_brush")`
- the factory resolves the resource through `resourcesInterface->source<KisBrush>(ResourceType::Brushes).bestMatch(...)`
- the resolved brush is cloned and then receives preset-local overrides such as spacing, autospacing, scale, angle, and brush application

That last point is important. The resource file defines the raw asset, but the preset still controls how the engine uses it.

#### Step A2: The PNG tip is interpreted by brush type and application mode

`KisPngBrush::loadFromDevice()` loads the PNG into a `QImage`, inspects whether it is grayscale and whether it has alpha, and then chooses a runtime interpretation:

- pure grayscale without alpha becomes a mask-like brush
- colored or alpha-bearing images can become `ALPHAMASK`, `LIGHTNESSMAP`, or `IMAGESTAMP` style brushes depending on their contents and preset metadata

That is a key design detail: the same asset format does not always imply the same dab semantics.

Once loaded, the brush tip is stored in a brush pyramid and later queried through:

- `maskWidth()`
- `maskHeight()`
- `characteristicSize()`
- `generateMaskAndApplyMaskOrCreateDab()`

So the engine never treats `random_particles.png` as "just a file". It becomes a reusable runtime brush object with scaling, subpixel alignment, spacing, and dab-generation behavior.

#### Step A3: The base dab is generated first

For the default pixel brush path, `KisBrushOp::paintAt()` builds a `KisDabCacheUtils::DabRequestInfo` and hands it to the threaded dab executor.

Later, `KisDabCacheUtils::generateDab()` decides how to turn the brush tip into pixels:

- if the brush application is `IMAGESTAMP`, it asks the brush for a full paint device with `brush->paintDevice(...)`
- otherwise it uses `brush->mask(...)` or `generateMaskAndApplyMaskOrCreateDab(...)` to produce a colored dab from the current paint color or color source

This is the point where the tip asset becomes an actual raster dab.

#### Step A4: The paper texture is applied as postprocessing

The paper material is not part of brush-tip loading. It is a later stage.

`KisBrushOpResources` constructs a `KisTextureOption` from the preset settings and the stroke-local resource interfaces. That object:

- reads `Texture/Pattern/*` settings
- resolves the linked `KoPattern`
- converts it into a cached `KisTextureMaskInfo`
- remembers scale, brightness, contrast, invert, cutoff, and texturing mode

`KisTextureMaskInfo::recalculateMask()` turns the pattern image into a raster mask:

- it reads the `KoPattern`'s `QImage`
- scales it according to the texture settings and LOD
- converts brightness/contrast/neutral point
- optionally uses alpha or grayscale-derived opacity
- caches the resulting mask in a `KisPaintDevice`

Then `KisDabCacheUtils::postProcessDab()` calls `textureOption->apply(dab, dabTopLeft, info)`.

That method does something very specific:

1. It computes the pattern patch position from the dab's image-space top-left corner.
2. It tiles the paper pattern over the dab region using `KisFillPainter`.
3. It applies the chosen texture blend mode and strength to the dab pixels.

That means the paper texture is anchored in image space, not in brush-local UV space. As the stroke moves, the dab samples a different part of the same repeating paper material instead of dragging the material with the brush tip.

#### Step A5: Cache behavior matters

Texture and sharpness options mutate the dab after it has been generated. Because of that, Krita marks such dabs as `needsPostprocessing`.

This matters for caching:

- the engine may preserve an original untextured dab
- then reapply postprocessing when the cached geometry is reused

Without that split, cached dabs could accumulate texture repeatedly and become incorrect.

### 8.3 Example B: `z)_Stamp_Leaves.kpp`

This preset is useful because it shows a different kind of image asset:

- `paintopid="paintbrush"`
- `brush_definition` uses `type="svg_brush"`
- `filename="leaves-scattered.svg"`

The rest of the stroke framework is the same, but the tip-loader path is different.

`KisBrushRegistry` again dispatches from the `brush_definition` type, but this time the factory resolves an SVG-backed brush resource. `KisSvgBrush::loadFromDevice()`:

- reads the raw SVG bytes
- renders them through `QSvgRenderer`
- rasterizes the result into a `QImage`
- converts the result into an indexed grayscale mask
- stores it as a brush tip image

So even though the asset is vector, the runtime paint engine still works with a rasterized `KisBrush` representation. That is a recurring Krita pattern: high-level resources can have very different source formats, but by the time the stroke engine uses them, they are normalized into a common brush/dab interface.

### 8.4 Generic processing model for asset-backed brushes

Putting both examples together, the runtime model looks like this:

1. The preset references external assets through `brush_definition` and optional `Texture/Pattern/*` fields.
2. The paintop factory declares those assets as linked resources.
3. The preset is cloned with a local resources snapshot for the stroke.
4. The brush resource is resolved into a concrete `KisBrush` subtype such as:
   - `KisPngBrush`
   - `KisGbrBrush`
   - `KisSvgBrush`
   - `KisImagePipeBrush`
5. The paintop asks the brush to create the base dab.
6. Optional postprocessing such as texture/paper application mutates the dab.
7. The final dab is composited into the target paint device.

The important architectural separation is:

- brush tip resource loading decides what the source shape/image is
- paintop logic decides where and how often to place it
- texture/paper processing decides how the already-generated dab is altered before compositing

### 8.5 Maintenance rules for asset-backed brushes

When you modify or debug this area, keep these rules in mind:

- If the preset cannot find its brush or pattern asset, start with linked-resource preparation and `resourcesInterface` lookups before touching painting code.
- If the tip shape is correct but the material feel is wrong, debug `KisTextureOption` and `KisTextureMaskInfo`, not `KisBrush`.
- If a cached textured brush looks progressively more distorted, check whether postprocessing is being reapplied to an already-postprocessed dab.
- If the same preset behaves differently at different zoom or LOD levels, check both the brush scaling path and the texture-mask recalculation path.
- If a brush asset comes from a different source format, such as PNG versus SVG, expect the loader to differ but the downstream dab pipeline to stay mostly the same.

## 9. Final Advice

When you maintain Krita's brush engine, keep three questions in your head:

1. Where is this feature evaluated: tool layer, paintop layer, brush-tip layer, or compositing layer?
2. Is this state per event, per dab, per stroke, or per document?
3. Does the feature still work when painting is threaded, mirrored, wrapped, selected, indirect, and low-detail?

If you can answer those three questions for a change, you usually understand the code well enough to implement it safely.
