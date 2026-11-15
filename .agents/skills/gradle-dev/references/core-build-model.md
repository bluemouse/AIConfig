# Core Gradle Build Model

## Table of contents

1. Project files and responsibilities
2. Wrapper, Gradle version, and Java runtime
3. Build lifecycle and task graph
4. CLI command selection
5. Properties and environment inputs
6. Multi-project structure
7. First-pass triage

## 1. Project files and responsibilities

A modern Gradle build is usually split by responsibility:

```text
project/
  settings.gradle.kts        # plugin repositories, dependency repositories, catalogs, included builds, project graph
  build.gradle.kts           # root conventions or shared defaults; avoid heavy logic here
  gradle.properties          # stable Gradle/project properties checked into source control
  gradle/libs.versions.toml  # dependency/plugin aliases and versions
  build-logic/               # included build for convention plugins in larger builds
  subproject/build.gradle.kts
  gradlew, gradlew.bat, gradle/wrapper/gradle-wrapper.properties
```

Guidelines:

- Put plugin repository policy in `pluginManagement { repositories { ... } }` in settings.
- Put dependency repository policy in `dependencyResolutionManagement { repositoriesMode.set(...) ; repositories { ... } }` in settings when the project uses centralized repositories.
- Keep module `build.gradle.kts` files declarative: apply convention plugins and declare module-specific dependencies/tasks only.
- Do not inject repositories from arbitrary subprojects; this makes dependency provenance and caching harder to reason about.
- Avoid `allprojects {}` and `subprojects {}` for new code. Prefer convention plugins that opt modules into shared behavior explicitly.

## 2. Wrapper, Gradle version, and Java runtime

Use the wrapper for all project commands:

```bash
./gradlew --version
./gradlew wrapper --gradle-version <version>
```

Rules:

- Commit `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.jar`, and `gradle/wrapper/gradle-wrapper.properties`.
- Do not edit `distributionUrl` casually. Upgrade with the `wrapper` task so metadata remains consistent.
- Distinguish the JVM that runs Gradle from Java toolchains used by compilation/tests.
- For reproducibility, configure toolchains in build logic instead of assuming developer `JAVA_HOME`.
- When a failure mentions unsupported class file version, toolchain, daemon JVM, or plugin compatibility, collect `./gradlew --version` first.

## 3. Build lifecycle and task graph

Gradle has three conceptual phases:

1. Initialization: read settings, determine included builds and projects.
2. Configuration: evaluate build logic and configure tasks for the requested graph.
3. Execution: run selected tasks and dependencies.

Diagnostic implications:

- Errors before task names appear are often settings/plugin/repository/version-catalog issues.
- Errors while calculating tasks are configuration or task graph issues.
- Errors in a named task are execution issues; inspect that task's inputs, outputs, toolchain, dependencies, and worker process.
- Lazy APIs help avoid configuring unrelated tasks during configuration.
- Configuration cache stores the configured task graph for a specific invocation; build cache stores task/artifact outputs.

## 4. CLI command selection

Start narrow, then widen:

```bash
./gradlew help                         # evaluates configuration with minimal execution
./gradlew tasks --all                  # discovers task names
./gradlew :module:tasks --all          # module-specific discovery
./gradlew :module:compileKotlin        # Kotlin compilation only when present
./gradlew :module:test --tests "pkg.ClassName" --stacktrace
./gradlew check --stacktrace
```

Use logging levels deliberately:

```bash
./gradlew failingTask --stacktrace
./gradlew failingTask --info
./gradlew failingTask --debug          # noisy; use only when needed
```

Use `--dry-run` to inspect a task graph without executing tasks:

```bash
./gradlew build --dry-run
```

Use `--continue` only when you want to collect multiple independent failures; do not use it to hide a root cause.

## 5. Properties and environment inputs

Common property locations:

- Checked-in project properties: `<project>/gradle.properties`.
- User-local properties: `~/.gradle/gradle.properties`.
- Command line: `-Pname=value` for project properties, `-Dname=value` for system properties.
- Environment variables: CI secrets, credentials, paths, `JAVA_HOME`.

Rules:

- Do not commit secrets or user-local paths.
- Prefer Gradle `Provider` APIs for environment values read during configuration.
- Be careful when adding environment/property reads if configuration cache is enabled; they become cache inputs.
- For credentials, use Gradle credentials/password providers or CI secret injection, not string literals.

## 6. Multi-project structure

Healthy multi-project builds have clear ownership:

- `settings.gradle.kts` declares project inclusion and logical names.
- Convention plugins in `build-logic` or `buildSrc` encode shared behavior.
- Each subproject applies only the conventions it needs.
- Dependencies flow through explicit project dependencies, published modules, or included builds.
- Tests and checks can run per module or aggregated at the root.

Prefer included builds for reusable build logic in large builds because they have explicit boundaries and can be shared/tested independently. `buildSrc` is convenient but changes to it can invalidate configuration for the whole build.

## 7. First-pass triage

Ask or inspect these before proposing broad changes:

```bash
./gradlew --version
./gradlew help --stacktrace
./gradlew tasks --all
```

Then inspect:

- `settings.gradle(.kts)` for plugin/dependency repositories, project inclusion, included builds, and catalogs.
- Root and failing module `build.gradle(.kts)` files for plugins, dependencies, task configuration, and toolchains.
- `gradle.properties` for cache, parallelism, JVM args, Kotlin settings, and feature flags.
- `gradle/libs.versions.toml` for aliases, versions, bundles, plugin ids, and version references.
- The first failure cause in the stack trace, not the last repeated failure summary.
