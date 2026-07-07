# Android Build Performance and CI

## Table of contents

1. Measurement sequence
2. Variant reduction
3. Android-specific expensive work
4. Resource and manifest work
5. Annotation processing and generated code
6. CI task selection
7. Build performance checklist

## 1. Measurement sequence

Use `gradle-dev` for general measurement, configuration cache, build cache, daemon, parallelism, and dependency-resolution rules. Then add Android-specific signals:

```bash
./gradlew help --profile
./gradlew :app:assembleDebug --profile
./gradlew :app:assembleDebug --info
./gradlew :app:lintDebug --profile
```

Android Studio Build Analyzer can help identify expensive Android tasks during IDE builds.

Do not run `--scan` automatically; ask first because scans may upload metadata.

## 2. Variant reduction

Variant count multiplies by build types and flavor dimensions.

Rules:

- Remove unused flavors/build types.
- Avoid flavor dimensions for values that can be runtime configuration.
- Disable variants only with a clear policy and after checking CI, publishing, tests, and developer workflows.
- Use `androidComponents.beforeVariants` for supported variant disabling/configuration.
- Avoid creating custom tasks for every variant when only one build type/flavor needs them.

## 3. Android-specific expensive work

Common hotspots:

- Resource processing and packaging.
- Kotlin/Java compilation in many Android modules.
- Annotation processing/code generation.
- Lint over many variants/modules.
- R8/minification for release variants.
- Instrumentation tests and emulator setup.
- Large dependency graphs or duplicate dependency families.

Fixes should be targeted:

- Move pure Kotlin logic to JVM modules when it does not need Android SDK/resources.
- Reduce module dependencies that bring heavy Android resources transitively.
- Use variant-specific task wiring only where needed.
- Prefer incremental/cache-compatible processors and generated-code tasks.
- Keep lint and R8 in CI, but run them on intentional variants.

## 4. Resource and manifest work

Guidelines:

- Keep resources in modules that own them.
- Avoid broad resource overlays across many variants.
- Keep manifest placeholders and generated manifest values stable and declared as task inputs where custom generation exists.
- Validate manifest merge failures with the specific variant's process/merge task output.

## 5. Annotation processing and generated code

Rules:

- Prefer KSP when available and compatible.
- Keep processors off modules that do not need them.
- Avoid kapt in pure Kotlin/JVM modules unless required.
- Declare generated sources through AGP/Kotlin/Gradle supported APIs.
- Treat generated-source tasks as Gradle tasks with declared inputs/outputs.

## 6. CI task selection

Common PR validation for an app:

```bash
./gradlew --no-daemon :app:assembleDebug :app:testDebugUnitTest :app:lintDebug --stacktrace
```

Release validation:

```bash
./gradlew --no-daemon :app:assembleRelease :app:bundleRelease :app:lintRelease --stacktrace
```

Instrumentation tests should be separate when they need emulators/devices:

```bash
./gradlew --no-daemon :app:connectedDebugAndroidTest --stacktrace
```

Rules:

- Keep fast PR validation separate from slower release/device validation where possible.
- Publish test, lint, and build reports as artifacts.
- Do not make every PR build every flavor/release artifact unless product risk requires it.
- Cache Gradle User Home carefully and apply `gradle-dev` cache correctness rules.

## 7. Build performance checklist

- Measure before changing settings.
- Use the wrapper and stable JDK/toolchain.
- Keep AGP/Kotlin/Gradle versions compatible.
- Minimize variants and variant-aware custom work.
- Prefer convention plugins over copy/paste Android blocks.
- Avoid eager task creation and legacy variant APIs.
- Move pure code to JVM modules when possible.
- Keep processors and plugins only where needed.
- Validate configuration-cache/build-cache behavior after plugin changes.
- Run release/lint tasks intentionally, not accidentally on every local build.
