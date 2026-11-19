---
name: skill-creator
description: Create portable skills for GitHub Copilot, Cursor, and Claude Code using a single-root layout, and iteratively improve them. Use when users want to create a skill from scratch, bootstrap under the skills directory and install to .agents/skills, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say "portable skill" explicitly. Does not trigger on creating custom agents (agent-creator) or slash commands and Copilot prompts (command-creator).
---

# Skill Creator

At a high level: capture intent → **choose an authoring path** (bootstrap under `skills/<name>/`, preferred, or direct scaffold with `create_skill.py`) → write a tool-neutral `SKILL.md` body with tool-specific guidance in `## Tool notes` → install when bootstrapping → run realistic test prompts with an agent that has the skill → evaluate results (qualitatively, and quantitatively when supported) → rewrite based on feedback → repeat, then expand the test set.

The shared creation skeleton — authoring-path decision, authoritative-edit rule, capture-intake flow, description-tuning loop, output summary, and the generic test-and-iterate loop — lives in [references/creation-common.md](references/creation-common.md); this body holds only the skill-specific delta.

**Tool-specific execution** (how to spawn eval runs, baselines, description optimization, and reload steps) lives in the `## Tool notes` section of the skill — read it after the tool-neutral body. Do not assume subagents, a particular CLI, or a browser unless the Tool notes document them.

Figure out where the user is in this process and help them progress. If they already have a draft skill, go straight to eval/iterate. If they prefer a lightweight pass without formal evals, follow their lead.

## When NOT to Use

- **Creating a custom agent** — use [../agent-creator/SKILL.md](../agent-creator/SKILL.md)
- **Creating a slash command or Copilot prompt** — use [../command-creator/SKILL.md](../command-creator/SKILL.md)

---

## Communicating with the user

Match the user's vocabulary; briefly explain terms like "Tool notes", "eval", or "assertion" when unsure they know them. If the user provides exact wording for skill instructions or the description, use it **verbatim** in generated files.

---

## Creating a skill

### Capture intent

Per [references/creation-common.md](references/creation-common.md). Skill-specific intake: what the skill enables, when it should trigger, where files are written, expected output format, tool-specific notes (eval mechanics, reload steps) per tool, and whether to set up test cases (objective outputs benefit; subjective outputs often don't).

### Where to edit (by path)

Per the authoritative-edit rule in [references/creation-common.md](references/creation-common.md). For skills: bootstrap edits go in `skills/<name>/SKILL.md` (+ `references/`, `scripts/`, `assets/`) and reinstall with `install_portable_skill.py`; direct-path edits go in `.agents/skills/<name>/SKILL.md`. Runtime read target is always `.agents/skills/<name>/`.

### Bundled scripts

`<SKILL_CREATOR_ROOT>` is the directory containing **this** skill's `SKILL.md`; `<SKILL_ROOT>` the directory containing the **target** skill's `SKILL.md` (after install). Run `python -m scripts.*` with `<SKILL_CREATOR_ROOT>` as the working directory so imports resolve. Under `<SKILL_CREATOR_ROOT>/`: `scripts/install_portable_skill.py` (install), `scripts/create_skill.py` (direct scaffold), `scripts/init_skill.py` (standalone), `scripts/quick_validate.py` (validate), `scripts/package_skill.py` (package), `scripts/aggregate_benchmark.py` (benchmark), `scripts/run_loop.py` (description eval loop), `eval-viewer/generate_review.py` (eval viewer).

### Anatomy and authoring

Installed layout (single root): `.agents/skills/<skill-name>/` — SKILL.md plus optional `scripts/`, `references/`, `assets/`; one real copy, no per-tool wrappers. Claude Code discovers skills through the `.claude/skills -> ../.agents/skills` bridge symlink (auto-created on install; install refuses and asks you to purge it first if `.claude/skills` is a real legacy directory); Cursor and GitHub Copilot read `.agents/skills/` directly.

**Progressive disclosure:** metadata (frontmatter) → `SKILL.md` body → bundled resources on demand. The body must be **tool-neutral** above `## Tool notes`, with tool-native mechanics in that `## Tool notes` H2. Bootstrap layout, worked install/scaffold/packaging examples, and a quality checklist: `references/portable-skill-layout.md`.

**Frontmatter:** `name` — kebab-case (lowercase letters, digits, hyphens; max 64 chars). `description` — primary trigger mechanism: what the skill does **and** when to use it, specific and slightly expansive to avoid under-triggering; keep all "when to use" phrasing here, not the body. `compatibility` — optional, rarely needed.

Quality bars: **correct** (clear scope, accurate capabilities, verifiable success criteria), **complete** (edge cases, explicit output format, stated boundaries), **efficient** (lean body, tool-specific shortcuts in `## Tool notes`, repeated work under `scripts/`), **no surprises** (no hidden behavior; decline misleading or unauthorized-access skills). When specifying output format, match the strictness to the need — exact templates for rigid formats, adaptable defaults otherwise; when style matters, input/output examples convey the desired style and level of detail better than descriptions alone.

**Bootstrap authoring:** create `skills/<skill-name>/` (SKILL.md with tool-neutral frontmatter and body — resolve `<SKILL_ROOT>` so paths work after install; optional `scripts/`, `references/`, `assets/`; `## Tool notes` when the skill has tool-specific mechanics), copying from an existing skill under `skills/` when starting from a known pattern. Then validate and install:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root <repo_root> --name <skill-name> --source skills/<skill-name> --overwrite
```

**Direct scaffold:** `create_skill.py --root <repo_root> --name <skill-name> --overwrite` — do **not** hand-create `.agents/skills/` directories. **Standalone copy** outside the single-root layout: `init_skill.py <skill-name> --path <install-path>` — the parent must be a skills root; the validator rejects category subfolders. Both commands in full: worked examples in `references/portable-skill-layout.md`.

**Updating an existing skill:** preserve the original `name` unless the user wants a rename; edit at the authoritative location per creation-common.md. Output summary per creation-common.md.

---

## Test prompts

Draft 2–3 realistic user prompts that should invoke this skill; confirm with the user before running. For each prompt note the expected behavior, the efficiency signal to watch for (unnecessary steps, over-long output, wrong tool usage), and which environment to test in.

Save eval prompts to `skills/<skill-name>/evals/evals.json` (bootstrap) or `.agents/skills/<skill-name>/evals/evals.json` (direct path) — prompts first, assertions later. Schema and example: `references/schemas.md`.

Follow the skill's `## Tool notes` for how to execute eval runs (Task subagent, parallel baselines, etc.).

---

## Running and evaluating test cases

The shared workspace layout, run-loop artifacts, and grading schemas live in `references/schemas.md` — read it before running a full eval. This section holds only the operating rules:

- Do not stop partway through a planned eval iteration. Do not use unrelated testing skills.
- Cap concurrent eval runs at the [../agent-runner/SKILL.md](../agent-runner/SKILL.md) defaults — at most 4 with-skill/baseline pairs (8 subagents) in flight; queue excess test cases in later batches within the same iteration.
- Spawn each test case's with-skill + baseline runs in the **same turn** — never with-skill first and baselines later. Baseline is `without_skill/` for new skills; snapshot the old skill and use `old_skill/` when comparing versions.
- Grade with `agents/grader.md` → `grading.json` per run (required by the viewer); aggregate with `python -m scripts.aggregate_benchmark` (pass `--primary/--baseline` explicitly whenever more than two arm directories exist — unselected multi-arm input is rejected rather than guessed); analyst pass with `agents/analyzer.md`; then **always** launch the viewer and show results to the human **before** revising the skill yourself. For iteration 2+, pass `--previous-workspace`.
- `run_status.json` (`{"status": "completed"|"errored"|"timeout"}`) in a run directory marks infrastructure failures, which are excluded from deltas and listed in `comparisons[].failed_runs`.
- Read `feedback.json` when the user is done; empty feedback means accepted. Kill any background viewer server when finished.
- Never eval on a dirty tree; sweep untracked files after every eval run (spawned runs can leave demo projects and other residue behind).

---

## Reviewing and improving the skill

After test runs, check for correctness (scope, accuracy, hallucinated files or APIs), completeness (edge cases, output format, escalation when needed), and efficiency (prompt too long to follow, repeated work, ignored native tool features documented in Tool notes). Improvement rules and the iterate loop: [references/creation-common.md](references/creation-common.md). After edits: rerun evals into `iteration-<N+1>/`, regenerate the viewer, collect feedback, repeat until the user is satisfied or progress stalls.

---

## Advanced: Blind comparison

Optional rigor when comparing two skill versions. Read `agents/comparator.md` and `agents/analyzer.md`. Requires independent parallel runs — see the skill's `## Tool notes`.

---

## Simplification and retirement decisions

A skill or guideline earns its place. When trimming, simplifying, or retiring guidance, do not argue from instruction length or compliance alone — compare arms:

1. **Arms**: `baseline` (target guidance removed, everything else identical), `current` (today's bytes), `candidate` (the simplification). Freeze each arm's bytes and hash them before running anything.
2. **Grade correctness and safety first**; efficiency only after correctness holds on the same paired cases. A baseline with worse efficiency but equal correctness says the guidance is process overhead; a baseline failing safety or task checks says it is load-bearing.
3. **Pair runs** by task and repeat number. Missing, errored, or mismatched runs are incomplete results — never a pass or a free efficiency win. Record uncertainty: a tie in a small sample is not equivalence.
4. **Report scope honestly**: the exact tested host/model. No cross-host or cross-model claim without testing them.

Retirement (removing a skill from the catalog) requires the same representative evidence plus a compatibility assessment of its consumers (cross-links, installed copies, docs). Trigger this review on each major frontier-model release, recording the tested model version and date with the decision.

---

## Description optimization

The `description` field drives skill discovery. Manual tuning steps (trigger-eval queries, user review, apply): [references/creation-common.md](references/creation-common.md), skill-specific notes in `references/description-eval-queries.md`; review UI asset: `assets/eval_review.html` (replace the `__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__` placeholders). Automated `run_loop.py` runs **only** where the skill's `## Tool notes` documents it (Claude Code / Cowork).

---

## Packaging

Validate, then package the installed skill:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .agents/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/package_skill.py .agents/skills/<skill-name>
```

Direct the user to the resulting `.skill` file for installation elsewhere.

---

## Tool notes

### Claude Code

Claude Code supports **subagents** — run the shared loop from **Running and evaluating test cases** in full (with-skill + baseline pairs spawned in one turn).

**Description optimization (shared Step 3, automated):** after shared Steps 1–2, run:

```bash
cd <SKILL_CREATOR_ROOT>
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path .agents/skills/<skill-name> \
  --model <model-id-for-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from the current session; apply `best_description` per shared Step 4. Run this **after** the skill content is in good shape and the user agrees.

**Cowork / headless:** subagents work (fall back to serial runs if timeouts are severe); no browser — use `generate_review.py --static <path>` and share the link, feedback downloads as `feedback.json`; generate the eval viewer **before** evaluating outputs yourself; `run_loop.py` works (uses `claude -p`).

**Claude.ai (no Claude Code CLI):** no subagents, no `run_loop.py`. Run test prompts sequentially, skip baselines and quantitative benchmarks, present results inline, use manual description optimization only (shared Steps 1–2 and 4).

### Cursor

Same shared loop as Claude Code, but spawn subagents with the **Task tool** (two Task subagents per test case, same turn). Deltas:

- **No `run_loop.py`** — it requires the Claude Code CLI. Use the manual description-optimization path: draft queries, review with `assets/eval_review.html`, revise the description, sync it, and ask the user to test with realistic prompts.
- **No browser / remote dev:** pass `--static <output.html>` and share the file path; the user downloads `feedback.json` from the static page — copy it into the workspace for the next iteration. Kill the background viewer with `kill $VIEWER_PID`.
- Optional frontmatter: add `disable-model-invocation: true` if the skill should load only when explicitly requested rather than via description matching.

### GitHub Copilot

Copilot Chat does not expose parallel subagents — use a **qualitative, sequential** loop unless the user explicitly runs scripts in a terminal:

1. Write `evals/evals.json` per the shared spec.
2. For each test prompt, write `eval_metadata.json` in the eval directory (even for qualitative runs).
3. Send the eval prompt in Copilot Chat as the user would naturally phrase it; save outputs under `<skill-name>-workspace/iteration-1/eval-<ID>/with_skill/outputs/` when the agent produces files.
4. **Skip parallel baselines** in chat — optionally ask the user to rerun the same prompt in a fresh chat without @-mentioning the skill and save to `without_skill/outputs/` for informal comparison.
5. Present each prompt + output to the user in chat, or generate a static review page when Python is available:

```bash
python <SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py \
  <workspace>/iteration-1 \
  --skill-name "<name>" \
  --static /tmp/<skill-name>-review.html
```

Skip `aggregate_benchmark` unless both with-skill and baseline runs exist. Prefer **human judgment** for Copilot evals; programmatic assertions and `agents/grader.md` apply only when outputs are saved to disk and graded in a separate step. Collect feedback in chat after each eval or batch; optionally document in `feedback.json` per the shared schema.

**Description optimization:** shared Step 3 (`run_loop.py`) is **not available** in Copilot — manual path only (shared Steps 1, 2, and 4). Write descriptions that state both **what** the skill does and **when** Copilot should use it — include file types, task phrases, and adjacent scenarios. Skills load when Copilot matches the skill `description` to the user's request.
