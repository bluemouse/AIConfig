# Kotlin Best Practices

Use this reference for code review, refactoring, maintainability, correctness, and efficiency guidance.

## Table of contents

1. Style and organization
2. Naming
3. Null safety
4. Immutability and encapsulation
5. Type modeling
6. API design
7. Collections and performance
8. Coroutines and concurrency
9. Exceptions and validation
10. Documentation and comments
11. Review checklist

## 1. Style and organization

- Follow official Kotlin style: four spaces, no tabs, Java-style braces, no unnecessary semicolons.
- Keep related declarations together. Do not sort class members alphabetically or purely by visibility.
- Class layout default: properties/init blocks, secondary constructors, methods, companion object. Keep nested classes near their use unless they are external-facing.
- Group overloads next to each other.
- Avoid meaningless file names like `Util.kt`, `Helpers.kt`, or `Extensions.kt` when a domain name is possible.
- Prefer top-level functions for cohesive stateless operations; do not force everything into classes.

## 2. Naming

- Names should explain domain intent, not implementation mechanics.
- Use nouns/noun phrases for classes and values (`PortRange`, `UserId`).
- Use verbs/verb phrases for actions (`parsePort`, `registerUser`).
- Use names that reveal mutation: `sort` mutates, `sorted` returns a copy; follow this convention in custom APIs.
- Avoid single-letter names except conventional local lambdas/math/generic contexts.
- Avoid generic names like `Manager`, `Wrapper`, `Data`, `Info`, and `Util` unless they are established domain terms.

## 3. Null safety

- Prefer non-null types by default.
- Use nullable types only for real absence.
- Convert platform/foreign nullability at boundaries.
- Use `?.`, `?:`, `let`, early returns, `requireNotNull`, or sealed results instead of `!!`.
- Replace multiple related nullable fields with a sealed state when only certain combinations are valid.
- Avoid storing nullable mutable state when a constructor argument, `lazy`, or state object can encode lifecycle.

## 4. Immutability and encapsulation

- Prefer `val` and immutable data classes.
- Keep mutable state private and expose read-only APIs.
- Copy mutable constructor inputs before storing them.
- Return snapshots or read-only views of collections.
- Use `private set` when a property should be publicly readable but internally mutable.
- Avoid hidden global mutable state in `object` declarations.

Example:

```kotlin
class Scoreboard(scores: List<Int>) {
    private val mutableScores = scores.toMutableList()

    val scores: List<Int>
        get() = mutableScores.toList()

    fun add(score: Int) {
        require(score >= 0)
        mutableScores += score
    }
}
```

## 5. Type modeling

- Use `data class` for values and DTO-like immutable data.
- Use `value class` for domain-specific wrappers around primitives/strings.
- Use `enum` for a fixed set of singleton constants.
- Use `sealed class/interface` for closed alternatives with different payloads or behavior.
- Use `data object` for singleton states in sealed hierarchies.
- Use `typealias` only for readability at local/module boundaries; it does not create a distinct type.
- Avoid boolean flag parameters when a named enum/sealed type is clearer.

## 6. API design

- Make invalid states unrepresentable where practical.
- Keep public function signatures small. Prefer named parameter objects only when parameters form a cohesive concept.
- Use named/default parameters instead of overloads when Kotlin callers are primary.
- Add overloads or `@JvmOverloads` only when Java callers need them.
- State public return types explicitly.
- Do not expose mutable implementation details.
- Avoid returning `Pair`/`Triple` from public APIs when a named data class clarifies meaning.
- Put validation at construction or boundary points.
- For library code, enable explicit API mode and document public contracts.

## 7. Collections and performance

- Use eager collections for normal small/medium data transformations.
- Use `Sequence` for large, lazy, or early-terminating pipelines.
- Avoid repeated list/string concatenation in loops.
- Prefer `buildList`, `buildMap`, `buildString`, `joinToString`, and mutable local accumulators when building results.
- Use `mapNotNull`, `sumOf`, `associateBy`, and `groupBy` directly instead of multi-pass equivalents.
- Know which operations throw: `first`, `single`, `reduce`, direct indexing.
- Prefer nullable variants for expected absence: `firstOrNull`, `singleOrNull`, `getOrNull`, `reduceOrNull`.
- Use `enumEntries<T>()` or `.entries` where available instead of repeated `values()`/`enumValues<T>()` calls.
- Measure before replacing readable code with low-level optimizations.

## 8. Coroutines and concurrency

- Keep coroutine use structured. Parent scopes own child jobs.
- Avoid `GlobalScope`.
- Avoid production `runBlocking` except at application boundaries.
- Do not catch and suppress `CancellationException`.
- Use immutable data sharing where possible.
- Keep synchronized/locked sections small and never call unknown user code while holding a lock.
- Inject dispatchers/scopes for testable asynchronous code.
- Use `StateFlow`/`SharedFlow` only when the project already uses coroutines and reactive streams are appropriate; otherwise use simple callbacks or synchronous APIs.

## 9. Exceptions and validation

- Use `require` for invalid caller arguments.
- Use `check` for invalid object state.
- Use `error` for impossible code paths.
- Use `toXOrNull` parsing APIs for expected invalid text.
- Preserve causes when wrapping exceptions.
- Do not return `null` and throw for the same failure mode in one API family.
- For expected domain failures with details, use a sealed result instead of broad exceptions.

## 10. Documentation and comments

- Use KDoc for public APIs with non-obvious contracts, failure modes, units, ownership, threading, or performance expectations.
- Comment why something is done, not what the syntax already says.
- Keep comments synchronized when refactoring. Stale comments are worse than absent comments.
- Prefer clearer names and smaller functions over explanatory comments for ordinary logic.

## 11. Review checklist

For any Kotlin code review, answer:

1. Does it compile with the declared Kotlin version?
2. Is the scope plain Kotlin, not accidentally platform-specific?
3. Are public APIs explicit, small, and immutable by default?
4. Are nullability and Java/platform types handled at boundaries?
5. Are sealed/enum/data/value/object constructs chosen appropriately?
6. Are collections/sequences chosen for the actual data size and laziness needs?
7. Are errors represented consistently?
8. Are coroutines structured and cancellable when used?
9. Are tests present for success, failure, and boundaries?
10. Can the code be understood by another developer without hidden conventions?
