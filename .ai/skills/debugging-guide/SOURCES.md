# Sources

Ported and adapted from `references/skills/debugging-guide/` in this repository.

## Game-engine development blog (archive)

- **Last reviewed:** 2026-07-10
- **Used for:**
  - `SKILL.md` → classify-before-trace, gotchas, progressive disclosure
  - `references/bug-taxonomy.md`, `references/scientific-debugging.md`, `references/reproduction-and-bisection.md`, `references/instrumentation-and-checks.md`, `references/determinism-and-replay.md`, `references/gotchas.md`
- **Aspects extracted:**
  - "A Taxonomy of Bugs" — bug classes and per-class prevention-by-design
  - "A Debugging Story" — hypothesis ranking, confirm-before-fix, repro shrinking, git bisect failure modes, determinism and record/replay

## Reverse-execution / record-replay tooling

- **URLs:**
  - https://rr-project.org/
- **Last reviewed:** 2026-07-10
- **Used for:**
  - `references/determinism-and-replay.md`
- **Aspects extracted:** Record/replay and reverse-execution to step backward from a failure; overhead/limits on large programs

## Sanitizers (compiler-maintained tripwires)

- **URLs:**
  - https://clang.llvm.org/docs/AddressSanitizer.html
  - https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
  - https://clang.llvm.org/docs/ThreadSanitizer.html
- **Last reviewed:** 2026-07-10
- **Used for:**
  - `references/instrumentation-and-checks.md`, `references/gotchas.md`
- **Aspects extracted:** ASan, UBSan, TSan as automated tripwires

## Bootstrap additions (not from reference skill)

- `references/debugging-report.md` — agent handoff report template
- `references/diagnostic-techniques.md` — consolidated tracing, comparison, and bug-class table
- Workflow steps for scope freeze, working-pattern comparison, verification ladder, and sibling-skill boundaries

## Refresh Workflow

1. Re-read upstream sources in `references/skills/debugging-guide/SOURCES.md`
2. Diff against the ported bootstrap references
3. Update corresponding `skills/debugging-guide/references/<topic>.md` and `SKILL.md` workflow/gotchas
4. Bump **Last reviewed** date above
