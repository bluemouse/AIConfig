# Parallel Scope Passes (deep effort)

Dispatch details for `code-reviewer` at `deep` effort. `SKILL.md` summarizes the flow:
align inline → one parallel pass per selected scope → cross-scope dedup → adversarial
verify → gap sweep. This file holds the prompt template and the per-environment
mechanics.

## Why Scope & Intent Alignment stays with you, not as a 7th parallel pass

It's shared context every domain lens needs (what the change is trying to do, anything
obviously incomplete or off-scope). Computing it once and handing the summary to every
scope pass avoids independent, possibly-inconsistent guesses at intent — and keeps it
distinct from the six domain checklists, which are genuinely independent lenses that
are safe (and faster) to run in parallel.

## Scope-pass prompt template

Paste real content, not a pointer; parallel passes do not have the parent `SKILL.md`
loaded:

```
You are reviewing a code change through the "<scope>" lens only.

## The diff under review
<the full resolved diff, or exact instructions to reproduce it, e.g. "run
`git --no-pager diff --staged` yourself in the repo at <cwd>">

## Context on intent (from a prior alignment pass)
<2-5 sentence summary: what the change appears to be trying to do, and any
drift/incompleteness already noticed>

## Your checklist for this scope
<the specific bullet list for this one scope, copied verbatim from
<SKILL_ROOT>/references/scope-checklists.md — paste the actual items, don't just refer
to the file; append any matching Conditional Extensions bullets for this scope>

## What to return
Read surrounding code as needed (call sites, related tests, existing
patterns) before flagging anything. Cap yourself at 6 candidates for this
scope.

Return each candidate as a markdown block with: Severity
(blocker/major/minor), Location (file and line), What's wrong, Why it matters,
Proposed fix.
```

## Cross-scope reconciliation

Once all scope passes return, collect all per-scope finding lists and dedupe by (file,
overlapping line range, similar description). If two scopes flag essentially the same
underlying issue (e.g. `security` and `correctness` both flag the same unvalidated
input), merge into one finding, tag it with both scopes, and keep the more severe
rating.

## Verify pass

For each deduped candidate, reread the exact diff hunk and surrounding code yourself;
assign CONFIRMED, PLAUSIBLE, or REFUTED. Be recall-biased — default to PLAUSIBLE, not
REFUTED, when genuinely unsure. Drop REFUTED findings.

## Sweep for gaps

One final fresh read — don't reuse any scope pass's notes — looking only for defect
classes nothing above caught. Specifically check for: a guard clause dropped during a
move/extract refactor, a mutable default evaluated once instead of per-call, a lock
scope that shrank, asymmetric test setup/teardown, a flipped config default, or any
checklist bullet for a selected scope that a scope pass never addressed at all.

## Environment dispatch

**Claude Code** — in a single turn, spawn one subagent per *selected* scope, all in
parallel when possible. Each prompt must include the full resolved diff (or exact git
commands to reproduce it), the intent summary, and checklist bullets copied verbatim
from `scope-checklists.md` (plus matching Conditional Extensions). Instruct each
subagent to read surrounding code with its available tools before flagging anything,
and to return up to 6 candidates in the shared markdown format. When subagent
completion notifications include `total_tokens` and `duration_ms`, note them if
comparing efficiency across review runs. Collect all subagent replies, then run
cross-scope dedup, verify pass, and gap sweep yourself.

**Claude.ai (no Claude Code CLI)** — no parallel subagents are available; run scope
passes sequentially yourself, keeping notes separate per scope, then dedup, verify, and
gap-sweep.

**Cursor** — use the Task tool with `subagent_type: "generalPurpose"` (it has
Read/Grep/Shell access to inspect surrounding code): one Task call per *selected* scope
in a single message, using the prompt template above with real diff content. You
receive only each subagent's **final text reply**, not its tool calls — append the
ReportFindings block below to each scope-pass prompt. For a quick native GitHub post you
may suggest the built-in `/code-review --comment`, but prefer github-guide for
`REQUEST_CHANGES`, multi-comment batching, or thread resolution via `gh api`.

```
Use Read/Grep/Shell as needed to inspect call sites, related tests, and existing patterns
before flagging anything.

If a ReportFindings tool is available in your environment, you may call it once at the end
with raw candidates (file, line, summary, failure_scenario, category: "<scope>") — but
your final reply text must still restate each candidate with Severity, Location, What's
wrong, Why it matters, and Proposed fix, because the orchestrator only receives your final
text message.
```

**GitHub Copilot** — Copilot Chat does not expose parallel subagents; run scope passes
**sequentially** in one session, reading `scope-checklists.md` for each scope (and
matching Conditional Extensions), applying the *how to look* heuristic, and keeping
notes separate per scope. After all scopes, run cross-scope dedup, verify pass, and gap
sweep yourself. Do not skip the verify or gap-sweep stages just because passes were
sequential — they are what separate `deep` from `standard`.
