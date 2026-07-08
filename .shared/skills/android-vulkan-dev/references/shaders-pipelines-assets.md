# Shaders, pipelines, and assets

## Use this file when

Use this reference for SPIR-V shader handling, NDK shader compilation, Android Studio shader packaging, descriptor sets, pipeline layouts, pipeline cache, and renderer assets on Android.

For generic `VkPipeline`, descriptor layout, and pipeline cache rules, use [vulkan-dev](../../vulkan-dev/SKILL.md) [pipelines.md](../../vulkan-dev/references/pipelines.md) and [descriptors.md](../../vulkan-dev/references/descriptors.md).

## Shader strategy

Vulkan consumes SPIR-V modules, not runtime GLSL strings. Prefer ahead-of-time compilation for shipped shaders.

### Compile with NDK glslc

Use the `glslc` tool from the Android NDK (see [Vulkan shader compilers](https://developer.android.com/ndk/guides/graphics/shader-compilers)):

```bash
# From project root; paths vary by NDK install
$ANDROID_NDK_HOME/shader-tools/linux-x86_64/glslc \
  -fshader-stage=frag \
  app/src/main/shaders/filter.frag \
  -o app/src/main/assets/shaders/filter.frag.spv
```

Rules:

- Compile all stage variants (vert, frag, comp) at build time, not during interactive frames.
- Version-control source GLSL/SPIR-V or generate SPIR-V in CI/Gradle and verify reproducibility.
- Validate SPIR-V with `spirv-val` when available.

### Android Studio / AGP packaging

Source shaders can live under:

```text
app/src/main/shaders/
```

Compiled `.spv` files are commonly packaged as assets:

```text
app/src/main/assets/shaders/
```

Runtime shader compilation is useful for generated shaders or tools, but avoid it during brush strokes or camera preview frames.

## Loading shader assets

Use `AAssetManager` passed from Kotlin to native code.

```cpp
std::vector<uint32_t> LoadSpirv(AAssetManager* assets, const char* path) {
    AAsset* asset = AAssetManager_open(assets, path, AASSET_MODE_BUFFER);
    if (!asset) throw std::runtime_error("missing shader asset");
    const size_t size = AAsset_getLength(asset);
    if (size == 0 || (size % 4) != 0) throw std::runtime_error("invalid SPIR-V size");
    std::vector<uint32_t> code(size / 4);
    AAsset_read(asset, code.data(), size);
    AAsset_close(asset);
    return code;
}
```

Handle errors without crashing release builds — return a structured error to Kotlin.

## Descriptor sets and pipelines (Android notes)

- Create pipelines during loading or background preparation, not during a brush stroke or camera frame.
- Persist `VkPipelineCache` on disk if startup benchmarks show benefit.
- Size descriptor pools for max frames-in-flight × max layers/filters the product supports.
- Limit shader permutation explosion. Prefer composable passes.

## Image processing shaders

For photo/filter workloads on Android:

- Keep color math explicit: input transfer function, working space, output transfer function.
- Prefer linear-light math for compositing when required by visual quality.
- Avoid precision loss in HDR/wide-gamut paths.
- Use LUTs for expensive tone/color operations when appropriate.
- Validate border handling, alpha premultiplication, and clamp/wrap behavior.

## Painting shaders

For brush rendering:

- Use brush stamp atlases or procedural brush generation as appropriate.
- Keep pressure/tilt/velocity data compact.
- Batch stroke segments when possible.
- Render into tiles/layers rather than the whole document.
- Keep preview and final-quality paths consistent enough that users are not surprised by export.

## Common shader/pipeline bugs

- Runtime shader compile stutter on first frame.
- Descriptor pool too small under realistic layer/filter counts.
- Pipeline recreated per frame.
- Wrong sRGB/linear conversion causing washed-out or oversaturated output.
- Premultiplied/unpremultiplied alpha mismatch.
- Assuming one device supports every format/filter operation.
