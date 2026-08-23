# kotlin.test and JUnit Patterns

## Table of contents

1. When to use the baseline stack
2. Basic test class
3. Assertions
4. Parameterized tests
5. Fixtures and lifecycle
6. Exceptions
7. Kotlin/JVM interop test gotchas

## 1. When to use the baseline stack

Use `kotlin.test` with JUnit Platform when:

- The project needs minimal dependencies.
- Tests are straightforward behavior checks.
- The team already uses JUnit.
- Kotest’s DSL/property features are unnecessary.

`kotlin.test` provides annotations and assertion functions while integrating with JVM test frameworks such as JUnit.

## 2. Basic test class

```kotlin
package com.example.validation

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class EmailValidatorTest {
    @Test
    fun `accepts simple valid email`() {
        assertTrue(isValidEmail("user@example.com"))
    }

    @Test
    fun `rejects blank email`() {
        assertFalse(isValidEmail(""))
    }

    @Test
    fun `normalizes before validating`() {
        assertEquals(
            NormalizedEmail("user@example.com"),
            parseEmail("  USER@example.com  "),
        )
    }
}
```

Rules:

- Use backticks for readable behavior names.
- Put expected value first in `assertEquals(expected, actual)`.
- Add assertion messages for looped/table tests.
- Prefer one behavior per test.

## 3. Assertions

Common `kotlin.test` assertions:

```kotlin
assertEquals(expected, actual)
assertNotEquals(unexpected, actual)
assertTrue(condition)
assertFalse(condition)
assertNull(value)
assertNotNull(value)
assertSame(expectedInstance, actual)
assertNotSame(unexpectedInstance, actual)
assertContains(collectionOrString, elementOrSubstring)
assertFailsWith<IllegalArgumentException> { parsePort("0") }
```

For richer collection/string matchers, consider Kotest assertions instead of writing complex manual assertions.

## 4. Parameterized tests

Plain table loop:

```kotlin
@Test
fun `parses valid ports`() {
    val cases = listOf(
        "1" to 1,
        "80" to 80,
        "65535" to 65535,
    )

    for ((raw, expected) in cases) {
        assertEquals(expected, parsePort(raw), "raw=$raw")
    }
}
```

JUnit Jupiter parameterized tests:

```kotlin
package com.example.validation

import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import kotlin.test.assertEquals

class PortParserParameterizedTest {
    @ParameterizedTest(name = "{0} parses to {1}")
    @CsvSource(
        "1, 1",
        "80, 80",
        "65535, 65535",
    )
    fun `parses valid ports`(raw: String, expected: Int) {
        assertEquals(expected, parsePort(raw))
    }
}
```

Prefer plain table loops for a handful of cases; use parameterized tests when IDE/reporting clarity matters.

## 5. Fixtures and lifecycle

JUnit lifecycle with Kotlin:

```kotlin
import org.junit.jupiter.api.BeforeEach
import kotlin.test.Test
import kotlin.test.assertEquals

class RegistryTest {
    private lateinit var registry: Registry

    @BeforeEach
    fun setUp() {
        registry = Registry()
    }

    @Test
    fun `stores value`() {
        registry.add("a")

        assertEquals(listOf("a"), registry.values)
    }
}
```

Rules:

- Prefer local `val` setup when only one test needs the fixture.
- Use `lateinit` only when lifecycle setup clearly improves readability.
- Reset mutable state before each test, not after a failure.
- Avoid companion-object mutable state unless it is truly immutable shared data.

## 6. Exceptions

```kotlin
@Test
fun `rejects total of zero`() {
    val error = assertFailsWith<IllegalArgumentException> {
        Percentage(part = 1, total = 0)
    }

    assertEquals("total must be greater than zero", error.message)
}
```

Rules:

- Assert the specific exception type.
- Assert the message only if it is part of the public contract or needed to distinguish branches.
- Use `require` failures for bad arguments and `check` failures for invalid state; test accordingly.

## 7. Kotlin/JVM interop test gotchas

- Java getters appear as Kotlin properties; assert the Kotlin-facing API when testing from Kotlin.
- Java platform types may be null at runtime. Add tests for Java boundary nulls when wrapping Java APIs.
- Use `::class.java` when Java APIs need `Class<T>`.
- Static Java methods can usually be called as functions on the Java class name.
- Avoid testing Java framework details unless the user’s task explicitly requires it.
