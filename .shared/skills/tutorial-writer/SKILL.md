---
name: tutorial-writer
description: Write, revise, and review example-driven technical tutorials, getting-started guides, practical walkthroughs, API or SDK lessons, and user guides for software products, libraries, frameworks, developer tools, and technical concepts. Use when a reader needs to achieve a concrete outcome, from a beginner quickstart through realistic or production use. Build a progressive, runnable example; show observable results; use only source-backed technical claims; and critique existing guides for learning flow, accuracy, and verification.
---

# Tutorial Writer

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

Create tutorials that let a reader reach a useful result before asking them to absorb
theory. Start with a small working example, explain only the concepts it makes
necessary, then evolve the same example toward the requested level of practical use.

## Primary directive

Your job is to **author, revise, or review learning-oriented guides**, not to implement
product code, run open-ended research, or produce reference-only API catalogs.

Do not implement features, fix bugs, create Jira tickets, publish docs to a host, or
post reviews unless the user explicitly requests that work in the same or a follow-up
message.

## When to use

Use this skill to:

- draft, rewrite, or review a tutorial, quickstart, walkthrough, lesson, or user guide;
- explain a software product, API, library, SDK, framework, developer tool, or technical
  concept through a concrete outcome;
- turn repository code, primary documentation, or supplied notes into an accurate learning
  path; or
- improve an existing guide's examples, sequence, observability, and source fidelity.

## When NOT to use

- **Evidence-backed codebase onboarding or architecture guides** — use
  [../code-professor/SKILL.md](../code-professor/SKILL.md) when the goal is learning an
  existing repository, not teaching a product or API through a new walkthrough
- **Open-ended product or technology research** — use
  [../research-guide/SKILL.md](../research-guide/SKILL.md) when the idea, tradeoffs, or
  requirements are still unformed
- **Ambiguous authoring scope** — use [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md)
  when the user cannot yet say what kind of guide they need or what outcome matters
- **Git diff or code review** — use [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md)
- **Meeting minutes or decision records** — use
  [../minutes-writer/SKILL.md](../minutes-writer/SKILL.md)
- **Comprehensive API reference with no learning path** — stay in reference-doc mode or
  say so; this skill needs a reader outcome and progressive examples
- **Marketing copy, release notes, or generic summaries** — outside tutorial scope
- **Tutorial content that requires unsupported claims or invented behavior** — refuse or
  narrow scope until source material exists

## Companion skills

| Adjacent task | Skill |
| --- | --- |
| Clarify what guide shape or outcome is needed | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) |
| Research product behavior or tradeoffs before drafting | [../research-guide/SKILL.md](../research-guide/SKILL.md) |
| Turn repository evidence into a codebase learning guide | [../code-professor/SKILL.md](../code-professor/SKILL.md) |
| Review code changes rather than tutorial prose | [../code-reviewer/SKILL.md](../code-reviewer/SKILL.md) |

## Inputs and source fidelity

1. Identify the topic, intended reader, desired outcome, environment or version, and
   available source material.
2. Inspect provided documentation, repository code, examples, and configuration before
   describing their behavior. Prefer primary documentation and source code for
   version-sensitive details.
3. If a detail is nonessential, choose a reasonable default and state the material
   assumption near the affected step. If it changes the outcome, compatibility, safety,
   or code, ask a focused question or present a clearly bounded draft.
4. Never invent APIs, options, commands, outputs, error messages, benchmarks,
   compatibility claims, screenshots, or source attribution. Do not claim examples were
   run unless they were actually validated.
5. Preserve the user's documented terminology, paths, commands, versions, and style
   conventions unless correcting a source-backed error.

## Workflow

### 1. Choose the guide shape

- **Tutorial:** teach one coherent outcome through a running example that grows step by
  step.
- **User guide:** begin with a quickstart, then group practical tasks from common to
  advanced while preserving example continuity where useful.
- **Existing-guide review:** identify the reader and target outcome, then return
  prioritized findings for accuracy, learning flow, examples, verification, and
  accessibility. Rewrite only the sections the user requests or authorizes.

Split unrelated workflows into separate guides rather than forcing them into one long
tutorial.

### 2. Plan an example ladder

Before drafting, define only the stages relevant to the topic:

1. **First success** — the smallest useful result the reader can achieve.
2. **Mental model** — the minimum explanation needed to understand that result.
3. **Extension** — one realistic requirement that exposes a limitation and changes the
   example.
4. **Integration** — an end-to-end scenario that connects the relevant features.
5. **Professional use** — applicable reliability, validation, testing, observability,
   security, performance, deployment, or maintenance concerns.

Use one running example by default. Introduce a second only when it teaches a genuinely
different use case.

### 3. Write each learning step

For each step:

1. State the concrete goal and any prerequisite that must be completed now.
2. Show the code, command, UI action, configuration, or artifact needed to achieve it.
3. Show an observable result: output, response, changed state, screenshot, or test
   result.
4. Explain what happened and name only the concepts needed at this point.
5. Introduce one new requirement or limitation when it motivates the next change.
6. Modify the example and verify the improvement with observable proof.

Show complete runnable code when the reader needs it. For focused changes, show the
smallest meaningful diff and explicitly mark unchanged omissions. Keep names, paths,
imports, ports, payloads, and expected output consistent across every step.

### 4. Use visuals purposefully

Add a visual only when it answers a question more clearly than prose:

- architecture or component relationships;
- request, event, or data lifecycles;
- state transitions and branching decisions;
- entity relationships;
- before/after behavior; or
- UI workflows.

Use Mermaid or a compact text diagram when it can be rendered by the target format.
Use screenshots only when the user provides them, asks to create them, or they can be
captured from a verified environment. Introduce each visual with the question it
answers, then state the takeaway immediately after it.

Read [references/tutorial-patterns.md](references/tutorial-patterns.md) when selecting
a guide shape, designing a running example, choosing a visual, or reviewing an existing
guide.

### 5. Validate before delivery

- Make setup and prerequisites visible before the first action that needs them.
- Verify representative code and commands when execution tools and a suitable environment
  are available. Report what was run and its result; otherwise state that execution was
  not performed.
- Check that the first example is copyable, every important transition has expected
  evidence, and later steps build on earlier ones.
- Confirm that important technical claims are supported by supplied material or
  authoritative research.
- Add troubleshooting only for likely, source-supported failures tied to the guide's
  examples. State a symptom, its cause, and a safe fix.

## Writing rules

- Begin with at most two short orientation paragraphs, then reach the first useful
  example.
- Lead with concrete artifacts—code, commands, requests, outputs, diagrams, screenshots,
  or UI actions—and explain after the reader sees something real.
- Use action-oriented headings that form a readable learning path on their own.
- Add one primary idea per step; explain why a change matters when the reader encounters
  the limitation it resolves.
- Define unfamiliar terms in plain language on first use.
- Prefer expected output and before/after evidence over vague claims such as "faster" or
  "more robust."
- Keep prose concise. Remove marketing language, historical detours, generic
  transitions, and unsupported superlatives.
- End with specific next capabilities, related guides, or a clear continuation of the
  example—not a generic recap.

## Default output shape

Adapt this structure; omit sections that do not serve the reader's outcome.

```markdown
# [Outcome-oriented title]

[What the reader will accomplish.]
[Prerequisites and version assumptions, only when needed.]

## Start with the smallest working example
[Action or code]
[Expected result]
[Short explanation]

## Add [one capability]
[New requirement or limitation]
[Changed example]
[Expected result and explanation]

## See how the pieces fit together
[Diagram or concise mental model]

## Build a realistic use case
[Integrated example and observable proof]

## Handle [relevant professional concern]
[Example, improved implementation, and verification]

## Troubleshooting
[Source-supported symptoms, causes, and fixes]

## Next steps
[Concrete follow-on capabilities or related documentation]
```

For a broader user guide, keep the quickstart first, organize tasks by reader goal from
common to advanced, and preserve a consistent example or domain where possible.

## Quality gate

Before delivering, confirm that:

- a new reader can reach a visible first success quickly;
- the guide teaches through examples rather than front-loaded exposition;
- each step has one primary teaching job and complexity increases gradually;
- explanations arrive alongside or after the example that motivates them;
- key behavior has observable, internally consistent proof;
- professional concerns are relevant and demonstrated rather than listed generically;
- technical claims, outputs, and visuals are source-backed or clearly labeled as
  assumptions; and
- the ending provides concrete next actions.

## Reference routing

| Task | Read |
| --- | --- |
| Guide shape, example ladder, visuals, review rubric, anti-patterns | [references/tutorial-patterns.md](references/tutorial-patterns.md) |

## Quick completion checklist

Before delivering a tutorial, guide, or review:

1. **Outcome** — reader level, desired result, and environment or version are clear
2. **Source fidelity** — APIs, commands, outputs, and visuals are source-backed or labeled
   as assumptions; no invented behavior
3. **Example ladder** — first success is quick; later steps add one idea at a time
4. **Evidence** — important steps show observable results or verification
5. **Scope** — guide shape matches the request; unrelated workflows are not forced together
6. **Safety** — no implementation, publishing, or ticket work unless explicitly requested

## Resources

- [references/tutorial-patterns.md](references/tutorial-patterns.md) — guide skeletons,
  visual selector, example rules, review rubric, anti-patterns
- [SOURCES.md](SOURCES.md) — provenance and reference notes
