# C# correctness, maintainability, safety, and performance best practices

Use this file when writing, reviewing, or refactoring C# code.

## Table of contents

1. Core principles
2. Null safety
3. Type and API design
4. Object construction and immutability
5. Methods, properties, and naming
6. Exceptions and validation
7. Async and cancellation
8. Collections and LINQ
9. Resource lifetime
10. Dependency injection and architecture
11. Logging and diagnostics
12. Security
13. Performance
14. Concurrency
15. Style and review checklist

## 1. Core principles

- Prefer boring, explicit, testable code over clever syntax.
- Make invalid states unrepresentable where practical.
- Keep public APIs stable, documented, nullable-annotated, and hard to misuse.
- Push I/O, clocks, randomness, process state, and external services behind abstractions when they affect tests.
- Use the type system before runtime checks: enums, value objects, generics, constraints, nullable annotations, records, and required members.
- Keep methods small enough to test and reason about, but do not fragment code into meaningless one-line wrappers.

## 2. Null safety

Default to `<Nullable>enable</Nullable>`.

Do:

```csharp
public static string Normalize(string value)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(value);
    return value.Trim().ToUpperInvariant();
}
```

Avoid:

```csharp
public static string Normalize(string? value) => value!.Trim().ToUpper();
```

Rules:
- Use non-nullable reference types for required inputs and outputs.
- Use nullable annotations only when null is a meaningful state.
- Use `ArgumentNullException.ThrowIfNull`, `ArgumentException.ThrowIfNullOrWhiteSpace`, and guard clauses at boundaries.
- Avoid returning null collections. Return empty collections where absence and empty are equivalent.
- Use `[NotNullWhen]`, `[MemberNotNull]`, etc., for helper methods that influence flow analysis.
- Treat null-forgiving `!` as a last resort with a nearby explanation.

## 3. Type and API design

Choose the right type:
- `class`: identity, lifecycle, mutable services, framework integration.
- `record class`: DTOs, messages, immutable-ish data with value equality.
- `record struct`: small value data with value equality; prefer `readonly` when immutable.
- `struct`: performance-sensitive value type with carefully managed copying.
- `enum`: closed set of named constants; define explicit values when serialized or persisted.
- `interface`: capability/contract boundary; keep small and cohesive.
- `delegate`/`Func`/`Action`: behavior parameter when a full interface is unnecessary.

Public API rules:
- Avoid boolean parameter traps; use named options, enums, or separate methods when behavior differs materially.
- Avoid exposing mutable collections. Return `IReadOnlyList<T>`, `IReadOnlyCollection<T>`, `ImmutableArray<T>`, or snapshots as appropriate.
- Avoid exposing `IQueryable<T>` outside query composition boundaries.
- Keep constructors cheap and side-effect free.
- Document threading, ownership, disposal, cancellation, nullability, and exceptions.

## 4. Object construction and immutability

Use `required` and `init` for complete construction:

```csharp
public sealed record UserProfile
{
    public required string Id { get; init; }
    public required string Email { get; init; }
    public string? DisplayName { get; init; }
}
```

Use constructors when invariants need validation:

```csharp
public sealed record EmailAddress
{
    public EmailAddress(string value)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(value);
        Value = value.Contains('@', StringComparison.Ordinal) ? value : throw new ArgumentException("Invalid email.", nameof(value));
    }

    public string Value { get; }
    public override string ToString() => Value;
}
```

Rules:
- Prefer immutability for messages, DTOs, options, and values.
- Avoid partially initialized objects.
- Use `with` expressions for non-destructive mutation of records.
- Avoid mutable static state.

## 5. Methods, properties, and naming

Properties should be cheap, deterministic, and side-effect free. Use methods for expensive, asynchronous, mutating, or failure-prone work.

Naming:
- PascalCase for public types, members, constants, enum members.
- camelCase for locals and parameters.
- `_camelCase` for private fields when consistent with the repo.
- Async methods returning `Task`/`ValueTask` should usually end with `Async`.
- Use `nameof` instead of magic strings for member names.

Avoid vague names: `DoWork`, `Helper`, `Manager`, `Data`, `Info`, `Util` unless the domain convention is established.

## 6. Exceptions and validation

Use exceptions for exceptional failures and contract violations, not expected control flow.

Common choices:
- `ArgumentNullException`, `ArgumentException`, `ArgumentOutOfRangeException` for bad inputs.
- `InvalidOperationException` for invalid object state or operation order.
- Custom exceptions only when callers can handle them distinctly.

Do not catch `Exception` unless adding context, translating boundaries, logging-and-rethrowing correctly, or preventing process crash at a top-level boundary.

Use `throw;` not `throw ex;` when rethrowing.

## 7. Async and cancellation

Rules:
- Use `Task`/`Task<T>` for most async APIs.
- Use `ValueTask` only when there is a measured allocation problem or a frequent synchronous fast path.
- Accept `CancellationToken` in asynchronous I/O, long-running operations, hosted services, and request pipelines.
- Pass the token through to lower layers.
- Do not ignore returned tasks.
- Avoid `Task.Run` as a fix for blocking I/O in ASP.NET/service code.
- Avoid locks across `await`.

Example:

```csharp
public async Task<Order> GetOrderAsync(string id, CancellationToken cancellationToken)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(id);

    var order = await repository.FindAsync(id, cancellationToken);
    return order ?? throw new InvalidOperationException($"Order '{id}' was not found.");
}
```

## 8. Collections and LINQ

Rules:
- Use collection expressions (`[]`, `[a, b]`, `[..items]`) only when the project language version supports them.
- Prefer arrays for fixed-size internal data, `List<T>` for mutable sequences, `Dictionary<TKey,TValue>` for lookups, `HashSet<T>` for membership, immutable collections for shared snapshots.
- Avoid repeated `Count()`/`Any()` on unknown `IEnumerable<T>` sources if it can enumerate repeatedly.
- Materialize deferred queries deliberately at boundaries.
- Use `StringComparer.Ordinal`/`OrdinalIgnoreCase` for non-linguistic keys.
- Be explicit about culture in parsing, formatting, and casing.

LINQ is excellent for declarative transformations. Prefer loops when performance, debugging, mutation, async, or complex error handling matters.

## 9. Resource lifetime

Rules:
- Dispose what you own.
- Do not dispose services owned by dependency injection.
- Use `using`/`await using` declarations for short-lived resources.
- Do not create a new `HttpClient` per request; use `IHttpClientFactory` in DI-based apps or a long-lived client where appropriate.
- Unsubscribe events or use weak/lifetime-bound subscriptions when publisher outlives subscriber.
- Dispose timers, streams, cancellation token sources, and unmanaged handles.

## 10. Dependency injection and architecture

Rules:
- Use constructor injection for required dependencies.
- Keep DI composition at the application boundary.
- Avoid service locator patterns in domain code.
- Keep domain logic independent of ASP.NET, EF Core, HTTP, filesystem, and wall-clock time when possible.
- Separate contracts from infrastructure only when it improves testability or substitutability.
- Avoid anemic abstraction layers that mirror one implementation with no benefit.

## 11. Logging and diagnostics

Rules:
- Use structured logging placeholders: `logger.LogInformation("Processed {Count} items", count);`
- Do not log secrets, tokens, passwords, or personal data unless explicitly allowed and redacted.
- Include stable identifiers and operation context.
- Do not log and rethrow at every layer; log at boundaries or where useful context exists.
- Use correlation IDs/activity tracing for distributed flows.

## 12. Security

Rules:
- Validate and normalize all external input.
- Use parameterized queries/ORM parameters, never string-concatenated SQL.
- Do not deserialize untrusted payloads into unsafe polymorphic types.
- Use constant-time comparison for secrets/tokens when relevant.
- Store secrets in secure configuration providers, not source code or logs.
- Use least privilege for filesystem, network, database, and cloud credentials.
- Keep dependencies updated and review vulnerability reports.
- Treat path construction, archive extraction, process execution, and reflection as security-sensitive.

## 13. Performance

Prefer clarity until measurements show a problem.

Fast-path tools:
- `Span<T>`/`ReadOnlySpan<T>` for parsing/slicing without allocation.
- `Memory<T>`/`ReadOnlyMemory<T>` when data must survive async boundaries.
- `ArrayPool<T>` for large temporary buffers with careful cleanup.
- `StringBuilder` for repeated string append; `string.Create` for specialized formatting.
- `CollectionsMarshal`/unsafe APIs only for expert, measured hot paths.

Avoid:
- Exceptions for normal control flow.
- Reflection in hot paths without caching.
- Boxing in tight loops.
- Capturing lambdas in hot paths when allocations matter.
- `DateTime.Now` in logic that needs deterministic tests; inject time provider/clock.

## 14. Concurrency

Rules:
- Prefer immutable data or single-owner mutation.
- Use `ConcurrentDictionary` and channels for appropriate producer/consumer patterns.
- Lock private objects only; never lock on `this`, `typeof(T)`, or strings.
- Keep critical sections small and synchronous.
- Do not mix blocking locks with async waits.
- Make thread-safety guarantees explicit in public APIs.

## 15. Style and review checklist

Before finalizing code, check:
- Builds under the repo target frameworks.
- Nullable warnings are fixed, not suppressed without reason.
- Async calls are awaited and cancellation is propagated.
- Public APIs have sensible nullability, names, and exception behavior.
- Resources are disposed correctly.
- Logging is structured and safe.
- Security-sensitive input is validated and encoded/parameterized.
- Tests cover success, failure, edge, cancellation, and regression cases.
- Performance-sensitive code is measured.
- Formatting/analyzers pass or deviations are explained.
