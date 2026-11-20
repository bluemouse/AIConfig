# Krita Programming Guide: Deep Engine Reference

Extended source-level reference complementing the focused references (`architecture-map.md`, `core-classes-and-contracts.md`, `implementation-playbooks.md`, `pixel-layer-gpu-performance.md`, `source-reading-map.md`). Read those focused references first; load this guide for checkout/build orientation, low-level tiled/memento mechanics, concrete multi-preset engine comparisons, mirroring internals, and asset/texture dab pipelines.

## 1. Checkout & Upstream Companion Docs

- Repository orientation: `HACKING`, `README.md`, and `libs/resources/ResourcesDesignNotes.md` (resource-snapshot rationale).
- External docs: [Krita User Manual](https://docs.krita.org/en/user_manual.html) (artist-observable behavior), [Build Instructions](https://docs.krita.org/en/untranslatable_pages/building_krita.html) (CMake/dependency setup), [Krita API Docs](https://api.kde.org/extragear-api/graphics-apidocs/krita/html/index.html).
- Code reading order and `rg` probes: see [source-reading-map.md](source-reading-map.md).

## 2. Non-Obvious Framework Seams

Subsystem boundaries and class tables live in [architecture-map.md](architecture-map.md) and [core-classes-and-contracts.md](core-classes-and-contracts.md). Keep these source-specific seams in mind when modifying existing engines:

- **Timing & opacity split:** in `KisBrushOp`, `updateTimingImpl()` delegates to `effectiveTiming(...)`; opacity/flow evaluate pre-queue, sharpness/texture run in `KisDabCacheUtils::postProcessDab()`, and final opacity also feeds `KoCompositeOp::ParameterInfo`.
- **Masking brushes require indirect painting:** `KisPainterBasedStrokeStrategy::initStrokeCallback()` and `initPainters()` wire masking brushes on top of indirect-painting temporary targets. Never alter painter initialization without testing masked presets.
- **LOD scaling:** `KisStrokesQueue` clones jobs for LOD buddy strokes; `KisBrushOp` scales geometry via `KisLodTransform::lodToScale(...)`.
- **Canvas-dependent resource snapshots:** `KisPaintOpPreset::cloneWithResourcesSnapshot(...)` clones linked/embedded resources (`KisPaintOpFactory::prepareLinkedResources` / `prepareEmbeddedResources`) **and** bakes canvas state (foreground/background color) into local storage so gradients and color sources stay deterministic on worker threads.
- **Plugin registration seam:** new engines under `plugins/paintops/` typically register via `K_PLUGIN_FACTORY_WITH_JSON(...)` and `KisPaintOpRegistry::instance()->add(new KisSimplePaintOpFactory<Op, Settings, Widget>(...))` (compare `plugins/paintops/experiment/experiment_paintop_plugin.cpp` and `plugins/paintops/spray/spray_paintop_plugin.cpp`). Step-by-step extension workflows: [implementation-playbooks.md](implementation-playbooks.md).

## 3. Low-Level Tiled Storage & Accessor Mechanics

High-level tile properties (`64x64` sparse CoW tiles, `extent()` vs `exactBounds()`, temporary vs fixed devices) live in [pixel-layer-gpu-performance.md](pixel-layer-gpu-performance.md). Low-level `libs/image/tiles3/` details that govern inner loops:

- **`KisTile` vs `KisTileData`:** `KisTile` holds grid coordinates `(col, row)` and extent linkage; `KisTileData` (`WIDTH = 64`, `HEIGHT = 64`) owns the pixel buffer, refcount, and CoW sharing across devices and undo revisions.
- **`KisTiledDataManager` transfer modes:**
  - `bitBlt(...)` — rectangle-exact copy sharing untouched full tiles via CoW.
  - `bitBltRough(...)` — tile-granular CoW share of every touched tile (copies excess border pixels; used for temporary devices and LOD sync where speed outweighs exact bounds).
- **Tile-native undo (`KisMementoManager`):** undo is built into tile storage rather than layered above it. `KisTiledDataManager::getTilesPair()` fetches both the live tile and committed baseline tile in one lookup so iterators read old/current state without duplicate hash traffic.
- **Span-oriented blitting (`KisRandomAccessor2`):** caches tile locks and exposes `rawData()`, `numContiguousColumns()`, `numContiguousRows()`, and `rowStride()`. `KisPainter::Private::applyDevice()` queries contiguous spans up to the next 64-pixel tile boundary and passes whole spans to `KoColorSpace::bitBlt()`.
- **Wrap-around accessor (`KisWrappedRandomAccessor`):** remaps coordinates into the wrap rectangle before delegating to tiled access — no duplicated image storage, paired with high-level dab splitting in `KisBrushOp::doAsynchronousUpdate()`.
- **Residency states:** `KisTileData` transitions across `NORMAL`, `COMPRESSED`, and `SWAPPED` (with slab pools for common pixel sizes). Extra full-region passes over large canvases trigger swap-in, decompression, and CoW allocation churn.
- **Composition-source helpers:** `createCompositionSourceDevice()` and `createCompositionSourceDeviceFixed()` preserve the target's composition source color space, default pixel/bounds, and wrap-around semantics.

## 4. Three Concrete Presets on One Paintop Framework

A `.kpp` file is not an engine; its `paintopid` selects the `KisPaintOpFactory` in `KisPaintOpRegistry` regardless of the preset's artist-facing name.

### 4.1 `b)_Airbrush_Soft.kpp` (`paintopid="paintbrush"` → `KisBrushOp`)

- **Registration:** `plugins/paintops/defaultpaintops/defaultpaintops_plugin.cc` via `KisSimplePaintOpFactory`.
- **Key settings:** `AirbrushOption/isAirbrushing=true` + explicit airbrush rate.
- **Execution:** stays entirely inside `KisBrushOp`; `KisToolFreehandHelper` inspects preset timing capabilities before stroke start, and temporal emission comes from `updateTimingImpl()` + option curves rather than a dedicated airbrush tool or engine.

### 4.2 `v)_Texture_Pointillism.kpp` (`paintopid="spraybrush"` → `KisSprayPaintOp`)

- **Registration:** `plugins/paintops/spray/spray_paintop_plugin.cpp` (custom factory, settings, widget; does **not** inherit `KisBrushBasedPaintOp` or use `KisDabRenderingExecutor`).
- **Execution:** `KisSprayPaintOp::paintAt()` clears/reuses a composition-source `KisPaintDevice`, delegates multi-particle synthesis with per-particle color variation to `SprayBrush::paint(...)`, commits the region in one `painter()->bitBlt(...)`, and mirrors via `painter()->renderMirrorMask(...)`.

### 4.3 `k)_Blender_Basic.kpp` (`paintopid="colorsmudge"` → `KisColorSmudgeOp`)

- **Registration:** `plugins/paintops/colorsmudge/colorsmudge_paintop_plugin.cpp` (inherits `KisBrushBasedPaintOp`, adds strategy layer).
- **Execution:** selects `KisColorSmudgeStrategyLightness`, `KisColorSmudgeStrategyMask`, `KisColorSmudgeStrategyStamp`, or legacy strategies from brush application + overlay + smudge mode; tracks separate source and destination dab rects to smear/blend prior canvas state alongside color rate/gradients; uses `KisInterstrokeDataFactory` when state must persist across strokes and manages precision-specific intermediate color spaces.

**Architectural takeaway:** `KisPaintOp` standardizes stroke lifecycle, spacing/timing, and resource snapshots while permitting radically different inner pipelines (async dab queue, synchronous particle batch, stateful local compositor).

## 5. Mirroring Internals

1. **Pre-construction injection:** `KisResourcesSnapshot::setupPainter()` calls `KisPainter::setMirrorInformation(...)` before paintop construction so engines can allocate mirror-aware auxiliary state immediately.
2. **LOD coordinate mapping:** `KisPainter::renderMirrorMask(...)` maps the image-space mirror axis center through `KisLodTransform` before computing mirrored rects — check this first for LOD-only mirror offsets.
3. **Two execution paths:**
   - **Generic (`KisPainter::renderMirrorMask`):** used by `KisSprayPaintOp`, `KisHairyPaintOp`, etc. Computes `mirrorX`/`mirrorY`, flips `KisFixedPaintDevice` in-place via `dab->mirror(...)`, and calls `bltFixed(...)` 1 or 3 times (overloads accept `KisPaintDevice` or fixed selection masks via `bltFixedWithFixedSelection(...)` after mirroring **both** dab and mask).
   - **Async pixel-brush (`KisBrushOp::doAsynchronousUpdate` → `addMirroringJobs`):** splits dirty space into non-overlapping rects, runs concurrent primary `bltFixed()` jobs, and appends mirror jobs with sequential barriers plus `skipMirrorPixels` tracking so dabs sharing an underlying `KisFixedPaintDevice` are never pixel-flipped twice.
4. **Geometry vs pixel helpers (`KritaUtils`):** `mirrorPoint(...)` and `mirrorRect(...)` transform coordinates only; `mirrorDab(...)` updates offset and optionally flips pixel bytes.
5. **Self-intersecting non-incremental mirrors:** `renderDabWithMirroringNonIncremental()` builds all mirrored rects, clears them, detects overlapping mirrored destinations, and falls back to a safe recomposite order to avoid cyclic self-blending.
6. **Verification matrix:** test horizontal-only, vertical-only, both axes, LOD active, wrap-around boundaries, active selection/masking brush, `renderMirrorMask` engines, and `KisBrushOp` async updates.

## 6. Asset-Backed Brush Tips & Paper Textures

Presets bind external assets via `brush_definition` XML (`.png`, `.gbr`, `.gih`, `.svg`) and `Texture/Pattern/*` settings (`KoPattern`). `KisBrushBasedPaintOp::prepareLinkedResources()` collects both (`KisBrushOptionProperties` + `KisTextureOption::prepareLinkedResources()`), and `cloneWithResourcesSnapshot()` isolates them for worker threads. For portability, `KisEmbeddedTextureData` stores pattern md5/filename/name plus optional base64 bytes; `loadLinkedPattern()` queries the resource DB first and falls back to embedded bytes.

### 6.1 PNG Tip + Subtract Paper Texture (`g)_Dry_Brushing.kpp`)

- **Settings:** `paintopid="paintbrush"`, `type="png_brush"` (`random_particles.png`), `Texture/Pattern/Enabled=true`, `TexturingMode=1` (`SUBTRACT`).
- **Tip load:** `KisBrushOptionProperties::readOptionSettingResourceImpl()` → `KisBrush::fromXML(...)` → `KisBrushRegistry` → `KisPredefinedBrushFactory("png_brush")` → `resourcesInterface->source<KisBrush>(ResourceType::Brushes).bestMatch(...)`, cloned with preset spacing/scale/angle/application overrides. `KisPngBrush::loadFromDevice()` inspects grayscale/alpha to classify `ALPHAMASK`, `LIGHTNESSMAP`, or `IMAGESTAMP`, builds a mip pyramid, and serves `maskWidth()`, `maskHeight()`, `characteristicSize()`, and `generateMaskAndApplyMaskOrCreateDab()`.
- **Base dab (`KisDabCacheUtils::generateDab`):** queued via `DabRequestInfo`; `IMAGESTAMP` calls `brush->paintDevice(...)`, while mask modes call `brush->mask(...)` / `generateMaskAndApplyMaskOrCreateDab(...)` with the active paint color/source.
- **Image-space paper postprocess (`KisDabCacheUtils::postProcessDab`):** `KisBrushOpResources` builds `KisTextureOption` → `KisTextureMaskInfo::recalculateMask()` (scales `KoPattern` `QImage` for texture scale + LOD, applies brightness/contrast/neutral/invert/cutoff, caches a `KisPaintDevice` mask). `textureOption->apply(dab, dabTopLeft, info)` tiles the pattern from `dabTopLeft` via `KisFillPainter` — anchoring paper grain in **image space** rather than dragging it with the tip.
- **Cache safety (`needsPostprocessing`):** dabs mutated by texture or sharpness are flagged `needsPostprocessing` so `KisDabRenderingQueue` caches the untextured base dab and reapplies postprocessing cleanly instead of accumulating grain across reused dabs.

### 6.2 Vector SVG Tip (`z)_Stamp_Leaves.kpp`)

- **Settings:** `paintopid="paintbrush"`, `type="svg_brush"` (`leaves-scattered.svg`).
- **Tip load:** `KisSvgBrush::loadFromDevice()` renders SVG bytes via `QSvgRenderer` into a `QImage`, converts to an indexed grayscale mask, and enters the identical `KisBrush` pyramid and `KisDabCacheUtils` pipeline used by raster tips.

### 6.3 Asset Debugging Rules

- Missing tip or texture on worker threads → check factory `prepareLinkedResources` / `prepareEmbeddedResources` and `resourcesInterface` snapshot before touching paint code.
- Correct tip silhouette, wrong grain feel → inspect `KisTextureOption` and `KisTextureMaskInfo::recalculateMask()`, not `KisBrush`.
- Texture darkens/distorts on repeated dabs → verify `needsPostprocessing` base-dab separation in `KisDabRenderingQueue`.
- Zoom/LOD grain mismatch → check both `KisBrush` scale and `KisTextureMaskInfo` LOD scaling.
