# MyPaint Application Architecture

Load this reference for questions about the MyPaint application, GTK input, tools, documents, layers, commands, undo/redo, brush preset ownership, resource flow, or UI integration.

## 1. Repository roles

- `mypaint.py`: launcher and source/install layout setup.
- `gui/`: GTK application, canvas view, mode stack, tools, windows, overlays, device handling, and most controllers.
- `lib/`: document model, layer tree, command stack, brush preset objects, bindings, tiled surface bridge, stroke recording, and GUI-independent infrastructure.
- `libmypaint-*/` in the MyPaint repository: bundled reference copy in some checkouts; app builds usually depend on the libmypaint found by `pkg-config` unless configured otherwise.
- `tests/`: Python and extension-level behavior tests.

## 2. Startup and runtime object graph

The startup path is staged to avoid GTK/GLib/gettext/libmypaint import-order problems:

```text
mypaint.py
  -> gui.main.main()
  -> gui.application.Application
  -> Gtk.Builder, main window, document model, document controller, canvas, file handler, brush manager
  -> Gtk.main()
```

Painting-relevant runtime graph:

```text
Application
  +-- gui.document.Document controller
  |     +-- ModeStack
  |     +-- active tool/mode, often gui.freehand.FreehandMode
  +-- gui.tileddrawwidget.TiledDrawWidget view
  +-- lib.document.Document model
        +-- RootLayerStack
        +-- live lib.brush.Brush
        +-- CommandStack
```

Ownership rule:

- `gui.*` responds to user interaction and owns transient controller state.
- `lib.document.Document` owns the saved model and command history.
- `lib.layer.*` owns layer semantics and paint surfaces.
- `lib.brush.BrushInfo` owns editable preset data.
- `lib.brush.Brush` mirrors preset settings into native brush mappings and owns live engine state through the binding.

## 3. Event-to-stroke path

Canonical live drawing path:

```text
GDK event
  -> TiledDrawWidget / CanvasController
  -> ModeStack active mode
  -> BrushworkModeMixin.stroke_to()
  -> lib.command.Brushwork.stroke_to()
  -> lib.layer.data.SimplePaintingLayer.stroke_to()
  -> lib.brush.Brush.stroke_to()
  -> C++/SWIG bridge (lib/brush.hpp)
  -> mypaint_brush_stroke_to(..., linear)
  -> libmypaint brush core
  -> surface draw_dab / get_color callbacks
```

Use this path to decide where to debug:

- Wrong input mode, cursor, tool, symmetry overlay, or view transform: start in `gui/`.
- Wrong undo split, command stack entry, or pending stroke state: start in `lib.command` and `gui.mode.BrushworkModeMixin`.
- Wrong layer target, alpha-lock behavior, layer visibility, or surface atomic region: start in `lib.layer`.
- Wrong dab count, brush dynamics, smudge, spacing, color, or pressure behavior: start in `lib.brush` and `libmypaint/mypaint-brush.c`.
- Wrong pixels, blend result, dirty box, or symmetry duplication: start in the surface backend.

## 4. Document, layers, commands

`lib.document.Document` is the model. It owns the root layer stack, active brush, command stack, autosave state, frame/resolution metadata, and document settings. Before saving/exporting or running model-wide operations, call or account for pending-state synchronization so active tools flush brushwork into the command history.

`RootLayerStack` coordinates current layer selection, background, render cache invalidation, path traversal, and painting symmetry state.

`SurfaceBackedLayer` descendants hold paintable surfaces. `SimplePaintingLayer.stroke_to()` wraps incremental brush calls in `begin_atomic()` and `end_atomic()`, so the native backend can batch dabs and return a dirty region after each input sample.

Brushwork is undoable by recording input samples and painting incrementally:

```text
Brushwork recorder
  -> lib.stroke.Stroke records samples
  -> layer paints immediately
  -> split_due / explicit commit produces command-stack entry
```

Do not push one undo command per dab. A dab is a renderer operation, not an application command.

## 5. Brush preset model

Use these terms precisely:

- `BrushInfo`: Python-level editable/serializable `.myb` preset data. Contains settings, mapping curves, metadata, observers, and UI-facing state.
- `Brush`: live runtime bridge object. Updates native mappings from `BrushInfo`, calls native `stroke_to`, and carries state needed for cursor/stroke behavior.
- `.myb`: JSON preset payload; libmypaint simulation consumes setting and input mappings, while MyPaint may also store host metadata.

When the user edits a brush in the UI, update `BrushInfo`; ensure observers propagate changed settings into the live `Brush`. When a brush is selected, copy settings into the global live brush while preserving runtime state where appropriate.

`lib/brush.py` appends `linear = (eotf() != 1.0)` before calling the native `stroke_to`, so HSV/HSL dynamics run in linear sRGB when the document uses a non-identity electro-optical transfer function.

## 6. Symmetry versus viewport mirroring

Separate these features:

- Viewport mirroring changes only the view transform and does not alter layer contents.
- Painting symmetry duplicates dabs in model space and changes the target surface.

Symmetry state path:

```text
gui.symmetry / action
  -> RootLayerStack.set_symmetry_state()
  -> SurfaceBackedLayer.set_symmetry_state()
  -> lib.tiledsurface.Surface.set_symmetry_state()
  -> native tiled surface
  -> begin_atomic refreshes symmetry transforms
  -> draw_dab duplicates each emitted dab
```

If the overlay is correct but paint is wrong, debug propagation into the native surface and the per-dab symmetry transform path. If the canvas view is mirrored but the model should not change, stay in view/controller code.

## 7. Application extension rules

- New menu, toolbar, action: wire through `gui/resources.xml` or current GTK action resources and attach the handler to an object registered by `Application`.
- New tool or interaction mode: subclass/compose a mode under `gui.mode` and route it through the mode stack.
- New undoable model change: add or extend a `lib.command.Command` subclass.
- New layer behavior: implement it in `lib.layer`, then expose controls in `gui`.
- New brush editor or preset behavior: modify `BrushInfo`, brushsettings metadata, and UI widgets together; verify native mappings update.

Keep durable behavior in `lib/` when it belongs to the model; keep event routing and display-only state in `gui/`.
