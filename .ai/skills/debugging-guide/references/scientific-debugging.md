# Scientific Debugging: Hypothesis-Driven Investigation

## Guideline

Debug like a scientist — form one falsifiable hypothesis about the cause, change exactly one
thing, predict the outcome before you run, observe, and let the result narrow the search;
never edit at random hoping the symptom goes away.

## Rationale

The default move on a reproducible bug is to break into the debugger _before_ the failure
and step through, comparing what the code actually does against what you believe it should
do — the bug lives in that gap. Random edits ("flailing") can make a symptom vanish
without removing the cause. A single-variable experiment with a prediction is decisive: a
confirmed prediction advances you; a violated prediction narrows the search. Confirm the
hypothesis cheaply _before_ committing to a fix direction.

## How to apply

1. State the hypothesis as something that could be false: "the `tt` pointer passed in is dangling," not "something's wrong with memory."
2. Read the evidence the failure already handed you and rank causes by likelihood:
   - Access violation / segfault → unmapped or dangling address (not permissions or threading).
   - Crash on first line of a function → rules out in-function logic; look upstream.
   - Mapped address with freed-memory fill pattern → use-after-free over random overwrite.
   - Assertion at API boundary → unexpected initial condition or violated contract.
   - Flaky under load, vanishes single-threaded → concurrency/race hypothesis.
3. Pick the cheapest experiment that could _disprove_ the leading hypothesis.
4. Change one variable, predict the result, run, observe. If confirmed, walk data flow one hop further; if refuted, take the next hypothesis.
5. Confirm before fixing: breakpoint where the suspect object is destroyed, log pointers, or add a temporary assertion — know the cause before changing code.
6. After the fix, re-run the repro — a fix you didn't verify is a hypothesis, not a fix.

## Example

```text
Symptom : read access violation, tt->object_types, first line of changed_objects()
Rank    : (1) tt is a dangling pointer        <- access violation = unmapped address
          (x) bug in changed_objects() logic  <- ruled out: crashes before any logic runs
          (x) permissions error               <- access violation is not a security issue
          (x) missing lock                    <- access violation is not a threading error
Look    : watch window shows tt mapped, but *tt is all 0xdddddddd  -> use-after-free
Confirm : breakpoint in destroy_truth(); destroyed Truth == later dereferenced. Holds.
Narrow  : trace callers to the stale holder; fix at source; re-run repro.
```

## Gotchas

- A symptom disappearing is not proof of a fix.
- Trust the error's actual meaning over its scary name.
- Confirming the obvious is cheap insurance before hours down a rabbit hole.
- Changing two things at once destroys the experiment.
- Stepping backward through _data flow_ (where did this value come from?) is usually more decisive than stepping forward through control flow.

## Related

- `reproduction-and-bisection.md` — reliable repro before stepping
- `instrumentation-and-checks.md` — cheap confirmation experiments
- `gotchas.md` — crash signal misreadings
