# Bug Taxonomy: Classes and Prevention-by-Design

## Guideline

Treat every bug as a member of a class, and for each class prefer a design change that makes
the whole class impossible (or trivially detectable) over fixing the one instance —
classify first, then ask "what would have prevented every bug like this?"

## Rationale

Bugs are not all the same animal; the cheapest fix differs per class, and the highest
leverage move is usually structural, not local. A logic error is 100% reproducible and
yields to readable code; an unexpected initial condition yields to an assertion; a leak
yields to allocation accounting; an overwrite yields to a page-guarding allocator or
sanitizer; a race yields to a single-threaded fallback and a thread sanitizer; a design
flaw yields only to a redesign. Spending a moment after each fix to identify the class
and the structural prevention turns one fix into immunity from a family of future bugs.

## Bug classes

| Class | Typical evidence | Structural prevention |
| --- | --- | --- |
| Typo / logic error | failing assertion, missing branch, boundary input | descriptive names, `const`, warnings, formatter, fewer code paths |
| Unexpected initial condition | bad input at API boundary, violated precondition | assert preconditions at the owning boundary |
| State mutation | first invalid write, wrong mutation order | fix at writer; preserve invariant |
| Leak | growing memory, resources not released on shutdown | allocation tagging, per-subsystem totals, zero-on-shutdown |
| Overwrite / use-after-free | sanitizer output, fill patterns, bounds fault | page-guard allocator (debug), ASan/UBSan, correct ownership |
| Race / concurrency | flake under load, TSan report, vanishes single-threaded | single-thread fallback for triage, TSan, enforce ordering |
| Build / config | wrong generated file, flag, env, dependency version | fix propagation at source, not consumer workaround |
| Platform behavior | OS/API/SDK difference | isolate platform contract; test affected platform |
| Integration / schema | payload mismatch, version skew, auth context | fix boundary contract; add contract/integration test |
| Flakiness | seed/order/time dependency | determinism, stress, circular log, record/replay |
| Design flaw / failed spec | repeated symptom at many call sites | type-safe single-purpose APIs; make misuse unrepresentable |

## How to apply

1. **Typo / logic error:** lower the surface area for wrong code — descriptive names, `const`, compiler warnings, formatter, fewer code paths. Reproducible; falls to careful read and debugger.
2. **Unexpected initial condition:** assert at the boundary that owns the contract — `assert(count < MAX)` documents the precondition and pins responsibility on the caller. See `instrumentation-and-checks.md`.
3. **Leak:** instrument allocations with file/line, total per subsystem, assert counter is zero on shutdown.
4. **Overwrite:** route suspect allocations through a page-guarding allocator or run ASan so bad writes fault at the offending instruction.
5. **Race:** add a single-threaded fallback to confirm threading involvement; run TSan; keep concurrency to simple patterns.
6. **Design flaw / failed spec:** step back and surface the unstated assumption; redesign so misuse is unrepresentable — single-purpose APIs, types that prevent wrong calls, explicit handles instead of implicit global state.

## Example

```c
// Unexpected initial condition -> assert the precondition (caller's responsibility).
void add_flags(flags_t *f, const flag_t *src, uint32_t n) {
    assert(f->count + n < MAX_FLAGS);
    memcpy(f->items + f->count, src, n * sizeof *src);
    f->count += n;
}

// Design flaw: ambiguous API — ensure_html_encoded() can't tell encoded from raw input.
void ensure_html_encoded(char *s);
// Fix the CLASS: make the type carry the state so misuse is unrepresentable.
typedef struct { char *raw; } raw_text_t;
typedef struct { char *html; } html_text_t;
html_text_t html_encode(raw_text_t in);
```

## Gotchas

- "Never free / never shut down" hides lifetime bugs — proper teardown exposes them early.
- A design flaw cannot be coded around — recognizing the class saves repeated symptom fixes.
- Reaching for "compiler bug" is the last resort after ruling out undefined behavior.

## Related

- `instrumentation-and-checks.md` — tripwires per class
- `determinism-and-replay.md` — intermittent bugs
- `diagnostic-techniques.md` — bug-class table during tracing
- [../../cpp-memory-guide/SKILL.md](../../cpp-memory-guide/SKILL.md) — C++ ownership and lifetime design (not active debugging)
