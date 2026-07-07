---
name: gradle-android-dev
description: Configure and debug Android Gradle Plugin builds for Android app and library projects. Use when working with com.android.application, com.android.library, android blocks, SDK levels, namespace, build types, product flavors, variants, lint, R8/ProGuard, signing, Android unit/instrumented test tasks, Android Studio sync, AGP upgrades, or Android build performance — even if the user says "fix my Android Gradle sync" without naming AGP. Always use gradle-dev for general Gradle concepts, wrapper, Kotlin DSL, dependency management, build cache/configuration cache, CI, and custom task logic. For plain Kotlin test design, use kotlin-testing. For Kotlin source language/API fixes, use kotlin-coding.
---

# Gradle Android Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Engineer Android Gradle Plugin (AGP) builds. Read bundled references on demand.

Always rely on [gradle-dev](../gradle-dev/SKILL.md) for shared Gradle concepts: wrapper usage, settings/repositories, Kotlin DSL syntax, version catalogs, dependency resolution, lazy tasks, custom Gradle tasks/plugins, configuration cache, build cache, and generic CI structure. Do not duplicate those rules here.

## Scope

Use this skill for Android Gradle Plugin (AGP) build work: Android app/library/test modules, `android {}` DSL, namespace and SDK levels, build types, product flavors, variants, source sets, manifest/resource processing, lint, R8/ProGuard, signing, AGP upgrades, Android Studio sync, Android unit/instrumented test **task** wiring, and Android-specific build performance.

Always rely on [gradle-dev](../gradle-dev/SKILL.md) for shared Gradle concepts. Do not duplicate those rules here; apply them and then add AGP-specific guidance.

## When NOT to Use

- General Gradle build engineering without Android/AGP context — [gradle-dev](../gradle-dev/SKILL.md)
- Plain Kotlin/JVM test design, Kotest/MockK, or flaky-test triage — [kotlin-testing](../kotlin-testing/SKILL.md)
- Kotlin language/API design in Android source — [kotlin-coding](../kotlin-coding/SKILL.md)
- Android UI/framework architecture, Compose, or Espresso test **code** — platform skills such as `android-native-dev` when available; this skill maps Android Gradle test **tasks** only

## Default workflow

1. Classify the Android build request:
   - New or reviewed module: app vs library vs test module, plugin id, namespace, SDK levels, dependencies, variants, and validation tasks.
   - Sync/configuration failure: collect Android Studio version when relevant, AGP version, Gradle version, JDK, Kotlin plugin version, command, root cause, settings, root build file, module build file, catalog, and `gradle.properties`.
   - Variant/flavor issue: collect requested variant, build type, flavor dimensions, source-set files, dependency declarations, and task name.
   - Packaging/release issue: inspect signing, minification, resources, manifest merge, R8 rules, packaging options, and generated artifacts.
   - Performance issue: use [gradle-dev](../gradle-dev/SKILL.md) measurement workflow first, then inspect AGP-specific variant count, resource processing, annotation processing, lint, R8, and Android Studio Build Analyzer clues.
2. Load shared Gradle guidance from [gradle-dev](../gradle-dev/SKILL.md) whenever the issue involves wrapper, DSL syntax, dependency management, task laziness, cache behavior, or CI. Load Android references only for Android-specific behavior.
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
- For build-cache/configuration-cache rules, apply [gradle-dev](../gradle-dev/SKILL.md) and then verify AGP/plugin compatibility.

## Tooling helper

This skill includes `scripts/android_gradle_project_check.sh`. Use it only when a local Android Gradle project is available and the user wants command discovery or checks run. Default mode is `--quick`.

```bash
scripts/android_gradle_project_check.sh --dry-run
scripts/android_gradle_project_check.sh --quick
scripts/android_gradle_project_check.sh --full
scripts/android_gradle_project_check.sh --perf
scripts/android_gradle_project_check.sh --device
```

The script detects Android modules and prints/runs likely assemble, unit-test, lint, and optional connected-test commands. It does not run external build scans automatically.

## Output patterns

When editing Android build files, return:

1. The exact file and block to change, preserving Kotlin/Groovy DSL style.
2. Whether the change is general Gradle ([gradle-dev](../gradle-dev/SKILL.md)) or Android-specific.
3. The affected variants/tasks.
4. The validation command.
5. Any compatibility assumption: AGP, Gradle, Kotlin plugin, JDK, compile SDK, or Android Studio version.

When debugging Android build failures, return:

1. The failure layer: sync/settings, plugin resolution, SDK/JDK compatibility, dependency resolution, manifest/resources, Kotlin/Java compile, unit tests, lint, R8/dex/package, signing, or device test.
2. The root-cause line and the smallest build file/source-set change.
3. The narrowest verification task.
4. A next diagnostic command if the first fix does not pass.

## Reference routing

| Task | Read |
|------|------|
| AGP module types, Android DSL, SDK/namespace, layout | [android-build-model.md](references/android-build-model.md) |
| AGP/Gradle/Kotlin/JDK compatibility, upgrades | [agp-versions-migration.md](references/agp-versions-migration.md) |
| Build types, flavors, variants, source sets, dependencies | [variants-source-sets-dependencies.md](references/variants-source-sets-dependencies.md) |
| Android test tasks, lint, R8, signing, release validation | [testing-lint-release.md](references/testing-lint-release.md) |
| Android build performance, variant reduction, CI | [performance-ci.md](references/performance-ci.md) |
| Sync, SDK/JDK, manifest, R8/dex, signing playbooks | [troubleshooting.md](references/troubleshooting.md) |
| General Gradle wrapper, catalogs, caches, CI | [gradle-dev](../gradle-dev/SKILL.md) |
| Plain Kotlin test design and frameworks | [kotlin-testing](../kotlin-testing/SKILL.md) |
| Kotlin language/API design | [kotlin-coding](../kotlin-coding/SKILL.md) |

## Companion skills

- Use [gradle-dev](../gradle-dev/SKILL.md) for all non-Android Gradle fundamentals and shared build engineering.
- Use [kotlin-coding](../kotlin-coding/SKILL.md) for Kotlin language/API/design issues in Android source code.
- Use [kotlin-testing](../kotlin-testing/SKILL.md) for plain Kotlin test design and test-framework patterns. Use Android-specific references here only for Android Gradle test task wiring.

## References

- [android-build-model.md](references/android-build-model.md): AGP module types, Android DSL, SDK/namespace/default config, and module layout.
- [agp-versions-migration.md](references/agp-versions-migration.md): AGP/Gradle/Kotlin/JDK compatibility, upgrade process, Kotlin DSL migration, and deprecation handling.
- [variants-source-sets-dependencies.md](references/variants-source-sets-dependencies.md): build types, flavors, variant selection, source-set overlays, dependency scopes, and generated sources.
- [testing-lint-release.md](references/testing-lint-release.md): Android unit/instrumented test tasks, lint wiring, R8/minification, signing, and release validation.
- [performance-ci.md](references/performance-ci.md): Android-specific performance triage, variant reduction, resource work, annotation processing, lint/R8 cost, CI command selection.
- [troubleshooting.md](references/troubleshooting.md): Android Studio sync, SDK/JDK, namespace, dependency, manifest/resource, R8/dex, and signing playbooks.
- [source-notes.md](references/source-notes.md): source synthesis, base-skill integration, and scope boundaries.
