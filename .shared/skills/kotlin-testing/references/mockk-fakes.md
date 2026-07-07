# Fakes and MockK

## Table of contents

1. Prefer fakes where possible
2. MockK setup
3. Basic mocking and verification
4. Suspend functions
5. Capturing arguments
6. Relaxed mocks
7. Spies and partial mocks
8. Interaction-test rules

## 1. Prefer fakes where possible

Use a fake when the dependency has simple behavior and stores state naturally:

```kotlin
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<UserId, User>()

    override suspend fun find(id: UserId): User? = users[id]

    override suspend fun save(user: User) {
        users[user.id] = user
    }
}
```

Advantages:

- Tests remain behavior-focused.
- Refactors do not break because internal calls changed.
- Coroutine behavior can be made deterministic.

Use mocks when:

- The protocol interaction is the behavior under test.
- You need to inject precise failure branches.
- The real dependency is expensive or nondeterministic.
- Verifying no duplicate calls/order matters.

## 2. MockK setup

```kotlin
dependencies {
    testImplementation("io.mockk:mockk:<mockk-version>")
}
```

Imports:

```kotlin
import io.mockk.clearMocks
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
```

## 3. Basic mocking and verification

```kotlin
class UserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val service = UserService(repository)

    beforeTest {
        clearMocks(repository)
    }

    test("returns user when repository finds it") {
        val expected = User(UserId("u1"), "Alice")
        every { repository.findBlocking(UserId("u1")) } returns expected

        service.findBlocking(UserId("u1")) shouldBe expected

        verify(exactly = 1) { repository.findBlocking(UserId("u1")) }
    }
})
```

Rules:

- Verify interactions only when they are part of the observable contract.
- Prefer exact arguments over broad `any()` when the argument matters.
- Clear or recreate mocks between tests.

## 4. Suspend functions

```kotlin
class AsyncUserServiceTest : FunSpec({
    val repository = mockk<UserRepository>()
    val service = UserService(repository)

    beforeTest {
        clearMocks(repository)
    }

    test("loads user") {
        runTest {
            val expected = User(UserId("u1"), "Alice")
            coEvery { repository.find(UserId("u1")) } returns expected

            service.load(UserId("u1")) shouldBe expected

            coVerify(exactly = 1) { repository.find(UserId("u1")) }
        }
    }
})
```

Use `coEvery` and `coVerify` for suspend functions.

## 5. Capturing arguments

```kotlin
test("saves normalized user") {
    runTest {
        val repository = mockk<UserRepository>()
        val slot = slot<User>()
        coEvery { repository.save(capture(slot)) } returns Unit

        UserService(repository).create("  Alice  ")

        slot.captured.name shouldBe "Alice"
    }
}
```

Prefer capturing when the object is produced inside the subject and cannot be asserted otherwise.

## 6. Relaxed mocks

```kotlin
val logger = mockk<Logger>(relaxed = true)
```

Use relaxed mocks only for side-effect collaborators whose calls are not the core assertion, such as logging or metrics. Do not relax domain dependencies where missing stubs should fail loudly.

## 7. Spies and partial mocks

```kotlin
val real = IdGenerator(prefix = "user")
val spy = spyk(real)
every { spy.randomSuffix() } returns "fixed"

spy.newId() shouldBe UserId("user-fixed")
```

Use spies sparingly. A need to mock part of the subject often means the production design needs a smaller dependency seam.

## 8. Interaction-test rules

- Assert returned values/state before interactions when possible.
- Avoid verifying every call; verify only calls that carry behavior.
- Avoid call-order assertions unless ordering is the contract.
- Do not mock data classes, value objects, collections, strings, or simple DTOs.
- Prefer fake clocks, fake ID generators, and fake repositories over static/global mocking.
- If MockK setup is longer than the behavior under test, reconsider the design.
