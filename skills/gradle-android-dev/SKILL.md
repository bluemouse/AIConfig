---
name: gradle-android-dev
description: Configure, debug, and optimize Android Gradle Plugin (AGP) builds for Android app and library modules. Use for com.android.application/library, android DSL, SDK levels, namespace, build types, flavors/variants, lint, R8/ProGuard, signing, Android test tasks, Studio sync, and AGP upgrades. Delegate general Gradle/caches/catalogs to gradle-dev and Kotlin code/tests to kotlin-coding.
---

# Gradle Android Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Engineer Android Gradle Plugin (AGP) builds. Read bundled references on demand.

## Scope and Boundaries

Covers Android Gradle Plugin (AGP) builds: app/library/test modules, `android {}` DSL, namespace/SDK levels, build types, flavors/variants, source sets, manifest/resources, lint, R8/ProGuard, signing, AGP upgrades, Android Studio sync, Android test **task** wiring, and AGP build performance.

Out of scope:
- General Gradle wrapper, DSL, catalogs, dependency resolution, caches, CI, and custom tasks — [gradle-dev](../gradle-dev/SKILL.md) (apply shared Gradle rules there first)
- Kotlin language/API design, unit-test frameworks (Kotest/MockK), or flaky-test triage — [kotlin-coding](../kotlin-coding/SKILL.md)
- Android app/Compose/Espresso code — [android-dev](../android-dev/SKILL.md); native/GPU code — [android-ndk-dev](../android-ndk-dev/SKILL.md) and [android-vulkan-dev](../android-vulkan-dev/SKILL.md)

## Default workflow

1. Classify the Android build request:
   - New or reviewed module: app vs library vs test module, plugin id, namespace, SDK levels, dependencies, variants, and validation tasks.
   - Sync/configuration failure: collect Android Studio version when relevant, AGP version, Gradle version, JDK, Kotlin plugin version, command, root cause, settings, root build file, module build file, catalog, and `gradle.properties`.
   - Variant/flavor issue: collect requested variant, build type, flavor dimensions, source-set files, dependency declarations, and task name.
   - Packaging/release issue: inspect signing, minification, resources, manifest merge, R8 rules, packaging options, and generated artifacts.
   - Performance issue: measure first, then inspect AGP variant count, resource processing, annotation processing/KSP, lint, R8, and Android Studio Build Analyzer clues.
2. Load only the matching Android references below.
3. Preserve the project's existing DSL and version-management style unless asked to migrate. For current Android examples, prefer Kotlin DSL.
4. Make the smallest safe AGP-specific change. Avoid changing Gradle/Kotlin/AGP versions together unless compatibility requires it.
5. Validate with the narrowest Android task, then widen:

```bash
./gradlew help
./gradlew :app:assembleDebug
./gradlew :app:testDebugUnitTest
./gradlew :app:lintDebug
./gradlew :app:assembleRelease
```

Run device/emulator tasks such as `connectedDebugAndroidTest` only when a device/emulator is available or the user asks for instrumentation validation.

## Android build rules

- Use `com.android.application` for apps, `com.android.library` for Android libraries, and `com.android.test` for standalone test modules.
- Set `namespace` explicitly in each Android module.
- Keep `compileSdk`, `minSdk`, and `targetSdk` intentional and centralized when the project has many modules.
- Prefer `androidComponents {}` for modern variant-aware build logic instead of legacy variant APIs.
- Keep build types and product flavors minimal; variant explosion slows configuration, dependency resolution, compilation, testing, and IDE sync.
- Keep Android dependencies in Android modules. Do not leak Android SDK types into plain JVM modules unless that module is intentionally Android-specific.
- Use `lint` as a verification task, not as a substitute for tests or compiler diagnostics.
- Treat R8/ProGuard changes as behavior changes. Add keep rules narrowly and validate release builds.
- Do not hardcode signing credentials in build files. Use local properties, environment-backed providers, or CI secrets.
- Verify AGP and plugin compatibility when enabling build or configuration cache.

## Tooling helper

This skill includes `scripts/android_gradle_project_check.sh`. Use it only when a local Android Gradle project is available and the user wants command discovery or checks run. Default mode is `--dry-run` (prints commands without executing); pass `--quick` to actually run the compact check pass.

```bash
scripts/android_gradle_project_check.sh --dry-run
scripts/android_gradle_project_check.sh --quick
scripts/android_gradle_project_check.sh --full
scripts/android_gradle_project_check.sh --perf
scripts/android_gradle_project_check.sh --device
```

The script detects Android modules and prints/runs likely assemble, unit-test, lint, and optional connected-test commands. It does not run external build scans automatically.

## Output patterns

- When editing Android build files: name the exact file and block to change (preserving Kotlin/Groovy DSL style), the affected variants/tasks, the validation command, and any AGP/Gradle/Kotlin/JDK/compile-SDK/Android-Studio compatibility assumptions.
- When debugging Android build failures: identify the failure layer (sync, plugin resolution, SDK/JDK, dependency resolution, manifest/resources, compile, unit tests, lint, R8/dex/package, signing, or device tests), give the root cause and smallest fix, the narrowest verification task, and a next diagnostic command if the first fix does not pass.

## Reference routing

| Task | Read |
|------|------|
| AGP module types, Android DSL, SDK/namespace, layout | [android-build-model.md](references/android-build-model.md) |
| AGP/Gradle/Kotlin/JDK compatibility, upgrades | [agp-versions-migration.md](references/agp-versions-migration.md) |
| Build types, flavors, variants, source sets, dependencies | [variants-source-sets-dependencies.md](references/variants-source-sets-dependencies.md) |
| Android test tasks, lint, R8, signing, release validation | [testing-lint-release.md](references/testing-lint-release.md) |
| Android build performance, variant reduction, CI | [performance-ci.md](references/performance-ci.md) |
| Sync, SDK/JDK, manifest, R8/dex, signing playbooks | [troubleshooting.md](references/troubleshooting.md) |
