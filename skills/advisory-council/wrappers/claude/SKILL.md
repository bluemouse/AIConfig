---
name: advisory-council
description: Convene an advisory council, think tank, panel, or structured debate with distinct expert, stakeholder, skeptical, operational, and creative perspectives on complex decisions, plans, strategies, designs, disputes, trade-offs, or competing options. Deliver ranked recommendations, decision gates, minority dissent, and a defensible resolution with evidence quality, assumptions, risks, and revisit triggers. Not for single-proposal red-teaming with a proceed/reject verdict or git diff review.
---

# advisory-council (Claude Code)

Read the shared skill first. It is the source of truth for council framing, role design, evidence ledgers, debate rounds, convergence rules, and output formats:

`../../../.shared/skills/advisory-council/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/advisory-council/`. Resolve paths to `references/` from that directory.

This wrapper adds Claude Code-native execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and Reload

- Project skills: `.claude/skills/<name>/SKILL.md` plus shared under `.shared/skills/<name>/`
- Restart or reload the Claude Code session after installing or editing skills

## Install or Refresh advisory-council

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name advisory-council --source skills/advisory-council --overwrite
```

## Native Council in Claude Code

Use subagents only when the decision is large enough to benefit from independent work:

1. Run the shared skill's charter, evidence ledger, role selection, and depth choice yourself first.
2. In a single turn, spawn one subagent per selected Round 1 council member when parallel independence matters.
3. Give every subagent the same charter and evidence ledger, plus only its own role brief. Do not include peer conclusions in Round 1.
4. Ask each subagent to return the shared Round 1 fields: position, evidence, assumptions, self-critique, expected failure mode, mind-changing evidence, and confidence.
5. Collect final replies, normalize claims, then run cross-examination and synthesis yourself. Dispatch a second round only for rigorous or high-stakes councils.

When subagent completion notifications include `total_tokens` and `duration_ms`, note them only if comparing council efficiency across runs.

## Claude.ai

If you are on Claude.ai rather than Claude Code, no parallel subagents are available. Use simulated council mode, label it honestly, write all independent Round 1 positions before cross-examination, and keep the final decision proportional to the prompt.

## Wrapper Policy

- Edit cross-tool council behavior in `../../../.shared/skills/advisory-council/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
