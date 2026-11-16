---
name: android-vulkan-dev
description: vulkan-through-ndk gpu rendering guidance for android 16/api 36+ apps. use when designing, implementing, reviewing, or troubleshooting android vulkan renderers, native surfaces, swapchains, devices, queues, command buffers, render passes, dynamic rendering, shaders, spir-v, descriptor sets, synchronization, validation layers, android vulkan profiles, wide color, camera/media interop, painting engines, image filters, and gpu performance. use android-ndk-dev for cmake/jni/native-library integration and android-dev for kotlin app architecture, compose ui, permissions, and sdk camera/media flows.
---

# Android Vulkan Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Use this skill for **GPU rendering on Android using Vulkan through the NDK**. Generic Vulkan 1.3 API calls (`Vk*`, `vkCmd*`, synchronization2, dynamic rendering, descriptors, pipelines) live in [vulkan-dev](../vulkan-dev/SKILL.md); API-agnostic renderer architecture (render graph, frames-in-flight, memory strategy) lives in [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md). This skill owns **Android surface lifecycle, WSI, AHB interop, Android Vulkan Profiles, wide color, and the Kotlin/NDK bridge**.

Assume Android 16/API 36+ targets, but always query Vulkan capability and extensions at runtime — never assume a feature.

## Scope

Covered here: Android Vulkan renderers (`Surface` → `ANativeWindow`, swapchain, lifecycle, resize, pause/resume), WSI/AVP selection, AHB interop, wide color/HDR swapchain formats, camera/media/painting engines through Vulkan, and Android-specific validation and GPU tuning. Delegate everything else per the Reference routing table.

## When Vulkan is appropriate

Use Vulkan when the product needs at least one of: real-time camera preview filters or video effects; high-performance painting/compositing/blend modes/layers/brush engines; large GPU image processing; wide-gamut/HDR paths; cross-platform renderer reuse; or precise frame pacing/explicit GPU resource control. For simple static UI, image display, or playback controls, Compose/Canvas/Media3 are simpler and safer.

## Renderer workflow

1. Define the rendering contract: inputs (surfaces/buffers/textures), output surface, frame rate, color space, latency, fallback.
2. Build the Kotlin/NDK boundary with [android-ndk-dev](../android-ndk-dev/SKILL.md): pass `Surface`, `AssetManager`, size, lifecycle events, renderer commands; no per-draw JNI chatter.
3. Query support: Vulkan version, queue families, extensions, memory types, formats, color spaces, AVP target.
4. Create instance, debug messenger (debug builds), surface from `ANativeWindow`, device, queues, allocator, swapchain, then render resources with Vulkan 1.3 modern defaults — all per [vulkan-dev](../vulkan-dev/SKILL.md).
5. Handle Android lifecycle: surface create/destroy, resize, pause/resume, device lost, swapchain out-of-date, backgrounding, shutdown.
6. Validate, profile, and tune on real devices across vendors.

## Kotlin/Surface boundary shape

Keep the app layer in Kotlin, the renderer in C++, and the call pattern coarse: attach/resize/renderFrame/close around an opaque `Long` handle — no per-draw JNI beyond `renderFrame`.

```kotlin
class VulkanRendererHost : Closeable {
    fun attach(surface: Surface, assets: AssetManager)  // nativeCreate -> opaque Long handle
    fun resize(width: Int, height: Int)                 // nativeResize(handle, w, h)
    fun renderFrame()                                   // nativeRenderFrame(handle) — sole per-frame JNI call
    override fun close()                                // clear handle, then nativeDestroy(handle)
}
```

The native side converts `Surface` to `ANativeWindow` and owns all Vulkan resources until explicit destruction.

## Essential rules

- Query capabilities, extensions, formats, and color spaces at runtime; design a clear fallback for unsupported devices.
- Recreate the swapchain on surface create/destroy/resize and on out-of-date/suboptimal presentation results.
- Apply display rotation during rendering using surface `currentTransform`/`preTransform` to avoid compositor rotation cost.
- Minimize render passes and bandwidth on tile-based mobile GPUs.
- Treat color space, format, transfer function, and alpha mode (wide color/HDR) as product requirements, not incidental details.

## Reference routing

- [setup-surface-device.md](references/setup-surface-device.md) — surface/ANativeWindow, extensions, device/swapchain, lifecycle
- [renderer-architecture-sync.md](references/renderer-architecture-sync.md) — resize/pause/rotation/device-lost, painting
- [shaders-pipelines-assets.md](references/shaders-pipelines-assets.md) — SPIR-V, glslc, shader packaging, descriptors, pipelines
- [camera-media-image-interop.md](references/camera-media-image-interop.md) — camera/media/AHB interop, painting/photo pipelines
- [performance-validation-release.md](references/performance-validation-release.md) — validation, AVP, profiling, release checks
- [source-map.md](references/source-map.md) — source links
- [vulkan-dev](../vulkan-dev/SKILL.md) — generic Vulkan 1.3 API
- [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md) — renderer architecture
- [android-ndk-dev](../android-ndk-dev/SKILL.md) — JNI/CMake/native libs
- [android-dev](../android-dev/SKILL.md) — Kotlin app layer
- [cpp-coding](../cpp-coding/SKILL.md) — C++ host code style
