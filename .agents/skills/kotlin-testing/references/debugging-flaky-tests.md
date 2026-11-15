# Debugging Failing and Flaky Kotlin Tests

## Table of contents

1. First response to a failing test
2. Failure categories
3. Flake isolation
4. Common Kotlin/JVM causes
5. Stabilization checklist

## 1. First response to a failing test

1. Copy the exact command, test name, exception, assertion message, and first project-code frame.
2. Re-run only the failing test:

```bash
./gradlew test --tests "com.example.UserServiceTest"
./gradlew test --tests "com.example.UserServiceTest.loads user"
```

3. Re-run with diagnostics:

```bash
./gradlew test --info --stacktrace
```

4. If it passes alone but fails in suite, suspect shared state, order dependence, parallel execution, time, or resource conflict.
5. Add or strengthen the regression assertion before changing production code when the failure is a real bug.

## 2. Failure categories

| Symptom | Likely cause | First fix |
|---|---|---|
| Assertion mismatch | wrong expectation or behavior regression | inspect contract, add boundary case |
| `NullPointerException` | platform type, `!!`, setup omission | remove unsafe null path, initialize fixture |
| `UninitializedPropertyAccessException` | `lateinit` setup not run or shared incorrectly | local fixture or `beforeEach` fix |
| `ClassCastException` | unsafe `as`, wrong generic fixture | correct type model or use `as?` branch |
| MockK missing call | subject did not call collaborator or stub mismatch | verify argument equality and code path |
| MockK unexpected call | shared mock or overly strict verification | clear mocks or verify only contract calls |
| Timeout | deadlock, hard-coded dispatcher, real delay | use `runTest`, injected dispatcher, virtual time |
| Order-dependent failure | global mutable state or non-isolated fixture | reset state, remove globals, isolate tests |

## 3. Flake isolation

Repetition commands:

```bash
for i in {1..20}; do ./gradlew test --tests "com.example.FlakyTest" || break; done
```

Isolation steps:

1. Run the test alone.
2. Run the class.
3. Run the package/module.
4. Run with parallelism disabled if configured.
5. Randomize or change test order if the framework supports it.
6. Add logging around time, thread, seed, temporary paths, and shared resources.

## 4. Common Kotlin/JVM causes

- Top-level `object` state survives across tests.
- Mutable companion object fields used as caches.
- `lateinit` fixtures shared across nested tests.
- `MutableList` or `MutableMap` fixture reused between tests.
- Test modifies a list passed into production code; production keeps the mutable reference.
- Equality assumptions differ between data classes, arrays, and collections.
- `Sequence` consumed once but asserted twice.
- Coroutine launched in a scope not owned by `runTest`.
- Dispatcher hard-coded to `Dispatchers.IO`/`Default` in code under test.
- Random UUID/time generated inside production without injectable seam.
- Temporary files/directories use fixed names.

## 5. Stabilization checklist

- Replace wall-clock time with injected `Clock` or test scheduler.
- Replace random IDs with injected generator or fixed seed.
- Replace global mutable objects with per-test instances.
- Copy mutable inputs at construction if immutability is part of the contract.
- Own and cancel all coroutine jobs/collectors.
- Reset mocks/fakes before each test.
- Use unique temporary directories/files.
- Avoid broad retries; fix root cause and keep a regression test.
