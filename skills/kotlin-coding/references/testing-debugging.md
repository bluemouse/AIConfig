# Kotlin Debugging

Use this reference for debugging compiler errors, runtime exceptions, performance issues, and verification commands.

For test design, framework choice, Kotest/MockK patterns, coroutine tests, property tests, coverage, and flaky-test triage, use [kotlin-testing](../../kotlin-testing/SKILL.md). That skill owns all test-design content; this reference covers debugging production Kotlin and choosing verification commands.

## Table of contents

1. Debug compiler/type errors
2. Debug Gradle/build errors
3. Debug runtime errors
4. Debug performance issues
5. Verification checklist

## 1. Debug compiler/type errors

Approach:

1. Copy the exact error and line.
2. Identify the rule: nullability, type inference, overload resolution, variance, smart cast, visibility, or grammar.
3. Reduce complex expressions into named `val`s to inspect inferred types.
4. Add explicit types at API boundaries or recursive/complex expression functions.
5. Fix the type model rather than casting around it.

Common fixes:

- Nullable receiver error: use `?.`, `?: return`, `?: throw`, or `requireNotNull`.
- Smart cast impossible: copy mutable/open property to local `val`.
- Type mismatch between `Int` and `Long`: convert explicitly.
- Invariance error with `MutableList`: change API to read-only `List<out T>` where mutation is not needed.
- `when` not exhaustive: handle all enum/sealed cases or return a value only when exhaustive.
- Ambiguous `it`: name lambda parameters.

## 2. Debug Gradle/build errors

For build-file edits, plugin wiring, version catalogs, task configuration, CI, or cache behavior, use [gradle-dev](../../gradle-dev/SKILL.md).

Local triage commands:

```bash
./gradlew failingTask --stacktrace
./gradlew tasks --all
./gradlew dependencyInsight --dependency kotlin-stdlib --configuration runtimeClasspath
```

Quick checklist before handing off to [gradle-dev](../../gradle-dev/SKILL.md):

- Is the Kotlin plugin applied to the right module?
- Are sources in `src/main/kotlin` and tests in `src/test/kotlin`?
- Is the JDK/toolchain compatible with the configured `jvmTarget`?
- Are plugin versions compatible with the Gradle wrapper?
- Are repositories declared where dependencies resolve?

Do not patch broad build settings blindly. Change the smallest setting that explains the failure.

## 3. Debug runtime errors

Stack-trace process:

1. Find the first project-code frame after the exception type/message.
2. Preserve the root cause; do not replace it with a generic exception.
3. Identify the violated invariant.
4. Add a regression test reproducing the failure — use [kotlin-testing](../../kotlin-testing/SKILL.md) for test design.
5. Fix the invariant at construction/input boundary when possible.

Kotlin-specific runtime failures:

- `NullPointerException`: check Java platform types, `!!`, unsafe casts, and initialization order.
- `UninitializedPropertyAccessException`: `lateinit` read before initialization; prefer constructor injection or setup fix.
- `ClassCastException`: replace `as` with `as?` or correct the generic/type model.
- `IllegalStateException` from `check`: fix state transition or calling order.
- `NoSuchElementException`: replace `first`/`single` with nullable variants if absence is expected.

## 4. Debug performance issues

Process:

1. Establish an input size and measurable symptom.
2. Add a focused benchmark or timing harness only after correctness tests pass.
3. Look for accidental allocations: repeated `+` on lists/strings, unnecessary `map` before `sum`, converting sequences/lists repeatedly, defensive copies in tight loops.
4. Compare eager collections and sequences with realistic data.
5. Prefer algorithmic improvements over micro-optimizations.

Kotlin-specific suspects:

- `enumValues<T>()` creates a new array; prefer `enumEntries<T>()` where available.
- `List + item` in a loop copies repeatedly.
- Boxing from nullable primitives (`Int?`) or generic numeric collections may matter in hot paths.
- Capturing lambdas and scope functions can allocate in some contexts; measure before changing readable code.
- Deep chains can be harder to debug; break them at meaningful names.

## 5. Verification checklist

Before returning Kotlin code or a fix, verify as much as possible:

- Code has imports and package context when needed.
- Public APIs have explicit return types.
- Nullability is intentional; no unjustified `!!`.
- A regression test covers the fix when debugging a runtime bug — use [kotlin-testing](../../kotlin-testing/SKILL.md) for test design.
- Build snippets use plain Kotlin/JVM only unless user supplied a platform context.
- Commands are project-appropriate:

```bash
./gradlew compileKotlin
./gradlew check
./gradlew ktlintCheck
./gradlew detekt
```

If commands cannot be run, state what should be run and why.
