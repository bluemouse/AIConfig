# Native memory, threads, and library ownership

## Use this file when

Use this reference when reviewing C++ ownership, JNI references, native handles, direct buffers, worker threads, or third-party library lifetimes.

## Ownership model

Every native object must have one owner and one release path.

```cpp
class NativeProcessor {
public:
    NativeProcessor(int width, int height);
    ~NativeProcessor();

    NativeProcessor(const NativeProcessor&) = delete;
    NativeProcessor& operator=(const NativeProcessor&) = delete;
    NativeProcessor(NativeProcessor&&) noexcept = default;
    NativeProcessor& operator=(NativeProcessor&&) noexcept = default;
};
```

Use RAII wrappers for:

- Allocated image buffers.
- File descriptors.
- `AImage`, `AImageReader`, `AMediaCodec`, `AHardwareBuffer`.
- Vulkan objects if used indirectly; otherwise use `android-vulkan-dev`.
- JNI global references.

## Native handles

When Kotlin owns a native handle, protect against double free and use-after-free.

- Store handle in one facade object.
- Set handle to zero before or immediately after native destroy.
- Make `close()` idempotent.
- For concurrent use, guard native object with a mutex or serialize calls on one dispatcher/thread.
- Never expose handle values outside the facade except for tests or internal bridge calls.

C++ destroy function pattern:

```cpp
extern "C" JNIEXPORT void JNICALL
Java_com_example_app_nativebridge_NativeImageProcessor_nativeDestroy(JNIEnv*, jobject, jlong handle) {
    delete reinterpret_cast<NativeProcessor*>(handle);
}
```

## JNI references

- Local references are valid only for the current native call and thread.
- Delete local references in loops that create many objects.
- Use `NewGlobalRef` only for objects that must outlive the call; release with `DeleteGlobalRef`.
- Cache `jclass`, `jmethodID`, and `jfieldID` carefully. Protect `jclass` with a global ref.
- Do not compare object identity using raw JNI reference pointer values.
- Check and clear exceptions when native code calls into Kotlin/managed methods and must continue.

## `JNIEnv*` and threads

- `JNIEnv*` is thread-local; never store and use it from another thread.
- Store `JavaVM*` globally if native threads need JNI access.
- Native-created threads must attach before JNI calls and detach before exit.
- Prefer creating threads from managed code when they need frequent callbacks to Kotlin.
- Keep callbacks coarse-grained. Do not call into Kotlin for every frame if a native queue can batch results.

Thread attach helper sketch:

```cpp
class ScopedEnv {
public:
    explicit ScopedEnv(JavaVM* vm) : vm_(vm) {
        if (vm_->GetEnv(reinterpret_cast<void**>(&env_), JNI_VERSION_1_6) != JNI_OK) {
            vm_->AttachCurrentThread(&env_, nullptr);
            attached_ = true;
        }
    }
    ~ScopedEnv() {
        if (attached_) vm_->DetachCurrentThread();
    }
    JNIEnv* get() const { return env_; }
private:
    JavaVM* vm_ = nullptr;
    JNIEnv* env_ = nullptr;
    bool attached_ = false;
};
```

## Direct buffers

Use direct buffers for repeated binary data when Kotlin and native code both need access.

Kotlin:

```kotlin
val input = ByteBuffer.allocateDirect(width * height * 4)
    .order(ByteOrder.nativeOrder())
```

C++:

```cpp
void* data = env->GetDirectBufferAddress(buffer);
jlong capacity = env->GetDirectBufferCapacity(buffer);
if (!data || capacity < expected_size) {
    // throw IllegalArgumentException or return error
}
```

Rules:

- Validate capacity and alignment.
- Define pixel format, stride, row alignment, and byte order at the boundary.
- Avoid holding direct-buffer pointers after the JNI call unless ownership and lifetime are explicit.

## Third-party C++ libraries

Before integrating a library:

- Verify license and source of binaries.
- Check supported ABIs and minimum Android API level.
- Check whether it uses exceptions, RTTI, threads, OpenMP, codecs, SIMD, or custom allocators.
- Ensure it uses a compatible STL and does not require unavailable libc symbols.
- Wrap it behind a narrow C++ adapter and a narrow Kotlin facade.
- Add smoke tests that load the library and exercise one simple call on each ABI.

## Native performance rules

- Minimize copies across Kotlin/native/media/GPU boundaries.
- Use contiguous buffers and cache-friendly memory layouts.
- Avoid heap allocation in per-frame loops.
- Use worker thread pools deliberately; too many native threads can fight camera/media/UI scheduling.
- Prefer explicit vectorized/SIMD code only after scalar correctness and benchmarks.
- Avoid logging inside hot loops.
