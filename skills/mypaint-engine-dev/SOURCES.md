# Sources

## MyPaint application repository

- **URL:** https://github.com/mypaint/mypaint
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → application/event path and ownership model
  - `references/architecture.md` → `gui/`, `lib/`, mode stack, brush preset flow
  - `scripts/mypaint_source_probe.py` → MyPaint file and symbol anchors
- **Aspects extracted:**
  - `BrushworkModeMixin` → `lib.command.Brushwork` → `SimplePaintingLayer.stroke_to()` chain
  - `lib/brush.py` `BrushInfo` / `Brush` split and `eotf()` linear flag
  - `lib/brush.hpp` delegation to `mypaint_brush_stroke_to(..., linear)`

## libmypaint repository

- **URL:** https://github.com/mypaint/libmypaint
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → brush-core invariants and unified API naming
  - `references/brush-engine.md` → preset schema, dab scheduler, smudge, determinism
  - `references/surface-layer-gpu.md` → tile format, blend passes, symmetry
  - `references/source-map.md` → libmypaint reading order
  - `scripts/mypaint_source_probe.py` → libmypaint file and symbol anchors
- **Aspects extracted:**
  - `mypaint_brush_stroke_to()` with view/barrel inputs and `linear` color-dynamics flag
  - `mypaint_surface_draw_dab()` / `mypaint_surface_get_color()` unified callback contract
  - `MYPAINT_TILE_SIZE` 64, premultiplied RGBA `1<<15` scale in `brushmodes.c`
  - `mypaint_mapping_calculate()` extrapolation and `assert (n != 1)`
  - `MyPaintTiledSurface` symmetry via `mypaint_tiled_surface_set_symmetry_state()`

## skills-ref/krita-engine-dev (bootstrap template)

- **Path:** `.shared/skills/krita-engine-dev/` (installed reference)
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` structure: `<SKILL_ROOT>`, When to Use / When NOT, reference routing, source verification workflow
  - `eval-queries.json` train/validation split pattern
  - `SOURCES.md` provenance layout

## skills-ref/mypaint-engine-dev (authoring bundle)

- **Path:** `skills-ref/mypaint-engine-dev/`
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/MyPaintProgrammingGuide.md` → extended maintainer guide distilled into focused references
- **Aspects extracted:**
  - Progressive module structure, parity pitfalls, GPU implementation order, validation matrix
