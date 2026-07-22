---
name: skill-creator
description: "Create portable skills for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create a skill from scratch, bootstrap under the skills directory and install to .shared/skills with tool wrappers, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say \"portable skill\" explicitly."
---

# skill-creator (Cursor)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, workspace artifacts, and packaging:

`../../../.shared/skills/skill-creator/SKILL.md`

Resolve `<SKILL_ROOT>` and `<SKILL_CREATOR_ROOT>` as `../../../.shared/skills/skill-creator`. Resolve paths to `scripts/`, `references/`, `assets/`, and `agents/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for content structure and portable conventions.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the agent rediscovers them
- Optional frontmatter: add `disable-model-invocation: true` in a wrapper if the skill should load only when @-mentioned

## Install or refresh skill-creator

From repo root:

```bash
python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root . --name skill-creator --source skills/skill-creator --overwrite
```

If bootstrap source exists at `skills/skill-creator/`, use that path for `--source` only.

## Scaffolding and validation (user skills)

**Bootstrap path (preferred):** author under `skills/<skill-name>/`, then install:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py skills/<skill-name>

python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root . \
  --name <skill-name> \
  --source skills/<skill-name> \
  --overwrite
```

**Direct path:** when bootstrap is not used:

```bash
python <SKILL_CREATOR_ROOT>/scripts/create_skill.py \
  --root . \
  --name <skill-name> \
  --overwrite
```

Validate all installed paths after scaffold or install. Expand `skills/<skill-name>/wrappers/cursor/SKILL.md` (bootstrap) or `.cursor/skills/<skill-name>/SKILL.md` (direct) with Cursor eval mechanics and reload notes.

## Running evals in Cursor

Use the **Task tool** to spawn subagents. The full benchmark loop (with-skill + baseline, grading, aggregation) is supported.

### Step 1: Spawn all runs in one turn

For each test case, launch **two** Task subagents in the **same turn** — with-skill and baseline — so they finish together.

Write `eval_metadata.json` in each eval directory (assertions may start empty).

**With-skill prompt:**

```
Execute this task:
- Skill path: .shared/skills/<skill-name>/
- Task: <eval prompt>
- Input files: <eval files or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what matters — e.g. final CSV, generated file>
```

**Baseline:**

- **New skill:** same prompt, no skill path → `without_skill/outputs/`
- **Improving a skill:** snapshot shared skill first (`cp -r .shared/skills/<name> <workspace>/skill-snapshot/`), point baseline at snapshot → `old_skill/outputs/`

### Step 2: Assertions while runs execute

Draft assertions per shared skill guidance. Update `eval_metadata.json` and `evals/evals.json`. Explain them to the user.

### Step 3: Capture timing

When Task notifications include `total_tokens` and `duration_ms`, write `timing.json` in each run directory immediately — this data is not persisted elsewhere.

### Step 4: Grade, aggregate, viewer

1. Grade runs using `agents/grader.md` → `grading.json` per run (`text`, `passed`, `evidence`)
2. Aggregate: `cd <SKILL_CREATOR_ROOT> && python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`
3. Analyst pass: `agents/analyzer.md`
4. Launch viewer:

```bash
python <SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "<name>" \
  --benchmark <workspace>/iteration-N/benchmark.json
```

**No browser / remote dev:** pass `--static <output.html>` and share the file path. User downloads `feedback.json` from the static page — copy it into the workspace for the next iteration.

5. Tell the user to review Outputs and Benchmark tabs, then return with feedback.

### Step 5: Feedback loop

Read `feedback.json` when the user is done. Empty feedback means accepted. Kill background viewer if used (`kill $VIEWER_PID`).

### Iteration

After improving the shared skill, rerun all cases into `iteration-<N+1>/` with `--previous-workspace` on the viewer. Baseline for new skills stays `without_skill`.

### Blind comparison

Supported via Task subagents. Read `agents/comparator.md`.

## Description optimization in Cursor

**Automated shared Step 3 (`run_loop.py`) is not available** — it requires the Claude Code CLI (`claude -p`).

Use the shared manual path:

1. Draft ~20 trigger eval queries (shared Step 1; see `references/description-eval-queries.md`)
2. Review with user via `assets/eval_review.html` (shared Step 2)
3. Revise `description` yourself using the shared writing guide and triggering notes
4. Shared Step 4: sync `description` into all wrapper frontmatter; ask the user to test with realistic prompts in Cursor chat

## TodoList

When running evals, add todos so steps are not skipped — e.g. "Create evals JSON and run generate_review.py for human review before revising the skill."

## Wrapper policy

- Edit cross-tool behavior in `../../../.shared/skills/skill-creator/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
