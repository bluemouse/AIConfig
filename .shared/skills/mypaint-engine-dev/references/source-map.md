# Source Map and Verification Workflow

Load this reference when the user asks where code lives, how to verify a claim against source, or how to plan a change across MyPaint and libmypaint repositories.

## 1. Repositories

- MyPaint application: `https://github.com/mypaint/mypaint`
- libmypaint brush engine: `https://github.com/mypaint/libmypaint`

Prefer checking the user's checkout or current upstream `master` when exact source state matters. The MyPaint repo may bundle `libmypaint-1.6.x/` as a reference tree, but `setup.py` normally links against the libmypaint discovered by `pkg-config`.

**API naming:** Older documentation refers to `mypaint_brush_stroke_to_2`, `mypaint_brush_stroke_to_2_linearsRGB`, and "Surface2". Current upstream libmypaint uses a unified `mypaint_brush_stroke_to(..., linear)` entry point and `MyPaintSurface` / `MyPaintTiledSurface` callbacks. Map legacy names to the symbols below when reading forks or old notes.

## 2. MyPaint source anchors

Read in this order for application-level painting work:

1. `mypaint.py`: launcher and setup path.
2. `gui/main.py`: GTK setup, gettext, GLib user directory initialization, application creation.
3. `gui/application.py`: Application object graph, builder resources, document/controller/window/canvas setup.
4. `gui/document.py`: canvas controller (`Document(CanvasController)`); view manipulation and document-controller glue.
5. `gui/mode.py`: mode stack, brushwork mixins, event handling abstractions.
6. `gui/freehand.py`: freehand painting mode and live stroke input.
7. `lib/document.py`: document model, `sync_pending_changes`, command stack ownership.
8. `lib/command.py`: undoable commands and brushwork command behavior.
9. `lib/stroke.py`: stroke sample recording and replay metadata.
10. `lib/layer/tree.py`: root layer stack, current path, symmetry state.
11. `lib/layer/data.py`: surface-backed layers and painting-layer `stroke_to`.
12. `lib/brush.py`: `BrushInfo`, live `Brush`, `eotf()`/linear flag, settings propagation, native stroke call.
13. `lib/brush.hpp`, `lib/python_brush.hpp`: bridge into libmypaint.
14. `lib/tiledsurface.hpp`: native tiled surface binding and symmetry propagation.

## 3. libmypaint source anchors

Read in this order for engine-level work:

1. `mypaint-brush.h`: public brush API (`mypaint_brush_stroke_to`, mapping setters, smudge buckets).
2. `mypaint-brush.c`: core brush state, settings, input integration, speed remap, stroke loop, dab assembly, RNG.
3. `mypaint-mapping.c`: mapping curve storage, base values, interpolation/extrapolation, validation assertions.
4. generated brush settings/inputs headers or JSON generator sources: setting/input IDs and metadata.
5. `mypaint-surface.h`: surface callback contract (`mypaint_surface_draw_dab`, `mypaint_surface_get_color`, atomics).
6. `mypaint-tiled-surface.h`: tiled surface interface and symmetry state hooks.
7. `mypaint-tiled-surface.c`: default CPU tiled surface, operation queue, dirty bbox, mask generation, blend pass dispatch, `get_color`.
8. `brushmodes.c`: blend mode kernels.
9. `helpers.c`: color helpers, spectral conversion constants, HSV/HSL, WGM functions.
10. `mypaint-symmetry.c` and `mypaint-symmetry.h`: symmetry matrices and transform helpers.
11. `rng-double.*`: deterministic random generator.

## 4. Change-impact map

- New brush setting: update settings metadata/generator, `.myb` parsing, UI editor metadata, mapping propagation, brush core usage, tests.
- New input channel: update input enum/metadata, input derivation, mapping evaluator expectations, preset UI, tests.
- New blend mode: update `DabOp`/operation data, surface process order, CPU kernel, GPU shader, dirty-region tests, UI controls.
- New surface backend: implement draw, get_color, begin/end atomic, tile/resource lifetime, dirty bbox, symmetry behavior, and same operation ordering.
- New layer behavior: update `lib.layer`, command/undo semantics, rendering cache invalidation, UI exposure, file serialization as needed.
- New GPU path: leave brush core unchanged first; replace surface backend and validate through golden images.

## 5. Verification script

Run this from a conversation with local checkouts available:

```bash
python <SKILL_ROOT>/scripts/mypaint_source_probe.py \
  --mypaint /path/to/mypaint \
  --libmypaint /path/to/libmypaint
```

The script checks for key files and symbol strings. It does not prove semantic correctness; it is a fast guard against stale source maps and missing files.

## 6. Source-verified anchors

Spot-checked against upstream `master` (2026-07):

- MyPaint exposes `gui/`, `lib/`, and `tests/`; documents use 15-bit Rec.709 linear RGB colorspace and depend on libmypaint via `pkg-config`.
- `lib/brush.py` contains `BrushInfo`, live `Brush.stroke_to`, and `linear = (eotf() != 1.0)` before native delegation.
- `lib/brush.hpp` calls `mypaint_brush_stroke_to(..., linear)`.
- `mypaint-brush.c` stores settings mappings, runtime states, smudge buckets, RNG, speed remap coefficients, and the stroke integrator loop.
- `mypaint-mapping.c` confirms 0 or 2..64 mapping points, non-decreasing X assertions, `base_value + mappings`, and linear extrapolation.
- `mypaint-tiled-surface.c` confirms atomic begin, symmetry update, 64×64 mask buffers, RLE opacity masks, tile operation queueing, blend pass dispatch, dirty bbox, and `get_color` mask sampling.
- `mypaint-surface.h` exposes unified draw/get_color callbacks with `paint` and `posterize` parameters.
- `helpers.c` contains color/spectral helper functions and constants.
