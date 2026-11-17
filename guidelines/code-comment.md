---
description: "Load when writing or updating code comments or commit messages — explain why not what, fix code before commenting, keep comments true, document API contracts, and justify TODO/FIXME markers."
---

# Code Comment Guidelines

Rules for writing and maintaining code comments — and commit messages, which
are comments about the change and follow the same principles. A comment is a
maintenance tool, not decoration: it carries the information code cannot
express — intent, constraints, context — and nothing else.

**Tradeoff:** These rules bias toward fewer, higher-value comments. When in
doubt, delete the comment rather than write one that restates the code.

## 1. Explain why, not what

**The code says what happens. The comment says why.**

Comment what the code cannot:
- Why this approach and not the obvious alternative.
- Why a value, limit, or formula is what it is.
- Why a call is skipped, reordered, duplicated, or deliberately absent.
- What external constraint (spec, platform quirk, bug workaround) forced this shape.

Bad:  `i++; // increment the counter`
Good: `// Back off 200ms: firmware drops commands sent sooner (datasheet §4.2, errata 3).`

## 2. Fix the code before commenting it

**If a comment exists to explain the code, rewrite the code instead.**

- Unclear code gets better names, smaller functions, earlier returns — not prose.
- A block narrated line-by-line is a symptom: extract a well-named function and
  delete the narration.
- Comment only what survives the rewrite — the why that names and structure
  cannot carry.

## 3. Keep comments true or delete them

**A wrong comment is worse than no comment; readers trust it.**

- When an edit changes behavior, update or remove every comment it invalidates
  in the same edit. Stale comments are the most common comment defect in
  generated diffs.
- Never leave a comment describing the old behavior of code you just changed.
- If a comment's claim cannot be verified against the current code, delete it.

## 4. Document contracts at API boundaries

**Public interfaces get doc comments even when the implementation is clear.**

Use the project's doc-comment format and state what a caller cannot learn from
the body:
- Purpose, preconditions, and postconditions.
- Parameter units and ranges, return-value meaning, error behavior.
- Ownership, lifetime, and thread-safety ("caller frees", "not thread-safe",
  "callers must hold mu").
- Side effects: I/O, mutation, caching, blocking.

Do not restate the signature (`/// @param x The x.`) — document what the
signature cannot say.

## 5. Mark gotchas with their justification

**TODO, FIXME, and workaround markers carry their reason.**

- Every marker names why it exists and, where possible, the exit condition or
  issue link: `// FIXME: leaks on early return; tracked in #412.`
- A bare `// TODO` or `// hack` with no context is a defect, not a comment.
- A workaround states what it works around and what would remove it.

## 6. Cite sources; stay self-contained

**Formulas, magic numbers, and ported algorithms carry their origin.**

- Magic values get their derivation or reference:
  `0.9773f // sqrt(1 - beta2^t), Adam paper eq. 1`.
- Ported or adapted code cites where it came from.
- A comment must make sense to a reader with only the repository — no chat
  context, session ids, or ephemeral review artifacts. Write the why inline.

## 7. Match the file; never narrate the session

**Comment density and style follow the surrounding code.**

- Use the project's existing comment convention — doc format, language, tone,
  punctuation.
- A sparsely-commented file stays sparse: comment the genuinely non-obvious,
  not everything you touched.
- No edit narration ("// changed from X to Y", "// added for the refactor") —
  commit messages carry that.
- Never commit commented-out code; version control keeps history.

## 8. Commit messages follow the same rules

**The diff says what changed. The commit message says why.**

- The subject states the why in one line; the body explains intent,
  constraints, and trade-offs — never a section-by-section narration of the
  diff.
- Self-contained: no chat context, session references, or "as discussed" —
  a reader with only the repository must understand it.
- Keep it true: never claim behavior the commit does not deliver.
- Match the project's commit convention — subject limits, format, tone.

---

**These guidelines are working if:** new comments answer why-questions the code
cannot, public contracts have doc comments, no stale comment survives the edit
that invalidated it, diffs contain no commented-out code or session
narration, and commit messages explain why without restating the diff.
