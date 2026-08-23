# Source Notes

## Base materials synthesized

This skill integrates Android-specific build and performance patterns from:

- `https://github.com/livekit/client-sdk-android/tree/main/.agent/skills/gradle-build-performance`
- `https://github.com/Kotlin/kotlinx-rpc/tree/main/.claude/skills/gradle_expert` as shared Gradle-build context through `gradle-dev`.
- Android Developers Gradle build overview, configure-build, AGP release notes, build variants, Kotlin DSL migration, and optimize-build guides.
- Gradle User Manual and Kotlin Gradle plugin documentation for shared concepts delegated to `gradle-dev`.

## Scope decisions

- `gradle-dev` owns general Gradle concepts and should be consulted first for wrapper, repositories, dependency management, Kotlin DSL, lazy APIs, caches, CI, and custom tasks.
- This skill owns Android Gradle Plugin specifics: `android {}` DSL, AGP compatibility, SDK/namespace, variants, source sets, manifests/resources, lint, R8, signing, Android test task names, Android Studio sync, and Android build performance.
- Android UI/framework coding and app architecture are out of scope except where they affect the build.

## Versioning policy

- Use placeholders for versions unless the project already declares versions or the user asks for current exact versions.
- Verify current AGP/Gradle/Kotlin/JDK compatibility before recommending exact upgrades.
- Stage risky upgrades and validate after each stage.
