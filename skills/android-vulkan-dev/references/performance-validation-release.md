# Vulkan performance, validation, and release

## Use this file when

Use this reference for validation layers, debug callbacks, Android Vulkan Profiles, GPU profiling, optimization, and release checks on Android.

For generic Vulkan performance triage and anti-patterns, use [vulkan-dev](../../vulkan-dev/SKILL.md) [best-practices.md](../../vulkan-dev/references/best-practices.md).

## Validation layers

Use `VK_LAYER_KHRONOS_validation` in debug/dev builds to catch API misuse. Do not enable validation in production release builds.

Rules:

- Check that the validation layer is available before enabling it.
- Use `VK_EXT_debug_utils` when available for debug messenger callbacks.
- Package validation layers for compatibility when needed, or use external validation layers on supported test devices.
- Treat validation warnings as bugs unless documented with device/vendor context.

## Android Vulkan Profiles (AVP)

Use [Android Vulkan Profiles](https://developer.android.com/ndk/guides/graphics/android-vulkan-profile) to choose a reliable feature baseline. Even when choosing a profile, still verify required features and extensions at runtime.

| Profile | Typical use |
| --- | --- |
| AVP 2021 | Baseline mobile features; broadest device coverage |
| AVP 2022 | Adds commonly available extensions and features for richer rendering |
| AVP 2025 | Newer feature set for apps targeting recent Android devices |

Product guidance:

- Choose the lowest profile that supports the product's required visual and performance features.
- Log missing features in diagnostics.
- Provide fallback for optional enhancements such as wide color, HDR, advanced formats, or newer synchronization features.

## Performance priorities on mobile GPUs

- Minimize render passes and external memory bandwidth.
- Apply display rotation during rendering instead of relying on compositor rotation when needed.
- Avoid software-emulated Vulkan for performance-critical paths.
- Avoid per-frame pipeline creation, descriptor pool rebuilds, shader compilation, and large allocations.
- Use staging uploads and persistent/ring buffers instead of many small allocations.
- Batch draws and brush segments.
- Prefer lower-resolution preview plus full-resolution export for photo tools.
- Keep GPU/CPU synchronization minimal; avoid waiting on GPU from UI thread.

## Profiling checklist

- Measure frame time and missed frames with Perfetto.
- Track CPU time spent building command buffers and waiting on fences.
- Track GPU workload if vendor tools are available.
- Check memory bandwidth and texture sizes for large images.
- Compare copy-based and zero-copy paths with real camera/media inputs.
- Test thermal behavior for sustained camera preview effects.

## Release checks

- Validation disabled in release.
- Debug logs and GPU markers controlled by build flags.
- Native symbols archived/uploaded for crash symbolication.
- Unsupported-device fallback or error path tested.
- Surface lifecycle, pause/resume, resize, rotation, and device-lost paths tested.
- Shaders compiled/packaged correctly and missing-shader errors are handled.
- No `vkDeviceWaitIdle` in steady-state frame loop.
- No per-frame heap allocation spikes in hot paths.
- App Bundle includes only required native ABIs and shader assets.
- 16 KB page-size compliance for native renderer `.so` files (see [android-ndk-dev](../../android-ndk-dev/SKILL.md)).

## Common production failures

- Works on one GPU vendor only because format/extension assumptions were not checked.
- Stutter from pipeline creation or shader loading during interaction.
- Black frame after resize because old swapchain resources were used.
- Crash on background/foreground due to rendering after surface destruction.
- Memory leak from deferred deletion queue not drained.
- GPU hang from missing synchronization or invalid resource lifetime.
