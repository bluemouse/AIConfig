# Variants, Source Sets, and Dependencies

## Table of contents

1. Build types
2. Product flavors
3. Variant-aware logic
4. Source-set overlays
5. Android dependencies
6. Dependency diagnostics

## 1. Build types

Common build types:

```kotlin
android {
    buildTypes {
        debug {
            applicationIdSuffix = ".debug"
            isDebuggable = true
        }
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

Rules:

- Keep debug behavior debug-only.
- Validate release builds whenever changing minification, resources, manifests, signing, or dependencies.
- Do not disable minification only to hide R8 failures; fix rules or code when release behavior requires minification.

## 2. Product flavors

Example:

```kotlin
android {
    flavorDimensions += "environment"
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
        }
        create("prod") {
            dimension = "environment"
        }
    }
}
```

Rules:

- Define `flavorDimensions` explicitly when using flavors.
- Keep flavor count minimal; variants multiply across flavor dimensions and build types.
- Prefer runtime/server configuration over build flavors when behavior can be data-driven safely.
- Use flavor-specific dependencies only when the code/resource boundary genuinely differs.

## 3. Variant-aware logic

Use `androidComponents` for modern variant-aware build logic:

```kotlin
androidComponents {
    beforeVariants(selector().withBuildType("debug")) { variantBuilder ->
        // Disable or adjust variants only when there is a clear build policy.
    }

    onVariants(selector().withBuildType("release")) { variant ->
        // Register variant-specific generated sources/tasks through providers.
    }
}
```

Rules:

- Prefer selectors over iterating every variant.
- Avoid eager task creation for every variant.
- Do not use legacy variant APIs for new code if an Android Components API exists.
- Do not disable variants that CI, publishing, tests, or developers still need.

## 4. Source-set overlays

Common source sets:

```text
src/main
src/debug
src/release
src/dev
src/prod
src/devDebug
src/androidTest
src/test
```

Rules:

- More specific variant source sets override/augment less specific ones.
- Keep the same package names unless variant-specific package changes are intentional.
- Avoid duplicating large classes/resources across source sets; prefer small variant-specific adapters/configuration.
- Put test fixtures or fake implementations in test source sets, not production source sets.

## 5. Android dependencies

Common scopes:

```kotlin
dependencies {
    implementation(libs.androidx.core.ktx)
    debugImplementation(libs.leakcanary.android)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.test.ext.junit)
}
```

Rules:

- Use `implementation` for module internals.
- Use `api` only in Android libraries when consumers compile against exposed dependency types.
- Use `debugImplementation` for debug-only tooling.
- Use `testImplementation` for local JVM unit tests.
- Use `androidTestImplementation` for instrumentation tests.
- Keep versioning/repository policy in `gradle-dev` guidance and project catalogs.

## 6. Dependency diagnostics

Commands:

```bash
./gradlew :app:dependencies --configuration debugRuntimeClasspath
./gradlew :app:dependencyInsight --dependency <name> --configuration debugRuntimeClasspath
./gradlew :app:dependencyInsight --dependency <name> --configuration releaseRuntimeClasspath
```

Triage:

- Duplicate class errors: find the two artifacts providing the class, then remove/align/exclude narrowly.
- Missing class at runtime: check runtime classpath for the requested variant, not just compile classpath.
- Flavor-only issue: inspect the specific variant configuration.
- AndroidX/legacy support conflict: align dependency families and remove stale transitive dependencies.
