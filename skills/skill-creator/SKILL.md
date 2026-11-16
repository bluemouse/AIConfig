---
name: skill-creator
description: Create portable skills for GitHub Copilot, Cursor, and Claude Code using a single-root layout, and iteratively improve them. Use when users want to create a skill from scratch, bootstrap under the skills directory and install to .agents/skills, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say "portable skill" explicitly. Does not trigger on creating custom agents (agent-creator) or slash commands and Copilot prompts (command-creator).
---

# Skill Creator

At a high level: capture intent → **choose an authoring path** (bootstrap under `skills/<name>/`, preferred, or direct scaffold with `create_skill.py`) → write a tool-neutral `SKILL.md` body with tool-specific guidance in `## Tool notes` → install when bootstrapping → run realistic test prompts with an agent that has the skill → evaluate results (qualitatively, and quantitatively when supported) → rewrite based on feedback → repeat, then expand the test set.

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

If the conversation already contains a workflow to capture, extract tools, steps, corrections, and formats from history first; confirm gaps with the user. Ask: what the skill enables, when it should trigger, where files are written, expected output format, tool-specific notes (eval mechanics, reload steps) per tool, and whether to set up test cases (objective outputs benefit; subjective outputs often don't). When ambiguity exceeds this intake — skill vs agent vs command, conflicting requirements, no shared picture of success — run the clarification loop in [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) first and carry its requirement ledger into the skill's scope and `description`. Match existing conventions in the target repo; use research tools (MCP, docs search, similar skills) when helpful.

### Choose authoring path

Pick **one** path before writing files. **Bootstrap** (`skills/<name>/SKILL.md` + optional `references/`, `scripts/`, `assets/`, installed by `install_portable_skill.py`) for repo-maintained skills revised over time. **Direct** (`create_skill.py` scaffolds `.agents/skills/<name>/`) for one-offs or quick first drafts without `skills/` bootstrap.

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Tool-neutral behavior | `skills/<name>/SKILL.md` → reinstall | `.agents/skills/<name>/SKILL.md` |
| Tool-only notes (`## Tool notes`) | Same file, `## Tool notes` section → reinstall | `.agents/skills/<name>/SKILL.md` |
| Bundled resources | `skills/<name>/scripts/`, `references/`, `assets/` → reinstall | Same under `.agents/skills/<name>/` |
| Runtime read target | `.agents/skills/<name>/` (install output) | Same |

Two rules govern every edit — stated once here, applying everywhere below:

1. **Never hand-edit `.agents/skills/` when bootstrap source exists.** Edit `skills/<name>/` and reinstall with `install_portable_skill.py` (reinstall before testing in the IDE). Only on the direct path (no bootstrap source) is `.agents/skills/<name>/SKILL.md` the canonical file to edit directly.
2. **Validate after every substantive edit:** `quick_validate.py` against the bootstrap path before install, and against the installed path after install or direct scaffold. Fix errors before handing off.

### Bundled scripts

`<SKILL_CREATOR_ROOT>` is the directory containing **this** skill's `SKILL.md`; `<SKILL_ROOT>` the directory containing the **target** skill's `SKILL.md` (after install). Run `python -m scripts.*` with `<SKILL_CREATOR_ROOT>` as the working directory so imports resolve. Under `<SKILL_CREATOR_ROOT>/`: `scripts/install_portable_skill.py` (install), `scripts/create_skill.py` (direct scaffold), `scripts/init_skill.py` (standalone), `scripts/quick_validate.py` (validate), `scripts/package_skill.py` (package), `scripts/aggregate_benchmark.py` (benchmark), `scripts/run_loop.py` (description eval loop), `eval-viewer/generate_review.py` (eval viewer).

### Anatomy and authoring

Installed layout (single root): `.agents/skills/<skill-name>/` — SKILL.md plus optional `scripts/`, `references/`, `assets/`; one real copy, no per-tool wrappers. Claude Code discovers skills through the `.claude/skills -> ../.agents/skills` bridge symlink (auto-created on install); Cursor and GitHub Copilot read `.agents/skills/` directly.

**Progressive disclosure:** metadata (frontmatter) → `SKILL.md` body → bundled resources on demand. The body must be **tool-neutral** above `## Tool notes` — no subagent product names, single-vendor CLI assumptions, or reload instructions for one IDE; tool-native mechanics (eval spawn commands, reload steps, description-optimization limits) live in the `## Tool notes` H2 at the end, with `### <Tool>` H3 subsections as needed, omitted entirely when the skill has none. Bootstrap layout, worked install/scaffold/packaging examples, and a quality checklist: `references/portable-skill-layout.md`.

**Frontmatter:** `name` — kebab-case (lowercase letters, digits, hyphens; max 64 chars). `description` — primary trigger mechanism: what the skill does **and** when to use it, specific and slightly expansive to avoid under-triggering; keep all "when to use" phrasing here, not the body. `compatibility` — optional, rarely needed.

Quality bars: **correct** (clear scope, accurate capabilities, verifiable success criteria), **complete** (edge cases, explicit output format, stated boundaries), **efficient** (lean body, tool-specific shortcuts in `## Tool notes`, repeated work under `scripts/`), **no surprises** (no hidden behavior; decline misleading or unauthorized-access skills). Writing patterns: `references/output-patterns.md` and `references/workflows.md`.

**Bootstrap authoring:** create `skills/<skill-name>/` (SKILL.md with tool-neutral frontmatter and body — resolve `<SKILL_ROOT>` so paths work after install; optional `scripts/`, `references/`, `assets/`; `## Tool notes` when the skill has tool-specific mechanics), copying from an existing skill under `skills/` when starting from a known pattern. Then validate and install:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root <repo_root> --name <skill-name> --source skills/<skill-name> --overwrite
```

Install creates the bridge symlink when it does not yet exist; if `.claude/skills` is a real directory (legacy install), install refuses and asks you to purge it first.

**Direct scaffold:** `create_skill.py --root <repo_root> --name <skill-name> --overwrite` — do **not** hand-create `.agents/skills/` directories; use `--overwrite` only when regenerating and the user confirms. **Standalone copy** outside the single-root layout: `init_skill.py <skill-name> --path <install-path>` — the parent must be a skills root (a directory named `skills`); the validator rejects category subfolders. Both commands in full: worked examples in `references/portable-skill-layout.md`.

**Updating an existing skill:** preserve the original `name` unless the user wants a rename; edit at the authoritative location per **Where to edit**. **Output summary** after creating or installing: authoritative edit path, installed skill path, bridge symlink status, and assumptions made about instructions or triggers.

---

## Test prompts

Draft 2–3 realistic user prompts that should invoke this skill; confirm with the user before running. For each prompt note the expected behavior, the efficiency signal to watch for (unnecessary steps, over-long output, wrong tool usage), and which environment to test in.

Save eval prompts to `skills/<skill-name>/evals/evals.json` (bootstrap) or `.agents/skills/<skill-name>/evals/evals.json` (direct path) — prompts first, assertions later. Schema and example: `references/schemas.md`.

Follow the skill's `## Tool notes` for how to execute eval runs (Task subagent, parallel baselines, etc.).

---

## Running and evaluating test cases

Follow the skill's `## Tool notes` for how to execute runs (parallel vs sequential, baselines, timing capture). This section defines the **shared workspace layout, run loop, and artifacts** all tools should use when running full evals.

Do not stop partway through a planned eval iteration. Do not use unrelated testing skills.

Cap concurrent eval runs at the [../agent-runner/SKILL.md](../agent-runner/SKILL.md)
defaults — at most 4 with-skill/baseline pairs (8 subagents) in flight; queue
excess test cases in later batches within the same iteration.

Workspace: `<skill-name>-workspace/` sibling to `.agents/skills/`, organized by `iteration-N/` and per-eval directories. Create directories as you go.

### The run loop (tools with subagents)

**Step 1 — Spawn all runs in one turn.** For each test case, spawn two subagents in the **same turn** (with-skill + baseline). Do not run with-skill first and baselines later. Write `eval_metadata.json` per eval directory (assertions may start empty). With-skill prompt:

```
Execute this task:
- Skill path: .agents/skills/<skill-name>/
- Task: <eval prompt>
- Input files: <eval files or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <artifacts to keep>
```

Baseline: `without_skill/outputs/` for new skills; snapshot the old skill to `skill-snapshot/` for improvements → `old_skill/outputs/`.

**Step 2 — Assertions while runs execute.** Draft objective, descriptively named assertions (skip forced assertions for subjective skills); update `eval_metadata.json` and `evals/evals.json`; explain them to the user.

**Step 3 — Capture timing.** When subagent completion notifications include `total_tokens` and `duration_ms`, write `timing.json` in each run directory immediately.

**Step 4 — Grade, aggregate, viewer.** Grade with `agents/grader.md` → `grading.json` per run; aggregate with `python -m scripts.aggregate_benchmark`; analyst pass with `agents/analyzer.md`; then **always** launch the viewer and show results to the human **before** revising the skill yourself. For iteration 2+, pass `--previous-workspace`.

**Step 5 — Feedback loop.** Read `feedback.json` when the user is done. Empty feedback means accepted. Kill any background viewer server when finished.

### Workspace artifacts

Each eval directory holds `eval_metadata.json` (eval_id, eval_name, prompt, assertions) plus run directories: `with_skill/outputs/` and a baseline (`without_skill/outputs/` for new skills, `old_skill/outputs/` when comparing versions — snapshot the prior shared skill before baseline runs on improvements). Each run directory holds `timing.json` (when your tool provides token/duration data) and `grading.json` (`text`, `passed`, and `evidence` on each expectation — required by the viewer; see `agents/grader.md`). JSON examples for every artifact: `references/schemas.md`.

**benchmark.json / benchmark.md:** produced by:

```bash
cd <SKILL_CREATOR_ROOT>
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
```

**Review viewer:**

```bash
python <SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "<name>" \
  --benchmark <workspace>/iteration-N/benchmark.json
```

Use `--previous-workspace` for iteration 2+. Use `--static <path>` when no browser is available.

**feedback.json** after user review (schema in `references/schemas.md`). Empty feedback means the user accepted the output.

---

## Reviewing and improving the skill

After test runs, check for correctness (scope, accuracy, hallucinated files or APIs), completeness (edge cases, output format, escalation when needed), and efficiency (prompt too long to follow, repeated work, ignored native tool features documented in Tool notes).

Improvement rules: **generalize** (fixes must help beyond the eval examples), **keep the file lean** (read transcripts, not just final outputs), **edit the tool-neutral body first** at the authoritative location per **Where to edit** (then Tool notes for tool-only gaps), **explain why** (reasoning over ALL-CAPS MUSTs), and **bundle repeated work** under `scripts/`.

After edits: rerun evals into `iteration-<N+1>/`, regenerate the viewer, collect feedback, repeat until the user is satisfied or progress stalls.

---

## Advanced: Blind comparison

Optional rigor when comparing two skill versions. Read `agents/comparator.md` and `agents/analyzer.md`. Requires independent parallel runs — see the skill's `## Tool notes`.

---

## Description optimization

The `description` field drives skill discovery. After creating or improving a skill, offer to tune it.

### Shared steps (all tools)

**Step 1 — Trigger eval queries:** ~20 realistic queries (should-trigger / should-not-trigger), concrete and edge-case heavy. See `references/description-eval-queries.md` for format, examples, and coverage guidance.

**Step 2 — User review:** use `assets/eval_review.html`. Replace placeholders:

- `__EVAL_DATA_PLACEHOLDER__` → JSON array of eval items (no quotes around it — JS variable assignment)
- `__SKILL_NAME_PLACEHOLDER__` → skill name
- `__SKILL_DESCRIPTION_PLACEHOLDER__` → current description

Open in a browser; user edits queries, toggles should-trigger, exports JSON (often to Downloads as `eval_set.json`).

**Step 3 (automated — tool-specific):** run `run_loop.py` only when the skill's `## Tool notes` documents it (Claude Code / Cowork). Otherwise skip to Step 4 after Steps 1–2.

**Step 4 — Apply:** Update skill frontmatter in the authoritative edit location (per **Where to edit**), reinstall if bootstrap. Show before/after when possible.

For how skill triggering works in general (name + description matching, one-step tasks the base model handles directly), see `references/description-eval-queries.md`.

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
