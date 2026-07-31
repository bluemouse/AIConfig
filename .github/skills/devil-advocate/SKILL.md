---
name: devil-advocate
description: Play devil's advocate, red-team, pressure-test, poke holes, pre-mortem,
  or challenge one proposal, plan, strategy, design, launch, pitch, or vendor decision.
  Find blind spots, load-bearing assumptions, failure modes, show-stoppers, and kill
  criteria; steelman first, then return findings, mitigations, and a proceed/proceed-with-conditions/rework/replace/reject
  verdict. Not for git diff review, PR descriptions, or multi-perspective council
  synthesis.
---

# devil-advocate (GitHub Copilot)

Read the shared skill first. It is the source of truth for adversarial review workflow, challenge lenses, finding severity, fixability, and verdicts:

`../../../.shared/skills/devil-advocate/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/devil-advocate/`. Resolve paths to `references/` from that directory.

This wrapper adds GitHub Copilot / VS Code-native execution. Copilot Chat usually has no parallel subagent API, so deep reviews should run challenge lenses sequentially.

## Discovery and Reload

- Project skills: `.github/skills/<name>/SKILL.md` plus shared under `.shared/skills/<name>/`
- Reload VS Code after installing or editing skills so Copilot rediscovers them

## Install or Refresh devil-advocate

From repo root or a terminal:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name devil-advocate --source skills/devil-advocate --overwrite
```

## Red Team Execution in Copilot

Use an inline or sequential review:

1. Frame and steelman the proposal first.
2. Select the relevant challenge lenses from the shared skill.
3. Keep candidate findings separated by lens until deduplication and ranking.
4. Apply the show-stopper gate strictly before using `REJECT`.
5. End with exactly one verdict and a concrete repair, replacement, or stop path.

If Copilot is running as a non-interactive coding agent, do not wait for user answers unless the missing decision is unsafe to assume. Record assumptions, decision gates, and kill criteria in the final report or pull request text.

## Wrapper Policy

- Edit cross-tool adversarial review behavior in `../../../.shared/skills/devil-advocate/`
- Edit Copilot-specific mechanics here
- Do not duplicate the full shared skill body in this file
