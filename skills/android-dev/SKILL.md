---
name: android-dev
description: Kotlin-only Android SDK app guidance for Android 16/API 36+. Use for Jetpack Compose UI, app architecture, CameraX/Media3, Photo Picker/storage, painting/photo features, permissions, lifecycle coroutines (viewModelScope, StateFlow), testing, performance, and App Bundle release. Excludes C++/JNI (android-ndk-dev), Vulkan renderers (android-vulkan-dev), and AGP builds (gradle-android-dev).
---

# Android Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`; resolve `references/` paths from it. App-layer entrypoint for Kotlin Android development — teach junior developers the decision process and safe defaults before final code. Assume `compileSdk`/`targetSdk` are Android 16 / API 36+ unless the user says otherwise; do not interpret "Android 16+" as minSdk 16 (modern Compose/Media/Vulkan guidance needs major fallback work there).

## Scope and routing

Kotlin only for app code — no Java classes; XML only for manifest, resources, legacy interop, and build metadata. Covers app architecture, Compose UI, camera/media, painting/photo flows, permissions, accessibility, app-layer performance/memory/lifecycle, and release quality. Everything else routes to sibling skills per the Reference routing table at the end.

## Workflow and architecture

1. Check project state first (wrapper, modules, `./gradlew assembleDebug`); build/sync issues → [gradle-android-dev](../gradle-android-dev/SKILL.md).
2. Pick the simplest correct API: Compose for UI, CameraX for capture/preview, Media3 for playback, Photo Picker for user-selected media, MediaStore for owned/shared media, WorkManager for deferrable work, NDK/Vulkan only for measured performance or GPU needs.
3. Design the data flow before writing code: UI event -> ViewModel -> use case/repository -> data source/native bridge -> immutable UI state.

Module boundaries, the dependency rule (domain has no Android framework dependency), DI, errors, permissions, and testing are in [architecture-and-quality.md](references/architecture-and-quality.md).

## Kotlin and coroutine rules

Apply [kotlin-coding](../kotlin-coding/SKILL.md) for language/stdlib correctness. Android-specific additions:

- Make suspend functions main-safe: the function performing blocking work switches to `Dispatchers.IO` or `Dispatchers.Default` internally.
- Use `viewModelScope` and structured concurrency. Never `GlobalScope`.
- Represent screen state as an immutable data class or sealed interface; expose `StateFlow` and collect it with lifecycle awareness.
- Use explicit error models for user-visible failures; do not swallow exceptions or expose raw stack traces to UI.
- Avoid `!!`, mutable global state, long-lived references to `Activity`, and uncancelled callbacks.

## Compose UI rules

Use Compose as the default UI toolkit; read [ui-camera-media.md](references/ui-camera-media.md) before any screen with camera preview, media playback, painting canvases, or heavyweight images.

- Use `AndroidView` for SDK views such as camera preview or platform media surfaces when Compose wrappers are not enough.
- Treat edge-to-edge (system-enforced starting at `targetSdk 35`, with `windowOptOutEdgeToEdgeEnforcement` opt-out removed at API 36) and predictive back (default system back animations enabled at `targetSdk 36`; migrate legacy `onBackPressed` / key interception to `OnBackInvokedCallback` or Compose `BackHandler` / `PredictiveBackHandler`) as release requirements — verify per the Android 16 checks below.

## Camera, media, painting, and photography defaults

- Camera: CameraX first; Camera2 only for manual sensor controls or custom stream combinations. Backpressure in analysis, close every `ImageProxy`, YUV off main.
- Media: Photo Picker for user-selected media (broad storage permissions only when picker/MediaStore cannot meet a real product need); Media3 for playback; custom pipelines drop to MediaCodec/MediaMuxer or NDK.
- Painting/images: Compose Canvas and Kotlin CPU filters for simple drawing and small images; tiled bitmaps, NDK C++, or Vulkan compute for large canvases, high-frequency brushes, filters, or real-time preview.

## Android 16/API 36 checks

These platform behavior changes break apps that still compile cleanly — verify each on an emulator/device before release, not just with compile checks.

- **Edge-to-edge enforcement (API 35+, opt-out removed at API 36).** System-enforced starting at `targetSdk 35`, and `windowOptOutEdgeToEdgeEnforcement` is removed at API 36. Call `enableEdgeToEdge()` in `Activity.onCreate()` and handle insets explicitly (`WindowInsets.safeDrawing`, scaffold `innerPadding`) — system bars overlay content by default. Details and code: [ui-camera-media.md](references/ui-camera-media.md).
- **Predictive back by default (`targetSdk 36`).** Default system back animations are enabled at `targetSdk 36`; legacy `onBackPressed()` and `KEYCODE_BACK` interception are not dispatched. Migrate custom back handling to `OnBackInvokedCallback` or Compose `BackHandler` / `PredictiveBackHandler` (and Navigation Compose back stacks), and test back from camera preview, modal sheets, and export flows.
- **JobScheduler/WorkManager quota behavior changed.** Do not assume pre-16 scheduling rates — test deferrable and expedited work under quota limits, including restricted standby buckets.
- **Foreground-service and notification rules.** Every foreground service needs a declared type (e.g. `camera`, `mediaPlayback`) with its required permission and a posted notification; FGS launches from the background are restricted, and runtime `POST_NOTIFICATIONS` denial must not break the feature.
- Also verify: large-screen/adaptive layouts, camera/media permission flows (denied, one-time, settings-disabled), and picker flows after process death.

Track upstream changes via the Android 16 behavior-changes links in [source-map.md](references/source-map.md); the full release checklist is in [performance-release-checklist.md](references/performance-release-checklist.md).

## Performance and release gates

Read [performance-release-checklist.md](references/performance-release-checklist.md) before finalizing code or reviewing a PR; App Bundle, R8, and signing validation → [gradle-android-dev](../gradle-android-dev/SKILL.md). Non-negotiable gates: `./gradlew assembleDebug` and `./gradlew lint test` pass; no disk/network/decode/bitmap work on the main thread; camera/media/native/Vulkan resources are lifecycle-bound and released; release builds are App Bundles with R8 shrinking and no debug logging.

## Reference routing

| Task | Read |
|------|------|
| Modules, ViewModel/use case/repository, DI, errors, permissions, testing | [architecture-and-quality.md](references/architecture-and-quality.md) |
| Compose, CameraX, Media3, Photo Picker, painting, photography, edge-to-edge | [ui-camera-media.md](references/ui-camera-media.md) |
| Speed, memory, power, jank, startup, profiling, release gates | [performance-release-checklist.md](references/performance-release-checklist.md) |
| Source links and update notes | [source-map.md](references/source-map.md) |
| Kotlin language/stdlib/API design | [kotlin-coding](../kotlin-coding/SKILL.md) |
| Kotlin test design and frameworks | [kotlin-coding](../kotlin-coding/SKILL.md) |
| AGP, variants, lint, R8, signing | [gradle-android-dev](../gradle-android-dev/SKILL.md) |
| JNI, CMake, native libraries | [android-ndk-dev](../android-ndk-dev/SKILL.md) |
| Vulkan renderer on Android | [android-vulkan-dev](../android-vulkan-dev/SKILL.md) |
