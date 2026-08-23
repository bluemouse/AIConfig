# Performance, memory, and release checklist

## Use this file when

Use this reference before finalizing a feature, reviewing a PR, profiling camera/media/painting/image code, or preparing a release.

## Performance budget

Define budgets before optimizing:

- Startup: cold/warm startup should be measured with Macrobenchmark where release quality matters.
- Frame time: aim for steady 60 fps or device refresh rate; avoid long main-thread work and allocation spikes.
- Camera preview: analyzer must not block preview; drop or coalesce frames when processing cannot keep up.
- Painting: input-to-display latency should stay within one or two frames for brush strokes.
- Export: run off main, show progress, support cancellation, and avoid keeping multiple full-resolution copies.
- Memory: budget by resolution, layer count, tile size, undo stack, and cache size.

## Measure first

Use tools appropriate to the bottleneck:

- Android Studio profiler for CPU, memory, allocations, and network.
- Perfetto/System Trace for jank, scheduling, camera/media pipeline, and long frames.
- Macrobenchmark for startup and scroll/frame performance.
- Baseline profiles for startup and hot paths.
- LeakCanary or memory profiler for lifecycle leaks.
- Android vitals/crash/ANR dashboards after release.
- For native code, use `android-ndk-dev` profiling guidance.
- For Vulkan, use `android-vulkan-dev` validation/profiling guidance.

## Main-thread checklist

No main-thread work for:

- Bitmap decode/resize/compress.
- EXIF parsing for large files.
- Camera image analysis.
- Media metadata scanning of many files.
- Database migrations or large queries.
- Network and disk IO.
- Native CPU filters or JNI calls that can block.
- Vulkan pipeline creation or shader compilation during interactive frames.

## Memory checklist for image apps

- Decode to display/export target size, not always source size.
- Keep full-resolution source, preview bitmap, layer tiles, and export buffers separate and bounded.
- Avoid storing large bitmaps in `SavedStateHandle`, navigation args, or Compose state.
- Use URI/document IDs in state; load pixels in repositories/workers.
- Recycle or release native buffers where applicable; in Kotlin rely on ownership and clear references promptly.
- Use caches with explicit max sizes.
- Account for YUV, RGBA, HDR, 10-bit, and wide-gamut buffer sizes.
- Keep undo/redo bounded by commands or tiles, not complete full-image copies per operation.

## Gradle and build quality

Run these checks before release. For AGP DSL, R8 rules, signing, variant selection, and App Bundle configuration, use [gradle-android-dev](../../gradle-android-dev/SKILL.md).

```bash
./gradlew clean assembleDebug
./gradlew lint test
./gradlew connectedCheck        # when instrumentation tests exist and devices are available
./gradlew bundleRelease         # release path for Play distribution
```

App-layer release expectations:

- Release builds are non-debuggable and free of debug logging.
- Native ABIs match tested devices; native symbols are handled when NDK is present (see [android-ndk-dev](../../android-ndk-dev/SKILL.md)).
- Generated APKs from the bundle are smoke-tested via bundletool or Play internal testing.

## Android 16/API 36 release checks

- Edge-to-edge is handled; no reliance on opt-out behavior.
- Predictive back uses supported APIs and is tested for navigation flows.
- Large-screen and foldable layouts do not lock orientation unnecessarily.
- WorkManager/JobScheduler behavior is tested under quota changes.
- Camera, media, and foreground-service declarations are correct.
- Runtime permissions include denied, one-time, and settings-disabled paths.
- Photo/media picker flows are tested after process death.

## PR review template

Ask the developer to answer:

1. What is the feature's main performance risk?
2. Which thread performs IO, decode, native, or GPU work?
3. Which lifecycle owns camera/media/native/GPU resources?
4. What is the memory budget for the largest image/video/layer set?
5. What happens when permission is denied or the device lacks a capability?
6. Which automated tests and manual device tests were run?
7. Did the release bundle include only required resources and ABIs?
