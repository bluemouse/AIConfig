---
name: skill-creator
description: "Create portable skills for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create a skill from scratch, scaffold `.shared/skills` with tool wrappers in `.cursor/skills`, `.claude/skills`, or `.github/skills`, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say \"portable skill\" explicitly."
---

# skill-creator (Claude Code)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, workspace artifacts, and packaging:

`../../../.shared/skills/skill-creator/SKILL.md`

Resolve `<SKILL_ROOT>` and `<SKILL_CREATOR_ROOT>` as `../../../.shared/skills/skill-creator`. Resolve paths to `scripts/`, `references/`, `assets/`, and `agents/` from that directory.

This wrapper adds **Claude Code-native** execution (including Cowork where noted). When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh skill-creator

```bash
python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root . --name skill-creator --source skills/skill-creator --overwrite
```

If bootstrap source exists at `skills/skill-creator/`, use that path for `--source` only.

## Running evals in Claude Code

Claude Code supports **subagents** — use the full benchmark loop from the shared workspace spec.

### Step 1: Spawn all runs in one turn

For each test case, spawn two subagents in the **same turn** (with-skill + baseline). Do not run with-skill first and baselines later.

Write `eval_metadata.json` per eval directory (assertions may start empty).

**With-skill:**

```
Execute this task:
- Skill path: .shared/skills/<skill-name>/
- Task: <eval prompt>
- Input files: <eval files or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <artifacts to keep>
```

**Baseline:** `without_skill/outputs/` for new skills; snapshot old shared skill to `skill-snapshot/` for improvements → `old_skill/outputs/`.

### Step 2: Assertions while runs execute

Draft assertions per shared skill guidance. Update `eval_metadata.json` and `evals/evals.json`. Explain them to the user.

### Step 3: Capture timing

When subagent completion notifications include `total_tokens` and `duration_ms`, write `timing.json` in each run directory immediately.

### Step 4: Grade, aggregate, viewer

1. Grade with `agents/grader.md` → `grading.json` per run (`text`, `passed`, `evidence`)
2. Aggregate: `cd <SKILL_CREATOR_ROOT> && python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>`
3. Analyst pass: `agents/analyzer.md`
4. **Always** launch the viewer and show results to the human **before** you revise the skill yourself:

```bash
python <SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "<name>" \
  --benchmark <workspace>/iteration-N/benchmark.json
```

For iteration 2+, pass `--previous-workspace <workspace>/iteration-<N-1>`. Cowork / headless: use `--static <path>` (see below).

5. Tell the user to review Outputs and Benchmark tabs, then return with feedback.

### Step 5: Feedback loop

Read `feedback.json` when the user is done. Empty feedback means accepted. Kill background viewer if used.

### Iteration and blind comparison

Rerun into new `iteration-*` folders; use `--previous-workspace` on the viewer. Blind comparison via `agents/comparator.md` when needed.

## Description optimization — shared Step 3 (automated)

Complete shared Steps 1–2 (eval queries per `references/description-eval-queries.md` + `eval_review.html`), then run:

```bash
cd <SKILL_CREATOR_ROOT>
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path .shared/skills/<skill-name> \
  --model <model-id-for-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from the current session. Tail progress for the user. Apply `best_description` per shared Step 4 (shared `SKILL.md` + sync wrappers).

Run this **after** the skill content is in good shape and the user agrees.

Triggering note: skills appear in `available_skills`; Claude invokes them when the description matches and the task benefits from specialized guidance.

## Cowork / headless Claude Code

- Subagents work; fall back to serial runs if timeouts are severe
- No browser: `generate_review.py --static <path>` — share link; feedback downloads as `feedback.json`
- **Generate the eval viewer before** you evaluate outputs yourself — get examples in front of the human first
- `run_loop.py` works (uses `claude -p`, not a browser)
- Packaging via `package_skill.py` needs Python + filesystem only

## Claude.ai (no Claude Code CLI)

If you are on Claude.ai rather than Claude Code: no subagents, no `run_loop.py`. Run test prompts sequentially yourself (read shared skill, execute prompt, show output). Skip baselines and quantitative benchmarks. Present results inline; skip browser viewer or use `--static` if you have filesystem access. Use manual description optimization only (shared Steps 1–2 and 4; skip Step 3).

## Updating skills in read-only environments

Copy to `/tmp/<skill-name>/`, edit, validate, package, then copy artifacts back if needed.

## TodoList

Include "Create evals JSON and run generate_review.py for human review" in todos during eval iterations.

## Wrapper policy

- Edit cross-tool behavior in `../../../.shared/skills/skill-creator/`
- Edit Claude Code / Cowork mechanics here
