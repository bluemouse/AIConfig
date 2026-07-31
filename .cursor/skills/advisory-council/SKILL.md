---
name: advisory-council
description: Convene an advisory council, think tank, panel, or structured debate
  with distinct expert, stakeholder, skeptical, operational, and creative perspectives
  on complex decisions, plans, strategies, designs, disputes, trade-offs, or competing
  options. Deliver ranked recommendations, decision gates, minority dissent, and a
  defensible resolution with evidence quality, assumptions, risks, and revisit triggers.
  Not for single-proposal red-teaming with a proceed/reject verdict or git diff review.
---

# advisory-council (Cursor)

Read the shared skill first. It is the source of truth for council framing, role design, evidence ledgers, debate rounds, convergence rules, and output formats:

`../../../.shared/skills/advisory-council/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/advisory-council/`. Resolve paths to `references/` from that directory.

This wrapper adds Cursor-native execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for council behavior and output.

## Discovery and Reload

- Project skills: `.cursor/skills/<name>/SKILL.md` plus shared package under `.shared/skills/<name>/`
- Reload the Cursor window after adding, editing, or reinstalling skills so the agent rediscovers them

## Install or Refresh advisory-council

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name advisory-council --source skills/advisory-council --overwrite
```

## Native Council in Cursor

Use Cursor subagents only when the decision is large enough to benefit from independent work:

1. Run the shared skill's charter, evidence ledger, role selection, and depth choice yourself first.
2. In a single message, launch one subagent per selected Round 1 council member when parallel independence matters.
3. Use `subagent_type: "generalPurpose"` for broad analysis, or `explore` for repository discovery roles when the role is read-only and codebase-focused.
4. Give every subagent the same charter and evidence ledger, plus only its own role brief. Do not include peer conclusions in Round 1.
5. Ask each subagent to return the shared Round 1 fields: position, evidence, assumptions, self-critique, expected failure mode, mind-changing evidence, and confidence.
6. Collect final replies, normalize claims, then run cross-examination and synthesis yourself. Dispatch a second round only for rigorous or high-stakes councils.

If the decision is lean or subagents are unavailable, use simulated council mode and explicitly label it.

## Cursor Interaction

Use `AskQuestion` only for a small number of blocking user decisions, such as criteria weights or whether a value trade-off is acceptable. Do not ask for facts that can be discovered from the workspace, attached files, or supplied context.

When the council depends on current external facts and web or MCP tools are available, gather those facts before treating a claim as evidence. Cite the source in the evidence ledger.

## Wrapper Policy

- Edit cross-tool council behavior in `../../../.shared/skills/advisory-council/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
