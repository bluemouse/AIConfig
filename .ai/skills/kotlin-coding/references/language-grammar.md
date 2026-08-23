# Kotlin Language Grammar and Semantics

Use this reference when answering syntax, type-system, declaration, compiler-error, or language-semantics questions.

## Table of contents

1. File structure and imports
2. Lexical rules and names
3. Types
4. Declarations
5. Functions and lambdas
6. Expressions and control flow
7. Classes, interfaces, objects, and inheritance
8. Generics and variance
9. Modifiers and visibility
10. Semantic gotchas

## 1. File structure and imports

A Kotlin source file is a sequence of optional file annotations, an optional package declaration, imports, and declarations.

```kotlin
@file:JvmName("Names")
package com.example.math

import kotlin.math.PI
import kotlin.math.pow as power

const val EPSILON = 1e-9
fun square(x: Double) = x * x
class Vector(val x: Double, val y: Double)
```

Rules:

- A `package` declaration, when present, is at the top of the file before imports and declarations.
- The package name does not have to match directories for the compiler, but style guides recommend package-shaped directories for maintainability.
- Without an explicit package, declarations are in the unnamed default package. Avoid this for reusable code.
- Imports can import classes, top-level functions/properties, object members, enum entries, and wildcard members. Use `as` to disambiguate.
- Default imports include core packages such as `kotlin.*`, `kotlin.collections.*`, `kotlin.io.*`, `kotlin.ranges.*`, `kotlin.sequences.*`, and `kotlin.text.*`; JVM files also receive `java.lang.*` and `kotlin.jvm.*`.

## 2. Lexical rules and names

Common tokens:

- Line comment: `// comment`
- Block comment: `/* comment */`; block comments can be nested.
- String template: `"name=$name, total=${items.sum()}"`
- Raw string: triple quotes, often with `trimIndent()` or `trimMargin()`.
- Escaped identifier: backticks allow keywords or spaces in names, mainly for tests: ``fun `rejects blank input`()``.

Naming defaults:

- Packages: lowercase, no underscores.
- Classes, interfaces, objects, type parameters: UpperCamelCase.
- Functions, properties, local variables: lowerCamelCase.
- Compile-time constants: `SCREAMING_SNAKE_CASE`.
- Private backing property for a public read-only view: `_items` plus `val items: List<T> get() = _items`.

## 3. Types

Core type forms:

```kotlin
String                  // non-null String
String?                 // nullable String
List<Int>               // generic type
Array<String>           // object array
IntArray                // primitive int array on JVM
(a: Int, b: Int) -> Int // function type with parameter names for readability
String.(Int) -> String  // function type with receiver
suspend () -> Unit      // suspend function type
```

Important types:

- `Any` is the root of non-null Kotlin classes; `Any?` also admits `null`.
- `Unit` means no meaningful return value and has one value, `Unit`.
- `Nothing` has no values and is the type of expressions that never complete normally (`throw`, `return`, `error(...)`).
- `T` and `T?` are different types. Use nullable types only when absence is valid.
- `List<T>` is read-only at the interface level; it is not necessarily deeply immutable.
- Primitive-looking types such as `Int`, `Long`, `Double`, and `Boolean` are Kotlin types. Nullable versions like `Int?` may be boxed on the JVM.

Equality:

```kotlin
a == b   // structural equality, null-safe, calls equals
a != b  // structural inequality
a === b // referential identity
a !== b // referential non-identity
```

Use `==` for values. Use `===` only for identity-sensitive code or singleton checks when identity matters.

## 4. Declarations

Variables and properties:

```kotlin
val answer: Int = 42       // read-only reference or property
var count: Int = 0         // mutable variable/property
const val MAX_RETRIES = 3  // top-level/object/companion, String or primitive, no custom getter
lateinit var service: Service // non-null var initialized later; not primitive; throws if read early
```

Top-level declarations are normal Kotlin. Use them for cohesive functions/constants, not dumping grounds.

Properties can have custom accessors and backing fields:

```kotlin
class Counter {
    var value: Int = 0
        private set

    val isPositive: Boolean
        get() = value > 0

    fun increment() {
        value += 1
    }
}
```

Use custom accessors for derived values or validation. Avoid side-effect-heavy getters.

## 5. Functions and lambdas

Function grammar patterns:

```kotlin
fun name(param: Type, optional: Type = default): ReturnType { ... }
fun name(param: Type): ReturnType = expression
fun <T> singleton(value: T): List<T> = listOf(value)
fun String.words(): List<String> = trim().split(Regex("\\s+"))
infix fun Int.percentOf(total: Int): Int = total * this / 100
operator fun Point.plus(other: Point): Point = Point(x + other.x, y + other.y)
tailrec fun gcd(a: Int, b: Int): Int = if (b == 0) a else gcd(b, a % b)
suspend fun fetch(): String = TODO()
```

Parameter and call rules:

- Parameter syntax is `name: Type`; parameters are read-only inside the function.
- Block-body functions must declare a return type unless returning `Unit`.
- Expression-body functions can infer return types, but public APIs should usually state them explicitly.
- Default parameters reduce overloads; after skipping one default at a call site, use named arguments for following arguments.
- `vararg` marks one parameter; pass an existing array with the spread operator `*array`.
- Infix functions must be member or extension functions with exactly one non-vararg, non-default parameter.
- Tail recursion optimization requires `tailrec` and a recursive call in tail position.

Lambda forms:

```kotlin
val doubled = numbers.map { it * 2 }
val sum = numbers.fold(0) { acc, n -> acc + n }
fun transaction(block: Transaction.() -> Unit) { ... }
```

Use trailing lambdas for APIs where the last argument is a function. Name lambda parameters when `it` is ambiguous or nested.

## 6. Expressions and control flow

Kotlin treats `if`, `when`, `try`, and `throw` as expressions.

```kotlin
val max = if (a > b) a else b

val label = when (value) {
    null -> "missing"
    0 -> "zero"
    in 1..9 -> "digit"
    is String -> "string:${value.length}"
    else -> "other"
}

val parsed = try {
    input.toInt()
} catch (e: NumberFormatException) {
    null
}
```

Rules:

- `if` used as an expression must cover both branches.
- `when` can match constants, ranges, type checks, arbitrary conditions, or no subject.
- `when` over `enum` or sealed hierarchies should be exhaustive. Avoid `else` when listing all cases makes compiler checking possible.
- `for (x in xs)` iterates anything with `iterator()`; ranges and progressions use `..`, `..<`, `downTo`, `step`.
- `break` and `continue` can target labels in nested loops.
- `return@label` returns from a lambda or labeled scope, not necessarily the outer function.

Null-safety operators:

```kotlin
val len: Int? = user?.name?.length
val name: String = user?.name ?: "anonymous"
val nonNull: User = requireNotNull(user) { "user is required" }
val value: String = nullable!! // avoid unless the invariant is externally guaranteed and documented
```

Smart casts work after checks when the compiler can prove the value cannot change unexpectedly:

```kotlin
if (x is String) println(x.length)
if (name != null) println(name.length)
```

Smart casts can fail for mutable properties, open properties, captured vars, or values changed by another thread. Copy to a local `val` first.

## 7. Classes, interfaces, objects, and inheritance

Class forms:

```kotlin
class Person(val id: UserId, var displayName: String)

class Account private constructor(val id: String) {
    companion object {
        fun create(id: String): Account {
            require(id.isNotBlank())
            return Account(id)
        }
    }
}

open class Shape {
    open fun area(): Double = 0.0
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = Math.PI * radius * radius
}
```

Rules:

- Classes and members are final by default. Use `open` deliberately.
- Overrides require `override`. An overridden member remains open unless marked `final override`.
- Do not call open members from constructors, property initializers, or `init` blocks of base classes.
- A subclass with a primary constructor initializes its superclass in the class header.
- Interfaces can declare abstract members and default method/property accessors. A class can implement multiple interfaces but extend only one class.
- If multiple supertypes provide the same member implementation, the class must override and can call `super<Type>.member()`.

Data classes:

```kotlin
data class User(val id: UserId, val name: String)
```

Use data classes for transparent values. Primary constructor should contain the identity/state properties you want in `equals`, `hashCode`, `toString`, `componentN`, and `copy`. Keep mutable body properties out of data-class equality unless this is intentional.

Sealed hierarchies:

```kotlin
sealed interface ParseResult {
    data class Success(val value: Int) : ParseResult
    data class Failure(val reason: String) : ParseResult
}

fun message(result: ParseResult): String = when (result) {
    is ParseResult.Success -> "value=${result.value}"
    is ParseResult.Failure -> result.reason
}
```

Use sealed classes/interfaces for closed variants and exhaustive `when`. Direct subclasses must be in the same package and module.

Enum classes:

```kotlin
enum class Severity { LOW, MEDIUM, HIGH }
```

Use enums for fixed singleton constants. Prefer `entries` or `enumEntries<T>()` over `values()`/`enumValues<T>()` in modern Kotlin because entries avoid repeated array creation.

Objects:

```kotlin
object IdGenerator { fun next(): String = ... }
data object Loading
```

Object declarations are singletons initialized lazily and thread-safely on first access. Use companion objects for factory functions or class-level constants.

Value classes:

```kotlin
@JvmInline
value class UserId(val value: String)
```

Use value classes to give domain meaning to a single underlying value without always allocating wrappers. They must have exactly one primary-constructor property. Validate through factory functions when construction must be constrained.

Nested and inner classes:

- Nested classes are static-like by default and do not capture the outer class.
- Mark `inner` only when the nested class must hold an outer-instance reference.

## 8. Generics and variance

Declaration-site variance:

```kotlin
interface Producer<out T> { fun get(): T }
interface Consumer<in T> { fun accept(value: T) }
```

Rules:

- `out T`: the type is produced; `Producer<Dog>` can be used as `Producer<Animal>`.
- `in T`: the type is consumed; `Consumer<Animal>` can be used as `Consumer<Dog>`.
- Invariant types like `MutableList<T>` are not subtype-compatible across `T` because they both consume and produce `T`.
- Use use-site projections (`List<out Number>`, `MutableList<in Int>`) when a particular API needs variance.
- Use `where` clauses for multiple bounds:

```kotlin
fun <T> copyWhenReady(value: T) where T : Closeable, T : Runnable { ... }
```

Inline reified type parameters:

```kotlin
inline fun <reified T> Any?.castOrNull(): T? = this as? T
```

Use `reified` only in inline functions when runtime type access is required.

## 9. Modifiers and visibility

Visibility:

- `public`: default everywhere.
- `internal`: visible inside the same module.
- `protected`: visible inside class/subclasses; not for top-level declarations.
- `private`: visible in the enclosing declaration or file for top-level declarations.

Common modifiers:

- Class/member model: `final`, `open`, `abstract`, `sealed`, `data`, `enum`, `annotation`, `value`, `inner`, `companion`, `fun interface`.
- Function behavior: `inline`, `noinline`, `crossinline`, `tailrec`, `operator`, `infix`, `suspend`, `external`.
- Property behavior: `const`, `lateinit`, `override`.

Use the conventional modifier order: visibility, platform/expect-actual if present, final/open/abstract/sealed/const, external, override, lateinit, tailrec, vararg, suspend, inner, enum/annotation/fun, companion, inline/value/infix/operator/data.

## 10. Semantic gotchas

- `val` prevents reassignment of the reference, not mutation of the object it references. `val xs = mutableListOf(1)` still allows `xs += 2`.
- Read-only collection interfaces are not immutable guarantees. Do not expose internal mutable collections directly.
- `List<T>` is covariant; `MutableList<T>` is invariant.
- Member functions win over extension functions with the same signature. Extensions are statically resolved by declared receiver type.
- `toInt()` throws; `toIntOrNull()` returns null.
- `String.plus` or repeated `+` in loops can allocate heavily; use `buildString` or `joinToString`.
- `lateinit` shifts initialization checks to runtime. Prefer constructor injection or nullable local state unless delayed initialization is truly needed.
- `lazy` is useful for expensive derived values, but choose thread-safety mode intentionally.
- `Result<T>` is convenient for local boundaries, but public API use should be deliberate and consistent.
- `Nothing` enables expressions such as `val x = nullable ?: error("missing")`.
