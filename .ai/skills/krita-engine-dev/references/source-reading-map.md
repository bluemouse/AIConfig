# Source reading map

This map is a high-confidence guide for KDE/krita source navigation. Re-verify against the user's local checkout when exact paths or symbols matter.

## First-pass reading order

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
13. `libs/image/brushengine/kis_distance_information.*`
14. `libs/image/brushengine/kis_paintop_utils.h`
15. `libs/image/brushengine/kis_paintop_factory.h`
16. `libs/image/brushengine/kis_paintop_registry.*`
17. `libs/image/brushengine/kis_paintop_preset.*`
18. `plugins/paintops/defaultpaintops/brush/kis_brushop.cpp`
19. `plugins/paintops/defaultpaintops/brush/KisDabRenderingExecutor.*`
20. `plugins/paintops/defaultpaintops/brush/KisDabRenderingQueue.*`
21. `plugins/paintops/libpaintop/KisDabCacheUtils.*`
22. `libs/brush/kis_brush.cpp`
23. `libs/image/kis_paint_device.*`
24. `libs/image/tiles3/kis_tiled_data_manager.*`
25. `libs/image/tiles3/kis_tile_data.*`
26. `libs/ui/canvas/kis_canvas2.cpp`
27. `libs/ui/opengl/kis_opengl_canvas2.cpp`

After this, read one alternate paintop under `plugins/paintops/` to avoid overfitting your mental model to the default brush.

## Questions to ask while reading each layer

### Tool/input layer

- Where is the initial `KisPaintInformation` created?
- Where does smoothing/stabilization alter position or pressure?
- What job type is submitted for points, lines, curves, and shapes?
- What stroke-local resources are created at stroke start?

### Stroke/scheduler layer

- What starts the stroke, adds jobs, ends it, and cancels it?
- How are projection updates interleaved with stroke work?
- Is LOD buddy work created or cloned?
- Where are undo transactions opened and closed?

### Paintop layer

- What paintop id does the preset use?
- What factory constructs the runtime class?
- What does `paintAt()` emit?
- Does `paintAt()` return spacing consistent with `updateSpacingImpl()`?
- Does the engine use async updates?

### Brush/dab layer

- Does the engine use a brush tip resource or synthesize its own local geometry?
- Are dabs fixed devices, temporary paint devices, particles, or local sampling operations?
- What is cached? What is postprocessed?
- Are resource lookups stroke-local?

### Pixel/composite layer

- What source color space does the dab use?
- What composite op and opacity/flow parameters are passed?
- Is there a selection mask?
- Are writes tile-contiguous or fragmented?

### Projection/canvas layer

- What node/device was marked dirty?
- How are dirty rects normalized for mirror/wrap/indirect modes?
- What projection update is scheduled?
- Is the canvas path OpenGL or QPainter?

## Source anchors by common task

| task | start here | continue here |
|---|---|---|
| understand freehand stroke start | `kis_tool_freehand_helper.cpp` | `freehand_stroke.cpp`, `kis_painter_based_stroke_strategy.cpp` |
| debug spacing or airbrush timing | `kis_paintop.h`, `kis_paint_information.h` | paintop `paintAt`, `updateSpacingImpl`, `updateTimingImpl`, `kis_paintop_utils.h` |
| modify default pixel brush | `kis_brushop.cpp` | `KisDabRenderingExecutor`, `KisDabRenderingQueue`, `KisDabCacheUtils`, option classes |
| add a new paintop | small plugin under `plugins/paintops/` | `kis_paintop_factory.h`, registry, settings/widget classes |
| debug brush asset loading | brush option/resource classes | `libs/brush/`, brush registry/factories, texture option classes |
| debug blend/composite result | `kis_painter.cc` | `kis_painter_blt_multi_fixed.cpp`, `libs/pigment/` composite ops |
| debug missing visual updates | dirty issue sites in stroke strategy | node dirty propagation, projection update scheduling, canvas update compression |
| optimize large strokes | `kis_brushop.cpp` async update | tile accessors, dirty rect splitting, `KisDabRenderingQueue`, `KisPainter::bltFixed` |
| understand OpenGL canvas | `libs/ui/canvas/kis_canvas2.cpp` | `libs/ui/opengl/`, texture tile/update classes |
| reason about layers/masks | `KisNode`, `KisLayer`, `KisPaintLayer` | projection leaves/planes and mask/device classes |

## Useful source probes

Run the bundled script on a checkout:

```bash
python scripts/krita_source_probe.py --root /path/to/krita
```

For a narrower search without the script:

```bash
grep -R "KisBrushOp::paintAt" -n plugins/paintops/defaultpaintops libs
rg "KisImage::startStroke|KisUpdateScheduler::startStroke|KisStrokesQueue::startStroke" libs
rg "doAsynchronousUpdate|KisDabRenderingExecutor|KisDabRenderingQueue" plugins/paintops libs
rg "renderMirrorMask|mirrorDab|mirrorRect" libs plugins/paintops
rg "prepareLinkedResources|prepareEmbeddedResources|cloneWithResourcesSnapshot" libs plugins/paintops
```

Prefer `rg` when available, but fall back to `grep -R` in minimal environments.

## Verifying a preset route

1. Inspect the preset `.kpp` or embedded preset data.
2. Find `paintopid`.
3. Search for the matching registry registration.
4. Open the runtime paintop class created by the factory.
5. Compare settings keys used by the preset with the settings object and option evaluators.

Do not assume a preset name maps to a similarly named engine. A preset named like a spray or blender can still route through a different paintop id.

## Local patch orientation

When suggesting a patch, always name:

- file(s) likely to change
- classes/methods likely to change
- whether settings serialization is affected
- whether preset compatibility is affected
- whether resource snapshotting is affected
- whether build/plugin registration is affected
- whether tests should be unit, integration, benchmark, or manual

## Staleness rule

Krita source paths and plugin registration details can change. If the user's checkout disagrees with this map, trust the checkout. Search by class names and paintop ids rather than forcing old paths.
