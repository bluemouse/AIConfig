# Sources

## KisPaintOp header (KDE/krita)

- **URL:** https://github.com/KDE/krita/blob/master/libs/image/brushengine/kis_paintop.h
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `SKILL.md` → Core Krita invariants, paintop contract
  - `references/core-classes-and-contracts.md` → `KisPaintOp` methods and spacing/timing contract
  - `references/architecture-map.md` → paintop framework responsibilities
  - `scripts/krita_source_probe.py` → symbol patterns for `kis_paintop.h`
- **Aspects extracted:**
  - Public `paintAt(info, currentDistance)` updates spacing/timing via `KisDistanceInformation`
  - Protected pure virtual `paintAt(const KisPaintInformation&)` returns `KisSpacingInformation`
  - `updateSpacingImpl`, `updateTimingImpl`, `doAsynchronousUpdate` hooks

## KisTiledDataManager source (KDE/krita)

- **URL:** https://github.com/KDE/krita/blob/master/libs/image/tiles3/kis_tiled_data_manager.cc
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/pixel-layer-gpu-performance.md` → sparse tiled storage model
  - `references/architecture-map.md` → pixel storage subsystem
  - `scripts/krita_source_probe.py` → tiled data manager anchors
- **Aspects extracted:**
  - Data area divided into compile-time-sized tiles (64×64 in current tree)
  - Sparse tile matrix with negative indexes and automatic growth
  - `bitBlt` / `bitBltRough` tile merge paths

## Krita tile data format (KDE Community Wiki)

- **URL:** https://community.kde.org/Krita/Tile_Data_Format
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/pixel-layer-gpu-performance.md` → tile dimensions and storage format
- **Aspects extracted:**
  - `TILEWIDTH 64` / `TILEHEIGHT 64` in tile file format
  - Tile compression and memento/swap integration via `KisAbstractTileCompressor`

## Building Krita (Krita docs)

- **URL:** https://docs.krita.org/en/untranslatable_pages/building_krita.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/krita-programming-guide.md` → build/checkout orientation
  - `references/source-reading-map.md` → contributor workflow context
- **Aspects extracted:**
  - Official build prerequisites and checkout expectations for source navigation

## Krita API documentation (KDE API docs)

- **URL:** https://api.kde.org/extragear-api/graphics-apidocs/krita/html/index.html
- **Last reviewed:** 2026-07-06
- **Used for:**
  - `references/krita-programming-guide.md` → companion doc links
  - `references/core-classes-and-contracts.md` → public API naming cross-check
- **Aspects extracted:**
  - High-level class index for image, brush engine, and UI modules

## skills-ref/krita-engine-dev (bootstrap template)

- **Path:** `skills-ref/krita-engine-dev/` (historical; the `skills-ref/` folder was deleted from this machine — the bootstrap skill is now the sole source of truth)
- **Last reviewed:** 2026-07-06
- **Used for:**
  - Initial bootstrap content: `SKILL.md`, all `references/`, `scripts/krita_source_probe.py`, `eval-queries.json`
- **Aspects extracted:**
  - Routing model, invariants, gotchas, reference bundle, and source probe script as reviewed in-repo
