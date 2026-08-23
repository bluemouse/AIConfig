# Kotlin Patterns

Use this reference for idiomatic Kotlin modeling, null handling, error design, extension functions, DSLs, coroutines, and interop boundaries.

## Table of contents

1. Model domain states explicitly
2. Null handling patterns
3. Error handling patterns
4. Extension function patterns
5. Value/data/enum/object patterns
6. Collection and sequence patterns
7. DSL and builder patterns
8. Coroutine patterns
9. Java interop boundary patterns
10. Anti-patterns

## 1. Model domain states explicitly

Prefer closed, named states over nullable strings, integer codes, or parallel booleans.

```kotlin
sealed interface LoadState<out T> {
    data object Loading : LoadState<Nothing>
    data class Loaded<T>(val value: T) : LoadState<T>
    data class Failed(val reason: String, val cause: Throwable? = null) : LoadState<Nothing>
}

fun <T> LoadState<T>.valueOrNull(): T? = when (this) {
    is LoadState.Loading -> null
    is LoadState.Loaded -> value
    is LoadState.Failed -> null
}
```

Use this pattern when:

- The set of alternatives is finite and known.
- Callers must handle all cases.
- Adding a new case should trigger compiler errors at `when` expressions.

Avoid `else` on sealed `when` expressions unless the hierarchy is intentionally open or interop forces it.

## 2. Null handling patterns

Expected absence:

```kotlin
fun findUser(id: UserId): User? = users[id]

val displayName = findUser(id)?.displayName ?: "unknown"
```

Required input:

```kotlin
fun rename(id: UserId, name: String) {
    require(name.isNotBlank()) { "name must not be blank" }
    // ...
}
```

Required state:

```kotlin
check(connection.isOpen) { "connection is closed" }
```

Required nullable value:

```kotlin
val token = requireNotNull(config.token) { "token must be configured" }
```

Early-return null handling:

```kotlin
fun parseLine(line: String): Entry? {
    val (key, value) = line.split('=', limit = 2).takeIf { it.size == 2 } ?: return null
    return Entry(key.trim(), value.trim())
}
```

Rules:

- Do not use `!!` as a shortcut. Use it only when the non-null guarantee is external, documented, and impossible to encode better.
- Prefer `?.let { }` for short nullable transforms; prefer `if (x == null) return` for multi-step logic.
- Avoid nullable fields when a sealed state, constructor requirement, or split type would be clearer.

## 3. Error handling patterns

Use exceptions for exceptional failures or invariant violations:

```kotlin
fun percentage(part: Int, total: Int): Int {
    require(total > 0) { "total must be positive" }
    return part * 100 / total
}
```

Use nullable return for simple expected absence:

```kotlin
fun parsePort(raw: String): Int? = raw.toIntOrNull()?.takeIf { it in 1..65535 }
```

Use sealed results for expected failure with information:

```kotlin
sealed interface PortParseResult {
    data class Valid(val port: Int) : PortParseResult
    data object Blank : PortParseResult
    data class Invalid(val raw: String) : PortParseResult
    data class OutOfRange(val value: Int) : PortParseResult
}
```

Use `Result<T>` for local pipelines or boundaries where Kotlin callers expect it:

```kotlin
fun readConfig(): Result<Config> = runCatching { parseConfig(loadText()) }
```

Rules:

- Do not swallow exceptions silently. Preserve the cause when wrapping.
- Use `runCatching` carefully; it catches broad `Throwable`. Re-throw cancellation exceptions in coroutine code.
- Keep public error behavior consistent across a module.

## 4. Extension function patterns

Good extension:

```kotlin
fun String.normalizedKey(): String = trim().lowercase()
```

Nullable receiver:

```kotlin
fun String?.orPlaceholder(): String = if (this.isNullOrBlank()) "-" else this
```

Rules:

- Use extensions when the operation reads naturally as receiver behavior and does not need private state.
- Keep extensions close to the type or close to the use site. Avoid a global `Extensions.kt` dumping ground.
- Remember static dispatch: an extension chosen for a `Base` reference will not switch to a `Derived` extension at runtime.
- A member with the same signature wins over an extension.

## 5. Value/data/enum/object patterns

Domain wrapper:

```kotlin
@JvmInline
value class UserId private constructor(val value: String) {
    companion object {
        fun parse(raw: String): UserId? = raw
            .trim()
            .takeIf { it.matches(Regex("[a-z0-9-]{3,64}")) }
            ?.let(::UserId)
    }
}
```

Transparent value:

```kotlin
data class Money(val cents: Long, val currency: Currency)
```

Singleton state:

```kotlin
data object EndOfInput
```

Fixed constant set:

```kotlin
enum class SortOrder { ASCENDING, DESCENDING }
```

Rules:

- Use `data class` for immutable values with meaningful structural equality.
- Use `value class` to prevent mixing raw strings/ints from different domains.
- Use `enum` when each value is a singleton constant. Use sealed classes when variants have different payloads or behavior.
- Use `object` for stateless singleton services only when global state and test replacement are not problems.

## 6. Collection and sequence patterns

Read-only public, mutable private:

```kotlin
class Registry {
    private val entriesById = mutableMapOf<UserId, Entry>()

    val entries: List<Entry>
        get() = entriesById.values.toList()

    fun register(entry: Entry) {
        entriesById[entry.id] = entry
    }
}
```

Large lazy pipeline:

```kotlin
fun firstMatchingLine(lines: Sequence<String>, needle: String): String? = lines
    .map { it.trim() }
    .filter { it.isNotEmpty() }
    .firstOrNull { needle in it }
```

Rules:

- Avoid exposing `MutableList`, `MutableMap`, or mutable iterators from public APIs.
- Use `toList()` or `toMap()` to snapshot data when returning results that should not change.
- Use `Sequence` for large or streaming data, multi-step transformation, and short-circuiting. Avoid it when a list pipeline is clearer and cheap.

## 7. DSL and builder patterns

Use a receiver lambda when the block configures one receiver.

```kotlin
class ReportBuilder {
    private val sections = mutableListOf<String>()

    fun section(title: String, body: String) {
        sections += "# $title\n$body"
    }

    fun build(): String = sections.joinToString("\n\n")
}

fun report(block: ReportBuilder.() -> Unit): String =
    ReportBuilder().apply(block).build()
```

Rules:

- Keep DSLs small and obvious. Do not use a DSL for one or two simple parameters.
- Add `@DslMarker` when nested receivers can be confused.
- Prefer named arguments over custom DSLs for ordinary constructors/functions.

## 8. Coroutine patterns

Use coroutines only when async or cancellable work is actually needed. Keep them structured.

```kotlin
class Worker(private val scope: CoroutineScope) {
    fun start(): Job = scope.launch {
        while (isActive) {
            doOneIteration()
            delay(100)
        }
    }
}
```

Rules:

- Do not use `GlobalScope` for application code.
- Do not use `runBlocking` inside suspend functions or production call paths. Reserve it for `main`, tests, or bridges at boundaries.
- Prefer `coroutineScope` or `supervisorScope` to control child lifetimes.
- Propagate cancellation. Do not catch and suppress `CancellationException`.
- Mark blocking work and dispatchers explicitly at boundaries. Keep pure CPU logic independent from coroutine machinery.
- Test suspend functions with coroutine test tools such as `runTest` when `kotlinx-coroutines-test` is available.

## 9. Java interop boundary patterns

Use explicit Kotlin wrappers around Java APIs that use platform types or `Optional`.

```kotlin
fun Properties.required(name: String): String =
    requireNotNull(getProperty(name)) { "missing property: $name" }
```

Rules:

- Treat platform types from Java as untrusted. Normalize them to nullable or non-null Kotlin types at the boundary.
- Use `@JvmOverloads` only when Java callers need overloads for default parameters.
- Use `@JvmStatic` or `@JvmField` only for deliberate Java API shape.
- Be careful with arrays: use `contentEquals` for content equality.
- Avoid leaking Kotlin-specific types to Java-facing APIs unless Java callers can use them comfortably.

## 10. Anti-patterns

- `!!` to satisfy the compiler instead of modeling absence.
- `var` fields that represent derivable state.
- `MutableList` or mutable map exposed from public APIs.
- Boolean flag parameters when an enum or sealed type would name behavior.
- Parallel nullable fields that should be one sealed state.
- `object` as hidden global mutable state.
- `Sequence` everywhere, including small/simple lists.
- Deeply nested scope functions with unclear `this`/`it`.
- Extension functions in unrelated packages that surprise readers.
- `runBlocking` in production library code.
- Catching `Exception` or `Throwable` without preserving or rethrowing cancellation/error cases.
