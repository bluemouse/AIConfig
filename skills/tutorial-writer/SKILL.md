---
name: tutorial-writer
description: "Write, revise, and critique example-driven technical tutorials, quickstarts, walkthroughs, SDK lessons, and user guides — building progressive runnable examples with observable outcomes and source-backed claims."
---

# Tutorial Writer

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`; resolve
`references/` paths from there.

Create tutorials that reach a useful result before absorbing theory: start with a
small working example, explain only the concepts it makes necessary, then evolve the
same example toward the requested level of practical use. Do not implement features,
fix bugs, create tickets, publish docs, or post reviews unless requested.

## When NOT to Use

- **Codebase onboarding / architecture guides** —
  [../code-professor/SKILL.md](../code-professor/SKILL.md) learns an existing
  repository; this skill teaches a product or API through a new walkthrough
- **Open-ended product or technology research** —
  [../research-guide/SKILL.md](../research-guide/SKILL.md) while the idea, tradeoffs,
  or requirements are still unformed
- **Ambiguous authoring scope** —
  [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) when the user cannot
  say what guide they need or what outcome matters
- **Git diff / code review** — [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Meeting minutes / decision records** — the `guidelines-minutes` guideline-skill
- **API reference with no learning path** — this skill needs a reader outcome and
  progressive examples
- **Marketing copy, release notes, generic summaries** — out of scope
- **Content needing unsupported claims or invented behavior** — refuse or narrow
  until source material exists

## Inputs and source fidelity

1. Identify the topic, intended reader, desired outcome, environment or version, and
   available sources.
2. Inspect provided documentation, code, and configuration before describing their
   behavior; prefer primary sources for version-sensitive details.
3. Nonessential details: pick a reasonable default and state the assumption near the
   affected step; if it changes the outcome, compatibility, safety, or code, ask a
   focused question or present a bounded draft.
4. Never invent APIs, options, commands, outputs, error messages, benchmarks,
   compatibility claims, screenshots, or source attribution; never claim examples ran
   unless validated.
5. Preserve the user's terminology, paths, commands, versions, and style conventions
   unless correcting a source-backed error.

## Workflow

**Guide shape.** Tutorial: one coherent outcome through a running example. User
guide: quickstart then common-to-advanced tasks, preserving example continuity.
Review: identify reader and target outcome, return prioritized findings (accuracy,
learning flow, examples, verification, accessibility), rewriting only authorized
sections.

**Example ladder.** One running example by default — a second only for a genuinely
different use case — progressing from quick first success through minimum mental
model, a limitation-exposing extension, end-to-end integration, and professional
use. See [references/tutorial-patterns.md](references/tutorial-patterns.md) §1 for
the stage pattern.

**Each learning step.** State the goal; show the code, command, UI action, or
configuration; show an observable result (output, response, state change,
screenshot, or test); then explain only the concepts needed now. When a new
limitation motivates the next change, verify with observable proof. Complete
runnable code when the reader needs it, else the smallest meaningful diff with
omissions marked; keep names, paths, and expected output consistent across steps.

**Visuals.** Add a visual only when it answers a question more clearly than prose;
frame it with that question and state the takeaway after (reference §2 selector).
Screenshots only when the user provides or requests them or a verified environment
can capture them.

**Validation.** Make setup and prerequisites visible before the first action needing
them. Verify representative code and commands when tools and a suitable environment
are available — report what ran and its result, or state execution was not
performed. Troubleshooting only for likely, source-supported failures tied to the
guide's examples: symptom, cause, safe fix.

## Writing rules

- Reach the first useful example within two short orientation paragraphs; lead with
  concrete artifacts (code, commands, outputs, diagrams, screenshots, UI actions) and
  explain after the reader sees something real.
- Expected output and before/after evidence over vague claims like "faster."

## Completion checklist

Before delivering a tutorial, guide, or review, confirm:

1. **Outcome** — reader level, desired result, environment or version clear.
2. **Source fidelity** — APIs, commands, outputs, visuals source-backed or labeled as
   assumptions; nothing invented.
3. **Example ladder** — quick first success; one idea per step; explanations follow
   the motivating example.
4. **Evidence** — key behavior has observable, consistent proof; professional concerns
   demonstrated, not listed.
5. **Scope** — guide shape matches the request; unrelated workflows not forced
   together.
6. **Safety** — no implementation, publishing, or ticket work unless requested.

## Resources

- [references/tutorial-patterns.md](references/tutorial-patterns.md) — example
  ladder, visual selector, review rubric, anti-patterns
