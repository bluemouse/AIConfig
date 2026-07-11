# Instrumentation and Checks: Tripwires

## Guideline

Build tripwires so a bug announces itself at the fault site instead of corrupting state
silently — assert preconditions and invariants, tag allocations, validate at API boundaries,
and run sanitizers — but only add a check that surfaces the fault **earlier or where it is
cheaper to act on**, never one that merely restates what a crash already told you.

## Rationale

Most expensive bugs are expensive because the symptom appears far from the cause: a buffer
overflow corrupts a neighbor that crashes minutes later; a use-after-free runs cleanly until
freed memory is touched. Tripwires collapse that distance. The discipline is to spend the
check budget where it shortens the gap between fault and detection.

## How to apply

1. Assert every precondition and invariant you control at the boundary that owns it. Treat the assert as executable documentation of the contract.
2. Instrument allocations: file/line tags, per-subsystem totals, assert zero on shutdown — proper teardown plus accounting makes leaks visible.
3. For overwrite-prone allocations (native/debug builds), use a page-guarding allocator so out-of-bounds or use-after-free faults at the offending instruction.
4. When chasing stale references, track liveness as **detection** (not ownership): non-owning refs with retain/release counts tagged with file/line; assert zero at destroy.
5. Run sanitizers in CI and locally when available: ASan (overflow/use-after-free), UBSan (undefined behavior), TSan (data races).
6. Before adding a check, ask what it surfaces that the existing crash/debugger does not. Keep it if it fires earlier, at lower diagnostic cost, or in an automated test; drop it if it only re-states the crash.

## Example

```c
assert(num_flags < MAX_FLAGS);

void *my_malloc(size_t n, const char *file, int line);
#define MY_ALLOC(n) my_malloc((n), __FILE__, __LINE__)
void system_shutdown(system_o *s) { assert(s->alloc_bytes == 0); }

void retain(truth_ref_t *r, const char *file, int line);
void release(truth_ref_t *r);
void destroy_truth(truth_o *t) { assert(t->refcount == 0); }
```

## Gotchas

- A check that only echoes the crash adds runtime cost for no diagnostic gain.
- Asserts must guard facts you control; asserting a hope sends you debugging the assertion.
- Refcounting-for-liveness as a fix converts crashes into leaks — use refs for detection only.
- Page-guarding allocators are heavy — enable for suspect subsystems or debug builds, not globally in shipping.
- Expensive validation gets disabled and rots; size tripwires so they can stay enabled where they matter.

## Related

- `bug-taxonomy.md` — which class each tripwire prevents
- `determinism-and-replay.md` — circular logs and crash dumps
- [../../cpp-memory-guide/SKILL.md](../../cpp-memory-guide/SKILL.md) — C++ ownership design (not active debugging)
