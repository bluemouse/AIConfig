---
name: android-dev
description: kotlin-only native android app development guidance for android 16/api 36+ apps. use when designing, implementing, reviewing, or troubleshooting android sdk app code, jetpack compose ui, app architecture, camera and media flows, painting/image/photo app features, permissions, testing, app bundle release, performance, memory, accessibility, and quality. prefer this skill for app-layer kotlin, compose, camerax/media3, lifecycle, coroutines, storage, and release decisions. delegate c++/jni/library integration to android-ndk-dev and vulkan renderer details to android-vulkan-dev.
---

# Android Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Use this skill as the app-layer entrypoint for Kotlin Android development. Teach junior developers by showing the decision process, safe defaults, and small Kotlin examples before giving final code.

Assume `compileSdk` and `targetSdk` are Android 16 / API 36 or newer unless the user gives a different modern target. Do not interpret "Android 16+" as minimum API 16. If the user requests `minSdk 16`, warn that modern Compose, Media, and Vulkan guidance will not apply without major fallback work.

## When to Use

- Designing or implementing Kotlin Android app architecture, Jetpack Compose UI, ViewModels, repositories, and use cases
- CameraX/Camera2, Media3, Photo Picker, MediaStore, painting/photo editing flows, permissions, and accessibility
- App-layer performance, memory budgets, lifecycle safety, and release quality gates for Android 16/API 36+
- Reviewing Kotlin Android diffs for architecture, Compose, camera/media, or release readiness

## When NOT to Use

- Plain Kotlin language/stdlib/API design without Android framework — [kotlin-coding](../kotlin-coding/SKILL.md)
- Kotlin test design, Kotest/MockK, coroutine tests, or flaky-test triage — [kotlin-testing](../kotlin-testing/SKILL.md)
- Android Gradle Plugin, `android {}` DSL, variants, lint, R8, signing, or sync failures — [gradle-android-dev](../gradle-android-dev/SKILL.md)
- C++, CMake, JNI, native libraries, native memory, or NDK debugging — [android-ndk-dev](../android-ndk-dev/SKILL.md)
- Vulkan instance/device/swapchain/shader/pipeline/synchronization on Android — [android-vulkan-dev](../android-vulkan-dev/SKILL.md)

## Scope boundaries

- Use Kotlin only for app code. Do not generate Java classes. XML is allowed only for manifest, resources, legacy interop, and build metadata.
- Use this skill for architecture, Compose UI, camera/media SDK usage, app permissions, testing, accessibility, memory/performance, and release quality.
- Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for AGP build files, SDK levels, variants, lint/R8 task wiring, and signing — not duplicated here.
- Use [android-ndk-dev](../android-ndk-dev/SKILL.md) when the task needs C++ code, JNI, native libraries, native memory management, or NDK build/debugging.
- Use [android-vulkan-dev](../android-vulkan-dev/SKILL.md) when the task needs Vulkan instance/device/swapchain/render-pass/pipeline/shader/synchronization logic or GPU image processing through the NDK.

## Development workflow

1. Classify the feature: UI, camera/media, storage, data, background work, native bridge, or Vulkan renderer.
2. Check project state before adding logic: Gradle wrapper exists, `settings.gradle.kts` includes modules, AndroidX is enabled, the app builds with `./gradlew assembleDebug`, and lint/test tasks are known. For build/sync issues, use [gradle-android-dev](../gradle-android-dev/SKILL.md).
3. Pick the simplest correct API: Compose for UI, CameraX for standard camera capture/preview, Media3 for playback, Android Photo Picker for user-selected media, MediaStore for owned/shared media, WorkManager for deferrable work, NDK/Vulkan only for measured performance or GPU needs.
4. Design the data flow before writing code: UI event -> ViewModel -> use case/repository -> data source/native bridge -> result -> immutable UI state.
5. Add performance and lifecycle constraints early: no blocking work on main, no unbounded image allocations, no leaked lifecycle observers, no native handles without explicit close/release.
6. Finish with build, lint, unit tests, instrumentation tests where useful, and a release checklist.

## Default architecture

Prefer a modular, testable architecture:

```text
app/                 application entry, DI, navigation shell
feature/<name>/      screens, ViewModels, feature-specific use cases
core/ui/             theme, design system, reusable Compose widgets
core/domain/         pure Kotlin domain models and repository interfaces
core/data/           repository implementations, Room, network, MediaStore
core/nativebridge/   optional Kotlin wrappers over NDK libraries
```

Dependency rule: UI depends inward on domain abstractions; domain never depends on Android framework, data, UI, NDK, or Vulkan implementation details. Put camera/media framework types at the edge and map to app models before crossing module boundaries.

For complete architecture, data, error, DI, coroutine, and testing guidance, read [architecture-and-quality.md](references/architecture-and-quality.md).

## Kotlin and coroutine rules

Apply [kotlin-coding](../kotlin-coding/SKILL.md) for language/stdlib correctness. Android-specific additions:

- Make suspend functions main-safe: the function that performs blocking work switches to `Dispatchers.IO` or `Dispatchers.Default` internally.
- Use `viewModelScope` and structured concurrency. Do not use `GlobalScope`.
- Represent screen state as an immutable data class or sealed interface. Expose `StateFlow` from ViewModel and collect it with lifecycle awareness in Compose.
- Use explicit error models for user-visible failures; do not swallow exceptions or expose raw stack traces to UI.
- Avoid `!!`, mutable global state, long-lived references to `Activity`, and uncancelled callbacks.

```kotlin
data class EditorUiState(
    val isLoading: Boolean = false,
    val image: ImageBitmap? = null,
    val errorMessage: String? = null
)

class EditorViewModel(
    private val loadPhoto: LoadPhotoUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow(EditorUiState())
    val uiState: StateFlow<EditorUiState> = _uiState.asStateFlow()

    fun open(uri: Uri) = viewModelScope.launch {
        _uiState.update { it.copy(isLoading = true, errorMessage = null) }
        runCatching { loadPhoto(uri) }
            .onSuccess { bitmap -> _uiState.update { it.copy(isLoading = false, image = bitmap) } }
            .onFailure { error ->
                _uiState.update {
                    it.copy(isLoading = false, errorMessage = error.toUserMessage())
                }
            }
    }
}

private fun Throwable.toUserMessage(): String = when (this) {
    is SecurityException -> "Permission denied"
    else -> message ?: "Something went wrong"
}
```

## Compose UI rules

Use Compose as the default UI toolkit. Read [ui-camera-media.md](references/ui-camera-media.md) before implementing screens with camera preview, media playback, painting canvases, image editing, or heavyweight images.

- Hoist state. Keep Composables mostly stateless and previewable.
- Use `remember` only for UI-local state. Use `rememberSaveable` for state that should survive configuration changes.
- Use `derivedStateOf` for derived values that are expensive or frequently invalidated.
- Use `LaunchedEffect`, `DisposableEffect`, and `rememberUpdatedState` for lifecycle-bound side effects; always clean up callbacks, players, sensors, and preview sessions.
- Use keys for lazy lists and stable model types for large feeds or media grids.
- Use `AndroidView` for SDK views such as camera preview or platform media surfaces when Compose wrappers are not enough.
- Support edge-to-edge layouts, predictive back, adaptive screen sizes, dark theme, dynamic type, and accessibility labels.

## Camera, media, painting, and photography defaults

- Camera preview/capture: start with CameraX. Use Camera2 only when the feature requires manual sensor controls, custom stream combinations, low-level timing, or device-specific capability queries.
- Image analysis: use backpressure, close every `ImageProxy`, keep YUV processing off main, and avoid conversion to large RGBA bitmaps unless required.
- Photo picking: prefer Android Photo Picker for user-selected media. Request broad storage permissions only when a real product requirement cannot be met by picker/MediaStore.
- Media playback: use Media3 for playback. Use lower-level MediaCodec/MediaMuxer or NDK APIs only for custom decode/encode pipelines.
- Painting: use Compose Canvas for simple drawing; use tiled bitmaps or a native/Vulkan renderer for large canvases, high-frequency brushes, filters, or non-destructive layer compositing.
- Image processing: CPU filters can live in Kotlin for small images, NDK C++ for heavy scalar/SIMD work, and Vulkan compute/render passes for real-time preview or large images.

## Android 16/API 36 checks

When targeting Android 16/API 36+, review platform behavior changes before release. At minimum verify edge-to-edge behavior (no `windowOptOutEdgeToEdgeEnforcement`), predictive back (`OnBackInvokedCallback` / Navigation Compose back stack), large-screen/adaptive behavior, JobScheduler/WorkManager quota behavior, camera/media permission flows, foreground-service declarations, and notification behavior.

## Performance and release gates

Read [performance-release-checklist.md](references/performance-release-checklist.md) before finalizing code or reviewing a PR. Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for App Bundle, R8, signing, and AGP release validation.

Minimum gates:

- `./gradlew assembleDebug` succeeds before feature work is considered complete.
- `./gradlew lint test` runs cleanly or has documented, justified suppressions.
- No disk, network, camera decode, bitmap conversion, or image processing blocks the main thread.
- Large images are decoded to target size, reused or pooled where safe, and released promptly.
- Camera/media/native/Vulkan resources are lifecycle-bound and released in `onCleared`, `DisposableEffect`, `onStop`, or explicit `close` paths.
- Release builds use App Bundles, R8/resource shrinking, signed configs, no debug logging, no bundled unused ABIs, and documented native symbol handling when NDK is present.

## Reference routing

| Task | Read |
|------|------|
| Modules, ViewModel/use case/repository, DI, errors, permissions, testing | [architecture-and-quality.md](references/architecture-and-quality.md) |
| Compose, CameraX, Media3, Photo Picker, painting, photography, edge-to-edge | [ui-camera-media.md](references/ui-camera-media.md) |
| Speed, memory, power, jank, startup, profiling, release gates | [performance-release-checklist.md](references/performance-release-checklist.md) |
| Source links and update notes | [source-map.md](references/source-map.md) |
| Kotlin language/stdlib/API design | [kotlin-coding](../kotlin-coding/SKILL.md) |
| Kotlin test design and frameworks | [kotlin-testing](../kotlin-testing/SKILL.md) |
| AGP, variants, lint, R8, signing | [gradle-android-dev](../gradle-android-dev/SKILL.md) |
| JNI, CMake, native libraries | [android-ndk-dev](../android-ndk-dev/SKILL.md) |
| Vulkan renderer on Android | [android-vulkan-dev](../android-vulkan-dev/SKILL.md) |

## Companion skills

- Use [kotlin-coding](../kotlin-coding/SKILL.md) for plain Kotlin language, stdlib, and coroutine semantics.
- Use [kotlin-testing](../kotlin-testing/SKILL.md) for test design, mocks, and flaky-test triage.
- Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for Android Gradle Plugin and build engineering.
- Use [android-ndk-dev](../android-ndk-dev/SKILL.md) for C++/JNI/native-library integration.
- Use [android-vulkan-dev](../android-vulkan-dev/SKILL.md) for Vulkan GPU rendering through the NDK.

## References

- [architecture-and-quality.md](references/architecture-and-quality.md): modules, ViewModel/use case/repository, DI, errors, permissions, testing, junior review checklist.
- [ui-camera-media.md](references/ui-camera-media.md): Compose, CameraX, Media3, Photo Picker, painting, photography, edge-to-edge, predictive back, and image-processing app patterns.
- [performance-release-checklist.md](references/performance-release-checklist.md): speed, memory, power, jank, startup, profiling, release, and app bundle checks.
- [source-map.md](references/source-map.md): source links and update notes used to build this skill.
