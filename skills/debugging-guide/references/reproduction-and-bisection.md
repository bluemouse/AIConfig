# Reproduction and Bisection

## Guideline

Before debugging, get a reliable reproduction, then aggressively shrink it to the smallest
deterministic steps that still trigger the bug; once it is ~100% reproducible, bisect the
version history to the commit that introduced it.

## Rationale

A reproducible bug lets you break in _before_ the failure and step through the cause. Shrinking
the repro iterates faster and reveals the shape of the root cause. Bisection turns "somewhere
in N commits" into a logarithmic search — but it is only as trustworthy as the repro and the
GOOD/BAD labels feeding it.

## How to apply

1. Confirm the bug reproduces. Treat "100% reproducible" as a working assumption, not a proven fact; revise if the bug later disappears.
2. Simplify the trigger. Replace a slow end-to-end path with the fewest steps that still fail (e.g. instead of a whole packaging task, "start app and create project twice").
3. If you can't simplify steps, simplify _data_: shrink the input until removing anything more makes the bug vanish.
4. With a deterministic repro, bisect history. Mark known-good and known-bad revisions; each step builds cleanly and runs the repro to label GOOD or BAD.
5. Read the offending commit with the bug in mind. A large diff may point at _which subsystem_ changed, not the buggy line — return to hypothesis-driven stepping.
6. For a random bug you can't shrink, increase reproduction rate by stressing the suspect system — see `determinism-and-replay.md`.

## Example

```bash
git bisect start
git bisect bad
git bisect good v2021.2
cmake --build build && ./app --new-project --new-project
git bisect bad   # or: git bisect good — repeat until it lands
git bisect reset
```

## Gotchas

- A flaky repro corrupts bisection — one mislabeled GOOD/BAD points at the wrong commit.
- Incremental builds during bisect can pick up stale objects; force clean rebuilds when results look inconsistent.
- Bisection is slow — try a direct hypothesis first; bisect when the cause is genuinely unclear.
- The offending commit names where the change landed, not necessarily the buggy line.
- For intermittent bugs, stress or determinism tactics come before bisect — see `determinism-and-replay.md`.

## Related

- `scientific-debugging.md` — hypothesis-first when bisect is too slow
- `determinism-and-replay.md` — intermittent repro tactics
- [../../git-guide/SKILL.md](../../git-guide/SKILL.md) — git mechanics during bisect
