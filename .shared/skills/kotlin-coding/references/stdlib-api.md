# Kotlin Standard Library API Reference

Use this reference when choosing standard-library APIs or explaining collection, sequence, string, range, scope-function, resource, or utility behavior.

## Table of contents

1. Stdlib package map
2. Collections
3. Collection operations
4. Sequences
5. Arrays and primitive arrays
6. Strings, regex, and text
7. Ranges, progressions, and numeric APIs
8. Scope functions and small utilities
9. Resource and IO helpers
10. API selection rules

## 1. Stdlib package map

Frequently used packages:

- `kotlin`: core types (`Any`, `Unit`, `Nothing`, `Result`, `Pair`, `Triple`, `Lazy`), exceptions, annotations, comparison helpers.
- `kotlin.collections`: collection interfaces, builders, operations, maps, sets, lists, `ArrayDeque`.
- `kotlin.sequences`: `Sequence<T>` and lazy transformations.
- `kotlin.ranges`: ranges and progressions.
- `kotlin.text`: strings, chars, regex helpers, conversions.
- `kotlin.io`: console/file helpers and `Closeable.use` on JVM.
- `kotlin.math`: math functions and constants.
- `kotlin.time`: `Duration`, time sources, and measurement helpers.
- `kotlin.test`: portable test assertions and annotations that can map to JUnit on JVM.

JVM-specific Kotlin projects can also use Java standard APIs directly; prefer Kotlin wrappers and extensions when they make the code clearer.

## 2. Collections

Main interfaces:

| Interface | Mutable peer | Notes |
|---|---|---|
| `Iterable<T>` | `MutableIterable<T>` | General iteration. |
| `Collection<T>` | `MutableCollection<T>` | Size, membership, iteration. |
| `List<T>` | `MutableList<T>` | Ordered, indexed, duplicates allowed. |
| `Set<T>` | `MutableSet<T>` | Unique elements. Default `mutableSetOf` is insertion ordered. |
| `Map<K, V>` | `MutableMap<K, V>` | Unique keys mapped to values. Default `mutableMapOf` is insertion ordered. |

Creation:

```kotlin
val names = listOf("Ada", "Grace")
val mutableNames = mutableListOf("Ada")
val ids = setOf(UserId("a"), UserId("b"))
val byId = mapOf(UserId("a") to User("Ada"))
val queue = ArrayDeque<Int>().apply { addLast(1); addLast(2) }
```

Rules:

- Expose `List`, `Set`, or `Map` in public APIs unless callers must mutate through the API.
- Assign mutable collections to `val` to prevent rebinding, but remember contents still mutate.
- Copy mutable inputs when storing them: `private val items = items.toList()`.
- Return defensive copies or stable read-only views when internals are mutable.
- Use `ArrayDeque` for stack/queue/deque behavior instead of `MutableList` head operations.

## 3. Collection operations

Transform/filter:

```kotlin
val activeNames = users
    .filter { it.isActive }
    .map { it.name }
    .sorted()
```

Common operations:

- Transform: `map`, `mapNotNull`, `flatMap`, `associate`, `associateBy`, `associateWith`.
- Filter: `filter`, `filterIsInstance`, `filterNotNull`, `partition`.
- Retrieve: `first`, `firstOrNull`, `single`, `singleOrNull`, `getOrNull`, `elementAtOrNull`.
- Aggregate: `count`, `sumOf`, `fold`, `reduce`, `minOfOrNull`, `maxOfOrNull`.
- Group: `groupBy`, `groupingBy`, `eachCount`, `fold` on grouping.
- Order: `sorted`, `sortedBy`, `compareBy`, `thenBy`.
- Window/chunk: `chunked`, `windowed`, `zip`.

Correctness rules:

- `first`, `single`, and index access throw when not satisfied. Use nullable variants for expected absence.
- `associateBy` overwrites duplicate keys. Use `groupBy` when duplicates are valid.
- `mapNotNull` is cleaner than `map { ... }.filterNotNull()`.
- Do not ignore returned collections. Most operations are non-mutating and return a new result.
- Use `filterTo`, `mapTo`, and `associateTo` only when destination reuse is intentional and documented.

Performance rules:

- For small collections, normal eager operations are usually clearest.
- Avoid repeated `list + item` in loops; it creates a new list each time. Use a builder or mutable accumulator then expose `toList()`.
- Prefer `sumOf` over `map { ... }.sum()` when possible.
- Prefer `asSequence()` for large or potentially infinite sources with multiple transformations and short-circuiting terminals.

## 4. Sequences

A `Sequence<T>` produces values lazily during iteration. Use it when laziness avoids intermediate collections or stops early.

Constructors:

```kotlin
val seq1 = sequenceOf(1, 2, 3)
val seq2 = list.asSequence()
val seq3 = generateSequence(1) { previous -> if (previous < 100) previous * 2 else null }
val seq4 = sequence {
    yield(1)
    yieldAll(listOf(2, 3))
}
```

Rules:

- Intermediate operations return sequences. Terminal operations include `toList`, `sum`, `count`, `first`, and `joinToString`.
- Some sequence implementations can be consumed only once; do not assume every sequence is reusable.
- Lazy operations have overhead. For small/simple data, prefer collections.
- Be careful with infinite sequences; always bound them with `take`, `first`, or another terminating condition.

## 5. Arrays and primitive arrays

Use arrays for interop or fixed-size indexed storage. Prefer collections for normal application modeling.

```kotlin
val objects: Array<String> = arrayOf("a", "b")
val ints: IntArray = intArrayOf(1, 2, 3)
val boxed: Array<Int> = ints.toTypedArray()
```

Rules:

- `Array<T>` and primitive arrays such as `IntArray` are different types.
- Arrays have fixed size; lists can grow/shrink.
- Use `contentEquals`, `contentHashCode`, and `contentToString` for array contents. `==` on arrays checks referential equality.
- Use the spread operator for varargs: `call(*array)`.

## 6. Strings, regex, and text

String APIs:

```kotlin
val message = "user=${user.id}"
val text = buildString {
    append("count=")
    append(items.size)
}
val lines = input.lineSequence().filter { it.isNotBlank() }.toList()
```

Rules:

- Strings are immutable. In loops or builders, use `buildString`, `StringBuilder`, or `joinToString`.
- Use templates instead of concatenation for readability.
- Use raw strings for regular expressions and multiline text.
- Use `toIntOrNull`, `toLongOrNull`, and similar APIs for expected parse failures.
- For regex, compile once if reused: `private val TokenRegex = Regex("...")`.

## 7. Ranges, progressions, and numeric APIs

```kotlin
for (i in 0 until size) { ... }     // excludes size
for (i in 0..<size) { ... }         // excludes size in modern Kotlin
for (i in size - 1 downTo 0) { ... }
for (i in 0..10 step 2) { ... }
if (x in 1..100) { ... }
```

Rules:

- Use `indices` or direct iteration instead of manual index loops when possible.
- Use `lastIndex` when index boundaries matter.
- Kotlin does not implicitly widen numeric types. Convert explicitly: `n.toLong()`.
- Use `floorDiv`/`mod` or clear tests when negative integer division behavior matters.

## 8. Scope functions and small utilities

Scope functions differ by receiver binding and return value:

| Function | Receiver inside block | Returns | Prefer for |
|---|---|---|---|
| `let` | `it` | block result | Nullable transform, local name. |
| `run` | `this` | block result | Compute with receiver. |
| `with` | `this` | block result | Group calls on existing non-null object. |
| `apply` | `this` | receiver | Configure a new object. |
| `also` | `it` | receiver | Side effect while preserving chain. |

Examples:

```kotlin
val length = name?.trim()?.let { trimmed -> trimmed.length } ?: 0
val config = Config().apply { retries = 3 }
val saved = repository.save(user).also { logger.info("saved ${it.id}") }
```

Rules:

- Avoid nesting scope functions deeply. Name intermediates when the receiver becomes unclear.
- Avoid `also` for essential logic hidden as a side effect.
- `takeIf`/`takeUnless` are useful for small predicates but can be less readable than `if` for complex conditions.

Other utilities:

```kotlin
require(age >= 0) { "age must be non-negative" }
check(state.isOpen) { "state must be open" }
val id = requireNotNull(rawId) { "id required" }
lazy(LazyThreadSafetyMode.PUBLICATION) { expensiveComputation() }
```

Use `require*` for caller argument violations, `check*` for object/state violations, and `error` for impossible paths.

## 9. Resource and IO helpers

For JVM resources implementing `Closeable`, use `use`:

```kotlin
val text = path.toFile().bufferedReader().use { reader ->
    reader.readText()
}
```

Rules:

- `use` closes the resource even when the block throws.
- Prefer line/sequence processing for large files.
- Keep IO at boundaries; pass parsed values into pure functions for easier tests.

## 10. API selection rules

- Expected absence: return `T?`, `firstOrNull`, `getOrNull`, `toIntOrNull`, or a sealed result.
- Invalid caller input: `require`/`requireNotNull`.
- Invalid object state: `check`/`checkNotNull`.
- Closed domain alternatives: sealed interface/class plus exhaustive `when`.
- Fixed constants with no payload variance: enum.
- Transparent values: data class.
- Singleton state/value: object or data object.
- Domain wrapper around one primitive/string: value class plus factory if validation is needed.
- Large, lazy, multi-step pipelines: `Sequence`.
- Small or simple transformations: eager collections.
