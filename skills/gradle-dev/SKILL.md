---
name: gradle-dev
description: Create, review, troubleshoot, optimize, and modernize Gradle builds for general JVM, Kotlin, and Java projects. Use when editing build.gradle.kts, settings.gradle.kts, gradle.properties, version catalogs, wrapper usage, custom tasks/plugins, test/check task wiring, CI commands, build cache, or configuration cache — even if the user says "fix my Gradle build" without naming a topic. For Android Gradle Plugin, AGP modules, variants, lint, R8, SDK configuration, or Android build performance, use gradle-android-dev. For Kotlin test design and framework patterns, use kotlin-testing. For Kotlin language/API design, use kotlin-coding. Avoids Android-specific guidance unless cross-referencing gradle-android-dev.
---

# Gradle Dev

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Engineer general Gradle builds: wrapper usage, build lifecycle, Kotlin DSL or Groovy DSL scripts, dependency management, version catalogs, task configuration, custom build logic, JVM/Kotlin/Java builds, testing/check tasks, CI commands, performance, and troubleshooting. Read bundled references on demand.

Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for Android Gradle Plugin (AGP) topics. Use [kotlin-testing](../kotlin-testing/SKILL.md) for Kotlin test design — this skill covers Gradle test task wiring only.

## Scope

Use this skill for general Gradle build work: wrapper usage, build lifecycle, Kotlin DSL or Groovy DSL build scripts, dependency management, version catalogs, task configuration, custom build logic, JVM/Kotlin/Java builds, testing/check tasks, CI commands, performance, and troubleshooting.

Use the companion [gradle-android-dev](../gradle-android-dev/SKILL.md) skill for Android Gradle Plugin (AGP) topics: `com.android.application`, `com.android.library`, `android {}`, SDK levels, variants, manifests/resources, R8, lint, Android Studio sync for Android projects, and Android-specific performance. This skill may explain general Gradle concepts that Android builds inherit, but it must not duplicate Android-specific rules.

## When NOT to Use

- Android Gradle Plugin, AGP variants, lint, R8, signing, or Android Studio sync — [gradle-android-dev](../gradle-android-dev/SKILL.md)
- Kotlin test design, Kotest/MockK patterns, property tests, or flaky-test triage — [kotlin-testing](../kotlin-testing/SKILL.md)
- Kotlin language/API design in source files — [kotlin-coding](../kotlin-coding/SKILL.md)

## Default workflow

1. Classify the request:
   - New build setup: choose plugins, project layout, wrapper, settings, repositories, dependencies, toolchains, and validation tasks.
   - Build review/refactor: inspect build boundaries, duplicate logic, dependency hygiene, task laziness, configuration-cache readiness, and CI commands.
   - Failure diagnosis: collect the exact command, Gradle version, JDK/toolchain, wrapper files, relevant `settings.gradle(.kts)`, `build.gradle(.kts)`, `gradle.properties`, version catalog, and the first/root stack-trace cause.
   - Performance issue: measure before editing, separate configuration time, dependency resolution time, compilation/test time, and packaging/publishing time.
   - Custom task/plugin work: design lazy, typed, incremental, cache-safe build logic and test it with TestKit when needed.
   - Android issue: switch to [gradle-android-dev](../gradle-android-dev/SKILL.md) after using this skill only for shared Gradle concepts.
2. Load only the needed references (see **Reference routing** below).
3. Prefer project-local truth over generic snippets. Preserve the existing DSL, plugin versions, repository policy, version catalog, and module structure unless the user asks to modernize them.
4. Make the smallest safe build change. Avoid broad `allprojects`, `subprojects`, `afterEvaluate`, eager task lookup, dynamic versions, hidden repository additions, and global mutable build state.
5. Validate with the wrapper. Prefer `./gradlew help` for configuration validation, then the smallest relevant task, then `./gradlew check` or CI-equivalent tasks.
6. Explain the Gradle-specific reason for changes: lifecycle phase, lazy provider, configuration/cache behavior, variant/attribute resolution, toolchain, or task graph impact.

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

## Tooling helper

This skill includes `scripts/gradle_project_check.sh`. Use it only when a local project is available and the user wants command discovery or checks run. Default mode is `--quick`.

```bash
scripts/gradle_project_check.sh --dry-run
scripts/gradle_project_check.sh --quick
scripts/gradle_project_check.sh --full
scripts/gradle_project_check.sh --perf
```

The script detects the wrapper, prints Gradle build files, lists likely plugins, and runs progressively stronger checks. It does not run external build scans automatically.

## Output patterns

When editing build files, return:

1. The files or snippets to change, using the existing DSL.
2. The reason each change belongs in that file or lifecycle phase.
3. The exact validation command.
4. Any compatibility assumption, such as Gradle, Kotlin Gradle plugin, JDK, or plugin version.

When debugging failures, return:

1. The likely layer: wrapper/JDK, settings/plugin resolution, dependency resolution, configuration, task graph, compilation, tests, packaging, publishing, or CI environment.
2. The root-cause line or minimal failing configuration.
3. The smallest fix.
4. A verification command and one deeper command if it still fails.

## Reference routing

| Task | Read |
|------|------|
| Wrapper, settings/build files, lifecycle, CLI, properties | [core-build-model.md](references/core-build-model.md) |
| Kotlin DSL, convention plugins, lazy providers, build logic | [kotlin-dsl-build-logic.md](references/kotlin-dsl-build-logic.md) |
| Repositories, catalogs, platforms, locking, dependency insight | [dependencies-versioning.md](references/dependencies-versioning.md) |
| Task creation, test tasks, JVM test suites, TestKit, CI | [tasks-testing-ci.md](references/tasks-testing-ci.md) |
| Configuration cache, build cache, profiling, failure playbooks | [performance-troubleshooting.md](references/performance-troubleshooting.md) |
| Kotlin/JVM plugin, source sets, compiler options, toolchains | [kotlin-gradle.md](references/kotlin-gradle.md) |
| Kotlin test design, frameworks, mocks, flakes | [kotlin-testing](../kotlin-testing/SKILL.md) |
| Kotlin language/API design | [kotlin-coding](../kotlin-coding/SKILL.md) |
| AGP, Android variants, lint, R8, signing | [gradle-android-dev](../gradle-android-dev/SKILL.md) |

## Companion skills

- Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for Android Gradle Plugin and Android build topics.
- Use [kotlin-coding](../kotlin-coding/SKILL.md) for Kotlin language/API/design work.
- Use [kotlin-testing](../kotlin-testing/SKILL.md) for Kotlin test design, test framework choices, mocks/fakes, coroutine tests, property tests, coverage, and flaky-test debugging.

## References

- [core-build-model.md](references/core-build-model.md): wrapper, settings/build files, lifecycle, CLI, properties, and basic triage.
- [kotlin-dsl-build-logic.md](references/kotlin-dsl-build-logic.md): Kotlin DSL, typed accessors, convention plugins, included builds, lazy providers, and custom build logic.
- [dependencies-versioning.md](references/dependencies-versioning.md): repositories, configurations, version catalogs, platforms/BOMs, constraints, dependency insight, locking, and verification.
- [tasks-testing-ci.md](references/tasks-testing-ci.md): task creation/configuration, test tasks, JVM test suites, custom task correctness, TestKit, and CI commands.
- [performance-troubleshooting.md](references/performance-troubleshooting.md): configuration cache, build cache, profiling, scans, daemon, parallelism, dependency-resolution cost, and failure playbooks.
- [kotlin-gradle.md](references/kotlin-gradle.md): Kotlin/JVM plugin, source sets, compiler options, toolchains, kapt/ksp boundaries, and Kotlin build diagnostics.
- [source-notes.md](references/source-notes.md): source synthesis, scope boundaries, and versioning policy.
