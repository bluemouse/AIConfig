---
name: kotlin-coding
description: Write, review, refactor, debug, and explain plain Kotlin/JVM language code, standard-library APIs, idioms, coroutines, and kotlinc workflows. Use when implementing Kotlin classes or functions, reviewing Kotlin diffs, fixing compiler or runtime errors, choosing stdlib APIs, or improving null-safety and type modeling — even if the user says "Kotlin help" without naming a topic. For test design, frameworks, mocks, property tests, coverage, or flaky-test triage, use kotlin-testing. For Gradle build files, version catalogs, task wiring, CI, or build cache, use gradle-dev. For Android Gradle Plugin builds, use gradle-android-dev. Excludes Android, KMP, Kotlin/Native, Kotlin/JS/Web, Compose, Ktor/backend, and platform-specific architecture.
---

# Kotlin Coding

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` and `scripts/` from that directory.

Write and review plain Kotlin/JVM code: language semantics, standard-library APIs, idioms, coroutines-as-language, `kotlinc`, compiler/runtime debugging, and maintainability. Read bundled references on demand — do not load all reference files unless the task requires them.

For test design, framework choice, mocks/fakes, coroutine tests, property tests, coverage, and flaky-test triage, use [kotlin-testing](../kotlin-testing/SKILL.md). That skill supersedes test-design content formerly in [testing-debugging.md](references/testing-debugging.md).

## Scope

Use this skill for plain Kotlin programming: language semantics, standard-library APIs, Kotlin/JVM command-line compilation, code review, refactoring, performance, and maintainability.

Do not provide Android, KMP, Kotlin/Native, Kotlin/JS/Web, Compose, Ktor, server/backend architecture, or platform-specific guidance. When a user supplies such code, still help with generic Kotlin correctness, syntax, style, and APIs, but avoid platform recommendations and defer platform build or test work to the appropriate companion skill.

## When NOT to Use

- Kotlin test design, Kotest/MockK setup, property tests, Kover, or flaky-test triage — [kotlin-testing](../kotlin-testing/SKILL.md)
- Gradle build engineering, version catalogs, task wiring, CI, or build/configuration cache — [gradle-dev](../gradle-dev/SKILL.md)
- Android Gradle Plugin, AGP variants, lint, R8, or Android Studio sync — [gradle-android-dev](../gradle-android-dev/SKILL.md)

## Default workflow

1. Classify the request:
   - New implementation or refactor: design the public API first; add a minimal regression test or hand off to [kotlin-testing](../kotlin-testing/SKILL.md) for full test strategy.
   - Code review: inspect correctness, nullability, type modeling, mutability, API boundaries, and performance.
   - Build/debug issue: identify the layer — compiler, runtime, or Gradle/build. For Gradle/build failures, use [gradle-dev](../gradle-dev/SKILL.md); for test failures, use [kotlin-testing](../kotlin-testing/SKILL.md).
   - Explanation: answer with language semantics and standard-library behavior.
2. Load only the references needed (see **Reference routing** below).
3. Prefer a small, type-safe design over clever abstraction. Use `val`, immutable public APIs, explicit domain names, and exhaustiveness over nullable or stringly typed state.
4. Produce code that compiles as-is when possible. Include imports, file/package context, and minimal `kotlinc` or compile commands when relevant.
5. Validate with the strongest available command. Prefer project wrappers: `./gradlew compileKotlin`, `./gradlew check`, then configured `ktlintCheck` or `detekt`. For small standalone files, use `kotlinc file.kt -include-runtime -d app.jar && java -jar app.jar`.
6. Explain any Kotlin-specific tradeoff briefly: nullability, variance, lazy vs eager collections, sealed hierarchy, coroutine cancellation, value class use, or Java interop boundary.

## Task patterns

### Implementing Kotlin code

- Start with the public shape: data classes, sealed result types, interfaces, extension functions, or top-level functions.
- Decide whether errors are exceptional (`throw`) or part of normal control flow (`sealed interface`, nullable return, or `Result`).
- When tests are in scope, use [kotlin-testing](../kotlin-testing/SKILL.md) for contract matrices, framework choice, and deterministic seams.
- Avoid framework assumptions. Keep examples as plain Kotlin/JVM unless the user explicitly supplies another context.

### Reviewing Kotlin code

Check in this order:

1. Does it compile, and are imports complete?
2. Are nullability and smart casts correct without unsafe `!!`?
3. Are state and errors modeled explicitly with `data class`, `data object`, `enum`, `sealed class/interface`, or `Result` where appropriate?
4. Are public APIs immutable, minimal, named clearly, and documented with KDoc when public?
5. Are collections, sequences, strings, and coroutines used efficiently for the actual input size and execution model?
6. Are tests meaningful and deterministic? If not, route test work to [kotlin-testing](../kotlin-testing/SKILL.md).

### Debugging Kotlin failures

- First identify the layer: syntax/type checker, Gradle configuration, test failure, runtime exception, or coroutine/concurrency issue.
- Gradle/build issues → [gradle-dev](../gradle-dev/SKILL.md). Test design or assertion failures → [kotlin-testing](../kotlin-testing/SKILL.md).
- Reduce to the smallest failing command and code path.
- For compiler errors, explain the type or grammar rule before proposing a fix.
- For runtime errors, preserve the original stack-trace cause and fix the invariant rather than suppressing the exception.

## Tooling helper

This skill includes `scripts/kotlin_project_check.sh`. Use it only when a local project is available and the user wants checks run. It detects Gradle wrappers, prints or runs likely compile/test/lint tasks, and falls back to `kotlinc` for simple standalone Kotlin files. Default mode is `--quick`.

```bash
scripts/kotlin_project_check.sh --dry-run
scripts/kotlin_project_check.sh --quick
scripts/kotlin_project_check.sh --full
```

## Kotlin code rules

- Prefer `val` over `var`; prefer immutable public collection types (`List`, `Set`, `Map`) over mutable ones.
- Avoid `!!`; use safe calls, Elvis, `requireNotNull`, `checkNotNull`, early returns, or sealed outcomes.
- Use `data class` for transparent immutable values, `data object` for singleton states, `enum` for fixed constants, and `sealed class/interface` for closed variants with exhaustive `when`.
- Use extension functions for behavior that is natural on a receiver but does not need access to private state. Remember extensions are statically resolved.
- Use `Sequence` only when lazy, multi-step processing avoids meaningful intermediate work. For small/simple collections, prefer eager collection operations.
- Use coroutines with structured concurrency only: no `GlobalScope`, no production `runBlocking`, propagate cancellation. For suspend test patterns, use [kotlin-testing](../kotlin-testing/SKILL.md).
- Use explicit return types on public functions and properties, recursive functions, complex expressions, and APIs where binary/source compatibility matters.
- Do not hide important work in scope functions. Choose `let`, `run`, `with`, `apply`, or `also` based on return value and receiver clarity.
- Do not expose mutable internals; copy or wrap as read-only views at API boundaries.
- Keep code formatted with official Kotlin style: four-space indentation, meaningful file names, related declarations together, and no needless `Util` files.

## Reference routing

| Task | Read |
|------|------|
| Language syntax, declarations, types, expressions | [language-grammar.md](references/language-grammar.md) |
| Standard-library packages, collections, sequences, strings | [stdlib-api.md](references/stdlib-api.md) |
| Idiomatic modeling, null safety, errors, coroutines, Java interop | [patterns.md](references/patterns.md) |
| Project layout, `kotlinc`, compiler options, ktlint/detekt, KDoc | [tooling.md](references/tooling.md) |
| Compiler/runtime/performance debugging | [testing-debugging.md](references/testing-debugging.md) |
| Style, correctness, efficiency, API design, review checklist | [best-practices.md](references/best-practices.md) |
| Test design, Kotest, MockK, coroutine tests, Kover, flakes | [kotlin-testing](../kotlin-testing/SKILL.md) |
| Gradle build files, catalogs, task wiring, CI, caches | [gradle-dev](../gradle-dev/SKILL.md) |
| AGP, Android variants, lint, R8, signing | [gradle-android-dev](../gradle-android-dev/SKILL.md) |

## Companion skills

- Use [kotlin-testing](../kotlin-testing/SKILL.md) for test design, framework choice, mocks/fakes, coroutine tests, property tests, coverage, and flaky-test debugging.
- Use [gradle-dev](../gradle-dev/SKILL.md) for Gradle build engineering, version catalogs, task wiring, CI, and build/configuration cache.
- Use [gradle-android-dev](../gradle-android-dev/SKILL.md) for Android Gradle Plugin and Android build topics.

## References

- [language-grammar.md](references/language-grammar.md): compact language grammar, declarations, types, expressions, modifiers, and semantic gotchas.
- [stdlib-api.md](references/stdlib-api.md): standard-library packages, collections, sequences, strings, ranges, scope functions, resources, and API selection.
- [patterns.md](references/patterns.md): idiomatic modeling, null safety, errors, extension functions, DSLs, coroutines, and Java interop boundaries.
- [tooling.md](references/tooling.md): project layout, `kotlinc`, compiler options, lint/static analysis, KDoc/Dokka, and dependency hygiene pointers.
- [testing-debugging.md](references/testing-debugging.md): compiler/runtime/performance debugging and verification commands (not test design).
- [best-practices.md](references/best-practices.md): style, correctness, efficiency, API design, concurrency, documentation, and review checklist.
- [source-notes.md](references/source-notes.md): source synthesis and scope notes.
