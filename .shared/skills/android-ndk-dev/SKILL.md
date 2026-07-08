---
name: android-ndk-dev
description: android ndk and c++ integration guidance for kotlin android 16/api 36+ apps. use when designing, implementing, reviewing, or troubleshooting native libraries, cmake, externalnativebuild, jni bridges from kotlin, prebuilt libraries, abi packaging, native memory, native threads, image/media processing in c++, native debugging, sanitizers, symbols, and performance profiling. prefer android-dev for app-layer kotlin, compose, sdk camera/media, permissions, and release architecture. prefer android-vulkan-dev for vulkan renderer internals and gpu rendering through the ndk.
---

# Android NDK Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Use this skill when an Android app needs C++ code or native libraries. Keep Kotlin as the app/control layer and make the native boundary small, explicit, measured, and lifecycle-safe.

Assume Android 16/API 36+ target and Kotlin-only managed app code. JNI is still the bridge mechanism between Kotlin/ART bytecode and C/C++ native code.

## When to Use

- Adding or reviewing C++ source, CMake, `externalNativeBuild`, JNI bridges, prebuilt `.so` libraries, or ABI packaging
- Native memory, threading, direct buffers, native handles, and camera/media/image processing in C++
- Native debugging (LLDB, tombstones, sanitizers), simpleperf profiling, symbols, and release native packaging

## When NOT to Use

- Kotlin app architecture, Compose UI, permissions, or SDK CameraX/Media3 — [android-dev](../android-dev/SKILL.md)
- Vulkan instance/device/swapchain/shader/pipeline/synchronization — [android-vulkan-dev](../android-vulkan-dev/SKILL.md)
- AGP `android {}` DSL, variants, lint, R8, signing — [gradle-android-dev](../gradle-android-dev/SKILL.md)
- General C++20 style and Core Guidelines — [cpp-coding](../cpp-coding/SKILL.md)
- C++ allocator/ownership design (arenas, PMR) — [cpp-memory-guide](../cpp-memory-guide/SKILL.md)
- GoogleTest/CMake native test targets — [cpp-testing](../cpp-testing/SKILL.md)

## Scope boundaries

- Own C++, CMake, `externalNativeBuild`, JNI, native libraries, ABIs, native memory/threading, native camera/media/image processing, debug symbols, sanitizers, and native profiling.
- Do not duplicate app architecture, Compose UI, permissions, or SDK camera/media guidance; use [android-dev](../android-dev/SKILL.md) for those.
- Do not implement Vulkan renderer details here; use [android-vulkan-dev](../android-vulkan-dev/SKILL.md) for instance/device/swapchain/shader/pipeline/synchronization/GPU image processing details.
- Defer AGP Gradle DSL details to [gradle-android-dev](../gradle-android-dev/SKILL.md); keep minimal CMake/JNI examples here.

## Native-code decision gate

Before adding NDK code, ask what benefit native code gives:

- Reuse an existing C/C++ library.
- Meet a measured CPU, latency, memory, or power goal not met by Kotlin/SDK APIs.
- Use native platform APIs or lower-level media/image capabilities.
- Provide shared code with another platform.

Do not add native code just to make code "faster" without measurement. JNI and marshaling add complexity and cost.

## Workflow

1. Define the boundary: a small Kotlin facade calls a small set of native entry points. Avoid chatty per-pixel or per-frame JNI calls.
2. Choose data ownership: Kotlin-owned arrays/buffers, native-owned handles, direct buffers, file descriptors, or hardware buffers.
3. Configure Gradle and CMake via [gradle-android-dev](../gradle-android-dev/SKILL.md) and [cmake-gradle-jni.md](references/cmake-gradle-jni.md). Build debug first, then release with symbols and 16 KB page-size compliance handled correctly.
4. Implement JNI with explicit lifetime, errors, threading, and cancellation. Apply [cpp-coding](../cpp-coding/SKILL.md) and [cpp-memory-guide](../cpp-memory-guide/SKILL.md) for C++ design.
5. Test with small deterministic inputs before camera/media integration. Use [cpp-testing](../cpp-testing/SKILL.md) for native unit tests where applicable.
6. Profile and debug with Android Studio, LLDB, simpleperf, sanitizers, and logs.
7. Package only needed ABIs and libraries in the App Bundle.

## Recommended project layout

```text
app/
  build.gradle.kts
  src/main/cpp/
    CMakeLists.txt
    native_api.cpp
    image_processor.cpp
    include/
      image_processor.h
  src/main/java/com/example/app/nativebridge/
    NativeImageProcessor.kt
```

Use `java/` as the Android source-set directory name if the project already has it, but put Kotlin files in it. Do not create Java classes unless the user explicitly requires legacy interop.

## Kotlin facade pattern

Expose native code through a Kotlin class with explicit lifecycle. Avoid exposing raw `Long` handles throughout the app.

```kotlin
class NativeImageProcessor : Closeable {
    private var handle: Long = nativeCreate()

    fun applyFilter(input: ByteBuffer, width: Int, height: Int): ByteBuffer {
        check(handle != 0L) { "NativeImageProcessor is closed" }
        require(input.isDirect) { "Use a direct ByteBuffer to avoid extra copies" }
        return nativeApplyFilter(handle, input, width, height)
    }

    override fun close() {
        val h = handle
        if (h != 0L) {
            handle = 0L
            nativeDestroy(h)
        }
    }

    private external fun nativeCreate(): Long
    private external fun nativeApplyFilter(handle: Long, input: ByteBuffer, width: Int, height: Int): ByteBuffer
    private external fun nativeDestroy(handle: Long)

    companion object {
        init { System.loadLibrary("image_processor") }
    }
}
```

## Core rules

- Keep JNI calls coarse grained. Pass batches, buffers, handles, or commands, not individual pixels or tiny objects.
- Use RAII in C++. Pair every native allocation, file descriptor, image, codec, hardware buffer, and global reference with a release path.
- Do not cache `JNIEnv*` across threads. Cache `JavaVM*` if native threads need to attach.
- Keep native worker threads away from UI callbacks unless they are explicitly attached and detached.
- Convert native errors into Kotlin exceptions or sealed error results at the boundary.
- Compile with warnings enabled and treat suspicious warnings as bugs.
- Hide native symbols by default; export only JNI entry points and intentional public C APIs.
- Test on real devices for camera/media/native performance; emulators are useful but not sufficient.
- Verify 16 KB page-size alignment for 64-bit `.so` files before Play release (see [cmake-gradle-jni.md](references/cmake-gradle-jni.md)).

## Reference routing

| Task | Read |
|------|------|
| Gradle, CMake, JNI, prebuilt libs, ABI, 16 KB pages | [cmake-gradle-jni.md](references/cmake-gradle-jni.md) |
| RAII, references, direct buffers, handles, threads | [native-memory-threads-libraries.md](references/native-memory-threads-libraries.md) |
| Native camera/media/image processing, Vulkan handoff | [camera-media-image-pipeline.md](references/camera-media-image-pipeline.md) |
| LLDB, simpleperf, sanitizers, symbols, release | [debugging-profiling-release.md](references/debugging-profiling-release.md) |
| Source links | [source-map.md](references/source-map.md) |
| AGP externalNativeBuild, variants, lint | [gradle-android-dev](../gradle-android-dev/SKILL.md) |
| C++ style and Core Guidelines | [cpp-coding](../cpp-coding/SKILL.md) |
| C++ memory/ownership | [cpp-memory-guide](../cpp-memory-guide/SKILL.md) |
| Native unit tests | [cpp-testing](../cpp-testing/SKILL.md) |
| App-layer Kotlin/Compose | [android-dev](../android-dev/SKILL.md) |
| Vulkan on Android | [android-vulkan-dev](../android-vulkan-dev/SKILL.md) |

## Companion skills

- Use [android-dev](../android-dev/SKILL.md) for Kotlin app architecture, Compose, SDK camera/media, and permissions.
- Use [android-vulkan-dev](../android-vulkan-dev/SKILL.md) for Vulkan GPU rendering through the NDK.
- Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for AGP build configuration and release packaging.
- Use [cpp-coding](../cpp-coding/SKILL.md), [cpp-memory-guide](../cpp-memory-guide/SKILL.md), and [cpp-testing](../cpp-testing/SKILL.md) for C++ implementation and testing.

## References

- [cmake-gradle-jni.md](references/cmake-gradle-jni.md): Gradle, CMake, JNI signatures, prebuilt libraries, ABI packaging, 16 KB page size.
- [native-memory-threads-libraries.md](references/native-memory-threads-libraries.md): RAII, references, direct buffers, native handles, threads, library ownership.
- [camera-media-image-pipeline.md](references/camera-media-image-pipeline.md): NDK camera/media/image processing and handoff to Vulkan.
- [debugging-profiling-release.md](references/debugging-profiling-release.md): Android Studio, LLDB, ndk-stack, simpleperf, sanitizers, symbols, release packaging.
- [source-map.md](references/source-map.md): source links and update notes used to build this skill.
