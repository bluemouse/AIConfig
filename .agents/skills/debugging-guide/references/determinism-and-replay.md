# Determinism and Replay: Intermittent Bugs

## Guideline

When a bug comes and goes, make it reproducible before trying to fix it — remove sources of
nondeterminism, stress the suspect system to raise the hit rate, capture state into a
circular log that dumps on detection, or record/replay execution to step through the "before"
after the fact.

## Rationale

A reproducible bug can be stepped through in a debugger _before_ it fails; a random one cannot.
The battle with intermittent bugs is converting them into deterministic ones. When you can't
get a clean repro, raise the reproduction rate (stress) and capture enough state at failure
(circular logs, crash dumps) to reconstruct the cause.

## How to apply

1. Hunt nondeterminism: uninitialized memory, unordered iteration, time/random seeds, thread scheduling, network timing, cache state. Confirm threading involvement with a single-threaded fallback — if the bug vanishes, it's likely a race.
2. Where feasible, make execution a deterministic function of inputs (same inputs → same state).
3. If you can't reproduce on demand, stress the suspect path — e.g. repeat the failing operation hundreds of times per frame to turn a once-an-hour crash into seconds.
4. Capture the "before" without a live debugger: log key events to a fixed-size circular buffer and dump it when the bug is detected.
5. For bugs that still resist, use record/replay or reverse-execution tooling; verify the capture reproduces the failure and accept overhead limits on large threaded programs.
6. At scale, group automatic crash reports by stack trace + message and prioritize by frequency and user impact.

## Example

```c
bool g_single_threaded = false;   // if bug vanishes, suspect a race

for (int i = 0; i < 200; ++i) { open_window(); close_window(); }

typedef struct { char lines[1024][128]; uint32_t head; } ring_log_t;
void log_event(ring_log_t *l, const char *msg);
void on_bug_detected(ring_log_t *l) { dump_ring(l); }
```

## Gotchas

- Logging or single-threaded mode can perturb timing and hide a race — when the bug vanishes under instrumentation, that is evidence of a timing bug, not a fix.
- A circular buffer that's too small drops needed events; size it for the plausible cause-to-detection window.
- Stressing can provoke a _different_ bug — confirm the stressed crash matches the original symptom.
- Record/replay has overhead and limits; treat as fallback after stress + logging fail.
- Making execution deterministic may require design changes when the system depends on wall-clock time, addresses, or thread interleaving.

## Related

- `reproduction-and-bisection.md` — shrink and bisect once deterministic
- `instrumentation-and-checks.md` — circular logs and sanitizer tripwires
- `gotchas.md` — heisenbug misreadings
