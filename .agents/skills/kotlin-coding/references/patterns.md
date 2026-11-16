# Kotlin Gotchas

Non-obvious Kotlin/JVM behaviors only. Language grammar, stdlib API selection, and default idioms are training-data restatement — this file does not repeat them.

## Extension functions are statically resolved

Extensions do not participate in dynamic dispatch. The extension is chosen by the *declared* type at the call site, not the runtime type:

```kotlin
open class Base
class Derived : Base()

fun Base.describe() = "base"
fun Derived.describe() = "derived"

val b: Base = Derived()
b.describe()  // "base" — the Base extension wins, not Derived
```

Rules:

- An extension chosen for a `Base` reference will not switch to a `Derived` extension at runtime. If behavior must vary by runtime subtype, make it a member (open function) instead of an extension.
- A member function with the same signature always wins over an extension, even when the extension is imported explicitly.
- Platform-type receivers from Java interop resolve extensions by the inferred static type — normalize the boundary to an explicit Kotlin type first.

## Sealed `when` exhaustiveness is compile-time only on the sealed type

```kotlin
sealed interface LoadState<out T> {
    data object Loading : LoadState<Nothing>
    data class Loaded<T>(val value: T) : LoadState<T>
    data class Failed(val reason: String) : LoadState<Nothing>
}

fun <T> LoadState<T>.valueOrNull(): T? = when (this) {
    is LoadState.Loading -> null
    is LoadState.Loaded -> value
    is LoadState.Failed -> null
}
```

Rules:

- Exhaustive `when` over a sealed hierarchy requires no `else`, and adding a new variant breaks compilation at every `when` — that is the point. Avoid `else` on sealed `when` expressions unless the hierarchy is intentionally open or Java interop forces it; `else` silently disables the exhaustiveness check.
- Exhaustiveness is checked per *static* type. `when` over a value typed as the sealed supertype is exhaustive; the same `when` over a value already narrowed to one variant is not, and `when` over a non-sealed supertype never is.
- Smart-cast narrowing inside a `when` subject can change which branches the compiler requires — if a `when` that used to compile demands `else` after a type change, check the subject's declared type first.
- `when` with a subject captures the subject once; `when (expensiveCall())` does not re-evaluate per branch, but neither can later branches observe side effects from earlier ones.
