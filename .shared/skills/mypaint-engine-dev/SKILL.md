---
name: mypaint-engine-dev
description: Write, review, debug, and implement MyPaint and libmypaint brush engines, stroke-to-dab rendering, tiled surfaces, layers, symmetry, smudge/pigment behavior, and GPU surface backends. Use when working on mypaint/mypaint or mypaint/libmypaint source navigation, .myb presets, live drawing, brush-engine parity, resource management, or designing a new painting application inspired by MyPaint — even if the user doesn't say MyPaint. Triggers on libmypaint, mypaint_brush_stroke_to, BrushInfo, BrushworkModeMixin, MyPaintTiledSurface, .myb, smudge buckets, paint_mode, and dab scheduling.
---

# MyPaint Engine Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Expert guidance for architecting, designing, debugging, and implementing MyPaint,
libmypaint, and compatible stroke rendering engines. Read bundled references on demand
— do not load all reference files unless the task requires them.

## When to Use

- Navigating or modifying MyPaint application code (`gui/`, `lib/`) or libmypaint brush core
- Debugging `.myb` presets, input mappings, dab scheduling, smudge, pigment, or stroke parity
- Implementing or porting tiled surface backends (CPU, Skia, Vulkan)
- Designing a new painting application's stroke system inspired by MyPaint
- Explaining pixel flow from GTK/tablet input through layers to canvas display
- Verifying claims against local or upstream MyPaint/libmypaint checkouts

## When NOT to Use

- General native crash/UAF debugging with no painting-engine context — use
  [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
- Standalone GPU renderer architecture (render graphs, bindless, frames-in-flight) without
  MyPaint surface/tile context — use
  [../gpu-rendering-guide/SKILL.md](../gpu-rendering-guide/SKILL.md)
- Qt desktop UI work unrelated to MyPaint's GTK stack — MyPaint uses GTK, not Qt
- CMake/build setup for non-painting C++ projects — use [../cmake-dev/SKILL.md](../cmake-dev/SKILL.md)
- Krita paintop/stroke scheduling — use [../krita-engine-dev/SKILL.md](../krita-engine-dev/SKILL.md)

## Operating stance

Treat MyPaint as two cooperating systems: the Python/GTK application owns UI, documents,
layers, tools, presets, undo, and live drawing workflow; libmypaint owns deterministic
brush-state integration, dab planning, and surface callbacks.

When exact code matters, inspect the user's checkout or upstream repositories. If local
checkouts are available, run `<SKILL_ROOT>/scripts/mypaint_source_probe.py` before making
strong claims about file paths or symbols.

## Response workflow

1. Classify the request and read every matching row in [Reference routing](#reference-routing).
2. Start from the right boundary: app layer, binding layer, brush core, surface backend,
   or display/compositing layer.
3. Give implementation guidance in this order unless the user asks otherwise:
   - architecture map and ownership;
   - concrete implementation plan;
   - parity-critical invariants;
   - performance risks;
   - tests and validation cases.
4. For new engines, keep the brush core deterministic and renderer-independent. Move
   acceleration into the surface backend first; do not rewrite the stroke state machine
   until a CPU reference path matches libmypaint.

## Core mental model

The live painting path is:

```text
GTK/tablet event
  -> gui.document (controller) / active gui.mode
  -> gui.mode.BrushworkModeMixin
  -> lib.command.Brushwork
  -> lib.layer.data.SimplePaintingLayer
  -> lib.brush.Brush
  -> lib/brush.hpp and lib/python_brush.hpp
  -> mypaint_brush_stroke_to(..., linear)
  -> mypaint-brush.c brush core
  -> MyPaintSurface / MyPaintTiledSurface callbacks
```

Key ownership rules:

- MyPaint application: session, tools, mode stack, document model, layer tree, undo/redo,
  brush preset editing, UI state, and display refresh.
- Binding layer: minimal bridge between Python objects and native libmypaint objects.
- libmypaint brush core: input sanitization, virtual cursor, setting mappings, dab scheduling,
  color/smudge state, and deterministic random input.
- Surface backend: tile allocation, dab mask/rasterization, blend passes, dirty bbox,
  `get_color`, and optional symmetry duplication.

## Non-negotiable brush-engine invariants

Preserve these unless the user explicitly wants a non-compatible engine:

- `.myb` presets use version 3 with a `settings` object. Unknown setting/input entries should
  warn and skip, not crash the whole preset.
- Setting values are `base_value + sum(mapping(input))`; mapping curves extrapolate using
  endpoint segment slopes instead of clamping.
- Use `mypaint_brush_stroke_to()` with explicit view zoom/rotation and barrel rotation;
  pass `linear=TRUE` when HSV/HSL dynamics must run in linear sRGB (`lib/brush.py` uses
  `eotf() != 1.0`).
- `mypaint_surface_draw_dab()` carries `paint_mode`, `posterize`, `lock_alpha`, and `colorize`.
- Clamp/sanitize raw inputs before integration: pressure floor, tilt range, small positive `dt`,
  reset on large time gaps or invalid positions.
- A stroke update is a state integrator, not a simple line rasterizer. Preserve partial dab
  carry, per-dab recomputation, post-loop state advancement, and shortest-angle interpolation.
- Advance the RNG exactly once per emitted dab, immediately after the draw operation.
- Keep smudge bucket state across dabs; do not replace smudge with stateless per-dab sampling.
- Surface pixels are sparse 64×64 tiles, premultiplied RGBA uint16, full scale 32768, not 65535.
- Composite passes are order-dependent. Preserve normal, pigment, lock-alpha, colorize, and
  posterize ordering.
- Dirty rectangles are correctness data, not only optimization hints.

## Reference routing

| Task | Read |
|------|------|
| Application/tools/layers/undo/UI integration | [architecture.md](references/architecture.md) |
| `.myb` presets, mappings, dab scheduler, smudge, pigment, determinism | [brush-engine.md](references/brush-engine.md) |
| Tiles, compositing, symmetry, layer rendering, GPU/Skia/Vulkan backends | [surface-layer-gpu.md](references/surface-layer-gpu.md) |
| Live drawing performance, debugging, regression and parity testing | [performance-validation.md](references/performance-validation.md) |
| Source navigation or verification against repositories | [source-map.md](references/source-map.md) |
| Extended background when focused references are insufficient (~2800 lines) | [MyPaintProgrammingGuide.md](references/MyPaintProgrammingGuide.md) |

When a task spans multiple areas, read **every matching row**.

## Source verification workflow

If the user provides local checkouts or asks for exact source navigation:

```bash
python <SKILL_ROOT>/scripts/mypaint_source_probe.py \
  --mypaint /path/to/mypaint \
  --libmypaint /path/to/libmypaint
```

The script checks file existence and symbol anchors. It does not prove semantic correctness.
If a path or symbol is missing, search the checkout rather than guessing.

**API note:** Older docs and forks may refer to `mypaint_brush_stroke_to_2` or "Surface2".
Current upstream libmypaint uses the unified `mypaint_brush_stroke_to()` and `MyPaintSurface`
callbacks documented in [source-map.md](references/source-map.md).

## Output patterns

For design reviews, use:

```text
Diagnosis
- Likely layer/boundary:
- Relevant source anchors:
- Why this boundary owns the behavior:

Implementation plan
1. ...
2. ...
3. ...

Parity and performance risks
- ...

Validation
- Unit tests:
- Determinism tests:
- Visual/golden tests:
```

For implementing a new stroke renderer, use:

```text
Architecture
- App/controller layer:
- Brush core:
- Surface backend:
- Resource/preset model:
- Display/GPU integration:

Core data structures
- BrushInfo/Preset:
- BrushState:
- MappingCurve:
- DabOp:
- Tile/LayerSurface:

Stroke loop
- input sanitize -> virtual cursor -> mapping eval -> dab scheduler -> draw callback -> dirty bbox

Validation gates
- preset parsing -> mapping math -> dab sequence -> pixel blend -> layer/UI integration -> performance
```

## Resources

- [architecture.md](references/architecture.md) — application architecture and event path
- [brush-engine.md](references/brush-engine.md) — libmypaint brush core and presets
- [surface-layer-gpu.md](references/surface-layer-gpu.md) — tiles, compositing, GPU strategy
- [performance-validation.md](references/performance-validation.md) — performance and parity testing
- [source-map.md](references/source-map.md) — source reading order and verification
- [MyPaintProgrammingGuide.md](references/MyPaintProgrammingGuide.md) — extended maintainer guide
- [SOURCES.md](SOURCES.md) — provenance and external references (read for attribution only)
