# Camera, media, and image pipelines in native code

## Use this file when

Use this reference for native CPU image processing, camera/media buffer ownership, codec integration, and deciding when to hand off to Vulkan.

## Pipeline choices

Start with app-layer SDK APIs unless native is justified:

- CameraX + Kotlin analyzer: simplest for standard frame analysis.
- Camera2 + Kotlin/native bridge: useful for custom capture controls with native processing.
- NDK media/camera APIs: useful for deeper native control or C++ library reuse.
- Vulkan: use `android-vulkan-dev` for real-time GPU filters, rendering, compositing, or hardware buffer interop.

## Frame data rules

For every frame crossing a boundary, define:

- Pixel format: YUV_420_888, RGBA_8888, RGBA_F16, RAW, encoded bitstream, etc.
- Width, height, crop rect, row stride, pixel stride, and plane count.
- Orientation and sensor transform.
- Color space, transfer function, HDR/wide-gamut metadata when relevant.
- Ownership and release path.
- Whether the frame can be dropped or must be processed.

Never assume rows are tightly packed unless the API guarantees it and the code checks it.

## Camera frame analyzer pattern

Use bounded work. For preview filters, newest-frame-wins is usually better than accumulating latency.

`ImageProxy.planes` cannot cross JNI directly — extract plane buffers on the Kotlin side first, then pass direct buffers or a pre-allocated native buffer handle:

```kotlin
class NativeAnalyzer(
    private val processor: NativeImageProcessor
) : ImageAnalysis.Analyzer {
    override fun analyze(image: ImageProxy) {
        try {
            val yPlane = image.planes[0]
            val uPlane = image.planes[1]
            val vPlane = image.planes[2]
            processor.processYuv(
                yBuffer = yPlane.buffer,
                uBuffer = uPlane.buffer,
                vBuffer = vPlane.buffer,
                yRowStride = yPlane.rowStride,
                uvRowStride = uPlane.rowStride,
                uvPixelStride = uPlane.pixelStride,
                width = image.width,
                height = image.height,
                rotationDegrees = image.imageInfo.rotationDegrees
            )
        } finally {
            image.close()
        }
    }
}
```

The Kotlin facade should copy or map plane data into direct `ByteBuffer`s (or a reusable native-owned buffer updated each frame) before the JNI call. Do not pass `Array<ImageProxy.PlaneInfo>` to native code.

If this is too chatty, pass a native-readable buffer/handle once and update only lightweight metadata per frame.

## Native image processing

Good NDK candidates:

- Large image resampling with a C++ library.
- CPU filters with SIMD/NEON.
- Denoise, demosaic, histogram, tone map, or image IO not available in SDK APIs.
- Shared image algorithms with desktop or server code.

Rules:

- Keep algorithms independent of JNI. JNI glue converts inputs, calls the algorithm, and converts outputs.
- Use explicit strides and planes.
- Avoid extra YUV->RGB->YUV conversions.
- Validate image size and overflow before allocation.
- Prefer tiling for very large images and export flows.

## Media decode/encode

For playback and common editing, use SDK/Media3 first. Use native APIs or C++ libraries when:

- The app needs custom codec integration or cross-platform pipeline code.
- The app needs custom filters between decode and encode.
- The app must interop with native GPU rendering or hardware buffers.

Rules:

- Keep decode/encode on dedicated worker threads.
- Release codec buffers promptly.
- Propagate timestamps and color metadata.
- Handle end-of-stream and cancellation.
- Keep audio/video synchronization explicit.

## Handoff to Vulkan

Use `android-vulkan-dev` when the app needs:

- Real-time preview filters at camera frame rate.
- Non-destructive image layers with blend modes and masks.
- Large painting canvases with low latency.
- Hardware-buffer or surface-based zero-copy GPU paths.
- Custom tone mapping, LUTs, color transforms, or compute shaders.

The NDK layer should expose surfaces, buffers, file descriptors, and lifecycle hooks. The Vulkan skill owns GPU device/resource/synchronization details.

## Common failures

- Forgetting to close `ImageProxy` or native image objects.
- Assuming YUV plane strides are width/height tightly packed.
- Creating or destroying native processors per frame.
- Letting a background analyzer outrun camera preview and build an unbounded queue.
- Dropping color/rotation metadata before export.
- Mixing CPU and GPU ownership without fences or documented synchronization.
