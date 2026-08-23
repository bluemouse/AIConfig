---
name: android-vulkan-dev
description: vulkan-through-ndk gpu rendering guidance for android 16/api 36+ apps. use when designing, implementing, reviewing, or troubleshooting android vulkan renderers, native surfaces, swapchains, devices, queues, command buffers, render passes, dynamic rendering, shaders, spir-v, descriptor sets, synchronization, validation layers, android vulkan profiles, wide color, camera/media interop, painting engines, image filters, and gpu performance. use android-ndk-dev for cmake/jni/native-library integration and android-dev for kotlin app architecture, compose ui, permissions, and sdk camera/media flows.
---

# Android Vulkan Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Use this skill for **GPU rendering on Android using Vulkan through the NDK**. Generic Vulkan 1.3 API calls (`Vk*`, `vkCmd*`, synchronization2, dynamic rendering, descriptors, pipelines) live in [vulkan-dev](../vulkan-dev/SKILL.md). API-agnostic renderer architecture (render graph, frames-in-flight model, memory strategy) lives in [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md). This skill owns **Android surface lifecycle, WSI, AHB interop, Android Vulkan Profiles, wide color, and the Kotlin/NDK bridge**.

Assume the app targets Android 16/API 36+ but still performs runtime Vulkan capability checks. Vulkan-capable devices and extension support vary; never assume a feature without querying it.

## When to Use

- Creating a Vulkan renderer on Android: `Surface` → `ANativeWindow`, swapchain, lifecycle, resize, pause/resume
- Android-specific extensions, AHardwareBuffer interop, wide color/HDR swapchain selection
- Camera/media preview filters, painting engines, and image processing through Vulkan on Android
- Android Vulkan Profiles (AVP), validation layers in debug, and mobile GPU performance tuning on Android

## When NOT to Use

- Generic `VkInstance`/`VkDevice`/barrier/descriptor/pipeline API details — [vulkan-dev](../vulkan-dev/SKILL.md)
- API-agnostic render-graph architecture and binding model — [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md)
- CMake, JNI, native library setup, native memory/threading — [android-ndk-dev](../android-ndk-dev/SKILL.md)
- Kotlin app architecture, Compose UI, CameraX/Media3, permissions — [android-dev](../android-dev/SKILL.md)
- General C++20 style — [cpp-coding](../cpp-coding/SKILL.md)

## Scope boundaries

- Own Android Vulkan surface/swapchain lifecycle, WSI extensions, AHB external memory, AVP selection, wide color, camera/media GPU interop, and Android-specific performance/validation.
- Use [android-ndk-dev](../android-ndk-dev/SKILL.md) for Gradle/CMake/JNI/native-library setup and native memory/threading fundamentals.
- Use [android-dev](../android-dev/SKILL.md) for app-layer Kotlin, Compose UI, CameraX/Media3, permissions, storage, ViewModels, and release architecture.
- Use [vulkan-dev](../vulkan-dev/SKILL.md) for Vulkan 1.3 implementation defaults (synchronization2, dynamic rendering, timeline semaphores, descriptor indexing).

## When Vulkan is appropriate

Use Vulkan when the product needs at least one of:

- Real-time camera preview filters or video effects.
- High-performance painting, compositing, blend modes, layers, masks, or brush engines.
- Large image processing with GPU compute/render passes.
- Wide-gamut/HDR-aware rendering paths.
- Cross-platform renderer reuse.
- Precise frame pacing or explicit GPU resource control.

Do not use Vulkan for simple static UI, basic image display, or standard playback controls. Compose/Canvas/Media3 are usually simpler and safer for those.

## Renderer workflow

1. Define the rendering contract: input surfaces/buffers/textures, output surface, frame rate, color space, latency, and fallback.
2. Build the Kotlin/NDK boundary with [android-ndk-dev](../android-ndk-dev/SKILL.md): pass `Surface`, `AssetManager`, size, lifecycle events, and renderer commands; avoid per-draw JNI chatter.
3. Query support: Vulkan version, queue families, required instance/device extensions, memory types, formats, color spaces, and Android Vulkan Profile target.
4. Create instance, debug messenger in debug builds, surface from `ANativeWindow`, physical/logical device, queues, allocator strategy, and swapchain. Follow [vulkan-dev](../vulkan-dev/SKILL.md) for device/memory/sync setup.
5. Build render resources using Vulkan 1.3 modern defaults from [vulkan-dev](../vulkan-dev/SKILL.md): dynamic rendering, synchronization2, frames-in-flight, descriptor layouts, pipelines, shader modules.
6. Handle Android lifecycle: surface create/destroy, resize, pause/resume, device lost, swapchain out-of-date, app backgrounding, and renderer shutdown.
7. Validate, profile, and tune on real devices across vendors.

## Kotlin/Surface boundary shape

Keep the app layer in Kotlin, the renderer in C++, and the call pattern coarse.

```kotlin
class VulkanRendererHost : Closeable {
    private var handle: Long = 0L

    fun attach(surface: Surface, assetManager: AssetManager) {
        close()  // release prior renderer if re-attaching
        val created = nativeCreate(surface, assetManager)
        require(created != 0L) { "Failed to create Vulkan renderer" }
        handle = created
    }

    fun resize(width: Int, height: Int) {
        if (handle != 0L) nativeResize(handle, width, height)
    }

    fun renderFrame() {
        if (handle != 0L) nativeRenderFrame(handle)
    }

    override fun close() {
        val h = handle
        handle = 0L
        if (h != 0L) nativeDestroy(h)
    }

    private external fun nativeCreate(surface: Surface, assets: AssetManager): Long
    private external fun nativeResize(handle: Long, width: Int, height: Int)
    private external fun nativeRenderFrame(handle: Long)
    private external fun nativeDestroy(handle: Long)

    companion object { init { System.loadLibrary("vulkan_renderer") } }
}
```

The native side should convert `Surface` to `ANativeWindow`, create a Vulkan surface, and own all Vulkan resources until explicit destruction.

## Essential rules

- Query capabilities and extensions at runtime. Design fallback or clear unsupported-device behavior.
- Use validation layers and debug utils in debug builds, never production release.
- Compile shaders to SPIR-V ahead of time when possible; avoid runtime shader compilation during interactive frames.
- Apply [vulkan-dev](../vulkan-dev/SKILL.md) modern defaults: synchronization2, dynamic rendering, timeline semaphores where available.
- Keep frames-in-flight bounded. Avoid CPU/GPU stalls from `vkDeviceWaitIdle` in normal frame paths.
- Recreate swapchain on surface changes and out-of-date/suboptimal presentation results.
- Apply display rotation during rendering using surface transform when needed to avoid compositor rotation cost.
- Minimize render passes and bandwidth on tile-based mobile GPUs.
- Treat color space, format, transfer function, and alpha mode as product requirements, not incidental details.
- Never destroy resources still in use by the GPU. Use fences, timeline semaphores, or deferred deletion queues.

## Reference routing

| Task | Read |
|------|------|
| Surface, ANativeWindow, extensions, device, swapchain, lifecycle | [setup-surface-device.md](references/setup-surface-device.md) |
| Android resize/pause/rotation/device-lost, painting architecture | [renderer-architecture-sync.md](references/renderer-architecture-sync.md) |
| SPIR-V, glslc, assets, descriptors, pipelines on Android | [shaders-pipelines-assets.md](references/shaders-pipelines-assets.md) |
| Camera/media/AHB interop, wide color, photo pipelines | [camera-media-image-interop.md](references/camera-media-image-interop.md) |
| Validation, AVP, profiling, release checks | [performance-validation-release.md](references/performance-validation-release.md) |
| Source links | [source-map.md](references/source-map.md) |
| Generic Vulkan 1.3 API | [vulkan-dev](../vulkan-dev/SKILL.md) |
| Renderer architecture | [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md) |
| JNI/CMake/native libs | [android-ndk-dev](../android-ndk-dev/SKILL.md) |
| Kotlin app layer | [android-dev](../android-dev/SKILL.md) |

## Companion skills

- Use [vulkan-dev](../vulkan-dev/SKILL.md) for concrete Vulkan 1.3 API implementation.
- Use [gpu-rendering-guide](../gpu-rendering-guide/SKILL.md) for API-agnostic renderer architecture.
- Use [android-ndk-dev](../android-ndk-dev/SKILL.md) for CMake/JNI/native-library integration.
- Use [android-dev](../android-dev/SKILL.md) for Kotlin app architecture, Compose, and SDK camera/media.
- Use [cpp-coding](../cpp-coding/SKILL.md) for C++ renderer host code style.

## References

- [setup-surface-device.md](references/setup-surface-device.md): Android surface, ANativeWindow, extensions, physical device selection, swapchain setup, lifecycle.
- [renderer-architecture-sync.md](references/renderer-architecture-sync.md): Android lifecycle, resize/device-lost, painting/photo renderer shape; defers generic sync to vulkan-dev.
- [shaders-pipelines-assets.md](references/shaders-pipelines-assets.md): SPIR-V, glslc, Android Studio shader packaging, descriptor sets, pipeline cache, assets.
- [camera-media-image-interop.md](references/camera-media-image-interop.md): Camera/media/hardware-buffer interop, image processing, painting/photo pipelines, wide color.
- [performance-validation-release.md](references/performance-validation-release.md): validation layers, Android Vulkan Profiles, profiling, optimization, release checks.
- [source-map.md](references/source-map.md): source links and update notes used to build this skill.
