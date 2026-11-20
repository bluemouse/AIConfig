---
name: prompt-clarifier
description: "Iteratively clarify ambiguous requirements, definitions, intent, scope, constraints, acceptance criteria, and authority before or during a task. Use when a prompt has multiple plausible readings, vague terms ('make it better', 'clean this up', 'fast and complete'), conflicting requirements or documents, or missing decisions that change the outcome — including when the user hands over a task and invites questions, or asks for something built from an underspecified spec or migration/plan request. Asks adaptive questions and produces a requirement ledger. Does not trigger on open-ended research (research-guide), planning (plan-guide), or debugging (debugging-guide)."
---

# Prompt Clarifier

Clarify only what materially affects the result through a short adaptive loop — `INSPECT` (read available context first) → `ASK` → `UPDATE` (map answers into the ledger and detect contradictions) → `CHECK` (apply stopping rules) — then proceed or hand off as soon as the task is `actionable`.

## Scope and boundaries

This skill owns the clarification dialogue and produces a settled requirement ledger following [references/requirement-ledger.md](references/requirement-ledger.md) (`.agents/workflow/<slug>/02-requirement-ledger.md` inside the dev-workflow harness; an inline confirmation summary standalone). Once settled, hand off execution to the downstream skill:

- **Open-ended discovery and feature research** → [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Ordered implementation planning** → [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Root-cause defect investigation** → [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)
- **Multi-perspective council deliberation** → [../advisory-council/SKILL.md](../advisory-council/SKILL.md)
- **Single-proposal adversarial stress-test** → [../devil-advocate/SKILL.md](../devil-advocate/SKILL.md)

## What to clarify

Inspect the prompt, conversation, attached files, and low-risk workspace context before asking — never re-ask for supplied or cheaply discoverable facts. Map each answer into the ledger, keep unanswered items explicit rather than silently guessing, and surface contradictions directly instead of inventing a silent compromise (conflict pattern in [references/question-patterns.md](references/question-patterns.md)).

Classify unresolved items and probe only relevant ledger dimensions (outcome, operational definitions, scope/constraints, acceptance criteria, environment, risk/authority — detailed in [references/requirement-ledger.md](references/requirement-ledger.md) and [references/question-patterns.md](references/question-patterns.md)):

- **Blocker:** different answers materially change architecture, workload, or safety — ask first.
- **Useful:** improves quality, but a reasonable default exists — state as a default/assumption unless the user wants to refine.
- **Optional:** omit unless invited.

Turn subjective terms ("fast", "clean", "safe") into measurable thresholds or concrete examples/non-examples.

## Asking

Ask 1–3 questions per turn by default (up to 5 only when independent, quick to answer together, and delaying them would force an extra round). When an active host workflow specifies its own pacing (e.g., one question per turn in `research-guide` or `plan-guide`), follow that skill's pacing.

Rank questions by information gain: prerequisites before dependents, scope/architecture/safety decisions first, no speculative downstream branch questions before the parent branch is chosen. Format each question as one concrete decision with short numbered items, mutually distinct lettered options, a marked `(recommended)` default, and a compact reply hint:

```text
I need two decisions before I can proceed:

1) Target outcome?
   a) Diagnose the cause
   b) Produce a fix (recommended)
   c) Diagnose and fix

2) Compatibility target?
   a) Existing project versions (recommended)
   b) Also support: <versions>
   c) Not sure - use the recommended default

Reply with `defaults`, `1c 2a`, or your own wording.
```

## Handling user responses

- **Partial answer:** acknowledge resolved items and re-ask only remaining blockers.
- **"Use your judgment":** apply recommended defaults and record them in the ledger/summary without re-confirming (unless high-impact or irreversible).
- **"Just do it":** proceed with explicit minimal assumptions on reversible low-risk work; still ask the smallest authorization question for destructive, external, costly, or safety-critical actions.
- **"Unsure":** offer 2–3 concrete options, recommend one with a one-sentence tradeoff, or propose a small reversible probe that gathers the missing fact.

## Stopping (`CHECK`)

Stop asking and mark the task `actionable` when outcome, deliverable, critical definitions, and success criteria are known or safely defaulted and authorized — do not chase complete knowledge when remaining uncertainty is low-impact and reversible. Before substantial execution, summarize the settled outcome, key constraint/scope, and acceptance criteria or assumptions in 1–3 sentences (combine with execution on small tasks).

If required information cannot be obtained safely, mark `blocked`: state the exact missing or conflicting requirement, why it blocks safe progress, and the smallest decision needed. During execution, re-open clarification only when new evidence exposes a hidden requirement, contradiction, or irreversible/safety risk.

## References

- [references/requirement-ledger.md](references/requirement-ledger.md) — required/optional ledger sections and `CHECK` rules
- [references/question-patterns.md](references/question-patterns.md) — question forms, operational definitions, and conflict-resolution template
- [references/examples.md](references/examples.md) — multi-round, conflicting-requirement, and mid-execution clarification examples

## Tool notes

### Claude Code

Questions are plain text and require **ending the turn** to get a reply:
1. Finish `INSPECT` (Read, Grep, Glob, or a read-only subagent for broad searches) before ending a turn; never burn a turn on a question a stated default covers.
2. Send the full question batch in one numbered message with lettered options, `(recommended)`, and the compact reply hint; complete any unblocked reversible work before ending the turn.
3. **Subagents and headless (`claude -p`):** cannot ask the user — skip `ASK`, apply safe defaults, report all assumptions explicitly, and emit the `blocked` summary instead of guessing on irreversible work. Resolve blockers in the parent before dispatching subagents.
4. **Claude.ai (no repo access):** ask for facts that would otherwise be inspected, or ask the user to paste relevant files/configs.

### Cursor

Use the **AskQuestion tool** for discrete choice batches (one question object per decision; put `(Recommended)` first; include `Not sure - use the recommended default` when safe; set `allow_multiple: true` only for true multi-select; fall back to numbered text for open-ended thresholds or examples). Treat open/attached files as supplied context and run Read/Grep/Glob (or an `explore` Task subagent) during `INSPECT`.

In **Plan mode**, front-load blocking decisions and record accepted defaults in the plan (`SwitchMode` to Plan mode when a request turns out to be architecture-shaped). Subagents spawned via the Task tool cannot ask the user — skip `ASK`, state assumptions in the return packet, and flag human-only blockers.

### GitHub Copilot

- **Interactive chat / agent:** use the host's structured question tool (e.g. `ask_user`) when exposed on the active Copilot surface; otherwise send concise numbered questions with lettered options, `(recommended)`, and a compact reply hint. Treat open editors and `#file`/`#selection` attachments as supplied context during `INSPECT`.
- **Background / issue coding agent (non-interactive):** do not stall waiting for a reply — apply recommended defaults, document every assumption and redirect impact in the PR description, prefer the smallest reversible change, and leave unsafe/irreversible work undone with a clear blocker note in the PR or issue comment.
- Suggest recording recurring project-level answers in `.github/copilot-instructions.md` or path-scoped `*.instructions.md`.
