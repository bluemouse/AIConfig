---
name: kotlin-coding
description: "Write, review, refactor, debug, and explain plain Kotlin/JVM language code, standard-library APIs, idioms, coroutines, and kotlinc workflows. Use when implementing Kotlin classes or functions, reviewing Kotlin diffs, fixing compiler or runtime errors, choosing stdlib APIs, or improving null-safety and type modeling \u2014 even if the user says \"Kotlin help\" without naming a topic. For test design, frameworks, mocks, property tests, coverage, or flaky-test triage, use kotlin-testing. For Gradle build files, version catalogs, task wiring, CI, or build cache, use gradle-dev. For Android Gradle Plugin builds, use gradle-android-dev. Excludes Android, KMP, Kotlin/Native, Kotlin/JS/Web, Compose, Ktor/backend, and platform-specific architecture."
---

# kotlin-coding wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/kotlin-coding/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/kotlin-coding` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/kotlin-coding/`.
- Keep only Claude Code-specific information in this wrapper.
