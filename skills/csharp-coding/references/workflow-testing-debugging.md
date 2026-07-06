# C# coding, testing, and debugging workflow

Use this file for step-by-step engineering process on real codebases.

## Table of contents

1. Intake checklist
2. Implementation loop
3. Test strategy
4. Debugging workflow
5. Compiler and analyzer failure triage
6. Runtime failure triage
7. Async and concurrency bugs
8. Performance workflow
9. Refactoring workflow
10. Completion report

## 1. Intake checklist

Before changing code, determine:
- Is this a console app, library, service, ASP.NET app, worker, test project, source generator, tool, or package?
- Which target framework and C# language version apply?
- Are nullable reference types enabled?
- Which test framework is used?
- Are analyzers and warning-as-error enabled?
- What is the smallest command that reproduces the issue?

Inspect before editing:

```bash
dotnet --info
find . -maxdepth 3 -name '*.sln' -o -name '*.slnx' -o -name '*.csproj' -o -name 'Directory.Build.*' -o -name '.editorconfig' -o -name 'global.json'
```

## 2. Implementation loop

1. Reproduce or characterize the current behavior.
2. Add a failing test when behavior is observable.
3. Make the smallest production change.
4. Run the targeted test/build.
5. Refactor while green.
6. Run broader verification.

For generated examples or greenfield code, still design the test seam and show how to run it.

## 3. Test strategy

### Unit tests

Use for pure logic, parsing, validation, mapping, calculations, domain services, and error handling.

A good unit test:
- Names the behavior, not the implementation.
- Has clear arrange/act/assert sections when helpful.
- Avoids sleeps, real time, network, filesystem, and database unless intentionally abstracted.
- Tests edge cases: null/empty, boundaries, culture, time zones, cancellation, exceptions.

### Integration tests

Use when behavior depends on framework wiring, dependency injection, serialization, database, HTTP, filesystem, message queues, or external process boundaries. Prefer in-memory/fake infrastructure where it preserves the real contract.

### Property or data-driven tests

Use for parsers, converters, numeric algorithms, normalization, and invariants. Keep generated input constraints explicit.

### Snapshot/golden tests

Use for generated text/JSON/code only when diffs are readable and stable. Normalize timestamps, GUIDs, paths, and ordering.

### Test naming

Use existing repository convention. Common choices:

```csharp
[Fact]
public void Parse_returns_error_for_empty_input()
```

or

```csharp
[TestMethod]
public void Parse_WhenInputIsEmpty_ReturnsError()
```

## 4. Debugging workflow

Use evidence before changing code:
1. Capture the exact error, stack trace, input, expected behavior, actual behavior, and environment.
2. Reduce to the smallest failing command or test.
3. Identify the layer: compile, analyzer, test assertion, runtime exception, I/O, concurrency, performance.
4. Form one hypothesis at a time.
5. Add temporary diagnostics or a focused test.
6. Remove temporary diagnostics after the fix.

Do not patch symptoms without explaining the root cause or explicitly labeling uncertainty.

## 5. Compiler and analyzer failure triage

For compiler diagnostics:
- Read the first error by location; later errors may cascade.
- Check generated files if the error points to `obj/` or generated code.
- Check target framework availability for APIs.
- Check namespace/using ambiguity and package versions.
- Check nullable flow warnings as design feedback, not noise.

For analyzer diagnostics:
- Look up the diagnostic ID if uncertain.
- Prefer code changes over suppressions.
- Use `.editorconfig` severity changes only when it is a team policy decision.
- Suppress with justification when the analyzer cannot model the invariant.

## 6. Runtime failure triage

### Exceptions

Classify exceptions:
- Programmer error: `ArgumentException`, `InvalidOperationException`, null contract violations. Fix validation or state transition.
- Environment/transient: I/O, network, timeout, database unavailable. Add retry/circuit/cancellation only where appropriate.
- Data/contract: serialization, schema, parsing, culture/time-zone issues. Fix contract handling and tests.

Rethrowing:

```csharp
catch (Exception ex)
{
    throw new InvalidOperationException("Add useful context.", ex);
}
```

Use `throw;` to preserve stack when rethrowing the same exception.

### Resource lifetime

Check `IDisposable`/`IAsyncDisposable`, stream ownership, `HttpClient` lifetime, database contexts, timers, cancellation token sources, and event unsubscription.

## 7. Async and concurrency bugs

Common causes:
- Blocking on async (`.Result`, `.Wait()`) causing deadlocks or thread-pool starvation.
- Forgetting `await`, losing exceptions.
- Using `async void` outside event handlers.
- Shared mutable collections without synchronization.
- Locking on public objects, strings, or `this`.
- Holding locks across `await`.
- Ignoring cancellation.

Preferred patterns:

```csharp
public async Task<Result> LoadAsync(string id, CancellationToken cancellationToken)
{
    ArgumentException.ThrowIfNullOrWhiteSpace(id);
    return await repository.LoadAsync(id, cancellationToken);
}
```

Use `Channel<T>`, `SemaphoreSlim`, immutable snapshots, concurrent collections, or actor-style ownership before low-level locks. If locking is needed, lock a private object or use the modern `Lock` type when the project supports it.

## 8. Performance workflow

Do not optimize blind. First identify the bottleneck.

1. Write a representative benchmark or measurement.
2. Inspect allocations, CPU, I/O, lock contention, and query/database behavior.
3. Change one thing.
4. Re-measure.
5. Keep readability unless the measurement justifies complexity.

Common C# performance levers:
- Avoid repeated LINQ allocations in hot paths.
- Avoid multiple enumeration.
- Prefer `StringBuilder`, `string.Create`, or interpolation handlers for heavy string construction.
- Use `Span<T>`/`ReadOnlySpan<T>` for parsing/slicing hot paths.
- Pool only when object lifetime and cleanup are clear.
- Prefer `Array.Empty<T>()` over new empty arrays.
- Use `Dictionary<TKey,TValue>`/`HashSet<T>` for membership lookups.
- Avoid exceptions for expected control flow.

Benchmarking:

```bash
dotnet add package BenchmarkDotNet
dotnet run -c Release --project benchmarks/MyBenchmarks
```

## 9. Refactoring workflow

Safe refactoring sequence:
1. Ensure tests exist or add characterization tests.
2. Make mechanical transformations first: rename, extract method/type, move code.
3. Preserve public API unless change is intentional.
4. Run tests after each meaningful step.
5. Remove dead code after verification.

Refactoring targets:
- Long methods with mixed abstraction levels.
- Duplicate validation/parsing/mapping logic.
- Classes with multiple responsibilities.
- Static/global state that blocks tests.
- Implicit null/exception behavior.
- Leaky abstractions around I/O and time.

## 10. Completion report

When finishing a real code task, include:
- Files changed.
- Behavior changed.
- Tests added/updated.
- Commands run and results.
- Known risks or unverified areas.

Example:

```text
Changed:
- src/Foo/Parser.cs: reject empty records before tokenization.
- tests/Foo.Tests/ParserTests.cs: added empty-record regression test.

Verified:
- dotnet test tests/Foo.Tests/Foo.Tests.csproj --filter EmptyRecord
- dotnet build Foo.sln -c Release

Risk:
- Full integration suite not run because database fixture is unavailable.
```
