---
name: devil-advocate
description: Play devil's advocate, red-team, pressure-test, poke holes, pre-mortem, or challenge one proposal, plan, strategy, design, launch, pitch, or vendor decision. Find blind spots, load-bearing assumptions, failure modes, show-stoppers, and kill criteria; steelman first, then return findings, mitigations, and a proceed/proceed-with-conditions/rework/replace/reject verdict. Not for git diff review, PR descriptions, or multi-perspective council synthesis.
---

# devil-advocate (Claude Code)

Read the shared skill first. It is the source of truth for adversarial review workflow, challenge lenses, finding severity, fixability, and verdicts:

`../../../.shared/skills/devil-advocate/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/devil-advocate/`. Resolve paths to `references/` from that directory.

This wrapper adds Claude Code-native execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and Reload

- Project skills: `.claude/skills/<name>/SKILL.md` plus shared under `.shared/skills/<name>/`
- Restart or reload the Claude Code session after installing or editing skills

## Install or Refresh devil-advocate

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name devil-advocate --source skills/devil-advocate --overwrite
```

## Deep Red Team in Claude Code

Use subagents only for deep red-team reviews where independence materially improves quality:

1. Frame and steelman the proposal yourself first.
2. Select distinct challenge lenses from the shared skill.
3. In a single turn, spawn independent subagents for the highest-value lenses.
4. Give each subagent the same proposal frame and only its assigned lens. Ask for candidate findings with causal chain, severity, evidence, disposition, and resolution path.
5. Collect final replies, deduplicate and rank findings yourself, then apply the show-stopper gate and issue exactly one verdict.

For quick or standard reviews, stay inline. Do not launch subagents merely to create more objections.

When subagent completion notifications include `total_tokens` and `duration_ms`, note them only if comparing red-team efficiency across runs.

## Claude.ai

If you are on Claude.ai rather than Claude Code, no parallel subagents are available. Run challenge lenses sequentially in one context, keep candidate findings separated by lens until deduplication, and label any uncertainty from missing independent review.

## Wrapper Policy

- Edit cross-tool adversarial review behavior in `../../../.shared/skills/devil-advocate/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
