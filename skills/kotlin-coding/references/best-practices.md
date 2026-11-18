# Kotlin non-obvious rules

Style, naming, API design, and stdlib selection are training-data restatement — this
file holds only the rules implementations tend to get wrong.

## Null safety and state modeling

- Convert platform/foreign nullability to explicit Kotlin types at boundaries; treat
  static analysis suppressions as code comments — narrow scope, explain why, remove when
  obsolete.
- Replace multiple related nullable fields with a sealed state when only certain
  combinations are valid; avoid nullable mutable state when a constructor argument,
  `lazy`, or state object can encode lifecycle.
- Do not return `null` and throw for the same failure mode in one API family; for
  expected domain failures with details, use a sealed result.

## Coroutines and concurrency

- Keep coroutine use structured — parent scopes own child jobs; avoid `GlobalScope`;
  avoid production `runBlocking` except at application boundaries.
- Never catch and suppress `CancellationException`.
- Inject dispatchers/scopes for testable asynchronous code.
- Keep synchronized/locked sections small; never call unknown user code while holding
  a lock.
- Use `StateFlow`/`SharedFlow` only when the project already uses coroutines and
  reactive streams are appropriate; otherwise use simple callbacks or synchronous APIs.

## Collections

- Use `Sequence` only for large, lazy, or early-terminating pipelines — eager
  collections for normal small/medium transformations.
- Know which operations throw (`first`, `single`, `reduce`, direct indexing) and prefer
  the `*OrNull` variants for expected absence.
- Avoid repeated list/string concatenation in loops — use `buildList`/`buildString`/
  `joinToString` or a mutable local accumulator.

## Exceptions and validation

- `require` for invalid caller arguments; `check` for invalid object state; `error`
  for impossible code paths; `toXOrNull` parsing APIs for expected invalid text.
- Preserve causes when wrapping exceptions.

See [tooling.md](tooling.md) for toolchain wiring.
