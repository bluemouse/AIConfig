# Android Gradle Troubleshooting

## Table of contents

1. Android Studio sync failures
2. SDK and JDK failures
3. Missing namespace or DSL errors
4. Dependency and duplicate class errors
5. Manifest/resource errors
6. Kotlin/Java compile errors
7. R8/dex/package errors
8. Signing errors

## 1. Android Studio sync failures

Triage:

1. Reproduce on the command line:

```bash
./gradlew help --stacktrace
```

2. Check Gradle, AGP, Kotlin plugin, JDK, and Android Studio compatibility.
3. Inspect `settings.gradle(.kts)` plugin management and repositories.
4. Inspect root/module build files for DSL/API errors.
5. If command line passes but IDE sync fails, check Android Studio version, Gradle JDK setting, and IDE caches only after build files are validated.

## 2. SDK and JDK failures

Symptoms:

- Missing compile SDK package.
- Unsupported Gradle JVM.
- AGP requires a newer JDK.
- Kotlin/JVM target mismatch.

Commands:

```bash
./gradlew --version
./gradlew :app:assembleDebug --stacktrace
```

Fixes:

- Install the required Android SDK platform/build tools.
- Set Gradle JDK compatible with AGP.
- Use Java/Kotlin toolchains through `gradle-dev` for compile/test tasks.
- Align Kotlin `jvmTarget` and Java compatibility when explicitly configured.

## 3. Missing namespace or DSL errors

If AGP reports missing namespace:

```kotlin
android {
    namespace = "com.example.module"
}
```

Rules:

- Add namespace per Android module.
- Do not set app `applicationId` in libraries.
- Do not rely on manifest package for namespace in modern builds.

If a DSL property is unresolved:

- Verify the Android plugin is applied in that module.
- Verify Kotlin vs Groovy DSL syntax.
- Verify the API exists in the project AGP version.
- Check if the block belongs under `android`, `androidComponents`, `lint`, `packaging`, or `defaultConfig`.

## 4. Dependency and duplicate class errors

Commands:

```bash
./gradlew :app:dependencyInsight --dependency <artifact-or-module> --configuration debugRuntimeClasspath
./gradlew :app:dependencies --configuration debugRuntimeClasspath
```

Fixes:

- Align dependency families with BOMs/platforms where available.
- Remove stale direct dependencies.
- Add narrow excludes only when you know which transitive edge is wrong.
- Check variant-specific configurations (`debugRuntimeClasspath`, `releaseRuntimeClasspath`, flavor variants).
- Use `gradle-dev` for repository, catalog, locking, and dependency verification rules.

## 5. Manifest/resource errors

Manifest merge failures:

- Inspect the merge report for the failing variant.
- Check `src/main`, build-type, flavor, and variant manifests.
- Fix the owning manifest; avoid broad `tools:replace` unless intentionally overriding.

Resource failures:

- Check resource name/type conflicts.
- Check source-set overlays for the failing variant.
- Check generated resources and task dependencies.
- Validate with the specific process/merge task if shown in the failure.

## 6. Kotlin/Java compile errors

Use `kotlin-coding` for source-language fixes. Android build triage:

- Confirm the failing variant/task.
- Check generated source availability.
- Check Java/Kotlin source directories.
- Check KSP/kapt generated sources and processor dependencies.
- Check toolchain/target compatibility.

Commands:

```bash
./gradlew :app:compileDebugKotlin --stacktrace
./gradlew :app:compileDebugJavaWithJavac --stacktrace
```

Task names vary by AGP/Kotlin version and variant; use `./gradlew :app:tasks --all` when unsure.

## 7. R8/dex/package errors

R8/dex symptoms:

- Missing classes only in release.
- Duplicate classes.
- Minification warnings/errors.
- Method count or desugaring issues.

Fixes:

- Validate release classpath with `dependencyInsight`.
- Add narrow keep rules for reflection/serialization/JNI/service loaders.
- Prefer library consumer rules for libraries.
- Do not disable minification as the final fix unless release policy allows it.
- Check mapping and R8 diagnostics for removed/renamed classes.

## 8. Signing errors

Fixes:

- Keep keystore path/passwords out of committed build files.
- Use providers reading local Gradle properties or environment variables.
- Validate release assemble/bundle tasks.
- Ensure CI secrets are present only in release jobs that need them.
