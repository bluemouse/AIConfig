# Sources

## OpenUSD (primary)

- **Repository:** https://github.com/PixarAnimationStudios/OpenUSD
- **Local checkout reviewed:** `/home/andy/DevHome/externals/OpenUSD` (`dev` branch)
- **Last reviewed:** 2026-07-07
- **Used for:**
  - All Hydra 2.0 scene-index contracts, datasource/schema APIs, dirtying semantics, plugin surfaces, USD imaging chain entry points, and Storm transparency/material-tag behavior cited in this skill
- **Key headers inspected:**
  - `pxr/imaging/hd/sceneIndex.h`, `sceneIndexObserver.h`, `filteringSceneIndex.h`, `retainedSceneIndex.h`
  - `pxr/imaging/hd/dataSource.h`, `dataSourceLocator.h`, `containerDataSourceEditor.h`, `retainedDataSource.h`, `overlayContainerDataSource.h`
  - `pxr/imaging/hd/dependencyForwardingSceneIndex.h`, `dependencySchema.h`
  - `pxr/imaging/hd/*Schema.h`, `tokens.h`
  - `pxr/imaging/hd/sceneIndexPlugin.h`, `sceneIndexPluginRegistry.h`, `renderer.h`, `rendererPlugin.h`
  - `pxr/imaging/hd/materialSchema.h`, `materialBindingsSchema.h`, `instancerTopologySchema.h`
  - `pxr/imaging/hdSt/primUtils.cpp`, `materialNetwork.cpp`
  - `pxr/usdImaging/usdImaging/stageSceneIndex.h`, `sceneIndices.h`
  - `pxr/imaging/hdx/taskControllerSceneIndex.h`
- **Aspects extracted:**
  - Scene-index existence/traversal invariants and observer notice semantics → `references/hydra2-core.md`
  - Retained and dependency-forwarding scene indices → `references/hydra2-core.md`, `references/examples.md`
  - Schema token layouts, material universal render context (`""`), instancing topology → `references/schemas-and-authoring.md`
  - Plugin `plugInfo.json`, `_AppendSceneIndex`, registry registration → `references/rendering-plugins-and-usd-ecosystem.md`
  - Storm `displayOpacity` masked path and material opacity/threshold tags → `references/transparency-materials.md`
  - Full source map and anti-hallucination traps → `references/source-verification.md`

## Official OpenUSD API docs

- **URLs:**
  - https://openusd.org/dev/api/_page__hydra__getting__started__guide.html
  - https://openusd.org/dev/api/hd_page_front.html
  - https://openusd.org/dev/api/hdx_page_front.html
  - https://openusd.org/dev/api/sdf_page_front.html
  - https://openusd.org/dev/api/tf_page_front.html
  - https://openusd.org/dev/api/vt_page_front.html
  - https://openusd.org/dev/api/plug_page_front.html
- **Last reviewed:** 2026-07-07
- **Used for:**
  - Hydra getting-started framing, module boundaries, and doc cross-links in `references/source-verification.md`

## Refresh workflow

1. Re-read the OpenUSD branch or release the user targets (default: `dev`).
2. Diff changed headers under `pxr/imaging/hd/`, `pxr/imaging/hdSt/`, `pxr/usdImaging/`, and `pxr/imaging/hdx/` against the prior review.
3. Update the matching `references/<topic>.md` and any examples whose `BuildRetained` signatures or token names changed.
4. Re-run `scripts/hydra2_lint.py` on `references/examples.md`.
5. Update the "Last reviewed" date and branch note in this file.
