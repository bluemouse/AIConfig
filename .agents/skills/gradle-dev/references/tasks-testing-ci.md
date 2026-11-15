# Tasks, Testing, and CI

## Table of contents

1. Task configuration rules
2. Task dependencies and ordering
3. Incremental and cacheable task design
4. Test tasks
5. JVM test suites
6. CI command design
7. Build logic tests

## 1. Task configuration rules

Register and configure lazily:

```kotlin
val verifyDocs = tasks.register("verifyDocs") {
    group = "verification"
    description = "Checks generated documentation."
}

tasks.named("check") {
    dependsOn(verifyDocs)
}
```

Configure all tasks of a type lazily:

```kotlin
tasks.withType<Test>().configureEach {
    useJUnitPlatform()
}
```

Avoid:

```kotlin
tasks.create("x")
tasks.getByName("check")
tasks.withType<Test> { }
tasks.all { }
```

## 2. Task dependencies and ordering

- `dependsOn`: declares required work and can bring another task into the graph.
- `finalizedBy`: runs finalizer after the task when the finalized task runs.
- `mustRunAfter`: ordering constraint if both tasks are already in the graph.
- `shouldRunAfter`: soft ordering preference.

Rules:

- Use `dependsOn` for required outputs, not for cosmetic ordering.
- Use `builtBy` when a file collection is produced by a task.
- Do not wire every verification task into every build task; attach verification to `check` unless artifact production truly requires it.
- Avoid task graph mutation in `gradle.taskGraph.whenReady`; model relationships declaratively.

## 3. Incremental and cacheable task design

For custom tasks:

- Use typed properties: `Property<T>`, `ListProperty<T>`, `RegularFileProperty`, `DirectoryProperty`, `ConfigurableFileCollection`.
- Annotate inputs and outputs: `@Input`, `@InputFile`, `@InputFiles`, `@OutputFile`, `@OutputDirectory`, `@Classpath`, `@CompileClasspath`, `@PathSensitive`.
- Make output deterministic: stable ordering, stable timestamps/content, no ambient environment unless declared as input.
- Do not write outside declared outputs.
- Do not use static/global mutable state.
- Add `@CacheableTask` only after repeat runs are `UP-TO-DATE` and cache correctness is understood.

## 4. Test tasks

Common JVM test configuration:

```kotlin
tasks.test {
    useJUnitPlatform()
    testLogging {
        events("failed", "skipped")
        exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
    }
}
```

Useful commands:

```bash
./gradlew test
./gradlew :module:test
./gradlew test --tests "com.example.MyTest"
./gradlew test --tests "com.example.MyTest.specific behavior"
./gradlew test --info
./gradlew test --stacktrace
./gradlew test --continuous
```

Rules:

- Configure test framework once in a convention plugin when many modules share it.
- Avoid making all tests run on every compile/assemble task; attach them to `check`.
- Use test filters for local debugging, not as permanent CI filters unless the task is intentionally scoped.
- Do not over-tune `maxParallelForks` without measuring CPU, memory, and test isolation.
- For Kotlin test design, use [kotlin-testing](../../kotlin-testing/SKILL.md); this reference covers Gradle task wiring only.

## 5. JVM test suites

Gradle's JVM Test Suite plugin can model additional suites such as integration tests:

```kotlin
testing {
    suites {
        val integrationTest by registering(JvmTestSuite::class) {
            useJUnitJupiter()
            dependencies {
                implementation(project())
            }
        }
    }
}

tasks.named("check") {
    dependsOn(testing.suites.named("integrationTest"))
}
```

Use it when a project needs first-class suites with separate dependencies/tasks. For a small project, a custom `Test` task may be simpler.

## 6. CI command design

A generic CI build should use the wrapper and no daemon:

```bash
./gradlew --no-daemon clean check --stacktrace
```

Optimize by splitting tasks only when CI can parallelize jobs safely:

```bash
./gradlew --no-daemon compileTestKotlin --stacktrace
./gradlew --no-daemon test --stacktrace
./gradlew --no-daemon check --stacktrace
```

Rules:

- Use the same commands locally and in CI where possible.
- Cache Gradle User Home carefully; include Gradle version, OS, lockfiles, wrapper properties, build logic, and catalog files in cache keys.
- Do not cache `build/` directories blindly unless the CI cache policy and task inputs support it.
- Enable local build cache and configuration cache only after validating correctness and plugin compatibility.
- Publish test reports and build reports as CI artifacts.
- Keep failure logs focused: `--stacktrace` by default; `--info` only for deeper investigation.

## 7. Build logic tests

For build logic:

- Unit-test pure helper functions normally.
- Functional-test plugin behavior with Gradle TestKit.
- Use temporary project directories with minimal settings/build files.
- Assert task outcome (`SUCCESS`, `UP_TO_DATE`, `FROM_CACHE`, `FAILED`) and generated files.
- Test both successful configuration and expected misconfiguration errors.
- Test across Gradle versions only when the plugin claims broad compatibility.
