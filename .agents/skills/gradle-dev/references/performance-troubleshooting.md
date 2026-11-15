# Performance and Troubleshooting

## Table of contents

1. Measurement-first workflow
2. Configuration cache
3. Build cache
4. Parallelism, daemon, and memory
5. Dependency-resolution performance
6. Common anti-patterns
7. Failure playbooks

## 1. Measurement-first workflow

Do not guess. Classify the slow work:

```bash
./gradlew help --profile
./gradlew build --dry-run
./gradlew build --stacktrace
./gradlew build --info
```

Use build scans only with user/project consent:

```bash
./gradlew build --scan
```

Look for:

- Configuration time: slow `help`, slow IDE sync, lots of eagerly configured tasks.
- Dependency resolution: slow metadata/download, dynamic versions, too many repositories, no caching, changing modules.
- Compilation/test execution: source changes, annotation processing, fork count, non-incremental tasks, test isolation.
- Packaging/publishing: archive creation, signing, remote repository latency.

## 2. Configuration cache

Configuration cache avoids re-running the configuration phase when the requested task graph and configuration inputs have not changed.

Trial command:

```bash
./gradlew help --configuration-cache --configuration-cache-problems=warn
./gradlew test --configuration-cache --configuration-cache-problems=warn
```

Checked-in property after compatibility is acceptable:

```properties
org.gradle.configuration-cache=true
```

Rules:

- Fix reported problems rather than suppressing them permanently.
- Avoid reading files, environment variables, system properties, or executing processes during configuration unless modeled through providers/value sources.
- Avoid storing non-serializable project/service/task objects in task state.
- Do not call `Configuration.resolve()` during configuration.
- Confirm the second run reuses the configuration cache.

## 3. Build cache

Build cache reuses task/artifact-transform outputs when inputs are unchanged.

Enable locally:

```properties
org.gradle.caching=true
```

Command-only trial:

```bash
./gradlew build --build-cache
```

Rules:

- First make repeat builds `UP-TO-DATE`; then expect useful cache hits.
- Verify custom tasks have complete inputs/outputs before marking cacheable.
- Remote cache push should normally be restricted to trusted CI builds.
- Do not cache tasks with undeclared network, clock, random, environment, or absolute-path dependencies.
- Use `--info` to inspect cache miss reasons for specific tasks.

## 4. Parallelism, daemon, and memory

Common project properties:

```properties
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8
```

Rules:

- Measure before and after enabling `org.gradle.parallel=true`; it helps independent projects/tasks and can hurt memory-constrained machines.
- The daemon improves local builds; CI often uses `--no-daemon` for predictable cleanup.
- Increase heap only when logs or profiling show memory pressure.
- Too much heap can reduce machine-level parallelism.

## 5. Dependency-resolution performance

Common causes:

- Dynamic versions or changing modules.
- Too many repositories or repositories in the wrong order.
- Repository misses due broad repository scope.
- Dependency substitution/composite builds that include too much work.
- Resolving configurations during configuration phase.

Commands:

```bash
./gradlew :module:dependencies --configuration compileClasspath
./gradlew :module:dependencyInsight --dependency <name> --configuration compileClasspath
```

Fixes:

- Use fixed versions and version catalogs.
- Centralize repositories and use content filters.
- Remove unused repositories and dependencies.
- Move resolution into task execution or model it as task inputs.

## 6. Common anti-patterns

Avoid:

- `allprojects` or `subprojects` blocks that eagerly configure every module.
- `afterEvaluate` for normal task/plugin wiring.
- `tasks.getByName`, `.get()`, `files(...).forEach` over generated outputs during configuration.
- Ad hoc `Exec` calls during configuration.
- Reading source/resource directories during configuration to calculate task inputs.
- Hidden repository/dependency injection in shared scripts.
- Root build files that contain every module's configuration.
- Build scripts that silently depend on user-local files.

## 7. Failure playbooks

### Plugin not found

1. Check plugin id and version.
2. Check `pluginManagement.repositories`.
3. Check version catalog plugin alias.
4. Check proxy/offline mode and repository credentials.
5. Run `./gradlew help --stacktrace`.

### Could not resolve dependency

1. Identify configuration.
2. Run `dependencyInsight` or `dependencies` for that configuration.
3. Check repositories and content filters.
4. Check version catalog alias, platform constraints, and lockfiles.
5. Avoid broad excludes; fix the coordinate/version/repository root cause.

### Unsupported class file or JVM target mismatch

1. Run `./gradlew --version`.
2. Inspect Java toolchain and Kotlin `jvmTarget`/compiler options.
3. Align Gradle runtime JDK, plugin compatibility, toolchain, and target bytecode.
4. Clean only if stale output is plausible; do not use `clean` as the primary fix.

### Task never runs or always runs

1. Check task graph with `--dry-run`.
2. Check `dependsOn`, `mustRunAfter`, `finalizedBy`, and `builtBy` wiring.
3. For always-running tasks, inspect undeclared outputs, changing inputs, `outputs.upToDateWhen { false }`, timestamps, random data, or environment reads.
4. Use `--info` for up-to-date and cache diagnostics.

### CI passes locally but fails remotely

1. Compare Gradle version, JDK, OS, environment variables, credentials, and repository access.
2. Check wrapper execution permissions.
3. Check dependency lock/verification metadata.
4. Check test parallelism and filesystem case sensitivity.
5. Reproduce with `--no-daemon --stacktrace` locally when possible.
