# Coroutine Testing

## Table of contents

1. Setup
2. runTest
3. Dispatcher and scope injection
4. Virtual time
5. Flow tests
6. Cancellation and error propagation
7. Flake triage

## 1. Setup

```kotlin
dependencies {
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:<coroutines-version>")
}
```

Common imports:

```kotlin
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.take
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceTimeBy
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
```

## 2. runTest

```kotlin
class UserServiceTest {
    @Test
    fun `loads user`() = runTest {
        val repository = FakeUserRepository().apply {
            save(User(UserId("u1"), "Alice"))
        }
        val service = UserService(repository)

        val result = service.load(UserId("u1"))

        assertEquals("Alice", result.name)
    }
}
```

Rules:

- Use `runTest` for suspend tests.
- Do not use production `runBlocking` for coroutine unit tests unless bridging legacy code.
- Let uncaught child coroutine failures fail the test.
- Keep assertions inside the `runTest` block when they depend on coroutine completion.

## 3. Dispatcher and scope injection

Production code should accept a dispatcher or scope when it changes execution context:

```kotlin
class ReportLoader(
    private val repository: ReportRepository,
    private val dispatcher: CoroutineDispatcher,
) {
    suspend fun load(id: ReportId): Report = withContext(dispatcher) {
        repository.fetch(id)
    }
}
```

Test:

```kotlin
@Test
fun `loads on injected dispatcher`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val loader = ReportLoader(fakeRepository, dispatcher)

    val deferred = async { loader.load(ReportId("r1")) }
    advanceUntilIdle()

    assertEquals(ReportId("r1"), deferred.await().id)
}
```

Rules:

- Inject dispatchers/scopes instead of hard-coding `Dispatchers.IO` in deeply tested logic.
- Avoid `GlobalScope`; use structured concurrency.
- If `Dispatchers.Main` appears in plain JVM code, isolate it behind injection or set/reset it in tests with coroutine test tools.

## 4. Virtual time

```kotlin
@Test
fun `debounces events`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)
    val search = SearchService(dispatcher)

    val results = mutableListOf<List<Result>>()
    val job = launch { search.results.toList(results) }

    search.query("a")
    search.query("ab")
    search.query("abc")

    advanceTimeBy(300)
    runCurrent()

    assertEquals(1, results.size)
    job.cancel()
}
```

Rules:

- Replace sleeps with `advanceTimeBy`, `runCurrent`, or `advanceUntilIdle`.
- Assert state before and after advancing time when timing is the behavior.
- Ensure launched collectors/jobs are cancelled at the end of tests.

## 5. Flow tests

Finite flow:

```kotlin
@Test
fun `emits first three statuses`() = runTest {
    val statuses = statusFlow()
        .take(3)
        .toList()

    assertEquals(listOf(Status.Started, Status.Running, Status.Done), statuses)
}
```

Flow with active collector:

```kotlin
@Test
fun `emits updates after save`() = runTest {
    val repository = UserRepository()
    val values = mutableListOf<List<User>>()

    val job = launch {
        repository.observeUsers()
            .take(2)
            .toList(values)
    }

    repository.save(User(UserId("u1"), "Alice"))
    advanceUntilIdle()

    assertEquals("Alice", values.last().single().name)
    job.cancel()
}
```

Rules:

- Use `take(n)` for finite assertions on ongoing flows.
- Cancel collectors that are not naturally completed.
- Avoid real delays and background dispatchers.

## 6. Cancellation and error propagation

```kotlin
@Test
fun `propagates cancellation`() = runTest {
    val job = launch {
        service.longRunningOperation()
    }

    job.cancel()

    assertTrue(job.isCancelled)
}
```

Rules:

- Do not swallow `CancellationException` in production or tests.
- Test cleanup/finally behavior if resources are acquired.
- Assert child coroutine failures are surfaced, not logged and ignored.

## 7. Flake triage

Coroutine flakes usually come from:

- Hard-coded dispatchers not controlled by the test scheduler.
- `Thread.sleep` or real timeouts.
- Work launched in a scope the test does not own.
- Flow collectors left running across tests.
- Race-prone assertions before `advanceUntilIdle`/`runCurrent`.
- Shared mutable fake state across parallel tests.

Fix by making scheduling explicit, owning/cancelling scopes, and using virtual time.
