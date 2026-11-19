# Sources

Ported and adapted from a historical reference skill that was deleted on 2026-11-19; this bootstrap skill is now the sole source of truth.

## Game-engine development blog (archive)

- **Last reviewed:** 2026-07-10
- **Used for:**
  - `SKILL.md` → classify-before-trace, gotchas, progressive disclosure
  - `references/bug-taxonomy.md`, `references/reproduction-and-bisection.md`, `references/instrumentation-and-checks.md`, `references/determinism-and-replay.md`, `references/gotchas.md`
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
- `references/diagnostic-techniques.md` — consolidated tracing, comparison, and bisection tactics
- Workflow steps for scope freeze, working-pattern comparison, verification ladder, and sibling-skill boundaries

## Refresh Workflow

1. Re-check the external sources above (game-engine blog archive, rr, sanitizers) for updated material
2. Update corresponding `skills/debugging-guide/references/<topic>.md` and `SKILL.md` workflow/gotchas
3. Bump **Last reviewed** date above
