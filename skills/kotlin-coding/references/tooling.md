# Kotlin Tooling — non-obvious wiring rules

For Gradle build engineering — plugin wiring, version catalogs, task configuration, CI,
build cache — use [gradle-dev](../../gradle-dev/SKILL.md); for Kotlin Gradle plugin
specifics see [gradle-dev/references/kotlin-gradle.md](../../gradle-dev/references/kotlin-gradle.md).

## Toolchain rules

- Configure a Java toolchain (`jvmToolchain(n)`) rather than relying on the Gradle
  daemon JDK.
- Keep Kotlin Gradle plugin, stdlib, and compiler plugin versions aligned unless the
  project has an explicit compatibility reason.
- Do not add Android, KMP, JS, Native, Compose, or server plugins in this skill's scope.
- Avoid copying experimental `-X` flags without confirming project version and need;
  pin `languageVersion`/`apiVersion` only when supporting older consumers.
- `-Xjsr305=strict` makes Java nullability annotations stricter at Kotlin boundaries —
  enable when interop null-safety matters.
- `explicitApi()` for public library APIs; `allWarningsAsErrors` in CI once the codebase
  is warning-free.

## Command-line compiler (small repros and error isolation only)

```bash
kotlinc hello.kt -include-runtime -d hello.jar && java -jar hello.jar
```

For real projects, prefer Gradle so dependencies, source sets, and compiler options
are accurate.

## Dependency hygiene

- Prefer stdlib first; add dependencies only when they reduce real complexity.
- Keep dependencies out of core domain code when simple data classes/functions suffice.
- Keep one dominant assertion style per module — do not mix multiple test
  assertion/mocking styles in a small module.

## Local check script

The bundled helper runs likely verification commands:

```bash
scripts/kotlin_project_check.sh --dry-run
scripts/kotlin_project_check.sh --quick
scripts/kotlin_project_check.sh --full
```

Uses `./gradlew` when present, otherwise `gradle`/`kotlinc`; `--quick` (default) runs
compile/test/check, `--full` adds clean plus configured lint/static-analysis tasks.
Not a replacement for project-specific CI — a safe local first pass.
