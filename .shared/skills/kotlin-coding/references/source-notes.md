# Source Notes and Scope Decisions

This skill synthesizes Kotlin language, tooling, and best-practice guidance from the requested source set while excluding Android, Kotlin Multiplatform, Kotlin/Native, Kotlin/JS/Web, Compose, Ktor/backend, and platform-specific architecture.

## Sources considered

Requested skill repositories:

- HoangNguyen0403/agent-skills-standard: `skills/kotlin/kotlin-language` and `skills/kotlin/kotlin-best-practices` were requested. The repository listing also shows sibling Kotlin skills for coroutines and tooling. The synthesized skill uses the same separation of concerns: language grammar, best practices, tooling, and validation flow.
- Jeffallan/claude-skills: `skills/kotlin-specialist` was read where available. Generic Kotlin patterns retained: sealed state modeling, null safety, scope functions, coroutine structured-concurrency cautions, detekt/ktlint validation, KDoc, explicit API mode, and output with implementation plus tests. Platform-specific content was removed.
- affaan-m/ECC: `skills/kotlin-patterns` was requested. The public repository describes ECC as a skills/rules harness and lists Kotlin reviewer/build-resolver coverage; this skill keeps the pattern-oriented review/build-debugging intent but avoids Android/KMP specifics.

Kotlin documentation:

- Kotlin docs home and language guide pages: basic syntax, packages/imports, functions, properties, classes, inheritance, interfaces, generics, extensions, data classes, sealed classes, enum classes, object declarations, inline/value classes, lambdas, scope functions, null safety, exceptions, collections, sequences, command-line compiler, Gradle configuration, JUnit/kotlin.test testing, coding conventions, and standard-library API overview.
- Standard-library API overview: core idioms, higher-order functions, collection operations, sequences, strings, JDK extensions, and common utility packages.

Best-practice article:

- Jim Hamilton, "Best Practices in Kotlin": consistency, style guide highlights, identifiers, extensions, operator precedence caution, null safety, final/open behavior, overriding rules, numeric/equality considerations, string templates, collections, class types, error handling, concurrency/coroutines, data integrity, stateless execution, encapsulation, type aliases, and scope functions.

## Scope decisions

- Keep plain Kotlin/JVM Gradle and `kotlinc` because they are core program-development tooling.
- Include coroutines only as language/library-level concurrency guidance, not as Android, server, KMP, or reactive architecture guidance.
- Include Java interop only where it affects plain Kotlin/JVM correctness: platform types, arrays, `Optional`, annotations, and API shape.
- Do not include Ktor, Spring, Android, Compose, KMP source sets, Kotlin/Native memory model, Kotlin/JS, browser, WebAssembly, backend deployment, or framework architecture.
- Prefer progressive references instead of one large `SKILL.md` so the active model can load only the topic needed.
- Test design, frameworks, mocks, property tests, coverage, and flaky-test triage are owned by the companion [kotlin-testing](../kotlin-testing/SKILL.md) skill; [testing-debugging.md](testing-debugging.md) covers compiler/runtime/performance debugging only.
- Gradle build engineering is owned by [gradle-dev](../gradle-dev/SKILL.md); [tooling.md](tooling.md) covers project layout, `kotlinc`, and consumer compiler/lint commands.
