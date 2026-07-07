# Test Data Patterns

## Table of contents

1. Local literals
2. Fixture functions
3. Builders
4. Edge-case matrices
5. Property generators
6. Golden samples
7. Randomness policy

## 1. Local literals

Prefer local literals for simple cases:

```kotlin
@Test
fun `trims display name`() {
    val user = User(name = "  Alice  ")

    assertEquals("Alice", user.displayName)
}
```

This keeps the test readable and avoids hidden defaults.

## 2. Fixture functions

Use fixture functions when many tests need a valid object with small variations:

```kotlin
fun user(
    id: UserId = UserId("u1"),
    name: String = "Alice",
    email: Email = Email("alice@example.com"),
): User = User(id = id, name = name, email = email)
```

Rules:

- Keep defaults valid and unsurprising.
- Put the varied fields in the test, not buried in fixture internals.
- Avoid global mutable fixture objects.

## 3. Builders

Use builders for large immutable objects with many optional fields:

```kotlin
class OrderBuilder {
    private var id: OrderId = OrderId("o1")
    private var status: OrderStatus = OrderStatus.Draft
    private var items: List<OrderItem> = listOf(OrderItem("sku-1", quantity = 1))

    fun status(value: OrderStatus) = apply { status = value }
    fun items(value: List<OrderItem>) = apply { items = value }

    fun build(): Order = Order(id = id, status = status, items = items)
}

fun order(block: OrderBuilder.() -> Unit = {}): Order = OrderBuilder().apply(block).build()
```

Use builders only when fixture functions become hard to read.

## 4. Edge-case matrices

Create explicit matrices for parser/validator/normalizer logic:

```kotlin
val invalidEmails = listOf(
    "",
    " ",
    "missing-at.example.com",
    "missing-domain@",
    "@missing-local.example.com",
)

for (raw in invalidEmails) {
    assertFalse(isValidEmail(raw), "raw=$raw")
}
```

Include Kotlin-specific edge cases:

- Empty and single-element collections.
- Duplicate keys/items.
- Unicode and whitespace variants for string logic.
- `Int.MIN_VALUE`, `Int.MAX_VALUE`, overflow-adjacent values.
- Nullable Java/platform inputs at boundaries.
- Mutable input collection modified after construction.

## 5. Property generators

Kotest generator example:

```kotlin
val portArb: Arb<Int> = Arb.int(1..65535)

val emailLocalPartArb: Arb<String> = Arb.stringPattern("[a-z]{1,12}")
```

Rules:

- Constrain generators to domain-valid values when testing valid invariants.
- Use invalid generators separately.
- Add examples for values generators might not hit often.
- Record and replay failing seeds/cases.

## 6. Golden samples

Use golden samples for stable text/binary transformations only when exact output is the contract:

- Parser/formatter fixtures.
- Serialization compatibility samples.
- Error report formatting.
- Generated source snapshots.

Rules:

- Keep golden files small and reviewed.
- Provide a clear update process.
- Pair golden assertions with semantic assertions when possible.
- Do not use snapshots to bless unknown output without review.

## 7. Randomness policy

- Prefer deterministic fixed examples.
- For random/property tests, use the framework’s reproducibility/seed support.
- Print the seed or failing input when adding custom random generation.
- Never make CI depend on unbounded random loops.
