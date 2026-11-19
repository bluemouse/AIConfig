---
name: krita-engine-dev
description: Write, review, debug, and implement Krita brush engines, paintops, stroke scheduling, tiled compositing, presets/resources, layer projection, and canvas/GPU display. Use when working on KDE/krita source navigation, adding or modifying a paint engine, designing a new painting application's stroke system, optimizing dab generation and live drawing, or explaining how pixels flow from stylus samples to layers and canvas updates — even if the user doesn't say Krita. Triggers on KisPaintOp, KisBrushOp, KisStrokesQueue, KisResourcesSnapshot, KisPaintDevice, dab cache, spacing/timing, LOD buddy strokes, KisTransaction, and paintop plugin registration.
---

# Krita Engine Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Expert guidance for architecting, designing, debugging, and implementing Krita brush engines,
stroke rendering, tiled raster painting, paintop plugins, resources/presets, layer/projection
updates, canvas/GPU integration, and live drawing performance. Read bundled references on demand
— do not load all reference files unless the task requires them.

## When to Use

- Navigating or modifying KDE/krita brush/stroke/paintop source
- Adding, modifying, or debugging a `KisPaintOp` or default brush engine
- Designing a new painting application's stroke system inspired by Krita
- Debugging spacing, dab generation, compositing, dirty rects, or live-drawing performance
- Registering paintop plugins, presets, linked/embedded resources, or stroke snapshots
- Explaining pixel flow from tablet input through layers to canvas/projection updates

## When NOT to Use

- General native crash/UAF debugging with no painting-engine context — scientific debugging
  methodology outside Krita brush/stroke/paintop code
- Standalone GPU renderer architecture (render graphs, bindless, frames-in-flight) without
  Krita canvas/projection context — use
  [../gpu-rendering-guide/SKILL.md](../gpu-rendering-guide/SKILL.md)
- Qt desktop UI work unrelated to stroke scheduling or paintops — use
  [../qt-dev/SKILL.md](../qt-dev/SKILL.md)
- CMake/build setup for non-Krita C++ projects — use [../cmake-dev/SKILL.md](../cmake-dev/SKILL.md)
- MyPaint/libmypaint stroke and dab scheduling — use
  [../mypaint-engine-dev/SKILL.md](../mypaint-engine-dev/SKILL.md)
- Krita build/environment setup only, with no brush-engine design or code changes

## Operating stance

Act as an experienced Krita painting-engine engineer. Give source-grounded, implementation-oriented guidance for Krita's raster stroke engine and for painting applications inspired by it.

Prefer concrete engineering advice over generic graphics commentary. Always separate:

- **Krita-specific guidance**: names, paths, classes, paintop conventions, and integration seams in KDE/krita.
- **General painting-engine design**: architecture patterns that can be reused in a new application.
- **Assumptions or uncertainty**: anything not verified against the user's checkout or current upstream source.

When exact code matters, ask for or inspect the user's Krita checkout if available. If a local checkout is available, run `<SKILL_ROOT>/scripts/krita_source_probe.py --root <krita-root>` before making strong claims about file paths or symbols.

## Fast routing model

For every request, first identify the layer where the problem or feature belongs:

1. **tool/input layer**: pointer/tablet events, smoothing, stabilizer, freehand helper, geometry commands.
2. **stroke scheduling layer**: `KisImage`, `KisUpdateScheduler`, `KisStrokesQueue`, stroke jobs, LOD buddy strokes, `KisTransaction`, tile mementos/undo.
3. **paintop layer**: `KisPaintOp`, settings, paintop factory/registry, plugin registration (CMake, plugin metadata), spacing, timing, async updates.
4. **brush/dab layer**: `KisBrush`, brush tips, dab cache, texture/sharpness postprocess, image assets.
5. **pixel/composite layer**: `KisPainter`, `KisPaintDevice`, tiled storage, color spaces, composite ops, selections.
6. **node/projection/layer layer**: `KisNode`, paint layers, masks, dirty regions, projection updates.
7. **canvas/ui/gpu layer**: OpenGL/QPainter canvas choice, prescaled projections, texture upload/display, input feedback.
8. **resources/presets layer**: `KisPaintOpPreset`, `KisPaintOpSettings`, linked/embedded resources, stroke-local snapshots.

Use this routing to avoid debugging compositing when the issue is spacing, or debugging brush tips when the issue is resource snapshotting.

## Workflow

### 1. Classify

- Identify the routing layer and whether the task is Krita-specific or general painting-engine design.
- Read every matching row in [Reference routing](#reference-routing) before proposing changes.

### 2. Answer or implement

When the user asks for architecture, implementation, debugging, or optimization help, route the request through the Fast routing model, name the concrete Krita classes and files to inspect or modify, design against Core Krita invariants and Gotchas, and close with the verification steps below.

### 3. Verify

- Run `krita_source_probe.py` when a local checkout is available.
- Exercise the edge matrix: mirror, wrap, selection, indirect painting, masking brush, LOD, undo, async drain.
- Name the hot path when optimizing: dab generation, postprocess, blit/composite, tile access, dirty update, texture upload, or UI throttling.

## Core Krita invariants

Keep these rules explicit in design and review answers:

- Krita does not paint directly to the widget. Brush engines paint into `KisPaintDevice` instances; projections and canvas widgets display the result later.
- A stroke is scheduled work, not an inline sequence of UI paint calls. `KisImage::startStroke()` enters the update/stroke scheduler.
- Runtime brush behavior belongs in a `KisPaintOp`; tools should own input geometry, not brush rendering semantics.
- `KisPaintInformation` carries per-sample tablet data; `KisDistanceInformation` carries stroke-local spacing/timing state.
- The sanctioned paint path is `KisPainter::paintAt()` (or line/curve dispatch), which calls `KisPaintOp::paintAt(info, currentDistance)`. Do not bypass that chain unless you can re-establish equivalent spacing/timing state updates.
- Worker-thread painting must use `KisResourcesSnapshot` and declared linked/embedded resources, not GUI-global resource lookups.
- Dirty rectangles are part of correctness. Too small causes missing updates; too large causes projection/canvas performance loss.
- Every paint-engine change must be considered under mirror, wrap-around, selection, indirect painting, masking brushes, LOD, undo, and asynchronous updates.
- The OpenGL canvas is primarily a display/projection acceleration layer. Do not assume the brush hot path is GPU-rendered unless the specific code path proves it.

## Gotchas

- **Spacing drift** — `updateSpacingImpl()` must match the spacing logic used inside `paintAt()`; otherwise dab density changes mid-stroke or on curves.
- **Dirty rects too small or too large** — under-reporting skips projection/canvas updates; over-reporting tanks live-drawing performance.
- **Postprocessing cached dabs** — applying sharpness/texture postprocess to already-postprocessed cached dabs corrupts output or wastes CPU.
- **LOD buddy strokes** — geometry and resources must scale through LOD transforms; full-resolution-only fixes are incomplete.
- **GUI resource lookups on worker threads** — stroke painting must use `KisResourcesSnapshot`, not live resource-database queries.
- **Per-dab heap allocation in `paintAt()`** — synchronous allocation in the hot path causes stutter; prefer fixed devices, pools, or async dab queues.
- **Forgetting async drain on stroke end** — engines using `doAsynchronousUpdate()` must flush pending dabs on end/cancel paths.
- **Preset id vs paintop id** — artist-facing preset names are not reliable routing keys; follow paintop id, factory, and settings object.

## Reference routing

| Task | Read |
|------|------|
| Overall brush/stroke architecture or end-to-end data flow | [architecture-map.md](references/architecture-map.md) |
| Class responsibilities, source paths, method contracts | [core-classes-and-contracts.md](references/core-classes-and-contracts.md) |
| Add/modify brush engines, register paintop plugins, design a new painting app | [implementation-playbooks.md](references/implementation-playbooks.md) |
| Tiled pixel storage, layer/projection, canvas/GPU interaction, performance | [pixel-layer-gpu-performance.md](references/pixel-layer-gpu-performance.md) |
| Navigate a Krita checkout or validate claims against source | [source-reading-map.md](references/source-reading-map.md) |
| Extended background when focused references are insufficient (~750 lines) | [krita-programming-guide.md](references/krita-programming-guide.md) |

When a task spans multiple areas, read **every matching row** — e.g. a new paintop plugin needs
[implementation-playbooks.md](references/implementation-playbooks.md),
[core-classes-and-contracts.md](references/core-classes-and-contracts.md), and
[architecture-map.md](references/architecture-map.md).

## Source verification workflow

If the user provides a local Krita checkout or asks for exact source navigation:

1. Run:

```bash
python <SKILL_ROOT>/scripts/krita_source_probe.py --root <krita-root>
```

2. Use the report to verify file existence and critical symbols.
3. Inspect the relevant files directly before proposing patches.
4. If a path or symbol is missing, say it may have moved and search the checkout rather than guessing.

If no checkout is available, use the bundled references as a high-confidence map, but phrase source-specific claims as path guidance rather than guaranteed current truth.

## Resources

- [SOURCES.md](SOURCES.md) — provenance and external references (read for attribution only)
