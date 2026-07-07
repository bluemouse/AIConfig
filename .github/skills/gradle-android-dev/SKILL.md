---
name: gradle-android-dev
description: "Configure and debug Android Gradle Plugin builds for Android app and library projects. Use when working with com.android.application, com.android.library, android blocks, SDK levels, namespace, build types, product flavors, variants, lint, R8/ProGuard, signing, Android unit/instrumented test tasks, Android Studio sync, AGP upgrades, or Android build performance \u2014 even if the user says \"fix my Android Gradle sync\" without naming AGP. Always use gradle-dev for general Gradle concepts, wrapper, Kotlin DSL, dependency management, build cache/configuration cache, CI, and custom task logic. For plain Kotlin test design, use kotlin-testing. For Kotlin source language/API fixes, use kotlin-coding."
---

# gradle-android-dev wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/gradle-android-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/gradle-android-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/gradle-android-dev/`.
- Keep only GitHub Copilot-specific information in this wrapper.
