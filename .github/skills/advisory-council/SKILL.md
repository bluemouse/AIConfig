---
name: advisory-council
description: Convene an advisory council, think tank, panel, or structured debate
  with distinct expert, stakeholder, skeptical, operational, and creative perspectives
  on complex decisions, plans, strategies, designs, disputes, trade-offs, or competing
  options. Deliver ranked recommendations, decision gates, minority dissent, and a
  defensible resolution with evidence quality, assumptions, risks, and revisit triggers.
  Not for single-proposal red-teaming with a proceed/reject verdict or git diff review.
---

# advisory-council (GitHub Copilot)

Read the shared skill first. It is the source of truth for council framing, role design, evidence ledgers, debate rounds, convergence rules, and output formats:

`../../../.shared/skills/advisory-council/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/advisory-council/`. Resolve paths to `references/` from that directory.

This wrapper adds GitHub Copilot / VS Code-native execution. Copilot Chat usually has no parallel subagent API, so preserve independence through disciplined sequential or simulated rounds.

## Discovery and Reload

- Project skills: `.github/skills/<name>/SKILL.md` plus shared under `.shared/skills/<name>/`
- Reload VS Code after installing or editing skills so Copilot rediscovers them

## Install or Refresh advisory-council

From repo root or a terminal:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name advisory-council --source skills/advisory-council --overwrite
```

## Council Execution in Copilot

Use simulated council mode by default:

1. State that the council is simulated unless a real independent worker mechanism is available.
2. Write all Round 1 positions before writing any cross-examination.
3. Keep notes claim-indexed so later concessions and refinements are visible.
4. Run cross-examination and convergence in the same chat, applying the shared quality gates.
5. Use concise output for low-stakes decisions; avoid dumping raw debate when the user needs the recommendation.

If Copilot is running as a non-interactive coding agent, do not wait for user answers unless the missing decision is unsafe to assume. Record assumptions and decision gates in the final report or pull request text.

## Wrapper Policy

- Edit cross-tool council behavior in `../../../.shared/skills/advisory-council/`
- Edit Copilot-specific mechanics here
- Do not duplicate the full shared skill body in this file
