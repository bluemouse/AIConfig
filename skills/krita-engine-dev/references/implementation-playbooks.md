# Implementation playbooks

## Playbook A: Modify the default pixel brush engine

Use this when the requested feature is option-driven dab stamping: size, opacity, flow, rotation, scatter, spacing, softness, texture, sharpness, color source, or async update policy.

1. Locate the option domain.
   - Settings and options usually live under `plugins/paintops/libpaintop/` or the default paintbrush plugin directory.
   - Runtime evaluation for the default engine centers on `plugins/paintops/defaultpaintops/brush/kis_brushop.cpp`.
2. Decide where the feature is evaluated.
   - Per sample: use `KisPaintInformation` and option evaluators.
   - Per dab: evaluate inside `KisBrushOp::paintAt()` before creating `DabRequestInfo`.
   - Postprocess: integrate with `KisDabCacheUtils::postProcessDab()` or a resource object used there.
   - Final composite: integrate with `KisPainter`/composite op path only if blending semantics change.
3. Thread settings through serialization and UI.
   - Add/extend `KisPaintOpSettings` data keys.
   - Update the config widget.
   - Preserve old preset compatibility with defaults.
4. Respect resource snapshotting.
   - Declare new linked/embedded resources in the factory path.
   - Ensure the runtime paintop uses the cloned stroke-local resource.
5. Preserve async behavior.
   - If dab generation remains heavy, keep it inside the executor/queue model.
   - If postprocessing changes cache semantics, ensure cached base dabs are not repeatedly mutated.
6. Test the edge matrix.
   - mirror h/v/both
   - wrap-around at edges and corners
   - selection and fixed selection masks
   - masking brush and indirect painting
   - LOD painting
   - preset save/load and bundle portability
   - airbrush/timing and very short lines

Common pitfalls:

- Adding per-dab heap allocation in `paintAt()`.
- Recomputing texture masks per dab when they can be cached per setting/resource/LOD.
- Applying postprocess to already-postprocessed cached dabs.
- Forgetting the LOD scale multiplier.
- Updating visual output without expanding dirty rects.

## Playbook B: Add a new Krita paintop plugin

Use this when the requested engine has fundamentally different semantics: particle spray, smudge/local sampling, procedural geometry, multi-dab synthesis, or a new simulation model.

1. Choose the base class.
   - Use `KisBrushBasedPaintOp` if the engine relies on brush tips and existing dab/resource infrastructure.
   - Derive from `KisPaintOp` directly if the engine is not naturally brush-tip based.
2. Define settings and runtime state.
   - Create a `KisPaintOpSettings` subclass for engine parameters.
   - Create a `KisPaintOpConfigWidget` for user controls.
   - Decide which state is per stroke, per dab, per resource, or per document.
3. Implement the paint contract.
   - `paintAt()` must emit work and return spacing.
   - `updateSpacingImpl()` must match the spacing logic used by `paintAt()`.
   - `updateTimingImpl()` is required for airbrush/timed emission.
   - Override line/curve only when default interpolation is wrong for the engine.
4. Decide sync vs async.
   - Synchronous engines can render temporary devices and blit immediately.
   - Heavy dab or particle engines may need a queue/executor and `doAsynchronousUpdate()`.
   - Async engines must handle final flush on stroke end/cancel paths.
5. Register the engine.
   - Use a plugin factory pattern similar to existing paintops under `plugins/paintops/`.
   - Register with `KisPaintOpRegistry` using a unique paintop id.
   - Update build files and plugin JSON metadata as required by the current checkout.
6. Declare resources.
   - Implement linked/embedded resource preparation for brush tips, patterns, gradients, images, or other assets.
   - Ensure preset clone/snapshot behavior works during threaded painting.
7. Validate integration.
   - Preset creation/edit/save/load.
   - Stroke start/end/cancel.
   - Undo/redo.
   - Dirty projection updates.
   - selections, mirroring, wrap, LOD, masking, indirect painting.

Recommended first files to compare:

- simple plugin registration: `plugins/paintops/experiment/` or `plugins/paintops/spray/`
- brush-tip-based runtime: default paintbrush and colorsmudge engines
- non-default behavior: spray, hairy, particle, sketch, color smudge

## Playbook C: Design a new stroke rendering engine for a painting application

Use this when the user is not modifying Krita directly but wants a Krita-like architecture.

### Core modules

1. **document model**
   - layer tree, masks, color spaces, image bounds, undo history, animation frames if needed.
2. **pixel storage**
   - sparse tiled/chunked storage, copy-on-write, snapshots/mementos, accessors exposing contiguous spans.
3. **stroke scheduler**
   - start/add/end/cancel lifecycle, job queue, dependency ordering, dirty-region collection, final flush.
4. **paint operation interface**
   - runtime engine contract: `paintAt`, `paintLine`, spacing, timing, async update, resource dependencies.
5. **resource and preset system**
   - immutable stroke snapshots, linked and embedded resources, serialization, versioned settings.
6. **compositor**
   - color-space conversion, blend modes, opacity/flow, selection masks, channel locks, GPU/CPU fallback strategy.
7. **projection and display**
   - dirty projection recomputation, canvas tiling/textures, display transforms, color management, UI throttling.
8. **tool/input layer**
   - tablet event sampling, smoothing/stabilizer, geometry tools, pressure/tilt/rotation mapping.

### Recommended data flow

```text
input sample -> stroke event -> scheduled stroke job -> paintop runtime -> dab/particle/local operation -> temporary or fixed source -> compositor -> tiled target device -> dirty node region -> projection update -> canvas display
```

### Essential contracts

- A paint operation returns spacing/timing consequences, not just pixels.
- Resources used by a stroke are immutable for that stroke.
- Final visual updates flow through dirty rectangles.
- Undo captures storage deltas at the right granularity.
- The UI never owns authoritative pixels.
- Async work has a final drain/flush path.

## Playbook D: Design GPU acceleration without breaking Krita-like semantics

Use this when the user asks about Vulkan/OpenGL/Metal/CUDA/compute acceleration for brush rendering.

Start by identifying which stage is being moved to GPU:

1. **canvas display only**: upload projection tiles/textures and render view transforms. This is safest and close to Krita's OpenGL canvas role.
2. **dab generation**: generate masks/noise/textures on GPU, then read back or composite on GPU.
3. **dab compositing**: blend source dabs into GPU-resident tiled layers.
4. **projection compositing**: compose layer tree on GPU.
5. **full GPU document model**: keep layers/tiles mostly GPU-resident with explicit synchronization and CPU fallback.

For each option, specify:

- authoritative storage: CPU tiles, GPU textures, or hybrid.
- synchronization: when CPU and GPU views become coherent.
- undo granularity: tile deltas, command log, or GPU snapshots.
- color management: where color conversion and blend modes execute.
- resource upload lifetime: brush tips, patterns, gradients, LUTs, random seeds.
- dirty tracking: tile/rect coverage across CPU and GPU queues.
- fallback path: non-GPU hardware, unsupported blend modes, huge images, memory pressure.

Critical warning: moving dab generation to GPU can be easy; preserving exact blend modes, color spaces, selections, undo, resource snapshots, and deterministic replay is the hard part.

## Playbook E: Debug a brush bug

Classify the symptom before changing code:

| symptom | likely subsystem |
|---|---|
| uneven dab spacing | `KisPaintInformation`, `KisDistanceInformation`, `KisPaintOpUtils::paintLine`, paintop spacing/timing |
| airbrush emits late or too fast | tool airbrush timer, `updateTimingImpl`, async update cadence |
| tip shape correct but blend wrong | `KisPainter::bltFixed`, color space, composite op, opacity/flow, selection |
| preset works in UI but fails during stroke | resource snapshot, linked/embedded resource declaration, threaded resource lookup |
| missing canvas updates | dirty rect collection, node dirty propagation, projection scheduling |
| mirror/wrap glitches | mirror geometry vs pixel mirroring, wrapped rect normalization, dirty rect coverage |
| LOD-only failure | LOD transform, buddy stroke job cloning, scaled resources, mirror axes in LOD coordinates |
| large-canvas slowdown | tile churn, conversions, per-dab allocation, decompression/swap, too-large dirty rects |

Debugging procedure:

1. Identify the paintop id used by the preset.
2. Reproduce with a minimal preset and a normal paint layer.
3. Add one complexity at a time: selection, mirror, wrap, LOD, indirect/mask, animation frame.
4. Trace source flow from tool to paintop to painter to dirty rects.
5. Measure before optimizing.
6. Validate preset save/load if settings/resources changed.

## Playbook F: Review a proposed patch/design

Use this checklist:

- Does the patch change tool geometry, paintop semantics, pixel compositing, storage, or UI display?
- Does it preserve the `paintAt` spacing/timing contract?
- Are all resources needed by worker-thread painting declared and snapshotted?
- Does it avoid GUI-thread resource/database access from paint code?
- Does it update dirty rects precisely enough?
- Does it work under mirror, wrap, selection, indirect, masking, and LOD?
- Does it preserve undo/redo and stroke cancel behavior?
- Does it avoid new per-dab allocations/conversions in hot paths?
- Does it keep CPU/GPU synchronization explicit if GPU work is involved?
- Are there tests or manual scenarios for both simple and complex strokes?
