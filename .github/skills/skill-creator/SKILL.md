---
name: skill-creator
description: Create portable skills for GitHub Copilot, Cursor, and Claude Code using
  a shared-first layout, and iteratively improve them. Use when users want to create
  a skill from scratch, bootstrap under the skills directory and install to .shared/skills
  with tool wrappers, edit or optimize an existing skill, run evals to test a skill,
  benchmark skill performance, or optimize a skill's description for better triggering
  accuracy — even if they do not say "portable skill" explicitly.
---

# skill-creator (GitHub Copilot)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, workspace artifacts, and packaging:

`../../../.shared/skills/skill-creator/SKILL.md`

Resolve `<SKILL_ROOT>` and `<SKILL_CREATOR_ROOT>` as `../../../.shared/skills/skill-creator`. Resolve paths to `scripts/`, `references/`, `assets/`, and `agents/` from that directory.

This wrapper adds **GitHub Copilot / VS Code-native** execution. Copilot Chat does not expose parallel subagents like Cursor or Claude Code — adapt the eval loop accordingly.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Reload VS Code** after installing or editing skills so Copilot rediscovers them
- Skills load when Copilot matches the skill `description` to the user's request

## Install or refresh skill-creator

From repo root (or ask the user to run in a terminal):

```bash
python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root . --name skill-creator --source skills/skill-creator --overwrite
```

If bootstrap source exists at `skills/skill-creator/`, use that path for `--source` only.

## Running evals in Copilot Chat

Use a **qualitative, sequential** loop unless the user explicitly runs scripts in a terminal outside Copilot.

### Recommended flow

1. Write `evals/evals.json` per shared skill spec
2. For each test prompt, write `eval_metadata.json` in the eval directory (even for qualitative runs)
3. For each test prompt:
   - Ensure the skill under test is installed (shared + this wrapper)
   - In **Copilot Chat**, send the eval prompt as the user would naturally phrase it
   - Save outputs under `<skill-name>-workspace/iteration-1/eval-<ID>/with_skill/outputs/` when the agent produces files
4. **Skip parallel baselines** in chat — Copilot has no subagent API. Optionally ask the user to rerun the same prompt in a fresh chat without @-mentioning the skill and save to `without_skill/outputs/` for informal comparison
5. Present each prompt + output to the user in chat (or generate a static review page — below)

### Optional: review viewer

When Python is available in the project terminal:

```bash
python <SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py \
  <workspace>/iteration-1 \
  --skill-name "<name>" \
  --static /tmp/<skill-name>-review.html
```

Share the HTML path with the user. Skip `aggregate_benchmark` unless both with-skill and baseline runs exist.

### Assertions and grading

Prefer **human judgment** for Copilot evals. Programmatic assertions and `agents/grader.md` apply only when outputs are saved to disk and graded in a separate step (terminal or another agent environment).

### Iteration

After improving the shared skill, save new runs under `iteration-<N+1>/`. When comparing iterations, regenerate the static viewer with `--previous-workspace <workspace>/iteration-<N-1>` if using saved outputs.

### Feedback

Collect feedback in chat after each eval or batch. Optionally document in `feedback.json` using the shared schema (`reviews`, `status: complete`). Empty feedback means the user accepted the output. Focus improvements on cases with specific complaints.

## Description optimization

**Shared Step 3 (`run_loop.py`) is not available** in Copilot (requires Claude Code CLI).

Manual path only:

1. Shared Step 1 — draft trigger eval queries (`references/description-eval-queries.md`)
2. Shared Step 2 — review with user via `assets/eval_review.html` in a local browser
3. Shared Step 4 — revise `description` in shared `SKILL.md`; sync to `.github/skills/`, `.cursor/skills/`, and `.claude/skills/` wrappers
4. Ask the user to try realistic prompts in Copilot Chat and confirm triggering

Write descriptions that state both **what** the skill does and **when** Copilot should use it — include file types, task phrases, and adjacent scenarios.

## Scaffolding and validation

Run in the integrated terminal:

```bash
python <SKILL_CREATOR_ROOT>/scripts/create_skill.py --root . --name my-skill
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .shared/skills/my-skill
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .github/skills/my-skill
```

After creating a new skill, reload VS Code.

## Wrapper policy

- Edit cross-tool behavior in `../../../.shared/skills/skill-creator/`
- Edit Copilot-specific mechanics here
