# Native debugging, profiling, and release

## Use this file when

Use this reference for native crashes, symbolication, memory bugs, profiling, sanitizer setup, or release packaging.

## Debugging tools

- Android Studio native debugger / LLDB for breakpoints and variables.
- Logcat with `android/log.h` for coarse diagnostics.
- `ndk-stack` for symbolizing tombstones when symbols are available.
- `addr2line`/LLVM tools for offline symbolication.
- Simpleperf for CPU profiling native code.
- Perfetto for app/system scheduling and trace correlation.
- Android Studio Memory Profiler, including JNI heap view for global references.

## Logging

Use structured tags and severity. Avoid logging in hot loops.

```cpp
#include <android/log.h>
#define LOG_TAG "NativeImageProcessor"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
```

Do not log file paths, user media metadata, or raw image data unless sanitized and necessary.

## Crash triage

For native crashes, collect:

- Device model, ABI, OS version, app version, and build type.
- Tombstone or native crash stack.
- Native debug symbols matching the exact build.
- Input size/format/stride and operation name.
- Thread name and lifecycle state.
- Whether sanitizer build reproduces it.

Common causes:

- Use-after-free of native handle after Kotlin object closed.
- `JNIEnv*` used on wrong thread.
- Local reference table overflow in loops.
- Buffer capacity/stride mismatch.
- Unsupported API symbol loaded on older device.
- Missing or incompatible `.so` dependency.

## Sanitizers and memory debugging

Use sanitizers in debug/testing builds, not production release builds unless a specific mitigation is designed for that purpose.

- AddressSanitizer: native memory errors such as out-of-bounds and use-after-free.
- HWAddressSanitizer on supported devices for lower-overhead memory bug detection.
- GWP-ASan for sampling-based heap error detection.
- UndefinedBehaviorSanitizer for selected undefined behavior classes if build supports it.

Run sanitizer builds on real devices and with representative image sizes. Many image bugs only appear at high resolution or unusual strides.

## CPU profiling

Use simpleperf or Android Studio profiler to answer:

- Which function consumes the most CPU?
- Is time spent in JNI marshaling, allocation, conversion, algorithm code, or locks?
- Are worker threads oversubscribed?
- Are cache misses or memory copies the bottleneck?

Optimization order:

1. Remove unnecessary copies and conversions.
2. Reduce resolution/work per frame.
3. Fix allocation and locking in hot loops.
4. Improve data layout and tiling.
5. Add SIMD/NEON or native library acceleration.
6. Move to Vulkan/GPU if the workload maps well and data transfer cost is acceptable.

## Release packaging

- Release builds should be non-debuggable.
- Strip native libraries in release packages.
- Preserve matching unstripped symbols in CI artifacts and upload native symbols where the distribution platform supports it.
- Hide all symbols except JNI/exported APIs.
- Verify App Bundle/APK contents for every ABI.
- Verify **16 KB page-size alignment** for `arm64-v8a` and `x86_64` libraries (APK Analyzer or `check_elf_alignment.sh`).
- Test clean install and upgrade on every shipped ABI.
- Include native library version and feature flags in diagnostic logs.

## Final native PR checklist

- Boundary is coarse-grained and documented.
- C++ algorithm is testable without JNI.
- Native objects use RAII and have explicit Kotlin lifecycle ownership.
- `JNIEnv*`, global refs, local refs, and thread attach/detach are correct.
- Buffers validate size, stride, format, and ownership.
- Sanitizer or memory-debug pass has run for risky code.
- Simpleperf/profiler evidence supports native implementation if performance was the reason.
- Release ABIs and symbols are handled.
