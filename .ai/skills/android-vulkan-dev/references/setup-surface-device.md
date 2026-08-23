# Setup, surface, device, and swapchain

## Use this file when

Use this reference when creating a Vulkan renderer on Android, wiring a Kotlin `Surface` to C++, creating the instance/device/swapchain, or handling lifecycle events.

For generic Vulkan 1.3 instance/device/queue/memory setup, use [vulkan-dev](../../vulkan-dev/SKILL.md) references starting at [capabilities-and-setup.md](../../vulkan-dev/references/capabilities-and-setup.md).

## Minimum support stance

Although this skill assumes Android 16/API 36+ as the app target, still query Vulkan support on the device. Vulkan originally requires Android 7.0/API 24+ plus supporting hardware, but target API is not the same as GPU capability.

## CMake linking sketch

Use [android-ndk-dev](../../android-ndk-dev/SKILL.md) for full CMake/JNI setup. Vulkan renderer targets commonly link Android, log, and Vulkan libraries.

```cmake
add_library(vulkan_renderer SHARED
    native_vulkan_api.cpp
    renderer.cpp
    swapchain.cpp
)

find_library(android-lib android)
find_library(log-lib log)
find_library(vulkan-lib vulkan)

target_link_libraries(vulkan_renderer PRIVATE
    ${android-lib}
    ${log-lib}
    ${vulkan-lib}
)
```

## Surface ownership

Kotlin owns the `Surface` lifecycle. Native owns the `ANativeWindow` reference it acquires and must release it.

```cpp
ANativeWindow* window = ANativeWindow_fromSurface(env, surface);
if (!window) {
    // return error or throw
}
// Store while renderer is attached.
// On destroy: ANativeWindow_release(window);
```

Rules:

- Do not render after surface destruction.
- Recreate or resize swapchain when surface size/format changes.
- Handle pause/resume. Stop frame production when not visible unless rendering is explicitly needed.
- Make shutdown wait for in-flight work or defer deletion safely.

## Required instance extensions

At minimum, Android surface presentation uses:

- `VK_KHR_surface`
- `VK_KHR_android_surface`

For debug builds, enable validation-related extensions when available, such as `VK_EXT_debug_utils`.

Always enumerate and check before enabling.

## Required device extensions

Swapchain presentation requires:

- `VK_KHR_swapchain`

Hardware-buffer interop (camera preview zero-copy paths) may require:

- `VK_ANDROID_external_memory_android_hardware_buffer`
- `VK_KHR_external_memory` and related semaphore/fence extensions when sharing with media producers

Query and enable only what the product path uses. See [camera-media-image-interop.md](camera-media-image-interop.md).

## Device selection

Check:

- Vulkan API version.
- Hardware device type. Performance-critical apps should avoid CPU/software Vulkan implementations.
- Queue families for graphics, compute, transfer, and present support.
- Required device extensions, especially swapchain support.
- Surface formats, present modes, capabilities, transforms, and min/max image counts.
- Memory properties and limits.
- Required features for the renderer or selected Android Vulkan Profile.

Prefer a clear unsupported-device error or a simpler fallback over enabling a path that half works.

## Swapchain defaults

- Present mode: `VK_PRESENT_MODE_FIFO_KHR` is required by Vulkan and is the safest baseline.
- Image count: use at least min image count plus one when allowed to reduce blocking.
- Format: choose sRGB or wide-gamut format based on product color requirements and supported formats.
- Transform: apply `currentTransform` during rendering and set `preTransform` appropriately.
- Usage: include color attachment, transfer, storage, or sampled bits only when actually needed.
- Sharing mode: exclusive unless queues require sharing.

For acquire/present flow, frames-in-flight, and `OUT_OF_DATE` handling, see [commands-and-swapchain.md](../../vulkan-dev/references/commands-and-swapchain.md) in [vulkan-dev](../../vulkan-dev/SKILL.md).

## Lifecycle events

Handle these explicitly:

- Surface created: create `ANativeWindow`, Vulkan surface, swapchain, render targets (dynamic rendering) or framebuffers (classic path).
- Surface changed/resized: drain or fence in-flight work, recreate swapchain-dependent resources.
- Surface destroyed: stop render loop, release swapchain/surface/window resources.
- App paused: stop submitting frames and release optional transient resources.
- Device lost: destroy/recreate the renderer or report fatal unsupported state.

## Common setup bugs

- Forgetting to enable `VK_KHR_android_surface` or `VK_KHR_swapchain`.
- Creating swapchain before verifying present support.
- Ignoring surface transform and paying compositor rotation cost.
- Rendering after `Surface` is destroyed.
- Using `vkDeviceWaitIdle` every frame instead of correct synchronization.
- Assuming the same swapchain format/color space on every device.
