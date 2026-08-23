# Krita brush/stroke architecture map

## Mental model

Krita is a layered image editor with scheduled strokes, paint operation plugins, tiled paint devices, resource-backed presets, color-managed compositing, and a projection/canvas display system. A raster brush stroke is not a direct widget draw. It is a sequence of scheduled jobs that ultimately composite dabs into a target `KisPaintDevice`, mark dirty regions, update layer projections, and refresh the canvas.

## Major subsystems

### UI and tool input

Typical source anchors:

- `libs/ui/tool/kis_tool_freehand_helper.cpp`
- `libs/ui/tool/strokes/freehand_stroke.h`
- `libs/ui/tool/strokes/freehand_stroke.cpp`
- `libs/ui/tool/strokes/kis_painter_based_stroke_strategy.cpp`
- `libs/ui/tool/kis_resources_snapshot.cpp`

Responsibilities:

- Convert tablet/mouse events into `KisPaintInformation`.
- Apply smoothing/stabilizer/pixel-perfect behavior.
- Build `KisResourcesSnapshot` at stroke start.
- Create stroke-local painters and strategy data.
- Submit jobs to `KisStrokesFacade` rather than painting inline.

Key lesson: tools own input interpretation and geometry; paintops own brush behavior.

### Image scheduler and stroke queue

Typical source anchors:

- `libs/image/kis_image.cc`
- `libs/image/kis_update_scheduler.cpp`
- `libs/image/kis_strokes_queue.cpp`
- `libs/image/kis_stroke_strategy.h`
- `libs/image/KisRunnableStrokeJobData.*`

Responsibilities:

- Accept strokes through `KisImage::startStroke()` / facade calls.
- Balance stroke jobs, projection updates, spontaneous image jobs, undo, and LOD paths.
- Clone or transform jobs for low-detail interactive painting when needed.
- Keep painting and projection synchronized enough for responsive live drawing.

Key lesson: live drawing responsiveness is a scheduler and dirty-update problem as much as a brush algorithm problem.

### Paintop framework

Typical source anchors:

- `libs/image/brushengine/kis_paintop.h`
- `libs/image/brushengine/kis_paint_information.h`
- `libs/image/brushengine/kis_distance_information.*`
- `libs/image/brushengine/kis_paintop_utils.h`
- `libs/image/brushengine/kis_paintop_factory.h`
- `libs/image/brushengine/kis_paintop_registry.*`
- `libs/image/brushengine/kis_paintop_preset.*`

Responsibilities:

- Define the runtime brush engine contract.
- Convert sample data into dabs, particles, smudge operations, or other local paint results.
- Report spacing and timing through the framework contract.
- Register engines through factories so presets can instantiate runtime paintops.

Key lesson: a preset chooses a paintop by paintop id; preset names are not reliable source-code routing information.

### Default raster brush path

Typical source anchors:

- `plugins/paintops/defaultpaintops/brush/kis_brushop.cpp`
- `plugins/paintops/defaultpaintops/brush/KisDabRenderingExecutor.*`
- `plugins/paintops/defaultpaintops/brush/KisDabRenderingQueue.*`
- `plugins/paintops/libpaintop/KisDabCacheUtils.*`
- `plugins/paintops/libpaintop/*Option*`
- `libs/brush/kis_brush.cpp`

Responsibilities:

- Evaluate size, ratio, rotation, scatter, opacity, flow, spacing, timing, softness, texture, and sharpness.
- Generate or reuse brush-tip dabs.
- Defer expensive dab generation through an async queue when useful.
- Flush prepared dabs through `KisPainter::bltFixed()` jobs.

Key lesson: the default pixel brush is option-driven dab generation plus asynchronous staging and batched compositing.

### Pixel storage and compositing

Typical source anchors:

- `libs/image/kis_paint_device.*`
- `libs/image/tiles3/kis_tiled_data_manager.*`
- `libs/image/tiles3/kis_tile_data.*`
- `libs/image/kis_random_accessor_ng.*`
- `libs/image/kis_painter.*`
- `libs/image/kis_painter_blt_multi_fixed.cpp`
- `libs/pigment/KoColorSpace.*`
- `libs/pigment/KoCompositeOp.*`

Responsibilities:

- Store pixels in sparse 64x64 tiles with copy-on-write behavior.
- Provide efficient accessors that expose tile-contiguous spans.
- Composite fixed dabs and devices through color-space-specific composite operations.
- Integrate selections, opacity, flow, channel locks, and composite ops.

Key lesson: many brush performance bugs are really tile access, conversion, or compositing bugs.

### Layers, nodes, projections, and canvas

Typical source anchors:

- `libs/image/kis_node.*`
- `libs/image/kis_layer.*`
- `libs/image/kis_paint_layer.*`
- `libs/image/kis_projection*`
- `libs/ui/canvas/kis_canvas2.cpp`
- `libs/ui/opengl/kis_opengl_canvas2.cpp`
- `libs/ui/kis_prescaled_projection.*`
- `libs/ui/kis_canvas_updates_compressor.*`

Responsibilities:

- Maintain the image node tree and layer/mask semantics.
- Recompute affected projections when nodes become dirty.
- Upload/display updated projection data on QPainter or OpenGL canvas paths.
- Keep user interaction responsive through throttled canvas/projection updates.

Key lesson: a dab is not visible just because it exists; it must be composited, marked dirty, projected, and displayed.

## Standard freehand raster stroke flow

1. A freehand tool samples a tablet or pointer event.
2. `KisToolFreehandHelper` creates or updates `KisPaintInformation` and handles smoothing/stabilization.
3. Stroke start creates `KisResourcesSnapshot` and stroke-local painters.
4. `FreehandStrokeStrategy` receives job data such as point, line, curve, polyline, rectangle, ellipse, or polygon.
5. `KisPainterBasedStrokeStrategy` initializes target devices, selections, transactions, indirect painting, masking-brush support, and painters.
6. `KisPainter::setPaintOpPreset()` asks `KisPaintOpRegistry` to create a concrete runtime paintop.
7. `KisPainter::paintAt()` or line/curve dispatch reaches `KisPaintOp`.
8. The paintop uses `KisPaintInformation` and `KisDistanceInformation` to decide where, when, and how to emit work.
9. For `KisBrushOp`, a dab request is submitted to `KisDabRenderingExecutor`.
10. `KisDabCacheUtils` and `KisBrush` generate the base dab; postprocess may apply sharpness and texture.
11. Async update jobs collect prepared dabs, split dirty regions, handle wrap/mirror, and call `KisPainter::bltFixed()`.
12. `KoColorSpace::bitBlt()` and the active composite op merge dab pixels into tiled destination storage.
13. Dirty rects are collected and issued to the node/image projection system.
14. Projection updates feed the QPainter/OpenGL canvas for visual refresh.

## Cross-cutting features

### Mirroring

Mirror state is injected through painter setup before paintop construction. Generic engines may use `KisPainter::renderMirrorMask()`. `KisBrushOp` handles mirroring inside its async update path with special care for shared dab devices.

Always test horizontal-only, vertical-only, both axes, LOD, selection, masking brush, and wrap-around edge cases.

### Wrap-around mode

Wrap-around is both coordinate remapping and update-region normalization. Low-level accessors can remap coordinates, while paintops may duplicate or clip dabs around the wrap rectangle before blitting.

Always test canvas edges, corners, mirrored wrap, and dirty-rect coverage.

### LOD painting

The stroke queue may create a low-detail buddy stroke. Paintops must scale geometry and resources correctly through LOD transforms. Changes that work only at full resolution are incomplete.

### Indirect painting and masking brushes

Some operations render into temporary devices and merge later. Painter initialization and dirty merge logic must preserve selection, masking brush, undo, and node update semantics.

### Resources and presets

A `.kpp` preset is a resource-backed engine configuration. It points to a paintop id plus settings and linked/embedded resources. Runtime painting should use stroke-local snapshots, not global resource database lookups.
