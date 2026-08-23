# Source Notes

## Base materials synthesized

This skill integrates patterns from:

- `https://github.com/Kotlin/kotlinx-rpc/tree/main/.claude/skills/gradle_expert`
- `https://github.com/livekit/client-sdk-android/tree/main/.agent/skills/gradle-build-performance`
- Gradle User Manual and current reference pages.
- JetBrains IntelliJ IDEA Gradle documentation.
- Kotlin Gradle plugin documentation.
- Android Gradle build documentation, only as boundary context for the companion `gradle-android-dev` skill.

## Scope decisions

- This skill owns generic Gradle semantics and build engineering.
- `gradle-android-dev` owns AGP and Android-specific build behavior.
- `kotlin-coding` owns Kotlin language/API design.
- `kotlin-testing` owns Kotlin test design and test-framework patterns.

## Versioning policy

- Prefer placeholders for exact plugin/library versions unless the user asks for current versions or supplies an existing catalog.
- Before recommending exact current versions, verify official release notes or the project's catalog.
- Check compatibility matrices before major Gradle, Kotlin, AGP, or JDK upgrades.

## Safety and privacy

- Do not run or recommend external build scans automatically; they can publish metadata.
- Do not commit credentials, local paths, or machine-specific values.
- Treat build scripts as executable code: inspect before running unknown tasks from untrusted repositories.
