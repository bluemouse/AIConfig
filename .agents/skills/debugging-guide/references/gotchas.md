# Debugging Gotchas

Common misreadings and anti-patterns that send investigations off track.

## Crash and memory signals

- **Access violation / segfault** is about an unmapped address, not permissions or threading — it almost always means a garbage or dangling pointer was dereferenced.
- A **freed-memory fill pattern** (e.g. `0xdddddddd` on Windows debug heaps) at a sane mapped address points to **use-after-free**, not a random overwrite — random writes rarely produce a clean repeating byte pattern.
- A crash on the **first line** of a function rules out "the bug is inside this function's logic" — look upstream for the bad input or lifetime.
- Reaching for **"compiler bug"** before ruling out your own undefined behavior is almost always wrong; test another compiler/opt level and inspect the assembly first.

## Reproduction and bisection

- A bug that lands "in the same spot every time" is a reasonable but **unproven** 100% repro; if it later "disappears," revise the assumption rather than trusting it.
- **`git bisect` lies** when the repro is flaky or GOOD/BAD is mis-tagged, and incremental builds can mislead — force clean rebuilds and only bisect a deterministic repro.
- The offending commit names **which subsystem changed**, not necessarily the buggy line — large diffs still need hypothesis-driven stepping.
- Bisection is slow; try a direct hypothesis first and bisect when the cause is genuinely unclear.

## Instrumentation and fixes

- Adding validation that only re-reports what the debugger already showed you (e.g. "this pointer was freed") buys nothing — instrument to surface the fault **earlier** or where it is cheaper to act on, not to restate it.
- A symptom **disappearing** is not proof of a fix — random edits can perturb timing or layout enough to mask a cause that is still present.
- **Garbage collection / refcount-for-liveness** doesn't fix a stale-reference bug — it converts a loud crash into a quiet leak plus subtler "two systems, two states" logic bugs.
- **"Never free / never shut down"** looks simpler but hides lifetime bugs — proper teardown exposes stale-pointer and double-ownership bugs early.

## Intermittent and concurrent bugs

- Adding logging or a single-threaded flag can **perturb timing** and hide a race (a heisenbug) — when the bug vanishes under instrumentation, that itself is evidence of a timing/ordering bug, not a fix.
- Stressing a path raises frequency but can also change allocation patterns — confirm the stressed crash is the **same** bug, not a new one you provoked.
- Record/replay tools have real overhead and limits on large threaded programs — verify the capture reproduces the failure before trusting it.

## Design and prevention

- A **design flaw** cannot be coded around at every call site — recognize the class and fix the API or type model.
- An assertion encodes a belief; a wrong assertion sends you debugging the check instead of the code — assert facts you control, not hopes.
