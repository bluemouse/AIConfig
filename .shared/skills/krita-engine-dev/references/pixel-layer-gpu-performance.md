# Pixel logic, layer system, GPU workflow, and performance

## Pixel storage model

Krita's painting model is built around `KisPaintDevice`, not a flat framebuffer. A paint device is a facade over color-space-aware, sparse, tiled storage. For normal raster layers, the backing store is tile-based through `KisTiledDataManager`.

Key properties:

- tiles are 64x64 pixels in the tiled data layer
- storage is sparse; untouched regions do not require real tile buffers
- tile data can be shared and copy-on-write
- undo/mementos are integrated with tile state
- accessors expose tile-local contiguous spans for efficient inner loops
- tile data may be pooled, compressed, or swapped under memory pressure

Design implication: algorithms should operate on rectangles/spans/tiles, avoid random per-pixel overhead across tile boundaries, and avoid unnecessary full-canvas copies.

## `extent()` vs `exactBounds()`

`KisPaintDevice::extent()` is typically tile-aligned and approximate. `exactBounds()` is slower but reflects real painted pixels more precisely.

Use `extent()` for rough working regions and tile-oriented operations. Use `exactBounds()` when correctness depends on actual non-default pixels.

## Temporary composition devices

Paintops often render into temporary devices or fixed devices before committing to the target.

Reasons:

- preserve destination color space and default bounds
- support wrap-around and coordinate conventions
- isolate local generation from final composition
- support masking/indirect painting
- allow mirrored reuse of a fixed dab
- reduce direct writes to the target device during complex generation

Important distinction:

- `KisFixedPaintDevice`: good for a generated dab with fixed bounds and fast blitting.
- `KisPaintDevice`: good for temporary local composition when normal tiled access/default bounds are needed.

## Compositing path

The final merge typically goes through `KisPainter` and color-space composite logic:

1. A source dab/device has pixels in a known color space.
2. `KisPainter` prepares composite parameters: opacity, flow, composite op, selection, channel flags, source/destination spans.
3. The destination `KisPaintDevice` provides writable tile spans through accessors.
4. `KoColorSpace::bitBlt()` invokes the active `KoCompositeOp`.
5. Dirty rectangles are recorded for projection/canvas updates.

When the dab shape is correct but the result blends incorrectly, inspect composite parameters, color-space conversion, selection masks, and opacity/flow before changing brush-tip code.

## Layer and projection system

Painting usually targets a node's paint device. The layer tree is not just display order; it is the document graph for masks, group layers, filters, projection leaves, animation frames, and isolation modes.

After paint is committed:

1. affected dirty rects are associated with the target node or merge path
2. projection update jobs recompute affected regions
3. canvas update logic consumes the updated projection
4. UI repaint displays the result

A stroke is visually complete only after compositing, dirty marking, projection update, and canvas refresh have all happened.

## GPU and canvas integration

Krita has OpenGL canvas support, but source guidance should distinguish display acceleration from paint computation.

Typical UI/canvas responsibilities:

- choose OpenGL or QPainter canvas path
- maintain coordinates and view transforms
- consume projection updates
- upload/update texture tiles or prescaled projection data
- apply display conversion/proofing/exposure where relevant
- throttle or compress UI updates to maintain responsiveness

Do not claim that the brush engine itself is GPU-rendered unless the user-provided source path proves it. In a Krita-like architecture, the OpenGL/Vulkan canvas can be only the final display backend while brush computation remains CPU/tiled.

## Designing a GPU brush path

When proposing GPU acceleration, choose a specific strategy.

### Strategy 1: GPU dab generation, CPU compositing

Good for procedural masks, noise, brush-tip transforms, or texture generation. Requires readback or shared memory transfer before `KisPainter`-style CPU compositing.

Risks:

- readback stalls
- format conversion cost
- nondeterministic noise/randomness unless seeded carefully
- duplicated CPU/GPU resource caches

### Strategy 2: GPU compositing into GPU-resident tiles

Good when many dabs target already GPU-resident layer tiles. Requires GPU implementations of composite ops, selection masks, color conversion, and undo snapshots or deltas.

Risks:

- huge blend-mode surface area
- color-management mismatch
- CPU tools/filters needing coherent data
- synchronization and memory pressure

### Strategy 3: GPU projection only

Good for compositing display projections while retaining CPU authoritative layer data.

Risks:

- layer effects/blend modes may still need CPU fallback
- projection coherency and tile upload bandwidth
- harder debugging if CPU and GPU projection paths diverge

### Strategy 4: full GPU document model

Highest potential throughput, highest complexity. Only recommend when the application can constrain color models, blend modes, resource formats, filters, undo, and hardware targets.

## Live drawing performance hot paths

### Dab generation

Potential costs:

- brush-tip scaling/rotation
- subpixel mask generation
- colorization or image stamp conversion
- texture and sharpness postprocessing
- per-dab heap allocations
- repeated resource lookups

Optimizations:

- cache base dab geometry separately from postprocess when safe
- pool fixed devices and temporary buffers
- precompute option/resource state per stroke
- avoid global resource/database access during painting
- use async generation for expensive dabs

### Compositing/blitting

Potential costs:

- color-space conversion
- composite op complexity
- selection mask alignment
- tile boundary overhead
- copy-on-write tile churn
- too many tiny blits

Optimizations:

- split/merge dirty rectangles into non-overlapping useful regions
- use contiguous tile spans
- batch dabs where possible
- keep source/destination color spaces compatible when possible
- avoid reading/writing the same wrapped/mirrored region concurrently

### Dirty/projection/canvas updates

Potential costs:

- dirty rects too large
- projection recomputation too frequent
- UI repaint/update storms
- texture upload bandwidth

Optimizations:

- throttle update cadence adaptively
- emit precise but not fragmented dirty regions
- combine dabs into practical update batches
- maintain final flush at stroke end
- use LOD preview path for interaction if available

## Resource management rules

- Freeze stroke resources in snapshots.
- Declare linked and embedded resources in factories.
- Do not load brush files or patterns from disk on the dab hot path.
- Keep texture masks cached by resource/settings/LOD where possible.
- Treat random sources as per-stroke or per-dab state, not accidental globals.
- Handle missing external resources through embedded fallback or clear user-facing errors.

## Performance review checklist

Before approving a brush-engine performance change, answer:

- What is the hot path: input processing, dab generation, postprocess, composite, tile access, projection, texture upload, or UI repaint?
- Does it reduce work per dab or merely defer it?
- Does it add allocations, locks, conversions, or resource lookups per dab?
- Does it increase dirty area or projection frequency?
- Does it preserve async final flush and cancellation?
- Does it behave on very large canvases and sparse layers?
- Does it behave with swapped/compressed tiles under memory pressure?
- Does it preserve mirror, wrap-around, LOD, selections, and indirect painting?

## Minimal manual benchmark scenarios

Use simple manual cases when no benchmark harness is available:

1. small canvas, normal paint layer, no selection: baseline feel
2. large sparse canvas: tile allocation and dirty/projection behavior
3. huge brush with texture: dab generation and postprocess pressure
4. low spacing fast stroke: compositor and scheduler pressure
5. airbrush held still: timing/async update cadence
6. mirror h/v/both: duplicated rendering and dirty rects
7. wrap-around at corners: normalization and concurrency safety
8. active selection: mask alignment and composite cost
9. LOD interactive painting: scale, preview responsiveness, final sync
10. undo/redo after heavy stroke: storage delta and command correctness
