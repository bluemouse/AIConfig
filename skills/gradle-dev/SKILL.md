---
name: gradle-dev
description: Create, review, troubleshoot, and optimize Gradle builds for JVM, Kotlin, and Java projects. Use for build.gradle.kts, settings.gradle.kts, gradle.properties, version catalogs, wrapper, custom tasks/plugins, test/check wiring, CI, and build or configuration cache — including "fix my Gradle build". Excludes Android/AGP (gradle-android-dev) and Kotlin code/tests (kotlin-coding).
---

# Gradle Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

## Scope and Boundaries

Covers general Gradle build engineering: wrapper, lifecycle, Kotlin/Groovy DSL, version catalogs, dependencies, custom tasks/plugins, JVM/Kotlin/Java builds, check/CI wiring, caches, and troubleshooting. Read bundled references on demand.

Out of scope:
- Android Gradle Plugin, variants, lint, R8, signing, or Studio sync — [gradle-android-dev](../gradle-android-dev/SKILL.md) (explain inherited Gradle fundamentals without duplicating AGP rules)
- Kotlin source language/API design, test frameworks (Kotest/MockK), or flaky-test triage — [kotlin-coding](../kotlin-coding/SKILL.md)

## Default workflow

1. Load only the needed references (see **Reference routing** below).
2. Prefer project-local truth over generic snippets. Preserve the existing DSL, plugin versions, repository policy, version catalog, and module structure unless the user asks to modernize them.
3. Make the smallest safe build change. Prefer target-scoped lazy configuration; reach for global hooks (`allprojects`, `subprojects`, `afterEvaluate`, eager task lookup, dynamic versions, hidden repository additions, global mutable build state) only when no supported lazy alternative exists, and note the maintenance cost in the build.
4. Validate with the wrapper. Prefer `./gradlew help` for configuration validation, then the smallest relevant task, then `./gradlew check` or CI-equivalent tasks.
5. Explain the Gradle-specific reason for changes: lifecycle phase, lazy provider, configuration/cache behavior, variant/attribute resolution, toolchain, or task graph impact.

## Build editing rules

- Use the Gradle Wrapper: `./gradlew` or `gradlew.bat`. Do not recommend relying on a globally installed Gradle for project builds.
- Prefer Kotlin DSL (`.gradle.kts`) for new examples unless the project is already Groovy DSL.
- Put repository policy in `settings.gradle(.kts)` with `dependencyResolutionManagement` when modernizing a build.
- Centralize dependency and plugin versions in `gradle/libs.versions.toml` or existing convention plugins for multi-project builds.
- Use plugin aliases or `plugins { id("...") version "..." apply false }` at the root, then apply plugins in modules.
- Use Java/Kotlin toolchains for reproducible builds. Do not rely on the Gradle daemon JVM to imply bytecode target compatibility.
- Use `tasks.register`, `tasks.named`, and `configureEach`; avoid `tasks.create`, `getByName`, `.get()` during configuration, and `afterEvaluate` unless there is no supported lazy API.
- For custom tasks, declare inputs/outputs with Gradle property types and annotations before enabling caching or claiming incrementality.
- Do not enable remote build-cache push for local developer machines unless the project already has that policy.
- Treat build scans as opt-in because they may publish build metadata externally. Prefer local logs/profile output unless the user asks for a scan.

## Validation commands

Use the narrowest command that proves the change:

```bash
./gradlew help
./gradlew tasks --all
./gradlew test --stacktrace
./gradlew check --stacktrace
./gradlew dependencyInsight --dependency <name> --configuration <configuration>
./gradlew help --configuration-cache --configuration-cache-problems=warn
./gradlew help --profile
```

For Windows examples, use `gradlew.bat` instead of `./gradlew`.

Report results and the failure slice, not raw output streams — prefer quiet output
(`-q`, `--console=plain`) and filtered reads over pasting full Gradle logs; quote
the first root-cause stack-trace cause, not the whole build output.

## Tooling helper

This skill includes `scripts/gradle_project_check.sh`. Use it only when a local project is available and the user wants command discovery or checks run. Default mode is `--dry-run` (prints commands without executing); pass `--quick` to actually run the compact check pass.

```bash
scripts/gradle_project_check.sh --dry-run
scripts/gradle_project_check.sh --quick
scripts/gradle_project_check.sh --full
scripts/gradle_project_check.sh --perf
```

The script detects the wrapper, prints Gradle build files, lists likely plugins, and runs progressively stronger checks. It does not run external build scans automatically.

## Reference routing

| Task | Read |
|------|------|
| Wrapper, settings/build files, lifecycle, CLI, properties | [core-build-model.md](references/core-build-model.md) |
| Kotlin DSL, convention plugins, lazy providers, build logic | [kotlin-dsl-build-logic.md](references/kotlin-dsl-build-logic.md) |
| Repositories, catalogs, platforms, locking, dependency insight | [dependencies-versioning.md](references/dependencies-versioning.md) |
| Task creation, test tasks, JVM test suites, TestKit, CI | [tasks-testing-ci.md](references/tasks-testing-ci.md) |
| Configuration cache, build cache, profiling, failure playbooks | [performance-troubleshooting.md](references/performance-troubleshooting.md) |
| Kotlin/JVM plugin, source sets, compiler options, toolchains | [kotlin-gradle.md](references/kotlin-gradle.md) |
