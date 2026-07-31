---
name: devil-advocate
description: Play devil's advocate, red-team, pressure-test, poke holes, pre-mortem, or challenge one proposal, plan, strategy, design, launch, pitch, or vendor decision. Find blind spots, load-bearing assumptions, failure modes, show-stoppers, and kill criteria; steelman first, then return findings, mitigations, and a proceed/proceed-with-conditions/rework/replace/reject verdict. Not for git diff review, PR descriptions, or multi-perspective council synthesis.
---

# devil-advocate (Cursor)

Read the shared skill first. It is the source of truth for adversarial review workflow, challenge lenses, finding severity, fixability, and verdicts:

`../../../.shared/skills/devil-advocate/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/devil-advocate/`. Resolve paths to `references/` from that directory.

This wrapper adds Cursor-native execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for review content and output structure.

## Discovery and Reload

- Project skills: `.cursor/skills/<name>/SKILL.md` plus shared package under `.shared/skills/<name>/`
- Reload the Cursor window after adding, editing, or reinstalling skills so the agent rediscovers them

## Install or Refresh devil-advocate

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name devil-advocate --source skills/devil-advocate --overwrite
```

## Deep Red Team in Cursor

Use Cursor subagents only for deep red-team reviews where independence materially improves quality:

1. Frame and steelman the proposal yourself first.
2. Select distinct challenge lenses from the shared skill.
3. In a single message, dispatch independent subagents for the highest-value lenses. Use `subagent_type: "generalPurpose"` unless the work is pure repository discovery, where `explore` may fit.
4. Give each subagent the same proposal frame and only its assigned lens. Ask for candidate findings with causal chain, severity, evidence, disposition, and resolution path.
5. Collect final replies, deduplicate and rank findings yourself, then apply the show-stopper gate and issue exactly one verdict.

For quick or standard reviews, stay inline. Do not launch subagents merely to create more objections.

## Cursor Interaction

Use `AskQuestion` only when a missing non-negotiable, risk tolerance, or decision owner preference would change the verdict. Otherwise state assumptions and use scenario branches.

When the review depends on current external facts and web or MCP tools are available, gather those facts before treating a claim as evidence. Cite the source in the finding.

## Wrapper Policy

- Edit cross-tool adversarial review behavior in `../../../.shared/skills/devil-advocate/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
