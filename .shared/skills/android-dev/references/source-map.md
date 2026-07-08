# Source map

Use these sources when updating or checking this skill. Prefer official Android documentation for facts that may change.

## Official Android documentation

- Android API reference: https://developer.android.com/reference
- Android 16 overview and migration: https://developer.android.com/about/versions/16
- Android 16 all-app behavior changes: https://developer.android.com/about/versions/16/behavior-changes-all
- Android 16 target behavior changes: https://developer.android.com/about/versions/16/behavior-changes-16
- Jetpack Compose course: https://developer.android.com/courses/jetpack-compose/course
- Android architecture pathway: https://developer.android.com/courses/pathways/android-architecture
- Develop UI with Compose: https://developer.android.com/develop/ui
- Camera and Media developer center: https://developer.android.com/media
- Android App Bundles: https://developer.android.com/guide/app-bundle

## Skills reviewed for patterns

- MiniMax android-native-dev (patterns absorbed into `android-dev`): project-state checks, Gradle sanity checks, Compose/Kotlin pitfalls, UI/accessibility/performance review patterns.
- ECC android-clean-architecture: module boundaries, dependency rules, use cases, repositories, data mapping, DI, anti-patterns.
- sickn33 android-jetpack-compose-expert: requested as inspiration for Compose focus; direct raw fetch was unavailable during package creation, so Compose guidance was grounded in official Android Compose docs and common best practices.
- sickn33 android-cli: requested as inspiration for CLI/build flow; direct raw fetch was unavailable during package creation, so build guidance was grounded in official Android/NDK docs and Gradle command conventions.

## Cross-skill boundaries

- `android-dev` owns app-layer Kotlin, Compose, architecture, SDK camera/media, permissions, performance gates, and release.
- `android-ndk-dev` owns native C++ integration, JNI, CMake, native libraries, native memory/threading, native debug/profiling.
- `android-vulkan-dev` owns Vulkan renderer internals, GPU resources, shaders, swapchain/surface, synchronization, validation, and GPU image processing.
