# Camera, media, image interop, and wide color

## Use this file when

Use this reference for camera preview filters, media frame processing, hardware-buffer interop, painting/photo pipelines, and wide-gamut rendering.

## Cross-skill split

- `android-dev` owns CameraX/Media3/permissions/UI decisions.
- `android-ndk-dev` owns JNI, native buffer ownership, and native camera/media APIs.
- This skill owns Vulkan resource import, rendering, synchronization, color, and GPU processing.

## Frame interop principles

For any camera/media frame entering Vulkan, document:

- Source API and owner.
- Pixel format and plane layout.
- Color space, transfer, range, and HDR metadata.
- Orientation, crop, timestamp, and transform.
- Synchronization/fence ownership.
- Release path and whether the renderer may retain the resource.

Avoid CPU copies when latency matters, but do not choose zero-copy paths before the synchronization and format complexity are justified.

## Hardware buffers

When using Android hardware buffers or external memory paths:

- Check required Vulkan extensions and features at runtime.
- Verify usage flags support sampling, storage, color attachment, or transfer as needed.
- Import memory with correct external-memory structures.
- Handle external synchronization explicitly.
- Provide fallback for unsupported devices or formats.

Do not assume `AHardwareBuffer` interop only because the app targets Android 16. Query support.

## Camera preview filters

Recommended architecture:

```text
CameraX/Camera2 source -> native bridge/buffer queue -> Vulkan renderer -> Surface output
```

Rules:

- Keep the camera pipeline from blocking on slow GPU work. Drop frames if needed.
- Use newest-frame-wins for live preview unless every frame must be encoded.
- Separate preview resolution from capture/export resolution.
- Keep camera controls and permissions in Kotlin/app layer.
- Keep renderer operations on a render thread with explicit lifecycle.

## Media frame processing

For video effects:

- Preserve timestamps.
- Keep decode, render/filter, and encode queues bounded.
- Avoid unnecessary RGB round trips if YUV sampling path is supported and correct.
- Handle end-of-stream, cancellation, and errors without leaking GPU resources.
- Use offline/export render path when quality matters more than interactive latency.

## Wide color and HDR

- Choose swapchain format and color space based on device support and product requirement.
- For Display P3 output, query `VK_COLOR_SPACE_DISPLAY_P3_NONLINEAR_EXT` and compatible formats.
- Track color through decode, processing, preview, and export.
- Use higher precision intermediate formats for HDR/wide-gamut filters when needed.
- Be explicit about tone mapping and gamut mapping.

## Photo editor pipeline

Interactive preview:

```text
source image or tile -> GPU texture -> adjustment/filter passes -> preview surface
```

Full export:

```text
source full-res tiles -> same operations at full quality -> encoder/output file
```

Rules:

- Avoid running export on the UI/render loop that drives preview.
- Export should be cancellable and report progress.
- Reuse shader logic where possible but allow different tile size/precision.
- Keep metadata handling in app/data layer; renderer should not own EXIF policy.

## Common interop bugs

- Missing synchronization between producer and Vulkan consumer.
- Rendering with wrong crop/rotation for camera sensor output.
- Treating YUV planes as tightly packed or same size.
- Dropping HDR/wide-gamut metadata and silently converting to sRGB.
- Holding external buffers longer than the producer expects.
- Blocking camera acquisition while waiting for GPU work.
