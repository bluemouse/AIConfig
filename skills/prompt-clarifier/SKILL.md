---
name: prompt-clarifier
description: Iteratively clarify ambiguous requirements, definitions, intent, scope, constraints, acceptance criteria, environment, risks, and expected outputs before or during a task. Use when a prompt has multiple plausible interpretations, uses vague or overloaded terms, omits decisions that would materially change the result, contains conflicting requirements, or leaves the AI unsure what successful completion means. Ask adaptive, high-information questions in small batches, update the working interpretation after every answer, and continue until the task is actionable, the user accepts explicit assumptions, or safety requires stopping.
---

# Prompt Clarifier

Clarify only what materially affects the result. Use a short adaptive dialogue instead of a static questionnaire, then proceed as soon as the task is actionable.

## Scope and boundaries

This skill owns the clarification dialogue itself: deciding what is unresolved, what to ask, when to stop asking, and how to record the resulting interpretation. It applies to any task type and runs before or during the work.

It does not own the work that follows — see **When NOT to Use** for deferrals.

Use this skill to settle blocking decisions, then hand the settled requirement ledger to the skill that performs the work (see **When NOT to Use**).

## When NOT to Use

- **Open-ended discovery and feature research with agreement gates** — use [../research-guide/SKILL.md](../research-guide/SKILL.md)
- **Turning a settled interpretation into an ordered implementation plan** — use [../plan-guide/SKILL.md](../plan-guide/SKILL.md)
- **Root-cause investigation of a reproducible defect** — use [../debugging-guide/SKILL.md](../debugging-guide/SKILL.md)

## Core contract

1. Inspect the prompt, conversation, available files, and low-risk sources before asking.
2. Identify unresolved decisions that could change the approach, output, safety, cost, or definition of success.
3. Ask the smallest high-value question set.
4. Incorporate the answers into a working requirement ledger.
5. Detect new ambiguity, contradictions, or dependencies revealed by the answers.
6. Repeat while material blockers remain and each next question has useful information value.
7. Confirm the final interpretation briefly, then perform the task or hand off to the owning skill per **When NOT to Use**, carrying the requirement ledger.

Do not confuse complete knowledge with sufficient specification. Stop asking when remaining uncertainty is low-impact, safely reversible, or covered by an explicit default.

## Clarification state machine

Move through these states:

`INSPECT -> ASSESS -> ASK -> UPDATE -> CHECK -> {ASK | CONFIRM | PROCEED | STOP}`

### INSPECT

Gather context that is already available without committing to a solution:

- Read the current prompt and relevant conversation history.
- Inspect provided files, configs, examples, schemas, or existing conventions.
- Use available read/search tools when a quick, low-risk lookup can resolve the question.
- Preserve facts already supplied by the user; never ask for them again.

### ASSESS

Create or update a private requirement ledger. Track only dimensions relevant to the task:

- **Outcome:** What change, answer, decision, or artifact is wanted?
- **Intent:** Why is it needed, and what decision or action should it support?
- **Audience:** Who will consume or use the result?
- **Deliverable:** What form, format, length, level of detail, or interface is expected?
- **Scope:** What is included, excluded, or explicitly unchanged?
- **Definitions:** What do vague, overloaded, domain-specific, or subjective terms mean here?
- **Inputs and sources:** What data, files, systems, or evidence may be used?
- **Constraints:** What technical, legal, policy, compatibility, performance, cost, time, style, or dependency limits apply?
- **Environment:** What runtime, platform, versions, tools, repository, or deployment context matters?
- **Acceptance criteria:** What observable conditions make the result correct or complete?
- **Risk and reversibility:** What could cause harm, data loss, publication, spending, or difficult rollback?
- **Authority:** What may the AI decide, change, send, publish, delete, or execute without further approval?

Classify each unresolved item:

- **Blocker:** Different answers would materially change the work or make it unsafe to proceed.
- **Useful:** Improves quality but a reasonable default exists.
- **Optional:** Nice to know; do not ask unless the user invites deeper refinement.

Ask about blockers first. Usually defer useful items to defaults and omit optional items.

### ASK

Ask one to three questions per turn by default. Ask up to five only when they are independent, easy to answer together, and delaying them would create extra rounds.

When another skill is driving the task and specifies its own question pacing — for example one decision per turn during a research dialogue or a planning pass — follow that skill's rule instead. Its pacing reflects the rhythm of that workflow; batching against it costs more than it saves.

Choose the next question by expected information gain:

1. Prefer a question that eliminates several plausible interpretations.
2. Prefer decisions that affect scope, architecture, safety, or acceptance criteria.
3. Ask prerequisite questions before dependent questions.
4. Avoid asking about details that can be inferred, discovered, or safely defaulted.
5. Do not ask speculative future questions before the current branch is selected.

Make each question easy to answer:

- Ask for one concrete decision per question.
- Use short numbered questions.
- Offer mutually distinct options when the likely answers are known.
- Mark a recommended default and explain it only when the reason is not obvious.
- Include `Not sure - use the recommended default` when appropriate.
- Permit compact replies such as `1b 2a` or `defaults`.
- Ask for an example and a non-example when a subjective term needs an operational definition.
- Use placeholders only when the user can fill them directly.

Use this pattern when suitable:

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

Do not ask:

- Questions already answered in the prompt or conversation.
- Questions answerable by a quick, low-risk inspection.
- Broad prompts such as "Can you clarify?" or "What do you want?"
- Multiple decisions hidden inside one sentence.
- "Anything else?" when no material ambiguity remains.
- Questions whose answers would not change the work.

### UPDATE

After each response:

1. Map every answer to the requirement ledger.
2. Preserve exact user language for critical definitions, constraints, and acceptance criteria.
3. Resolve explicit choices and defaults.
4. Mark unanswered items as unresolved rather than silently guessing.
5. Detect contradictions with earlier answers or supplied artifacts.
6. Identify new dependent questions revealed by the answer.
7. Restate only what is necessary when the user's reply is ambiguous.

When the user gives a partial answer, acknowledge the resolved part and ask only the remaining blocker. Do not repeat the full questionnaire.

When an answer conflicts with an earlier requirement, present the conflict neutrally and ask for a single resolution:

```text
These two requirements conflict: support OpenGL 3.3 only, and use compute shaders, which require a later version. Which requirement should take priority?
```

### CHECK

Proceed when all of the following are true:

- The intended outcome is unambiguous enough to act on.
- The deliverable and relevant scope are known.
- Critical terms have operational meanings.
- Material constraints and environment assumptions are known or safely defaulted.
- Success can be evaluated.
- Safety-sensitive or irreversible actions have the required authorization.
- No unresolved contradiction changes the chosen path.

Continue asking when at least one blocker remains and the answer would materially change the result.

Stop the loop when:

- The task is actionable.
- The user explicitly accepts stated assumptions or recommended defaults.
- Further questions have diminishing value and a reversible path is available.
- The user cannot provide more detail; propose a concrete default or a small exploratory step.
- The task cannot be performed safely without missing information; explain the specific blocker.

There is no fixed round limit. Do not continue merely to make the specification exhaustive.

### CONFIRM

Before substantial execution, summarize the interpretation in one to three sentences. Include:

- The requested outcome and deliverable.
- The most important scope or constraint.
- The definition of success or accepted assumptions.

For small tasks, combine confirmation with immediate execution. Do not require another approval unless the action is destructive, externally visible, expensive, safety-sensitive, or the user requested confirmation.

### PROCEED

If **When NOT to Use** applies, hand off to that skill with the requirement ledger — do not perform that work here.

Otherwise, start all unblocked, reversible work. If only one branch is blocked, continue other independent work and ask about the blocked branch rather than freezing the entire task.

During execution, re-enter the state machine when new evidence reveals:

- A hidden requirement or dependency.
- A contradiction between the requested outcome and the environment.
- A decision with materially different tradeoffs.
- A safety, authorization, cost, or irreversible-action concern.
- Acceptance criteria that cannot be tested as stated.

Do not reopen settled decisions without new evidence.

### STOP

If safe progress is impossible, state:

1. The exact missing or conflicting requirement.
2. Why it blocks the task.
3. The smallest decision needed to continue.

## Handling common ambiguity types

### Ambiguous intent

Ask what outcome or downstream decision the user wants, not merely what topic they are interested in.

Weak: `What do you mean?`

Strong: `Should the result help you choose an API, implement it, or explain it to reviewers?`

### Ambiguous definitions

Turn subjective or overloaded language into observable criteria.

Ask for:

- A measurable threshold.
- A concrete example and non-example.
- The domain-specific meaning among plausible alternatives.
- The authority or standard that defines the term.

Example: `By "fast," do you mean under 16 ms per frame, faster than the current build, or another target?`

### Ambiguous requirements

Prioritize the decisions that alter architecture or workload:

- Must-have behavior versus preferred behavior.
- In-scope and out-of-scope cases.
- Compatibility and platform targets.
- Expected inputs and outputs.
- Failure behavior and edge cases.
- Acceptance tests.

### Conflicting requirements

Do not invent a compromise silently. Name the conflict, explain the practical consequence briefly, and ask which priority wins. Offer a feasible alternative when one is obvious.

### Unknown user preference

Use the existing project or conversation convention when low-risk. State the default only if it materially affects the result.

### User says "use your judgment"

Choose the recommended default and continue. Record the decision in the confirmation instead of asking for confirmation again, unless the action is high-impact or irreversible.

### User says "just do it"

Proceed with explicit, minimal assumptions for reversible low-risk work. For destructive, externally visible, costly, legally sensitive, or safety-critical work, ask the smallest required authorization question.

### User is unsure

Offer two or three concrete choices, recommend one, and explain the decisive tradeoff in one sentence. When possible, propose a reversible exploratory step that produces information.

## Question quality test

Before sending a question, verify:

- **Materiality:** Would different answers change the result?
- **Answerability:** Can the user answer without doing your work for you?
- **Specificity:** Does it request one concrete decision or fact?
- **Novelty:** Is the answer absent from available context?
- **Timing:** Is this the earliest point at which the decision is needed?
- **Efficiency:** Is this the highest-value unresolved question now?
- **Neutrality:** Does it avoid forcing the user toward an unstated assumption?

Rewrite or omit any question that fails this test.

## Interaction examples

Read [references/examples.md](references/examples.md) when the current task involves multiple clarification rounds, conflicting requirements, or ambiguity discovered during execution.

Read [references/question-patterns.md](references/question-patterns.md) when selecting a question form for definitions, scope, acceptance criteria, technical environments, risk, or authority.
