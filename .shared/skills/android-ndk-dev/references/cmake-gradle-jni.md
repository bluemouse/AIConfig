# CMake, Gradle, JNI, and libraries

## Use this file when

Use this reference when setting up an NDK module, adding C++ source, importing prebuilt libraries, writing Kotlin `external` functions, or packaging ABIs.

## Gradle setup

For full AGP `android {}` DSL, variant selection, and `externalNativeBuild` troubleshooting, use [gradle-android-dev](../../gradle-android-dev/SKILL.md). Minimal app-module setup:

```kotlin
android {
    namespace = "com.example.app"
    compileSdk = 36
    ndkVersion = "28.0.13004108"  // pin; r28+ aligns 16 KB by default

    defaultConfig {
        minSdk = 26
        targetSdk = 36

        externalNativeBuild {
            cmake {
                cppFlags += listOf("-std=c++20", "-Wall", "-Wextra")
            }
        }
        ndk {
            abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64")
        }
    }

    externalNativeBuild {
        cmake {
            path = file("src/main/cpp/CMakeLists.txt")
        }
    }
}
```

Choose ABI filters by product requirement. For modern performance-sensitive apps, always include `arm64-v8a`. Do not ship ABIs that the app does not test.

## 16 KB page-size compliance

Google Play requires 16 KB page-size support for apps targeting Android 15+ with native code (64-bit `.so` files). See [Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes).

Requirements:

- **AGP 8.5.1+** and **NDK r28+** (recommended): 64-bit libraries are 16 KB-aligned by default.
- **NDK r27:** set `ANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON` in CMake, or add linker flags for `arm64-v8a`/`x86_64`:

```cmake
if(ANDROID_ABI STREQUAL "arm64-v8a" OR ANDROID_ABI STREQUAL "x86_64")
    target_link_options(image_processor PRIVATE
        "-Wl,-z,max-page-size=16384"
        "-Wl,-z,common-page-size=16384"
    )
endif()
```

Verification:

- Android Studio APK Analyzer: check ELF segment alignment (expect 16 KB / 0x4000 for 64-bit libs).
- Run `check_elf_alignment.sh` from the NDK on release APKs.
- Test on a 16 KB page-size emulator system image when available.

Only **arm64-v8a** and **x86_64** require 16 KB alignment; 32-bit ABIs remain 4 KB.

## Prefab dependencies

For third-party native dependencies distributed as Prefab packages (AAR), use Gradle `implementation` with Prefab-enabled artifacts and `find_package()` in CMake. Pin versions in the catalog and verify each dependency's `.so` files are 16 KB-aligned before release.

## CMake defaults

```cmake
cmake_minimum_required(VERSION 3.22.1)
project(image_processor LANGUAGES C CXX)

add_library(image_processor SHARED
    native_api.cpp
    image_processor.cpp
)

target_compile_features(image_processor PRIVATE cxx_std_20)
target_compile_options(image_processor PRIVATE -Wall -Wextra -Wpedantic)

target_include_directories(image_processor PRIVATE include)

find_library(log-lib log)
find_library(android-lib android)

target_link_libraries(image_processor PRIVATE ${log-lib} ${android-lib})
```

Rules:

- Keep CMake targets small and named by product capability.
- Put public native headers in `include/`; keep JNI glue separate from core C++ algorithms.
- Use `target_compile_features` instead of global compiler flags when possible.
- Prefer imported targets for third-party libraries.
- Do not hard-code host paths or NDK internals.

## JNI naming and registration

For small apps, generated JNI symbol names are acceptable. For larger apps, prefer `RegisterNatives` to keep names stable and reduce fragile mangling.

Kotlin:

```kotlin
package com.example.app.nativebridge

internal object NativeBindings {
    init { System.loadLibrary("image_processor") }
    external fun nativeVersion(): String
}
```

C++ generated symbol style:

```cpp
extern "C" JNIEXPORT jstring JNICALL
Java_com_example_app_nativebridge_NativeBindings_nativeVersion(JNIEnv* env, jobject) {
    return env->NewStringUTF("1.0");
}
```

RegisterNatives style:

```cpp
static jstring NativeVersion(JNIEnv* env, jobject) {
    return env->NewStringUTF("1.0");
}

static const JNINativeMethod kMethods[] = {
    {"nativeVersion", "()Ljava/lang/String;", reinterpret_cast<void*>(NativeVersion)},
};

JNIEXPORT jint JNI_OnLoad(JavaVM* vm, void*) {
    JNIEnv* env = nullptr;
    if (vm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK) return JNI_ERR;
    jclass clazz = env->FindClass("com/example/app/nativebridge/NativeBindings");
    if (!clazz) return JNI_ERR;
    if (env->RegisterNatives(clazz, kMethods, sizeof(kMethods) / sizeof(kMethods[0])) != 0) return JNI_ERR;
    return JNI_VERSION_1_6;
}
```

## Marshaling strategy

Prefer these boundary types:

- Primitive values for configuration.
- `ByteBuffer.allocateDirect` for repeated binary buffers.
- File descriptors for large file/media streams.
- Native handles wrapped by Kotlin classes for long-lived native objects.
- `AssetManager` for packaged assets.
- `Surface`/`ANativeWindow` only for renderer/media outputs owned by lifecycle.

Avoid:

- Per-pixel JNI calls.
- Repeated string/object allocation per frame.
- Passing large bitmaps repeatedly across JNI.
- Returning raw `Long` handles to many call sites.

## Prebuilt libraries

For a third-party `.so` or static library:

- Match ABI, STL/runtime, API level, and license requirements.
- Keep each ABI in a clear directory such as `src/main/jniLibs/arm64-v8a/libfoo.so` or import through CMake.
- Do not mix incompatible C++ runtimes.
- Document transitive native dependencies.
- Test loading on every shipped ABI with a clean install.

## ABI and app bundle rules

- Use Android App Bundle configuration splits for native libraries.
- Ship only tested ABIs.
- Keep release symbols separately for crash symbolication.
- Strip release binaries but retain native debug symbols in CI artifacts or Play Console symbol upload.
- Validate package contents before release.

## Common build failures

- `undefined reference`: missing library in `target_link_libraries`, wrong source file, or C++ name mangling mismatch.
- `java.lang.UnsatisfiedLinkError`: library not packaged, wrong ABI, wrong JNI name/signature, or missing transitive `.so`.
- `dlopen failed`: missing dependency, unsupported API symbol on device, incompatible STL, or ABI mismatch.
- duplicate symbols: static libraries linked into multiple shared objects or duplicate object files.
- works in debug but not release: R8/obfuscation changed class names used by JNI, symbols stripped incorrectly, or release-only ABI filters differ.
