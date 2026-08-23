# Grilling Protocol

Use this protocol only for Research Reviewer Grilling Mode. Its purpose is to turn material uncertainty in a research report into explicit, user-owned decisions without asking the user to gather facts the reviewer can investigate.

Run Grilling Mode by default for standard and rigorous reviews. Do not run it for focused reviews unless the user requests it, and do not run it when the user explicitly requests no grilling.

## Build the decision tree

Create one decision node for each unresolved blocker or major finding, material assumption, contradiction, or scope choice. Add prerequisite edges between nodes. Typical prerequisite order is:

1. Target users, problem, and desired outcome.
2. Scope, non-goals, and constraints.
3. Recommended direction and alternatives.
4. Requirements, acceptance signals, risks, and rollout decisions.

Facts that can be established from the report, repository, or cited sources are not user decisions. Investigate them before asking a question. A fact investigation remains an unsettled prerequisite for its dependent decisions.

## Work in rounds

The frontier is every decision node whose prerequisites are settled. Ask all independent frontier questions in one round, then stop and wait for the user's responses. Recompute the frontier after each response round. Do not ask a downstream question in the same round as an unresolved prerequisite.

Use this question format:

```markdown
❓ **Q1 - [Decision title]**: [Why this decision is required, the report section or finding it resolves, and any relevant evidence.]

Options:
1. [Option A]: [consequence or trade-off.]
2. [Option B - Recommended]: [consequence or trade-off and why available evidence favors it.]
3. Stop grilling: End the interview and continue the review without further grilling.
```

Rules:

- Offer at most three options total: one or two defensible, materially distinct substantive paths and `Stop grilling`.
- Mark exactly one substantive option as `Recommended`. Explain the recommendation with evidence or an explicit trade-off; do not present it as certainty.
- When evidence permits only one responsible action, offer that action and `Stop grilling` rather than fabricating alternatives.
- Do not include an `other` option. The user may still provide a concise alternative response, but it is not a listed option.
- Phrase the question so a user can answer with an option number or a concise alternative.

## Stop grilling

If the user selects `Stop grilling` for any question, end Grilling Mode immediately. Continue the normal audit and issue its review report without further grilling. Record the stop in the grilling decision record, preserve all unresolved decision nodes as findings or open questions, and do not infer decisions from the stop.

## Finish and record outcomes

The grill is complete when every material decision is resolved, explicitly preserved as a finding or open question, or ended by `Stop grilling`. Let any pending fact investigation finish and fold its result into the frontier before completing normally; do not treat a decision still blocked on fact investigation as complete unless the user selects `Stop grilling`. Before finalizing:

- Re-evaluate findings, severity, confidence, and verdict using the answered decisions.
- Preserve unanswered questions as findings and open questions; do not infer an answer from silence.
- Record each resolved decision, chosen option, recommendation, rationale, accepted risk, and any user-requested stop in the review report.
- Do not hand off to implementation planning until the user confirms the shared understanding and the verdict permits it.