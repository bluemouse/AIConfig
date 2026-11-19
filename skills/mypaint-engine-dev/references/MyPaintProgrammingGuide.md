---
title: "MyPaint and libmypaint Programming Guide"
author: "Engineering"
tags:
  - mypaint
  - libmypaint
  - mypaint-app
  - architecture
  - brush-engine
  - stroke-rendering
  - rendering
  - symmetry
summary: "Maintainers guide to MyPaint and libmypaint, covering application startup, document and layer architecture, brush preset flow, stroke-to-dab execution, rendering, symmetry, and validation."
date: "2026-03-01"
last_updated: "2026-07-06"
libmypaint_reference_version: "upstream master (unified mypaint_brush_stroke_to API; mypaint repo may bundle 1.6.x)"
---

# Part I — MyPaint Application Architecture

---

## Module A: Repository and Runtime Architecture

> **Learning objective:** Understand how the Python application is laid out,
> how it starts, how it reaches libmypaint, and which contributor workflows are
> worth memorizing before touching code.

### A.1 Repository Shape

At a high level the repository splits into several concerns:

- `mypaint.py`: launcher script used when running from source or from an
  installed script wrapper.
- `gui/`: GTK application code, windows, tools, mode handling, overlays, and
  most controller logic.
- `lib/`: the document model, layer tree, command stack, brush preset objects,
  the SWIG/C++ bridge, and other non-UI infrastructure.
- `libmypaint-1.6.1/`: bundled libmypaint source tree used as a local
  reference and for standalone library work.
- `tests/`: Python-level tests for document, rendering, and bindings.
- `po/`, `glade/`, `desktop/`, `backgrounds/`, `palettes/`: translations,
  UI definitions, icons, and packaged assets.

One practical nuance matters immediately: `setup.py` normally builds MyPaint's
extension against **the libmypaint discovered by `pkg-config`**. The vendored
`libmypaint-1.6.1/` tree is not consumed automatically unless you explicitly
build/install it and point the environment at it.

### A.2 Startup Sequence

The startup path is intentionally staged because GTK, GLib, gettext, and
libmypaint have import-order constraints.

1. `mypaint.py` resolves the installation layout, sets up `sys.path`, verifies
   data locations, configures logging, and then calls `gui.main.main()`.
2. `gui.main.main()` applies GTK workarounds, caches GLib user directories via
   `lib.glib.init_user_dir_caches()`, parses command-line arguments, initializes
   gettext through `lib.gettext_setup.init_gettext()`, and only then imports
   `gui.application`.
3. `gui.application.Application` creates the shared `Gtk.Builder`, loads
   `gui/resources.xml` and `gui/mypaint.glade`, creates the main window,
   document model, document controller, canvas widget, file handler, brush
   manager, device monitor, and the rest of the shared app object graph.
4. Control returns to `gui.main.main()`, which applies theme preferences,
   installs the exception hook, and enters `Gtk.main()`.

**Do not casually change this ordering.** The comments in `gui.main.py` and
`gui.application.py` are there because importing `lib.mypaintlib` too early can
break GLib user-directory lookup or GTK/icon behavior on some platforms.

### A.3 Runtime Object Graph

The runtime graph that matters most for painting looks like this:

```text
Application singleton
  |
  +-- Gtk.Builder resources (`gui/resources.xml`, `gui/mypaint.glade`)
  +-- Main window (`gui.drawwindow`)
  +-- Document model (`lib.document.Document`)
  |     |
  |     +-- RootLayerStack
  |     +-- Brush (`lib.brush.Brush`)
  |     +-- CommandStack
  |
  +-- Document controller (`gui.document.Document`)
  |     |
  |     +-- ModeStack (`gui.mode`)
  |     +-- active tool/mode (`gui.freehand`, `gui.symmetry`, ...)
  |
  +-- Canvas view (`gui.tileddrawwidget.TiledDrawWidget`)
  |
  +-- FileHandler / BrushManager / device monitor / overlays
```

If you remember only one rule of ownership, remember this:

- **Application code owns the session and the UI.**
- **`lib.document.Document` owns the saved model.**
- **`libmypaint` owns brush-state integration and dab generation.**

### A.4 Contributor Workflow Shortcuts

These commands are the fastest way to orient yourself while developing:

- `python setup.py demo`: smoke-test the application without installing.
- `python setup.py nosetests`: run doctests and lighter Python-focused tests.
- `python setup.py test`: run the broader suite, including extension/libmypaint
  coverage.
- `python setup.py clean --all`: clear stale build outputs when debugging odd
  rebuild behavior.

If you need to test a local libmypaint change through the app, pair a local
libmypaint install with `PKG_CONFIG_PATH` and the `build_ext --set-rpath`
workflow described in `BUILDING.md`.

---

## Module B: Document, Layers, Commands, and MVC Responsibilities

> **Prerequisites:** Module A.
>
> **Learning objective:** Understand where MyPaint stores document state, where
> it stores temporary UI state, and how brushwork becomes undoable.

### B.1 The MVC Split

The codebase states this explicitly in `lib.document.Document`:

- **Model:** `lib.document.Document`
- **View:** mainly `gui.tileddrawwidget`
- **Controller:** mainly `gui.document` and `gui.mode`

That split is useful because it tells you where to debug:

- If the document saved the wrong thing, inspect the model.
- If the canvas looks wrong but the model is correct, inspect the view.
- If the wrong action happened in response to input, inspect controllers and
  modes.

### B.2 What the Document Model Owns

`lib.document.Document` is the in-memory representation of everything the user
expects to save:

- the `RootLayerStack`
- the live `lib.brush.Brush`
- the `CommandStack`
- autosave/cache state
- frame and resolution metadata
- document-specific JSON settings serialized into ORA

The document model is GUI-independent enough to be exercised from `tests/`
without the full application running. That is why many maintainability tasks
belong in `lib/` rather than `gui/`.

One subtle but important maintenance detail comes directly from the
`lib.document.Document` docstring: not every pending user-visible change is
immediately represented as a finalized command-stack entry. Before save, export,
or other large model operations, code may need to call
`sync_pending_changes()` so that active tools flush their pending state into
the document and undo history.

### B.3 Layers and Surfaces

`lib.layer.tree.RootLayerStack` is the document-scale manager for:

- background handling
- current layer selection
- render cache invalidation
- path-based traversal within the layer tree
- painting symmetry state

Actual paint data lives in descendants of `SurfaceBackedLayer` in
`lib/layer/data.py`. Painting layers delegate dab rendering to
`lib.tiledsurface.Surface`, which exposes `begin_atomic()` / `end_atomic()`
around each incremental stroke update.

That means there are two different "rendering" levels in the codebase:

1. **Painting into a layer surface** via libmypaint.
2. **Compositing layers for display** in the canvas renderer.

Do not confuse them.

### B.4 Undoable Brushwork

Brush strokes are not pushed directly onto the command stack one dab at a time.
Instead:

1. `gui.mode.BrushworkModeMixin` manages an active `lib.command.Brushwork`
   recorder per document.
2. `Brushwork.stroke_to()` records the incoming input samples into a
   `lib.stroke.Stroke` and paints incrementally to the target layer.
3. When `split_due` becomes true, or the mode commits explicitly, the recorded
   segment becomes a command-stack entry.

This split is why stroke bugs can appear in different forms:

- The visible paint may be correct, but undo segmentation may be wrong.
- The dab sequence may be correct, but the recorded stroke metadata may be
  wrong.
- The mode may fail to commit or tail off a stroke cleanly, producing an
  unexpected continuation on the next event sequence.

### B.5 Common Extension Points

Junior maintainers should learn these extension points early:

- **New menu or toolbar action:** add it in `gui/resources.xml` and make sure
  its handler lives on an object registered by `gui.application.Application`.
- **New painting or interaction tool:** subclass a mode in `gui.mode` and wire
  it through `gui/resources.xml`.
- **New undoable model change:** add or extend a `lib.command.Command`
  subclass.
- **New layer behavior:** extend the layer classes in `lib.layer`.
- **New brush editor or preset behavior:** work across `lib/brush.py`,
  `lib/brushsettings.py`, and the related UI in `gui/`.

Whenever a feature touches both model and UI, resist the temptation to put
everything in `gui/`. Most durable behavior belongs in `lib/`.

---

## Module C: From Tablet Event to libmypaint Stroke

> **Prerequisites:** Modules A-B.
>
> **Learning objective:** Trace the exact path from a GTK event to a libmypaint
> stroke update, and understand how preset data and live brush state move
> through that path.

### C.1 Event Routing Through the Mode Stack

Pointer events hit `gui.tileddrawwidget.TiledDrawWidget`, whose handlers are
owned by `gui.document.CanvasController`. The controller delegates button,
motion, scroll, and key events to the current mode at the top of its
`ModeStack`.

For painting, the default mode is `gui.freehand.FreehandMode`, which uses
`gui.mode.BrushworkModeMixin`.

### C.2 The High-Level Stroke Path

The call path that matters most is:

```text
Gdk event
  -> gui.document.CanvasController
  -> active mode in gui.mode.ModeStack
  -> gui.mode.BrushworkModeMixin.stroke_to()
  -> lib.command.Brushwork.stroke_to()
  -> lib.layer.data.SimplePaintingLayer.stroke_to()
  -> lib.brush.Brush.stroke_to()
  -> lib/brush.hpp / lib/python_brush.hpp
  -> mypaint_brush_stroke_to()
  -> prepare_and_draw_dab()  (inside mypaint_brush_stroke_to; no _internal symbol exists)
```

Understanding this chain makes the rest of the guide much easier to place in
context.

### C.3 Recording Versus Painting

`Brushwork.stroke_to()` performs two jobs at once:

- it records the user's input into a `lib.stroke.Stroke`, which later becomes
  undoable stroke metadata;
- it forwards the same sample to the current layer for immediate painting.

That separation matters because the engine's return value is reused for
**stroke splitting**. The layer asks the brush whether the stroke should now be
split; the active mode then decides whether to commit the current `Brushwork`
command and begin a new one.

### C.4 Atomic Layer Updates

`SimplePaintingLayer.stroke_to()` wraps each incremental update with:

1. `self._surface.begin_atomic()`
2. `brush.stroke_to(...)`
3. `self._surface.end_atomic()`

The atomic block is a contract between the Python layer model and the native
surface backend:

- libmypaint may enqueue many dab operations while painting;
- the surface may defer tile processing until `end_atomic()`;
- dirty rectangles become visible to the rest of the app only after the atomic
  block completes.

### C.5 Brush Presets in MyPaint Versus libmypaint

MyPaint uses two related but distinct brush representations:

- `lib.brush.BrushInfo`: the editable, serializable preset object used by the
  application and stored as `.myb` JSON.
- `lib.brush.Brush`: the live brush engine instance that mirrors those settings
  into libmypaint mappings and keeps per-stroke state.

This split explains several non-obvious behaviors:

- Selecting a new brush usually copies settings into the global live brush
  without discarding the runtime state you need for cursor tracking.
- Editing a preset in the UI changes `BrushInfo`, which must then be synced
  into the live brush mappings.
- Some fields in `.myb` are host/UI metadata and not part of the simulation.

The `.myb` details are covered in Module 2; the key idea here is that MyPaint
and libmypaint agree on the preset schema, but they do not use the same in-RAM
objects for the whole lifecycle.

### C.6 The Native Boundary

The Python-to-native boundary is intentionally thin:

- `lib/brush.py` exposes the Python-facing `Brush`.
- `lib/python_brush.hpp` provides minimal exception-handling wrappers.
- `lib/brush.hpp` forwards to the unified `mypaint_brush_stroke_to(..., linear)`.

That means nearly all "real brush math" happens below the binding boundary.
If a visual brush bug survives up to `lib.brush.Brush.stroke_to()`, the next
place to inspect is almost always `mypaint-brush.c`.

---

## Module D: Symmetry, Mirroring, and View Transforms

> **Prerequisites:** Modules A-C.
>
> **Learning objective:** Distinguish viewport mirroring from painting
> symmetry, understand where symmetry state lives in MyPaint, and know how one
> user dab becomes multiple libmypaint dabs.

### D.1 Two Different "Mirror" Features

MyPaint exposes two features that users casually call "mirroring", but they are
implemented very differently:

- **Viewport mirroring** changes only how the canvas is viewed.
- **Painting symmetry** duplicates dabs in model space and changes the painted
  result.

Viewport mirroring is handled in `gui.document.Document`:

- `mirror_horizontal_cb()` calls `TiledDrawWidget.mirror()`
- `mirror_vertical_cb()` rotates the view by `pi` and then mirrors it

These actions do **not** tell libmypaint to duplicate dabs. They only alter the
view transform.

### D.2 Painting Symmetry State in the App

Painting symmetry lives at the document layer-tree level in
`lib.layer.tree.RootLayerStack`, which owns:

- whether symmetry is active
- the symmetry center (`x`, `y`)
- the symmetry type
- the number of rotational lines

The UI pieces are spread across:

- the `SymmetryActive` action in `gui/resources.xml`
- `gui.symmetry.SymmetryEditMode`
- `gui.symmetry.SymmetryEditOptionsWidget`
- `gui.symmetry.SymmetryOverlay`

The root stack emits `symmetry_state_changed`, and the current paintable layer
receives the propagated state via `_propagate_symmetry_state()`.

### D.3 Propagation to the Native Surface

The state flow from the UI to libmypaint is:

```text
GUI action / symmetry edit mode
  -> RootLayerStack.set_symmetry_state()
  -> SurfaceBackedLayer.set_symmetry_state()
  -> lib.tiledsurface.Surface.set_symmetry_state()
  -> lib/tiledsurface.hpp::TiledSurface::set_symmetry_state()
  -> mypaint_tiled_surface_set_symmetry_state()
```

The C++ bridge currently passes `symmetry_angle = 0.0`, while libmypaint's
native symmetry state supports an angle field. That is important when comparing
what the library can represent with what the current MyPaint UI exposes.

### D.4 How libmypaint Duplicates Dabs

libmypaint does not duplicate the whole stroke at the Python layer. It
duplicates **individual dabs** inside the surface backend.

The sequence is:

1. MyPaint updates pending symmetry state on `MyPaintTiledSurface`.
2. `mypaint_tiled_surface_begin_atomic()` refreshes the symmetry matrices by
   calling `mypaint_update_symmetry_state()`.
3. The brush engine emits a normal dab.
4. `draw_dab_internal()` renders the original dab, then applies each symmetry
   transform to the dab center and angle and renders the mirrored/rotated copies.

The supported symmetry families are:

- vertical
- horizontal
- vertical + horizontal
- rotational N-fold
- snowflake

For the simplest vertical case, the mirrored dab center is:

```text
symm_x = 2 * center_x - x
```

### D.5 Maintainer Notes

When debugging symmetry, remember these constraints:

- Viewport mirroring and painting symmetry are separate features.
- The root stack is the source of truth for symmetry state in the app.
- The current layer receives propagated symmetry state; changing the current
  layer can therefore change where the live surface state is updated.
- libmypaint updates symmetry matrices at the atomic boundary, not directly
  inside the UI callback.

If a symmetry bug is visible in the overlay but not in paint, inspect the
propagation path. If paint is wrong but the overlay is correct, inspect the
native tiled-surface and symmetry code.

---

# Part II — libmypaint Architecture and Data Model

---

## Module 1: The Dab Engine Architecture

> **Learning objective:** Understand what a dab engine is, how it is structured
> into two independent layers, and what the API surface looks like. This mental
> model informs every subsequent module.

### 1.1 What Is a Dab Engine?

libmypaint is a **dab engine**, not a polyline engine.

- A **stroke** is a time-ordered sequence of **dabs**.
- A **dab** is a localized render operation with geometry + color + blending.
- Brush settings are not static constants; they are evaluated dynamically from
  the current input state.

At each input event, the engine runs a small simulation step:

1. Normalize and sanitize event inputs (`pressure`, tilt, `dt`, view params).
2. Advance internal state to the event time.
3. Compute how many dabs are pending for the remaining movement/time.
4. Emit zero or more dabs; for each emitted dab, interpolate state, evaluate
   settings, render, then advance the random input.
5. Save the fractional dab remainder (`partial_dabs`) for the next event.

Conceptually this is a **state integrator + dab planner + surface compositor**,
executed once per input event.

### 1.2 Architecture Layers: Brush Core and Surface Backend

The system separates into two independent layers, which is the most important
architectural decision in the codebase:

```text
┌─────────────────────────────────────────────────────┐
│  BRUSH CORE  (platform-agnostic)                    │
│  Input sanitization  → Virtual cursor               │
│  Setting evaluation  → Dab scheduling               │
│  Per-dab assembly    → Surface callback             │
└───────────────────────────┬─────────────────────────┘
                            │  draw_dab(x, y, r, hardness,
                            │           opa, color, blends...)
┌───────────────────────────▼─────────────────────────┐
│  SURFACE BACKEND  (renderer-specific)               │
│  Mask rasterization  → Blend/composite execution    │
│  Tile management     → Dirty-region tracking        │
└─────────────────────────────────────────────────────┘
```

The brush core houses all stroke semantics; pixel math lives in the surface
backend. This boundary enables portability: the same brush core can target a
CPU raster backend, a Skia backend, or a Vulkan backend without changing any
brush logic.

### 1.3 Public API: `mypaint_brush_stroke_to` and `MyPaintSurface`

Current upstream libmypaint uses a **unified** brush entry point and surface
callback contract. Older forks and notes may still refer to separate "Surface1"
and "Surface2" APIs or to `mypaint_brush_stroke_to_2`; map those names to the
symbols below.

| Component | Role |
| --- | --- |
| `mypaint_brush_stroke_to()` | Single stroke entry; passes `viewzoom`, `viewrotation`, `barrel_rotation`, and `linear` |
| `mypaint_surface_draw_dab()` | Draw callback with `paint`, `posterize`, `lock_alpha`, `colorize` |
| `mypaint_surface_get_color()` | Canvas pickup for smudge; `paint` selects spectral vs additive sampling |
| `MyPaintTiledSurface` | Default CPU tiled backend with symmetry, atomics, and per-tile operation queues |

MyPaint binding:

- `lib/brush.hpp` calls `mypaint_brush_stroke_to(..., linear)`.
- `lib/brush.py` sets `linear = (eotf() != 1.0)` before delegating to the C++
  bridge so HSV/HSL dynamics run in linear sRGB when required.

Use this unified API for all new work. `paint_mode` (spectral pigment mixing)
and `posterize` are carried on the draw callback, not on a separate stroke entry
point.

### 1.4 Deterministic Execution Contract

A compliant implementation satisfies:

- Same input sample stream + same initial brush state + same random seed
  ⟹ same dab sequence and identical output.
- Random input is advanced **exactly once per emitted dab**, immediately after
  `drawDab` — not once per input event.
- Numeric clamping, interpolation order, and floating-point operation order are
  fixed.

Two details are especially parity-critical:

- **Dab count is recomputed after each emitted dab** using remaining event
  time. This is required because dynamic settings (especially radius and
  spacing) can change mid-event.
- **Angular channels** (`ascension`, `barrel_rotation`) use shortest-path
  interpolation, preventing wraparound discontinuities.

Time handling:
- Clamp non-positive `dt` to a small positive epsilon (`0.0001`).
- Treat `dt > 5.0` as a stroke reset boundary (no dabs emitted).
- Keep this policy stable across platforms — it affects both stroke
  segmentation and determinism.

### 1.5 Implementation Strategy for New Engines

libmypaint itself is a **CPU-only** engine — no OpenGL or Vulkan inside the
library. The brush core calls surface callbacks, and the default tiled
implementation composites pixels in CPU tile buffers.

For a GPU-accelerated engine, the recommended approach is:

1. Implement and validate brush core behavior using a CPU reference path
   (matching libmypaint math exactly).
2. Run visual parity tests (see `performance-validation.md` §5–9)
   before touching the GPU path.
3. Replace only the surface backend with a GPU implementation.
4. Keep blend ordering, clamps, and per-dab parameter resolution identical so
   the GPU path changes performance, not stroke semantics.

---

## Module 2: Brush Presets and the .myb Format

> **Prerequisites:** Module 1.
>
> **Learning objective:** Understand the `.myb` JSON preset format, all
> setting and input identifiers, parsing constraints, and how to author a
> brush from scratch. After this module you can load and validate `.myb`
> presets.

### 2.1 Preset Data Model

libmypaint's loader (`mypaint_brush_from_string`) expects a top-level object:

```json
{
  "version": 3,
  "settings": {
    "setting_name": {
      "base_value": <number>,
      "inputs": {
        "input_name": [[x0, y0], [x1, y1], ...]
      }
    }
  }
}
```

Strict loader constraints:

- `version` must be exactly `3`.
- `settings` key must exist.

Per-entry behavior is more tolerant:

- Unknown setting or input names emit warnings and are skipped.
- Wrong value shapes emit warnings and skip that entry.
- Other valid settings in the same file still apply.

Top-level metadata (`comment`, `group`, `parent_brush_name`) is ignored by
the simulation engine and is treated as host/UI metadata.

### 2.2 Settings Reference

A setting has a `base_value` and an optional set of input mappings. Each
mapping is a piecewise curve that modulates the setting based on a stylus or
derived input (see §2.3). The final setting value is:

```text
setting_value = base_value + Σ curve_i(input_i)
```

The full set of setting identifiers in libmypaint 1.6.x:

| Setting ID | Description |
| --- | --- |
| `opaque` | Base paint opacity (0–1) |
| `opaque_multiply` | Opacity multiplier (combined with `opaque`) |
| `opaque_linearize` | Perceptual linearization of opacity/coverage |
| `radius_logarithmic` | Brush radius in log space (pixels = exp(value)) |
| `hardness` | Dab edge hardness (0=soft/airbrush, 1=hard stamp) |
| `anti_aliasing` | Minimum softness zone for small dabs |
| `dabs_per_basic_radius` | Dabs per base-radius unit of travel |
| `dabs_per_actual_radius` | Dabs per current dynamic radius of travel |
| `dabs_per_second` | Time-based dab emission rate |
| `radius_by_random` | Gaussian noise applied to radius (log space) |
| `speed1_slowness` | Smoothing coefficient for `speed1` |
| `speed2_slowness` | Smoothing coefficient for `speed2` |
| `speed1_gamma` | Log curve gamma for `speed1` remapping |
| `speed2_gamma` | Log curve gamma for `speed2` remapping |
| `offset_by_random` | Gaussian jitter offset from stroke path |
| `offset_by_speed` | Offset along motion direction proportional to speed |
| `offset_by_speed_slowness` | Smoothing for speed-offset direction |
| `slow_tracking` | Event-rate stabilizer (position low-pass) |
| `slow_tracking_per_dab` | Per-dab stabilizer strength |
| `tracking_noise` | Random cursor perturbation (tremor) |
| `color_h` | Base brush color hue (0–1 turns) |
| `color_s` | Base brush color saturation |
| `color_v` | Base brush color value |
| `restore_color` | Host UI hint: restore color on brush selection |
| `change_color_h` | Per-dab hue shift (turns) |
| `change_color_l` | Per-dab lightness shift (HSL) |
| `change_color_hsl_s` | Per-dab saturation shift (HSL, context-scaled) |
| `change_color_v` | Per-dab value shift (HSV) |
| `change_color_hsv_s` | Per-dab saturation shift (HSV, context-scaled) |
| `smudge` | Smudge amount (0=no smudge, 1=full wet drag) |
| `smudge_length` | How long sampled color is retained before re-pickup |
| `smudge_radius_log` | Log-scale radius offset for smudge pickup area |
| `smudge_length_log` | Log-scale adjustment for resample cadence |
| `smudge_bucket` | Which smudge state bucket to use (0–255) |
| `smudge_transparency` | Abort dab if sampled alpha is below threshold |
| `eraser` | Erase strength (0=paint, 1=full erase) |
| `stroke_threshold` | Pressure threshold below which stroke does not start |
| `stroke_duration_logarithmic` | Controls `stroke` input progression speed |
| `stroke_holdtime` | How long `stroke` input stays at max before resetting |
| `custom_input` | Target value for the `custom` input channel |
| `custom_input_slowness` | Smoothing for `custom` input |
| `elliptical_dab_ratio` | Aspect ratio of the dab ellipse (1=circular) |
| `elliptical_dab_angle` | Rotation angle of the dab ellipse (degrees) |
| `direction_filter` | Smoothing for the `direction` input channel |
| `lock_alpha` | Lock-alpha blend amount (paint only over existing opaque pixels) |
| `colorize` | Colorize blend amount (apply brush hue to destination) |
| `snap_to_pixel` | Snap dab centers and radius to pixel grid |
| `pressure_gain_log` | Non-linear pressure amplification |
| `gridmap_scale` | Scale of the `gridmap_x/y` coordinate grid |
| `gridmap_scale_x` | Per-axis X scale for gridmap |
| `gridmap_scale_y` | Per-axis Y scale for gridmap |
| `offset_y` | Fixed Y offset from stroke path (canvas space) |
| `offset_x` | Fixed X offset from stroke path (canvas space) |
| `offset_angle` | Angular offset from stroke direction (FLIP-alternated) |
| `offset_angle_asc` | Angular offset from tilt ascension (FLIP-alternated) |
| `offset_angle_view` | Angular offset relative to view rotation (FLIP-alt.) |
| `offset_angle_2` | Second angular offset from stroke direction |
| `offset_angle_2_asc` | Second angular offset from tilt ascension |
| `offset_angle_2_view` | Second angular offset relative to view rotation |
| `offset_angle_adj` | Adjusts the reference angle for all offset_angle terms |
| `offset_multiplier` | Scale factor for all directional offsets |
| `posterize` | Posterize blend amount |
| `posterize_num` | Number of quantization levels (1–128) |
| `paint_mode` | Spectral pigment mixing factor (0=additive, 1=spectral) |

### 2.3 Inputs Reference

The following input identifiers are used as keys in the `inputs` map of each
setting. They correspond to the dynamic channels computed by the brush core
during a stroke (see Module 3 for how each is derived):

| Input ID | Description | Typical Range |
| --- | --- | --- |
| `pressure` | Tablet pressure | 0–1 |
| `speed1` | Fine-grained filtered pen speed (log-remapped) | ≈ 0–4 |
| `speed2` | Gross (slowly-changing) filtered speed (log-remapped) | ≈ 0–4 |
| `random` | Per-dab uniform random value | 0–1 |
| `stroke` | Normalized stroke progress | 0–1 |
| `direction` | Stroke motion angle, 180°-periodic | 0–180 |
| `direction_angle` | Stroke motion angle, full 360° | 0–360 |
| `tilt_declination` | Stylus tilt from perpendicular | 0–90 |
| `tilt_ascension` | Stylus roll/azimuth | −180–180 |
| `tilt_declinationx` | Per-axis tilt X | −90–90 |
| `tilt_declinationy` | Per-axis tilt Y | −90–90 |
| `attack_angle` | Angle between ascension and stroke direction | −180–180 |
| `barrel_rotation` | Stylus barrel twist | −180–180 |
| `viewzoom` | Canvas zoom level (logarithmic) | varies |
| `brush_radius` | Current brush radius (log space) | varies |
| `gridmap_x` | X position on wrapping 256-px grid | 0–1 |
| `gridmap_y` | Y position on wrapping 256-px grid | 0–1 |
| `custom` | User-defined filtered input | varies |

### 2.4 Annotated Example — Minimal Preset

```json
{
  "version": 3,
  "settings": {
    "opaque": {
      "base_value": 1.0,
      "inputs": {
        "pressure": [[0.0, -0.99], [0.4, -0.5], [0.7, 0.0], [1.0, 1.0]]
      }
    },
    "radius_logarithmic": {
      "base_value": 1.01,
      "inputs": {
        "pressure": [[0.0, -1.86], [0.25, -1.42], [0.5, -0.35], [0.75, 1.42], [1.0, 2.13]]
      }
    },
    "hardness":              { "base_value": 0.89, "inputs": {} },
    "dabs_per_actual_radius": { "base_value": 5.82, "inputs": {} },
    "dabs_per_second":        { "base_value": 70.0, "inputs": {} },
    "slow_tracking":          { "base_value": 4.47, "inputs": {} },
    "slow_tracking_per_dab":  { "base_value": 2.48, "inputs": {} },
    "speed1_slowness":        { "base_value": 0.04, "inputs": {} },
    "speed1_gamma":           { "base_value": 2.87, "inputs": {} }
  }
}
```

Reading the `pressure` curve on `opaque`:

- At `pressure=0.0`: `opaque = 1.0 + (-0.99) = 0.01` (almost invisible).
- At `pressure=0.7`: `opaque = 1.0 + 0.0 = 1.0` (full opacity).
- At `pressure=1.0`: `opaque = 1.0 + 1.0 = 2.0` — then clamped to 1.0 in the
  engine. Overshoot like this is common; it ensures the pressure-to-opacity
  response reaches maximum before full pressure.

The `radius_logarithmic` curve drives radius tapering: at low pressure the
curve subtracts a large value (very small radius); at high pressure it adds
(large radius). The engine exponentiates the final value to get pixel radius.

### 2.5 Full Settings Template (All Keys)

Use this as a reference or validation fixture. A parser that can load this
file without warnings handles all setting/input IDs:

```json
{
  "version": 3,
  "settings": {
    "opaque": { "base_value": 1.0, "inputs": {} },
    "opaque_multiply": { "base_value": 1.0, "inputs": {} },
    "opaque_linearize": { "base_value": 0.0, "inputs": {} },
    "radius_logarithmic": { "base_value": -0.693147, "inputs": {} },
    "hardness": { "base_value": 0.5, "inputs": {} },
    "anti_aliasing": { "base_value": 0.0, "inputs": {} },
    "dabs_per_basic_radius": { "base_value": 2.0, "inputs": {} },
    "dabs_per_actual_radius": { "base_value": 0.0, "inputs": {} },
    "dabs_per_second": { "base_value": 0.0, "inputs": {} },
    "radius_by_random": { "base_value": 0.0, "inputs": {} },
    "speed1_slowness": { "base_value": 0.5, "inputs": {} },
    "speed2_slowness": { "base_value": 0.5, "inputs": {} },
    "speed1_gamma": { "base_value": 1.0, "inputs": {} },
    "speed2_gamma": { "base_value": 1.0, "inputs": {} },
    "offset_by_random": { "base_value": 0.0, "inputs": {} },
    "offset_by_speed": { "base_value": 0.0, "inputs": {} },
    "offset_by_speed_slowness": { "base_value": 0.5, "inputs": {} },
    "slow_tracking": { "base_value": 0.0, "inputs": {} },
    "slow_tracking_per_dab": { "base_value": 0.0, "inputs": {} },
    "tracking_noise": { "base_value": 0.0, "inputs": {} },
    "color_h": { "base_value": 0.0, "inputs": {} },
    "color_s": { "base_value": 1.0, "inputs": {} },
    "color_v": { "base_value": 1.0, "inputs": {} },
    "restore_color": { "base_value": 0.0, "inputs": {} },
    "change_color_h": { "base_value": 0.0, "inputs": {} },
    "change_color_l": { "base_value": 0.0, "inputs": {} },
    "change_color_hsl_s": { "base_value": 0.0, "inputs": {} },
    "change_color_v": { "base_value": 0.0, "inputs": {} },
    "change_color_hsv_s": { "base_value": 0.0, "inputs": {} },
    "smudge": { "base_value": 0.0, "inputs": {} },
    "smudge_length": { "base_value": 0.5, "inputs": {} },
    "smudge_radius_log": { "base_value": 0.0, "inputs": {} },
    "eraser": { "base_value": 0.0, "inputs": {} },
    "stroke_threshold": { "base_value": 0.0, "inputs": {} },
    "stroke_duration_logarithmic": { "base_value": 0.0, "inputs": {} },
    "stroke_holdtime": { "base_value": 0.0, "inputs": {} },
    "custom_input": { "base_value": 0.0, "inputs": {} },
    "custom_input_slowness": { "base_value": 0.5, "inputs": {} },
    "elliptical_dab_ratio": { "base_value": 1.0, "inputs": {} },
    "elliptical_dab_angle": { "base_value": 0.0, "inputs": {} },
    "direction_filter": { "base_value": 0.0, "inputs": {} },
    "lock_alpha": { "base_value": 0.0, "inputs": {} },
    "colorize": { "base_value": 0.0, "inputs": {} },
    "snap_to_pixel": { "base_value": 0.0, "inputs": {} },
    "pressure_gain_log": { "base_value": 0.0, "inputs": {} },
    "gridmap_scale": { "base_value": 1.0, "inputs": {} },
    "gridmap_scale_x": { "base_value": 1.0, "inputs": {} },
    "gridmap_scale_y": { "base_value": 1.0, "inputs": {} },
    "smudge_length_log": { "base_value": 0.0, "inputs": {} },
    "smudge_bucket": { "base_value": 0.0, "inputs": {} },
    "smudge_transparency": { "base_value": 0.0, "inputs": {} },
    "offset_y": { "base_value": 0.0, "inputs": {} },
    "offset_x": { "base_value": 0.0, "inputs": {} },
    "offset_angle": { "base_value": 0.0, "inputs": {} },
    "offset_angle_asc": { "base_value": 0.0, "inputs": {} },
    "offset_angle_view": { "base_value": 0.0, "inputs": {} },
    "offset_angle_2": { "base_value": 0.0, "inputs": {} },
    "offset_angle_2_asc": { "base_value": 0.0, "inputs": {} },
    "offset_angle_2_view": { "base_value": 0.0, "inputs": {} },
    "offset_angle_adj": { "base_value": 0.0, "inputs": {} },
    "offset_multiplier": { "base_value": 1.0, "inputs": {} },
    "posterize": { "base_value": 0.0, "inputs": {} },
    "posterize_num": { "base_value": 1.0, "inputs": {} },
    "paint_mode": { "base_value": 0.0, "inputs": {} }
  }
}
```

### 2.6 Parser Constraints

From mapping internals (`mypaint-mapping.c`):

- Control-point count per input must be `0` or `2..64` (exactly `1` is
  invalid).
- Control-point x-values must be non-decreasing.

These are guarded by assertions in libmypaint internals. A robust external
loader should validate them explicitly before runtime, not rely on library
assertions.

Setting base values via the official API path also refreshes cached derived
data (e.g., speed-remap coefficients — see Module 4). Writing through the
setter path is required for parity.

### 2.7 Authoring a Brush From Scratch

To build a functional "pen/brush" preset:

1. Start with `{"version": 3, "settings": { ... }}`.
2. Set size: `radius_logarithmic.base_value` (log space; `exp(1.01)` ≈ 2.7 px).
3. Set softness: `hardness.base_value` (0.9 = crisp edge, 0.3 = soft).
4. Set paint amount: `opaque.base_value` with a `pressure` curve.
5. Set spacing: `dabs_per_actual_radius` (higher = denser stroke), optionally
   plus `dabs_per_second` for time-based emission.

Add advanced settings (`smudge`, color shifts, offsets, `lock_alpha`, `eraser`,
`posterize`/`paint_mode`) only after basic strokes render correctly.

**Color fields:** Most hosts treat "active UI color" as application state and
overwrite `color_h/s/v` at runtime when a brush is selected. If your presets
must be self-contained (portable), store sensible `color_h/s/v` defaults. Set
`restore_color` to a non-zero value as a hint to hosts that support it.

**Parity note:** `restore_color` is a host-UI hint only; libmypaint's brush
simulation engine ignores it during drawing.

---

# Part III — The Stroke Pipeline

---

## Module 3: Input Processing and Derived Channels

> **Prerequisites:** Modules 1–2.
>
> **Learning objective:** Understand what input data the engine receives, how
> it is sanitized, and how all 18 dynamic input channels are derived from raw
> stylus events. This module covers everything that happens before settings
> are evaluated.

### 3.1 Stylus Event Inputs

A single input sample contains:

| Field | Description |
| --- | --- |
| `x`, `y` | Canvas-space coordinates |
| `pressure` | Tablet pressure (0–1), amplified if `pressure_gain_log` ≠ 0 |
| `xtilt`, `ytilt` | Normalized stylus tilt components, each in [−1, 1] |
| `barrel_rotation` | Stylus barrel twist (turns → degrees) |
| `dt` | Time since previous sample, in seconds |
| `viewzoom` | Canvas zoom level |
| `viewrotation` | Canvas rotation (radians → degrees internally) |

`xtilt` and `ytilt` are raw tablet values converted to the derived tilt inputs
described in §3.4.

### 3.2 Input Sanitization Contract (Parity-Critical)

Before derived inputs are updated, apply defensive normalization:

- Clamp `xtilt` and `ytilt` to `[−1, 1]`.
- Clamp pressure floor: `pressure ≤ 0` becomes `0`.
- Clamp non-positive time: `dt ≤ 0` becomes `0.0001`.
- Reject non-finite/insane positions by forcing a safe reset path (`x/y` and
  dynamic view inputs forced to zero for that call).

Reproducing only the "happy path math" is not enough for robust parity —
these sanitization rules are observable.

### 3.3 Virtual Cursor Stage

libmypaint does not derive all channels from raw event position directly.
It first computes a **virtual cursor** by applying:

1. **Tracking noise injection** (`tracking_noise`): random Gaussian
   perturbation to cursor position, simulating hand tremor.
2. **Slow position tracking** (`slow_tracking`): low-pass filter on cursor
   position, smoothing jitter at the cost of lag.

Many downstream channels (speed, direction, stroke progression) depend on
this filtered state, not just raw sample deltas.

### 3.4 Tilt Derivation

Raw `xtilt`/`ytilt` values (each in [−1, 1]) are converted as follows:

```text
tilt_ascension   = degrees(atan2(-xtilt, ytilt))
rad              = hypot(xtilt, ytilt)
tilt_declination = 90 - rad * 60          // 0° = flat, 90° = upright
tilt_declinationx = xtilt * 60
tilt_declinationy = ytilt * 60
```

When both tilt components are zero, `tilt_declination` defaults to `90°`
(upright stylus fallback).

### 3.5 The Derived Input Vector

All 18 dynamic inputs, with their `.myb` IDs and derivation source:

| Input ID | How It Is Derived |
| --- | --- |
| `pressure` | After `pressure_gain_log` amplification |
| `speed1` | Logarithmic remap of fine-grained filtered speed (see Module 4) |
| `speed2` | Logarithmic remap of gross (slowly-changing) filtered speed |
| `random` | Per-dab value from Knuth LFIB RNG, advanced once per dab |
| `stroke` | Normalized stroke progress (0→1, resets via `stroke_holdtime`) |
| `direction` | Stroke motion angle, 180°-periodic (ignores 180° turns) |
| `direction_angle` | Stroke motion angle, full 360° |
| `tilt_declination` | From §3.4 |
| `tilt_ascension` | From §3.4 |
| `tilt_declinationx` | From §3.4 |
| `tilt_declinationy` | From §3.4 |
| `attack_angle` | Smallest angular difference between ascension and stroke direction (+ 90° frame adjust) |
| `barrel_rotation` | Stylus barrel twist |
| `viewzoom` | Derived in logarithmic radius space, not raw zoom |
| `brush_radius` | Current dynamic radius in log space |
| `gridmap_x` | Wrapped/modulo X over a scaled 256-cell grid |
| `gridmap_y` | Wrapped/modulo Y over a scaled 256-cell grid |
| `custom` | Exponential smoothing toward `custom_input` target |

### 3.6 Stateful vs Instantaneous Channels

Several inputs are **stateful** — they depend on prior state updated each step:

- `speed1`, `speed2`: time-filtered speed channels (exponential moving average)
- `direction`, `direction_angle`: filtered motion direction channels
- `custom`: low-pass toward `custom_input` target
- `stroke`: accumulates over the entire stroke, resets based on `stroke_holdtime`

Because these depend on prior state, **update order is part of compatibility**
(see §3.7).

Speed channels are also **zoom-adjusted**: velocity components are scaled by
`viewzoom` before speed filtering, ensuring speed inputs reflect screen-space
motion independent of canvas zoom level.

### 3.7 Update Ordering (Do Not Reorder)

For parity, this order is mandatory:

```text
1. Sanitize inputs (pressure, tilt, time)
2. Update virtual cursor (slow_tracking, tracking_noise)

3. Inside the dab emission loop (per emitted dab):
   a. Interpolate inputs to dab time (x, y, pressure, tilt, dt)
   b. Compute derived input vector from CURRENT state (speed, direction)
   c. Evaluate settings from mappings using current derived inputs
   d. Update stateful channels (speed, direction, custom) for NEXT step
```

Step 3c must see speed/direction **before** the current step is integrated.
Reordering 3b/3c/3d breaks parity: settings will observe the wrong speed or
direction state.

---

## Module 4: Setting Evaluation — Mapping Curves

> **Prerequisites:** Modules 1–3.
>
> **Learning objective:** Understand the exact evaluation rule for brush
> settings — including piecewise curve interpolation, the critical
> extrapolation behavior, and the speed input logarithmic remapping. This
> module covers the complete math needed to implement a setting evaluator.

### 4.1 The Core Mapping Rule

At each update step, libmypaint evaluates all settings from one shared input
snapshot (`pressure`, `speed1/2`, direction, tilt, etc.) and stores the
resulting per-setting values. Settings do not depend on other settings
directly; they depend on inputs via mappings.

Each setting has:
- a `base_value`
- zero or more input mappings, each a piecewise linear curve

$$
\text{setting\_value} = \text{base\_value} + \sum_i \text{curve}_i(\text{input}_i)
$$

When a setting has no input mappings, the evaluator takes a constant fast
path: `setting_value = base_value`.

### 4.2 Piecewise Curve Evaluation

Given sorted control points `(x₀, y₀), (x₁, y₁), ...`:

1. Locate the segment containing `x` by scanning forward until `x ≤ x₁`.
2. If no segment contains `x` (i.e., `x` is past the last point), the last
   segment is used (extrapolation — see §4.3).
3. Within the located segment, apply linear interpolation:

$$
y = \frac{y_1 \cdot (x - x_0) + y_0 \cdot (x_1 - x)}{x_1 - x_0}
$$

The special cases `x₀ == x₁` (degenerate segment) or `y₀ == y₁` (flat
segment) return `y₀` directly, avoiding division by zero.

### 4.3 Extrapolation Behavior (Parity-Critical)

This is the most commonly missed parity detail:

- If `x` is **below** the first control point, libmypaint uses the **first
  segment slope** (left extrapolation).
- If `x` is **above** the last control point, libmypaint uses the **last
  segment slope** (right extrapolation).

**It does NOT clamp to endpoint y-values.** Implementations that clamp
instead will diverge from libmypaint at input extremes — which are frequently
reached by stylus behavior.

### 4.4 Speed Input Formula

The `speed1` and `speed2` inputs are not raw pixel-per-second values. They
are remapped through a logarithmic curve so that the dynamic range perceived
by the user is approximately linear:

```text
y = log(gamma + x) * m + q
```

where:

- `x` = filtered physical speed (pixels/second, zoom-adjusted)
- `gamma = exp(speed1_gamma)` or `exp(speed2_gamma)` from the **base** brush
  settings
- `m` and `q` are precomputed using fixed constraints:
  - `fix1_x = 45`, `fix1_y = 0.5`
  - `fix2_x = 45`, `fix2_dy = 0.015`
  - `c1 = log(fix1_x + gamma)`
  - `m = fix2_dy * (fix2_x + gamma)`
  - `q = fix1_y - m * c1`

This remap is **precomputed when base values change** and reused at runtime.
Implementations that use raw speed directly will produce visibly different
brush response when any `speed`-driven settings are active.

Note: `pressure` at this stage has already been transformed by
`pressure_gain_log` in the input-update stage, so gain must not be applied
a second time here.

### 4.5 Mapping Constraints Summary

From §2.6, for each setting-input mapping:
- Control-point count is `0` or `2..64` (`1` is invalid).
- x-values must be non-decreasing.

Validate these before runtime evaluation; they are not re-validated during
simulation.

---

## Module 5: Dab Scheduling and Emission

> **Prerequisites:** Modules 1–4.
>
> **Learning objective:** Understand how the engine turns one input event into
> zero or more dab operations. The complete scheduler loop — partial dab carry,
> per-dab recompute, interpolation contract, and parity pitfalls — is
> specified in [brush-engine.md](brush-engine.md) §5.

### 5.1 The Event-Phase Scheduling Model

For each input event, scheduling has two phases:

1. **Emit full dabs** while `partial_dabs + dabs_todo >= 1.0`.
2. **Advance state without drawing** by the remaining fractional dab amount.

The second phase is parity-critical. Even when no dab is emitted, state still
advances to event time so the next event starts from the correct dynamic state.

### 5.2 Additive Dab Count Formula

For the remaining movement/time from current brush state to target sample:

$$
\text{count} = \frac{\text{distance}}{R_{\text{actual}}} \cdot \text{dabsPerActualRadius}
             + \frac{\text{distance}}{R_{\text{base}}} \cdot \text{dabsPerBasicRadius}
             + dt \cdot \text{dabsPerSecond}
$$

Where:

- $R_{\text{actual}}$ = current dynamic radius (`actual_radius` state).
- $R_{\text{base}} = \exp(\text{base\_value}(\text{radius\_logarithmic}))$,
  clamped to radius limits.
- `distance` may be Euclidean or ellipse-adjusted (see `brush-engine.md` §5).

Mode-specific spacing source:

- Spacing terms use evaluated state values, with fallback to base values when
  the state value is invalid (zero/NaN).

The partial-dab carry, recompute loop, per-dab interpolation, and
ellipse-adjusted distance details are in [brush-engine.md](brush-engine.md) §5.

---

## Module 6: Per-Dab Parameter Assembly

> **Prerequisites:** Modules 1–5.
>
> **Learning objective:** Understand how each dab's final parameters are
> assembled from brush settings and state. After this module you can implement
> `prepare_and_draw_dab()` — the function that bridges the scheduler loop
> and the surface backend.

### 6.1 Assembly Pipeline

For each emitted dab, parameters are resolved in this order:

1. Build base opacity from `opaque` and `opaque_multiply`.
2. Apply optional `opaque_linearize` correction (§6.3).
3. Start dab center at `actual_x/actual_y`.
4. Apply directional offsets, speed offset, random offset (§6.4).
5. Resolve radius (including optional `radius_by_random` adjustment).
6. Build color path (base HSV → RGB, smudge, eraser, color dynamics —
   see Module 7).
7. Apply geometry refinements (`hardness`, anti-aliasing minimum,
   snap-to-pixel — §6.5).
8. Submit to `mypaint_surface_draw_dab()`.

This ordering is part of behavior parity.

### 6.2 Geometry and Guard Rails

Key geometric parameters passed to the surface:

- dab center (`x`, `y`) after offsets/snapping
- `radius`
- `hardness`
- `aspect_ratio`, `angle`

Radius is clamped in the brush core to `[0.2, 1000]` pixels
(`ACTUAL_RADIUS_MIN`, `ACTUAL_RADIUS_MAX`). The tiled surface path then adds
finer guards — dabs with `radius < 0.1`, `hardness == 0`, or `opaque == 0`
are skipped entirely (see `surface-layer-gpu.md` §4).

### 6.3 Opacity Linearize Correction

Raw per-dab opacity:

```text
opaque = clamp(max(0, SETTING(opaque)) * SETTING(opaque_multiply), 0, 1)
```

If `opaque_linearize` is non-zero, libmypaint remaps per-dab alpha using an
estimated overlap count, so that visually the stroke feels linearly proportional
to `opaque` even when dabs are densely packed:

```text
dabs_per_pixel = (dabs_per_actual_radius + dabs_per_basic_radius) * 2.0
dabs_per_pixel = max(1.0, dabs_per_pixel)
dabs_per_pixel = 1.0 + opaque_linearize * (dabs_per_pixel - 1.0)

beta     = 1.0 - opaque
beta_dab = pow(beta, 1.0 / dabs_per_pixel)
opaque   = 1.0 - beta_dab
```

`opaque_linearize` is read from the **base value** (not a dynamic mapping),
and overlap estimation uses evaluated spacing state.

### 6.4 Position Offsets and Radius Noise

Offset order during dab assembly:

1. **Directional offsets** via `directional_offsets()` using `FLIP` and
   `exp(offset_multiplier) * base_radius` scaling. These implement the
   `offset_angle*`, `offset_x`, `offset_y` settings, creating lateral arm
   offset patterns.
2. **Speed offset** using low-pass speed vectors: `norm_dx_slow/norm_dy_slow`,
   scaled by `offset_by_speed * 0.1 / viewzoom`.
3. **Random offset** as Gaussian noise in base-radius units (`offset_by_random`).

`radius_by_random` applies Gaussian noise in log-radius space and re-clamps
the resulting radius. libmypaint also applies a conditional opacity correction
to partly preserve coverage when noisy radius expands.

**FLIP state:** Alternates `+1 / −1` on each emitted dab. All directional
offset settings that use FLIP produce **mirrored arm patterns** across
consecutive dabs. Multi-bucket brushes store independent smudge state per arm
via the `smudge_bucket` setting (see Module 7).

**Gaussian noise formula** (Irwin–Hall approximation — see Module 10, §10.5):

```text
rand_gauss = (rng_next() + rng_next() + rng_next() + rng_next()) * 1.73205 - 3.46410
```

### 6.5 Anti-Aliasing and Snap-To-Pixel

Anti-aliasing is not a post-filter; it is a **geometric reparameterization**
done before rendering. If the fadeout thickness `radius * (1 - hardness)` is
below `anti_aliasing`, radius and hardness are jointly adjusted to preserve
optical radius while widening the edge transition.

Snap-to-pixel (`snap_to_pixel > 0`) linearly interpolates dab center toward
the nearest pixel center (`n + 0.5`) and radius toward 0.5-pixel increments.
Near full snap, libmypaint subtracts a tiny radius epsilon to avoid precision
artifacts on neighbor pixels.

### 6.6 Blend-Mode Control Semantics

- `eraser` does not switch blend modes; it scales `eraser_target_alpha`:
  `eraser_target_alpha *= (1 - eraser)`.
- `lock_alpha` uses dedicated lock-alpha blend passes in the surface backend,
  preserving destination alpha while updating RGB.
- `colorize` uses a non-separable color blend applying brush hue/chroma to
  destination pixels while preserving destination luminance/alpha.
  Luminance coefficients: `0.2126`, `0.7152`, `0.0722`.

The actual blend pass execution order is in `surface-layer-gpu.md` §5.

---

# Part IV — Color and Paint

---

## Module 7: Color Dynamics and Smudge

> **Prerequisites:** Modules 1–6.
>
> **Learning objective:** Understand the full color computation pipeline per
> dab: base color construction, smudge pickup and mixing, HSV/HSL dynamics,
> eraser, and the spectral pigment path. After this module you can implement
> all color-related behavior.

### 7.1 Per-Dab Color Pipeline (Order Is Mandatory)

The complete order within `prepare_and_draw_dab()`:

```text
1. Base brush color (HSV base values) → RGB
2. Smudge pickup (if recentness threshold triggers)
3. Update smudge bucket with new canvas sample
4. Apply smudge: mix bucket color into brush color → adjust eraser_target_alpha
5. Apply eraser: eraser_target_alpha *= (1 - eraser)
6. Apply HSV color dynamics
7. Apply HSL color dynamics (after HSV, same dab)
8. Submit color + eraser_target_alpha to surface draw callback
```

Do not reorder stages 2–7. Specifically: do not apply color dynamics before
smudge (stage 6 must follow stage 4), and do not apply eraser before smudge
(stage 5 must follow stage 4).

### 7.2 Base Color Source

libmypaint initializes dab color from brush **base values**:

- `base_value(color_h)` — hue (0–1 turns)
- `base_value(color_s)` — saturation
- `base_value(color_v)` — value

These are converted HSV → RGB before dynamics. This is why hosts treat
"current UI color" as host state and write these base values when activating
a brush.

### 7.3 Smudge Bucket Architecture

libmypaint can run in:

- **Single-bucket mode** (default): legacy smudge state in brush storage.
- **Multi-bucket mode** (`mypaint_brush_new_with_buckets(n)`): `n` independent
  buckets (up to 256), one selected per dab via `smudge_bucket`.

Bucket selection: `round(smudge_bucket)` clamped to `[0, n-1]`.

Multiple buckets matter for brushes with mirrored/offset dab arms (set via
`offset_angle*` and FLIP) that need independent wet-state memory per arm.

Each bucket stores 9 floats:

| Field | Description |
| --- | --- |
| `SMUDGE_R/G/B/A` | Accumulated smudge color |
| `PREV_COL_R/G/B/A` | Previously sampled canvas color |
| `PREV_COL_RECENTNESS` | Sample freshness (decays per dab) |

### 7.4 Pickup Trigger and Recentness Decay

Smudge pickup is controlled by a decaying freshness value and a threshold test.

Per dab:

```text
update_factor = max(0.01, smudge_length)
recentness    = PREV_COL_RECENTNESS * update_factor
resample_if:
    recentness < min(1.0, pow(0.5 * update_factor, smudge_length_log) + margin)
```

If resampling happens, `recentness` is reset to `1.0`.

Practical interpretation:

- Larger `smudge_length` → old pickup is retained longer before re-sampling.
- Lower `smudge_length` → frequent pickup (high canvas responsiveness).
- `smudge_length_log` shifts the resample cadence non-linearly.

Pickup radius:

```text
smudge_radius = clamp(radius * exp(smudge_radius_log),
                      ACTUAL_RADIUS_MIN, ACTUAL_RADIUS_MAX)
```

After sampling, `smudge_transparency` can abort the dab early:

- Positive threshold: skip dab when sampled alpha is below threshold.
- Negative threshold: inverted behavior.

This early return happens before the final dab draw, so the setting can
suppress visible paint output in transparent regions.

### 7.5 Smudge Mix and Apply Stages

Two separate operations occur after pickup:

**1. Bucket update (`update_smudge_color`)**

- Legacy branch: EMA-like blend in RGBA.
- Pigment branch: spectral-aware mixing; for very low sampled alpha, falls
  back to alpha-only damping to avoid noise.

**2. Brush-color application (`apply_smudge`)**

```text
smudge_factor      = min(1, smudge)
eraser_target_alpha = clamp((1 - smudge_factor) + smudge_factor * smudge_alpha, 0, 1)
// then mix bucket color into brush color proportional to smudge_factor
```

`eraser` is applied afterward (see §7.1 step 5).

**Pickup source differs by API mode:**

- `mypaint_surface_get_color` with `paint` (spectral vs additive weighting), or
  `-1.0` to force legacy behavior when the `legacy_smudge` condition holds.

This split is parity-critical for matching old brushes in newer pipelines.

### 7.6 HSV Color Dynamics

When any HSV dynamic is non-zero, RGB is converted to HSV and updated:

```text
h += change_color_h           // hue shift (turns, wraps cyclically)
s += s * v * change_color_hsv_s   // context-scaled saturation shift
v += change_color_v           // value shift
```

Then HSV is converted back to RGB.

Notes:

- `change_color_hsv_s` is **multiplicative** on current saturation/value,
  not a plain additive offset.
- `change_color_h` uses normalized hue turns (fraction of full circle, not
  degrees).

### 7.7 HSL Color Dynamics

When any HSL dynamic is non-zero, current RGB is converted to HSL and updated:

```text
l += change_color_l
s += s * min(abs(1 - l), abs(l)) * 2 * change_color_hsl_s
```

Then HSL is converted back to RGB.

The saturation formula scales response by available headroom around lightness,
avoiding overly aggressive saturation shifts near extremes (0 or 1).

**Important:** HSL dynamics are applied **after** HSV dynamics on the same
dab color. Reordering these two stages breaks parity.

### 7.8 Linear-sRGB color dynamics (`linear` flag)

When `linear=TRUE` is passed to `mypaint_brush_stroke_to()`:

1. De-linearize RGB using exponent `1/2.2`.
2. Run HSV/HSL dynamics.
3. Re-linearize using exponent `2.2`.

This conversion is skipped unless at least one dynamics setting is active
for the dab (optimization).

### 7.9 Spectral / Pigment Smudge Behavior

Pigment paths use 10-band spectral conversion and weighted geometric mean
(WGM) mixing:

```text
spectral_result[i] = spectral_a[i]^fac_a * spectral_b[i]^fac_b
```

with alpha-proportional weights (`fac_a + fac_b = 1`).

To reduce low-alpha artifacts (dark fringing), libmypaint blends between
additive RGB and spectral results instead of forcing full spectral mixing at
all opacities. The spectral conversion constants and the full WGM formula are
in Module 10.

### 7.10 Draw-callback extensions

- `posterize`: quantizes destination RGB under the dab and blends the
  quantized result by posterize opacity. Alpha is unchanged.
  - `posterize_num` → `ROUND(posterize_num * 100)` clamped to `[1, 128]`.
- `paint_mode` mixes additive RGB and spectral pigment paths:
  - `0.0` = additive-only, `1.0` = spectral-only, intermediate = blend both.
  - When `0`, the spectral pigment passes (`Normal_Paint`, `LockAlpha_Paint`) are skipped.

### 7.11 Parity Pitfalls

- Do not model smudge as stateless per-dab sampling; bucket state is required.
- Preserve pickup gating and early-return from `smudge_transparency`.
- Keep legacy-vs-spectral `get_color` sampling split, including the `-1.0` legacy fallback.
- Preserve operation order: pickup/update bucket → apply smudge → apply
  eraser → draw.
- Do not treat `change_color_hsv_s` / `change_color_hsl_s` as simple additive
  knobs; both are context-scaled.
- In linear-sRGB paths, do not skip the de-linearize/re-linearize bracket when
  dynamics are active.

---

# Part V — Surface and Rendering

---

## Module 8: Canvas Model — Tiles and Pixel Format

> **Prerequisites:** Modules 1–7.
>
> **Learning objective:** Understand the canvas storage model: tile geometry,
> pixel format, coordinate conventions, the atomic execution model, and dirty-
> region tracking. After this module you can implement the surface backend's
> storage layer.

### 8.1 Tile Geometry

libmypaint uses a **sparse tile system**. The canvas is conceptually infinite
and divided into a uniform grid of square tiles:

```text
TILE_SIZE = 64          // pixel side length (MYPAINT_TILE_SIZE)
tile_x    = floor(pixel_x / TILE_SIZE)   // tile column index
tile_y    = floor(pixel_y / TILE_SIZE)   // tile row index
```

Tiles are allocated on demand when first written. A tile is identified by its
integer coordinates `(tx, ty)`. Tiles do not need to be contiguous in memory.

### 8.2 Pixel Format

Each tile is a flat `uint16_t` array of `TILE_SIZE × TILE_SIZE × 4` elements,
stored in row-major RGBA order:

```text
buffer[y * TILE_SIZE * 4 + x * 4 + 0]   // R (premultiplied)
buffer[y * TILE_SIZE * 4 + x * 4 + 1]   // G (premultiplied)
buffer[y * TILE_SIZE * 4 + x * 4 + 2]   // B (premultiplied)
buffer[y * TILE_SIZE * 4 + x * 4 + 3]   // A
```

The numeric range is **0 to 32768 (= 2^15)**, not 0–65535. All channels use
premultiplied alpha.

```text
max_value  = (1 << 15) = 32768
full_alpha = (1 << 15) = 32768
```

Float ↔ integer conversion:

```text
uint16_t r16 = (uint16_t)(r_float * 32768)
float r_float = r16 / 32768.0f
```

Because alpha is premultiplied, straight (unmultiplied) color is:

```text
r_straight = r16 / alpha16      // only valid when alpha16 > 0
```

**Why 15 bits?** Using `1<<15` (not `1<<16`) keeps the product of two max-range
values within `uint32_t` without overflow: `32768 × 32768 = 2^30 < 2^32`. This
allows all blend arithmetic to stay in 32-bit integer without overflow guards.

### 8.3 Pixel Coordinate Convention

libmypaint treats pixel `(xp, yp)` as having its **center at** `(xp + 0.5, yp + 0.5)`.

All dab rasterization and distance calculations use this convention:

```text
dx = pixel_center_x - dab_center_x = (xp + 0.5) - x
dy = pixel_center_y - dab_center_y = (yp + 0.5) - y
```

Implementations that use `(xp, yp)` as the pixel center produce slightly
shifted output, especially visible on hard-edged or small dabs.

### 8.4 Tile Footprint of a Dab

A dab centered at `(x, y)` with radius `r` potentially writes to tiles:

```text
r_fringe = r + 1.0   // +1 safety margin
tx1 = floor(floor(x - r_fringe) / TILE_SIZE)
tx2 = floor(floor(x + r_fringe) / TILE_SIZE)
ty1 = floor(floor(y - r_fringe) / TILE_SIZE)
ty2 = floor(floor(y + r_fringe) / TILE_SIZE)
```

The dab operation is queued independently for each `(tx, ty)` in the range
`[tx1..tx2] × [ty1..ty2]`. Inside each tile, the dab center is expressed in
tile-local coordinates: `x_local = x - tx * TILE_SIZE`.

### 8.5 Atomic Execution Model

`begin_atomic` / `end_atomic` bracket a logical rendering batch:

- **`begin_atomic`**: reset the dirty bbox to zero.
- Each **`draw_dab`** call: validate and enqueue the dab operation per tile;
  expand the dirty bbox to include the dab's bounding box. **No pixels are
  written at this point.**
- **`end_atomic`**: flush all queued tile operations; return the dirty bbox.

During `end_atomic`:

1. Collect the set of tiles with pending operations.
2. For each such tile (optionally in parallel with OpenMP):
   - Acquire the tile buffer (`tile_request_start`).
   - Pop and process all queued dab operations in order.
   - Release the tile buffer (`tile_request_end`).
3. Clear the operation queue and return the dirty bounding box.

**Operation ordering guarantee:** Within one tile, dab operations are applied
in the order they were enqueued. Blend modes are order-dependent; different
emission orderings produce different results (especially with partially-
transparent or smudge-heavy brushes).

### 8.6 Dirty-Region Tracking

The application uses the dirty bbox to decide which canvas regions to
re-composite or re-display. This design decouples stroke latency from UI
refresh latency.

In libmypaint, `stroke_to` calls `begin_atomic`/`end_atomic` around the
entire input event, so there is typically one atomic batch per input sample.

---

## Module 9: Advanced Surface Features

> **Prerequisites:** Modules 1–8.
>
> **Learning objective:** Understand the three advanced surface-layer features:
> canvas color pickup (`get_color`), the operation queue and deferred
> execution model, and symmetry painting.

### 9.1 Canvas Color Pickup (`get_color`)

`get_color` reads the average canvas color under a circular region. It is the
mechanism by which smudge state is updated (see Module 7, §7.4–7.5).

**Sampling mask** — always uses these fixed parameters, regardless of brush
settings:

```text
hardness     = 0.5     // always soft
aspect_ratio = 1.0     // always circular
angle        = 0.0
radius       = max(smudge_radius, 1.0)   // enforced minimum 1 pixel
```

**Adaptive sampling rate** (for performance):

```text
if radius <= 2.0:
    sample_interval    = 1         // sample every pixel
    random_sample_rate = 1.0       // plus 100% random
else:
    sample_interval    = (int)(radius * 7)   // guaranteed every N pixels
    random_sample_rate = 1.0 / (7 * radius)  // plus ~1/N% random
```

**Weighted color accumulation:**

```text
// Weight is the mask opacity value
weight   = mask_opacity * pixel_alpha / 32768^2
sum_weight += mask_opacity / 32768
sum_a      += weight    // alpha-weighted contribution
```

Legacy (additive RGB) path:

```text
sum_r += mask_opacity * rgba_r / 32768
// ... repeat for g, b
result_r = sum_r / sum_weight    // normalize
result_r /= result_a             // de-premultiply
```

Pigment (spectral-aware) path:

```text
fac_a = new_alpha / (old_sum_a + new_alpha)
fac_b = 1 - fac_a
avg_spectral[i] = spectral_pixel[i]^fac_a * avg_spectral[i]^fac_b
result = spectral_to_rgb(avg_spectral) * paint + rgb_additive * (1 - paint)
```

**Critical constraint:** `get_color` reads the tile buffer directly. If there
are pending draw operations in the operation queue that have not yet been
flushed, the pickup will sample stale data. libmypaint handles this by calling
`process_tile_internal()` on each tile before reading it during `get_color`.
An implementation must ensure queued dab operations are applied before the
buffer is sampled.

### 9.2 Operation Queue and Deferred Execution

`draw_dab` does not immediately composite pixels. Instead:

1. Validates the dab (radius, hardness, opacity guard rails from
   `surface-layer-gpu.md` §4).
2. Determines which tiles the dab overlaps (§8.4).
3. Creates a copy of the dab operation and **enqueues** it for each
   overlapping tile.
4. Expands the dirty bounding box.

No pixel blending occurs at `draw_dab` time. Actual blending is deferred to
`end_atomic` (see Module 8, §8.5).

This deferred model enables:

- Batching many dabs from one input event into one atomic flush.
- Parallelizing tile processing across CPU cores.
- Clean synchronization points for GPU backends (see Module 11).

### 9.3 Symmetry Painting and Mirroring

Module D described the application-side wiring. This section focuses on the
libmypaint-side execution model.

First, keep the two features separate:

- **Viewport mirroring** in `gui.document` only transforms the view.
- **Painting symmetry** in libmypaint duplicates dabs in model space and
  changes the layer contents.

**Legacy symmetry note:**

For every dab at `(x, y)`, a reflected dab is automatically drawn at
`(2*center_x - x, y)` with the dab angle negated:

```text
symm_x = surface_center_x + (surface_center_x - x)
draw_dab(symm_x, y, radius, ..., angle = -angle)
```

**Tiled-surface symmetry pipeline:**

1. MyPaint writes pending symmetry state into `MyPaintTiledSurface`.
2. `mypaint_tiled_surface_begin_atomic()` calls `mypaint_update_symmetry_state()`
   to refresh the transform matrices.
3. `draw_dab_internal()` renders the original dab.
4. If symmetry is active, `mypaint_transform_point()` is applied for each
   matrix and `draw_dab_internal()` renders the mirrored or rotated copies.

`MyPaintTiledSurface` supports additional symmetry types:

- **Vertical / horizontal**: mirror across an axis.
- **Vertical + horizontal**: one dab becomes a multi-axis mirrored family.
- **Rotational N-fold**: additional dabs are rotated around a center point.
- **Snowflake**: rotational copies plus reflected copies.

The symmetry center has both X and Y coordinates, and the native symmetry state
also supports an angle. The current MyPaint binding passes `0.0` for that
angle, so the library's representational envelope is slightly larger than the
application's current UI.

---

# Part VI — Spectral Pigment Reference

---

## Module 10: Spectral Conversion Reference

> **Prerequisites:** Module 7 (smudge and color); blend-pass order in
> `surface-layer-gpu.md` §5.
>
> **Learning objective:** Understand the exact constants and formulas for
> libmypaint's 10-band spectral model. After this module you can implement
> the spectral pigment path with full numerical accuracy.

### 10.1 10-Band Spectral Basis

libmypaint's spectral representation uses a reduced 10-band model. The three
RGB primaries are each represented as a 10-element spectral power distribution:

```text
// Exact values from helpers.c — libmypaint 1.6.x:
spectral_r[10] = {0.00928, 0.00973, 0.01125, 0.01511, 0.02480,
                   0.08362, 0.97787, 1.00000, 0.99996, 1.00000}
spectral_g[10] = {0.00285, 0.00392, 0.01213, 0.74826, 1.00000,
                   0.86570, 0.03748, 0.02282, 0.02175, 0.02138}
spectral_b[10] = {0.53705, 0.54665, 0.57550, 0.25878, 0.04171,
                   0.01266, 0.00749, 0.00677, 0.00670, 0.00668}
```

### 10.2 RGB to Spectral Conversion

```text
WGM_EPSILON = 0.0001   // avoid zero reflectance (log(0) in WGM)
offset      = 1.0 - WGM_EPSILON

r_adj = r * offset + WGM_EPSILON
g_adj = g * offset + WGM_EPSILON
b_adj = b * offset + WGM_EPSILON

spectral[i] = spectral_r[i] * r_adj
            + spectral_g[i] * g_adj
            + spectral_b[i] * b_adj
```

### 10.3 Spectral to RGB Conversion

Uses the 3×10 T-matrix (pseudo-inverse of the upsampling basis):

```text
// T_MATRIX_SMALL[3][10] — exact values from helpers.c:
T[0] = {0.02660, 0.04978, 0.02245, -0.21845, -0.25689, 0.44588,
        0.77237, 0.19450, 0.01404, 0.00769}
T[1] = {-0.03260, -0.06102, -0.05249, 0.20666, 0.57250, 0.31784,
         -0.02122, -0.01939, -0.00152, -0.00084}
T[2] = {0.33948, 0.63540, 0.77152, 0.11322, -0.05525, -0.04822,
        -0.01297, -0.00152, -0.00009, -0.00005}

rgb_raw[c] = sum(T[c][i] * spectral[i] for i in 0..9)
rgb[c]     = clamp((rgb_raw[c] - WGM_EPSILON) / offset, 0, 1)
```

### 10.4 Weighted Geometric Mean (WGM) Mixing

Spectral mixing of color A and color B with weights `fac_a`, `fac_b = 1 - fac_a`:

```text
spectral_result[i] = spectral_a[i]^fac_a * spectral_b[i]^fac_b
```

Alpha-proportional weights (as used in brush compositing):

```text
fac_a = opa_a / (opa_a + opa_b * bottom_alpha / 32768)
fac_b = 1 - fac_a
```

`WGM_EPSILON` prevents `0^fac = 0` from collapsing the mix. The value
`0.0001` is hardcoded and must not be changed without recalculating the T-matrix.

### 10.5 Gaussian Noise via Irwin–Hall Approximation

libmypaint implements Gaussian noise using the 4-sample Irwin–Hall
approximation (sum of 4 uniform randoms, scaled):

```text
sum       = rng_next() + rng_next() + rng_next() + rng_next()
rand_gauss = sum * 1.73205080757 - 3.46410161514
// Approximately N(0, 1)
```

The scale factor `√3 ≈ 1.732` and offset `−2√3 ≈ −3.464` center and
normalize the Irwin–Hall(4) distribution. This is used for:

- `offset_by_random` (position jitter),
- `radius_by_random` (radius noise),
- `tracking_noise` (cursor perturbation).

GPU implementations should replicate this exact formula with a reproducible
seeded RNG to preserve determinism.

### 10.6 RNG: Knuth Lagged Fibonacci Generator

libmypaint uses a Knuth lagged Fibonacci generator (LFIB) initialized via
`rng_double_new(seed)`. The parameters used (low-quality settings, sufficient
for visual noise):

```text
KK = 10     // long lag
LL = 7      // short lag
QUALITY = 19
```

The generator produces doubles in [0, 1). The RNG state is carried across
dabs; advancing it outside the dab emission order breaks determinism.

---

# Part VII — GPU Implementation

---

## Module 11: GPU Backend Architecture

> **Prerequisites:** All previous modules.
>
> **Learning objective:** Understand how to map libmypaint's CPU rendering
> model to a GPU backend using Skia/Skiko or Vulkan. After this module you
> can implement a GPU-accelerated surface backend.

### 11.1 CPU / GPU Split Strategy

Keep the brush core (mapping, dab planning, state machine) on the CPU and move
only the surface backend to the GPU; for the rationale and the
renderer-architecture background, see the `gpu-rendering-guide` skill and
`surface-layer-gpu.md` §9.

### 11.2 Skia / Skiko Backend Strategy

Skia does not natively expose libmypaint blend semantics, but can be mapped
at the dab level using `SkCanvas` and custom shaders.

**Dab shape shader (`SkRuntimeEffect` / SkSL):**

```glsl
// In SkSL:
uniform float2 center;
uniform float  radius;
uniform float  aspect_ratio;
uniform float  angle;
uniform float  hardness;

float opa(float2 pos) {
    float2 d = pos - center;
    float cs = cos(angle), sn = sin(angle);
    float xxr = d.y * sn + d.x * cs;
    float yyr = (d.y * cs - d.x * sn) * aspect_ratio;
    float rr  = (xxr*xxr + yyr*yyr) / (radius * radius);
    if (rr > 1.0) return 0.0;
    float s1_offset = 1.0;
    float s1_slope  = -(1.0 / hardness - 1.0);
    float s2_offset = hardness / (1.0 - hardness);
    float s2_slope  = -hardness / (1.0 - hardness);
    return (rr <= hardness)
        ? s1_offset + rr * s1_slope
        : s2_offset + rr * s2_slope;
}
```

**Blend mode mapping:**

- Normal / Eraser: `SkBlendMode::kSrcOver`
- Lock-Alpha: `SkBlendMode::kSrcATop`
- Colorize: no direct Skia equivalent — use `SkRuntimeEffect` shader
- Posterize: use `SkRuntimeEffect` with the quantization formula

**Tile granularity:** Map each libmypaint 64×64 tile to an `SkSurface` or
`SkPixmap`. Flush the dab draw list for each tile at `end_atomic`.

**Latency:** Skia batches draw calls internally; calling `SkSurface::flush()`
at `end_atomic` is the synchronization point. This maps cleanly to the
`begin_atomic`/`end_atomic` contract.

### 11.3 Vulkan Backend Strategy

Vulkan provides explicit control over memory, synchronization, and pipeline
— ideal for maximum throughput and minimum latency.

**Tile storage:** Each tile is a `VkImage` region (or a texel in a texture
array). Use `R16G16B16A16_UNORM` with values scaled to 0–32768 (full range =
32768 / 65535). Alternatively, `R16G16B16A16_SFLOAT` for higher precision.

**Compute shader pipeline** (one workgroup = one tile):

```glsl
layout(local_size_x = 8, local_size_y = 8) in;

layout(set=0, binding=0, rgba16) uniform image2D tile;
layout(set=0, binding=1) readonly buffer DabList {
    DabParams dabs[];
};
layout(push_constant) uniform PC {
    int num_dabs;
    ivec2 tile_origin;   // tile_x * 64, tile_y * 64
};

void main() {
    ivec2 local_px = ivec2(gl_LocalInvocationID.xy);
    ivec2 px = tile_origin + local_px;
    vec2 px_center = vec2(px) + vec2(0.5);

    vec4 color = imageLoad(tile, local_px);

    for (int i = 0; i < num_dabs; i++) {
        DabParams d = dabs[i];
        float rr  = compute_rr(px_center, d);
        float opa = compute_opa(rr, d.hardness);
        color = blend(color, d, opa);    // apply blend passes in correct order
    }

    imageStore(tile, local_px, color);
}
```

**Key implementation decisions:**

- Keep the dab parameter list per tile small (one buffer per tile, uploaded
  before dispatch).
- Use `VK_IMAGE_LAYOUT_GENERAL` for read-modify-write operations in compute.
- Synchronize with a `VkMemoryBarrier` (`SHADER_WRITE → SHADER_READ`) before
  any `get_color` reads.

**Latency reduction strategies:**

- **Front-buffer rendering:** Write dab results into a staging buffer that is
  continuously displayed, rather than waiting for a full frame to complete.
- **Double-buffered tiles:** While the GPU processes the last `end_atomic`
  batch, the CPU accumulates new dabs into a second queue.
- **Workgroup size:** `8×8 = 64` threads per workgroup processes one quarter-
  tile per dispatch. For small dabs (few pixels affected), a 1D dispatch over
  only the affected pixel count may be faster.

### 11.4 Blend Mode Shader Implementation

Each blend pass (see `surface-layer-gpu.md` §5) maps to a shader subfunction. In Vulkan GLSL:

```glsl
// Normal (over) blend — premultiplied alpha:
vec4 blend_normal(vec4 dst, vec3 src_rgb, float src_a, float opa_weight) {
    float opa_a = opa_weight;
    float opa_b = 1.0 - opa_a;
    float out_a = opa_a * src_a + opa_b * dst.a;
    vec3  out_c = opa_a * src_a * src_rgb + opa_b * dst.rgb;
    return vec4(out_c, out_a);
}

// Lock-alpha: paint only where destination has alpha:
vec4 blend_lock_alpha(vec4 dst, vec3 src_rgb, float opa_weight) {
    float opa_a = opa_weight * dst.a;
    float opa_b = 1.0 - opa_weight;
    vec3  out_c = opa_a * src_rgb + opa_b * dst.rgb;
    return vec4(out_c, dst.a);           // alpha unchanged
}

// Colorize: apply source hue/saturation, preserve destination luma:
vec4 blend_colorize(vec4 dst, vec3 src_rgb, float opa_weight) {
    vec3 dst_s = dst.a > 0 ? dst.rgb / dst.a : vec3(0);
    vec3 src_with_dst_luma = set_lum(src_rgb, lum(dst_s));
    float opa_a = opa_weight;
    float opa_b = 1.0 - opa_a;
    return vec4(opa_a * src_with_dst_luma * dst.a + opa_b * dst.rgb, dst.a);
}
// Luma coefficients: (0.2126, 0.7152, 0.0722)
```

### 11.5 Canvas Color Pickup on GPU

Canvas color pickup (Module 9, §9.1) requires reading from the tile texture,
which may conflict with in-flight write operations.

Strategy:

1. Before any `get_color` call in a dab emission loop, flush the tile
   (commit all pending draw operations).
2. Issue a memory barrier (`SHADER_WRITE → SHADER_READ`).
3. Dispatch a small reduction compute shader that computes the weighted color
   average within the dab radius, using the same `rr` formula (with
   `hardness=0.5`) as the weight function.
4. Read back the result via a small staging buffer.

For GPU backends, read-back latency is significant. Minimize `get_color`
calls by obeying the `smudge_length` throttling that the brush core provides
— this is why `smudge_length > 0` is important for performance, not just
aesthetics.

### 11.6 Recommended Implementation Order

For a new GPU brush engine, this sequence reduces risk:

1. Implement the brush core in CPU (dab planning, mapping evaluation, state
   machine) with a simple CPU surface backend writing to a plain pixel buffer.
2. Validate brush core correctness against libmypaint reference output using
   unit tests and golden image comparison.
3. Replace the CPU surface backend with a GPU tile backend:
   a. Start with a Vulkan or Skia backend that renders Normal-mode only.
   b. Add Lock-Alpha, Colorize, Posterize passes.
   c. Add smudge (`get_color` with GPU readback).
   d. Add spectral pigment mixing last (most complex, least common usage).
4. Optimize: tile parallelism, command buffer reuse, staging buffer pools.

## References

- MyPaint repository: https://github.com/mypaint/mypaint
- libmypaint repository: https://github.com/mypaint/libmypaint
- `BUILDING.md` in this repository
- Key source roots in this repository: `gui/`, `lib/`, `libmypaint-1.6.1/`,
  and `tests/`
- MyPaint Manual: https://www.mypaint.app/en/docs/manuals/v1.2.0/
- `.myb` preset format sources in libmypaint/MyPaint projects
- Skia documentation: https://skia.org/docs/
- Vulkan specification: https://www.khronos.org/vulkan/
