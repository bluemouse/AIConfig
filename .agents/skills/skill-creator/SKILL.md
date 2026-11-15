---
name: skill-creator
description: Create portable skills for GitHub Copilot, Cursor, and Claude Code using a single-root layout, and iteratively improve them. Use when users want to create a skill from scratch, bootstrap under the skills directory and install to .agents/skills, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say "portable skill" explicitly. Does not trigger on creating custom agents (agent-creator) or slash commands and Copilot prompts (command-creator).
---

# Skill Creator

A skill for creating portable skill definitions and iteratively improving them.

At a high level, creating a skill goes like this:

- Decide what the skill should do, when it should trigger, and how success is measured
- **Choose an authoring path** — bootstrap under `skills/<name>/` (preferred) or direct scaffold with `create_skill.py` (see below)
- Write a tool-neutral `SKILL.md` body; put tool-specific guidance in `## Tool notes` sections
- **Install** when using bootstrap (`install_portable_skill.py`); direct scaffold writes installed paths immediately
- Create a few realistic test prompts and run them with an agent that has access to the skill
- Help the user evaluate results qualitatively and, when supported, quantitatively
- Rewrite content based on feedback (in bootstrap or installed paths, per path)
- Repeat until satisfied, then expand the test set

**Tool-specific execution** (how to spawn eval runs, baselines, description optimization, and reload steps) lives in the `## Tool notes` section of the skill — read it after the tool-neutral body. Do not assume subagents, a particular CLI, or a browser unless the Tool notes document them.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft skill, go straight to eval/iterate. If they prefer a lightweight pass without formal evals, follow their lead.

## When NOT to Use

- **Creating a custom agent** — use [../agent-creator/SKILL.md](../agent-creator/SKILL.md), which follows a shared-first layout for agents
- **Creating a slash command or Copilot prompt** — use [../command-creator/SKILL.md](../command-creator/SKILL.md), which follows a shared-first layout for commands

---

## Communicating with the user

Users may range from experts to people new to terminals and config files. Match their vocabulary. Briefly explain terms like "Tool notes", "eval", or "assertion" when unsure they know them.

- "evaluation" and "benchmark" are usually fine
- For "JSON" and "assertion", explain briefly unless the user clearly knows them

If the user provides exact wording for skill instructions or the description, use it **verbatim** in generated files.

---

## Creating a skill

### Capture intent

Start by understanding intent. If the conversation already contains a workflow to capture, extract tools used, steps, corrections, and formats from history first. Confirm gaps with the user.

Ask:

1. What should this skill enable the coding agent to do?
2. When should it trigger? (phrases, contexts)
3. Where should files be written? (repo root, output directory)
4. Are there tool-specific notes for Claude Code, Cursor, or GitHub Copilot?
5. Are there tool-specific notes (eval mechanics, reload steps) for Claude Code, Cursor, or GitHub Copilot?
6. What's the expected output format?
7. Should we set up test cases? Objective outputs (transforms, extraction, fixed workflows) benefit from tests; subjective outputs (tone, design) often don't.

### Interview and research

Ask about edge cases, formats, examples, success criteria, and dependencies before writing test prompts.

The questions above are a fixed intake. When the request is ambiguous beyond them — the user is unsure whether they need a skill, an agent, or a command; requirements conflict; or nobody can yet say what a good result looks like — run the clarification loop in [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) before authoring files, and carry its requirement ledger into the skill's scope and `description`.

Check the target repository for existing skill conventions before generating files. If `skills/`, `.agents/skills/`, or tool-specific skill folders already exist, match their style.

Use available research tools (MCP, docs search, similar skills in the repo) when helpful — in parallel when your environment allows.

### Choose authoring path

Pick **one** path before writing files. Do not hand-edit installed layers (`.agents/skills/`) when bootstrap source exists — edit bootstrap and reinstall.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained skill shipped like a product; repo already uses or wants `skills/<name>/`; skill will be revised and reinstalled over time | `skills/<name>/SKILL.md` + optional `references/`, `scripts/`, `assets/` | `install_portable_skill.py` |
| **Direct** | One-off or new skill in a project without `skills/` bootstrap; quick scaffold into installed layout | `.agents/skills/<name>/` (via script) | `create_skill.py` |

**Prefer bootstrap when:**

- The skill is part of this repo's portable config (maintained alongside other skills)
- The user asks to bootstrap, migrate, or reinstall a skill from `skills/<name>/`

**Prefer direct scaffold when:**

- The target project has no `skills/` directory and no plan to add bootstrap source
- The user wants a fast first draft before deciding whether to adopt bootstrap later

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Tool-neutral behavior | `skills/<name>/SKILL.md` → reinstall | `.agents/skills/<name>/SKILL.md` |
| Tool-only notes (`## Tool notes`) | Same file, `## Tool notes` section → reinstall | `.agents/skills/<name>/SKILL.md` |
| Bundled resources | `skills/<name>/scripts/`, `references/`, `assets/` → reinstall | Same under `.agents/skills/<name>/` |
| Runtime read target | `.agents/skills/<name>/` (install output; do not hand-edit) | Same |

After bootstrap edits, run `install_portable_skill.py` before testing in the IDE.

### Bundled scripts

Resolve `<SKILL_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve `<SKILL_ROOT>` as the directory containing the **target** skill's shared `SKILL.md` (after install).

| Script | Path |
| --- | --- |
| Install bootstrap skill | `<SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py` |
| Create portable skill (direct) | `<SKILL_CREATOR_ROOT>/scripts/create_skill.py` |
| Standalone scaffold | `<SKILL_CREATOR_ROOT>/scripts/init_skill.py` |
| Validate | `<SKILL_CREATOR_ROOT>/scripts/quick_validate.py` |
| Package | `<SKILL_CREATOR_ROOT>/scripts/package_skill.py` |
| Aggregate benchmark | `<SKILL_CREATOR_ROOT>/scripts/aggregate_benchmark.py` |
| Description eval loop | `<SKILL_CREATOR_ROOT>/scripts/run_loop.py` |
| Eval viewer | `<SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py` |

Bootstrap source for this meta-skill lives at `skills/skill-creator/`; installed copies live under `.agents/skills/skill-creator/`.

**Module scripts:** run `python -m scripts.*` with `<SKILL_CREATOR_ROOT>` as the working directory so imports resolve.

### Anatomy of a portable skill

**Installed layout (single root):**

```
repo/
├── .agents/skills/<skill-name>/       # The skill (install output; one real copy)
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
└── .claude/skills -> ../.agents/skills   # Claude Code bridge symlink (auto-created on install)
```

Claude Code discovers skills through the `.claude/skills` bridge symlink; Cursor and GitHub Copilot read `.agents/skills/` directly. There are no per-tool wrapper copies.

**Bootstrap layout** (when the skill ships bootstrap source):

```
repo/
├── skills/<skill-name>/
│   ├── SKILL.md                       # Skill body (author here; tool-neutral above `## Tool notes`)
│   ├── scripts/                       # Optional bundled helpers
│   ├── references/                    # Optional on-demand docs
│   └── assets/                        # Optional templates / output files
```

**Progressive disclosure:** metadata (frontmatter) → `SKILL.md` body → bundled resources on demand.

Keep behavior that applies everywhere in the skill body above `## Tool notes` (`skills/<name>/SKILL.md` at bootstrap, `.agents/skills/<name>/` after install). Put tool-native integration only in `## Tool notes` sections (see below).

### Bootstrap a new skill

When bootstrap is the chosen path, create or edit `skills/<skill-name>/`:

1. Add `SKILL.md` with tool-neutral frontmatter (`name`, `description`) and body. Resolve `<SKILL_ROOT>` in the body so paths work after install.
2. Add optional `scripts/`, `references/`, and `assets/` as needed.
3. Add a `## Tool notes` section (with `### <Tool>` subsections) when the skill has tool-specific mechanics — eval spawn commands, reload steps, description-optimization limits. Keep it out of the tool-neutral body.
4. Validate bootstrap source before install:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py skills/<skill-name>
```

Copy from an existing skill under `skills/` or a reference template when starting from a known pattern.

### Install a bootstrap skill

When bootstrap source exists at `skills/<skill-name>/`:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py skills/<skill-name>

python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root <repo_root> \
  --name <skill-name> \
  --source skills/<skill-name> \
  --overwrite
```

Install copies the bootstrap package to `.agents/skills/<name>/` and creates the Claude Code bridge symlink (`.claude/skills -> ../.agents/skills`) when it does not yet exist. If `.claude/skills` is a real directory, install refuses and asks you to purge the legacy install first.

Validate the installed skill:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .agents/skills/<skill-name>
```

Do not hand-edit `.agents/skills/` for bootstrapped skills — reinstall from bootstrap instead.

### Scaffold a new skill (direct path)

Use `create_skill.py` for **direct** scaffold when bootstrap under `skills/<name>/` is not the chosen path. Do **not** hand-create `.agents/skills/` directories — let the script generate them.

For **bootstrap** authoring, create or edit `skills/<name>/` (see **Bootstrap a new skill** and **Install a bootstrap skill**) instead of running `create_skill.py`.

```bash
python <SKILL_CREATOR_ROOT>/scripts/create_skill.py \
  --root <repo_root> \
  --name <skill-name> \
  --overwrite
```

Use `--overwrite` only when regenerating and the user confirms.

**Validate immediately** — do not skip this step after scaffold or substantive edits:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .agents/skills/<skill-name>
```

Fix validation errors before handing off to the user. Edit the skill body, remove unused placeholders, and expand `## Tool notes` subsections per tool.

### Scaffold a standalone skill

When the user needs a full copy outside the single-root layout (e.g. a personal skills directory):

```bash
python <SKILL_CREATOR_ROOT>/scripts/init_skill.py <skill-name> --path <install-path>
```

The parent path should be a skills root (a directory named `skills`, e.g. `.agents/skills/` or a bootstrap `skills/`) — the validator rejects scaffolds nested in category subfolders.

### Skill body rules

The `SKILL.md` body must be **tool-neutral** above `## Tool notes`: workflows, formats, bundled resources, security expectations. No subagent product names, no single-vendor CLI assumptions, no reload instructions for one IDE.

Resolve `<SKILL_ROOT>` in the body as the directory containing the skill's `SKILL.md` (the installed `.agents/skills/<name>/` folder).

### Tool notes rules

Tool-native mechanics live in a `## Tool notes` H2 section at the end of the body, with `### Claude Code`, `### Cursor`, and `### GitHub Copilot` H3 subsections as needed. Tool notes must:

- Stay out of the tool-neutral body above them
- Hold all tool-native execution details (eval mechanics, reload steps, spawn commands)
- Stay optional — omit the section entirely when the skill has no tool-specific mechanics

The installed copy is one real file per skill; there are no per-tool wrapper copies to keep in sync.

### Output summary

After creating or installing files, summarize for the user:

- Authoritative edit path (`skills/<skill-name>/` or `.agents/skills/<skill-name>/`)
- Installed skill path (`.agents/skills/<skill-name>/`)
- Bridge symlink status (`.claude/skills -> ../.agents/skills`)
- Assumptions made about instructions or triggers

### Updating an existing skill

- Preserve the original `name` unless the user wants a rename
- If `skills/<name>/` exists, edit bootstrap files first (see **Where to edit**), then reinstall with `install_portable_skill.py` — do not patch `.agents/skills/` by hand
- If no bootstrap source, edit `.agents/skills/<name>/SKILL.md` directly
- Re-run `quick_validate.py` after substantive edits (bootstrap source path before install, or the installed path after)
- Re-run `create_skill.py --overwrite` only on the **direct** path when regenerating from scratch and the user confirms

### Write the SKILL.md

- **name**: kebab-case identifier (lowercase letters, digits, hyphens; max 64 characters)
- **description**: Primary trigger mechanism — what the skill does **and** when to use it. Be specific and slightly expansive so under-triggering is less likely. Keep all "when to use" phrasing in `description`, not the body.
- **compatibility**: optional; rarely needed

---

## Skill writing guide

Every skill you create should be **correct**, **complete**, and **efficient on the specified tool**. Use these as explicit quality bars during drafting and review.

### Correctness

- Define a clear scope — what the skill owns and what it must defer to the user or other skills
- State accurate capabilities; do not instruct behavior the target tools cannot perform
- Include concrete success criteria the agent can verify before finishing
- Prefer citing files, functions, or code regions over vague references
- When the skill must refuse or escalate, say when and how

### Completeness

- Cover the happy path and common edge cases (missing context, empty inputs, failed commands, ambiguous requirements)
- Specify output format (sections, JSON shape, bullet structure)
- Define boundaries: what not to change, what not to assume, when to ask clarifying questions
- Include a short workflow section when the skill has ordered steps
- Split long domain content into `references/` — load on demand only

### Efficiency (tool-native)

- Keep tool-neutral instructions lean — every line should earn its place in context
- Put tool-specific shortcuts in `## Tool notes` (e.g. Task subagents in Cursor, Claude `-p` patterns, Copilot frontmatter)
- Avoid duplicating repo-wide rules the base model already follows
- Prefer imperative instructions; explain *why* when it helps generalization
- Bundle repeated work under `scripts/` when every run reinvents the same helper

### Anatomy (shared package)

```
<skill-name>/
├── SKILL.md
├── scripts/      # Executable helpers
├── references/   # Docs loaded on demand
└── assets/       # Templates, files for output (not loaded as context)
```

### Progressive disclosure

1. Metadata (~100 words) — always visible
2. `SKILL.md` body (<500 lines ideal)
3. Bundled resources — unlimited; scripts may run without loading

Split long content into `references/`. For files >300 lines, add a table of contents.

**Domain variants:** e.g. `references/aws.md`, `references/gcp.md` — agent reads the relevant file only.

### Principle of lack of surprise

No malware or hidden behavior. Decline requests for misleading or unauthorized-access skills.

### Writing patterns

See `references/output-patterns.md` and `references/workflows.md`.

See `references/portable-skill-layout.md` for path conventions, layouts, and a worked example.

---

## Test prompts

Draft 2–3 realistic user prompts that should invoke this skill. Confirm with the user before running.

For each prompt, note:

- **Expected behavior** — what a correct, complete response looks like
- **Efficiency signal** — unnecessary steps, over-long output, or wrong tool usage to watch for
- **Tool** — which environment to test in

Save eval prompts to `skills/<skill-name>/evals/evals.json` when bootstrapping, or `.agents/skills/<skill-name>/evals/evals.json` on the direct path (prompts first; assertions later):

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema.

Follow the skill's `## Tool notes` for how to execute eval runs (Task subagent, parallel baselines, etc.).

---

## Running and evaluating test cases

Follow the skill's `## Tool notes` for how to execute runs (parallel vs sequential, baselines, timing capture). This section defines the **shared workspace layout and artifacts** all tools should use when running full evals.

Do not stop partway through a planned eval iteration. Do not use unrelated testing skills.

Cap concurrent eval runs at the [../agent-runner/SKILL.md](../agent-runner/SKILL.md)
defaults — at most 4 with-skill/baseline pairs (8 subagents) in flight; queue
excess test cases in later batches within the same iteration.

Workspace: `<skill-name>-workspace/` sibling to `.agents/skills/`, organized by `iteration-N/` and per-eval directories. Create directories as you go.

### Workspace artifacts

**eval_metadata.json** (per eval):

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

**Run directories:** each eval typically has `with_skill/outputs/` and a baseline (`without_skill/outputs/` for new skills, or `old_skill/outputs/` when comparing versions). Snapshot the prior shared skill before baseline runs on improvements.

**timing.json** (when your tool provides token/duration data):

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

**grading.json:** use `text`, `passed`, and `evidence` on each expectation (required by the viewer). See `agents/grader.md`.

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

**feedback.json** after user review:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "...", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user accepted the output. Kill any background viewer server when finished.

### Assertions

Draft objective, descriptively named assertions while runs execute. Skip forced assertions for subjective skills. Update `eval_metadata.json` and `evals/evals.json`.

---

## Reviewing and improving the skill

After test runs:

1. **Correctness** — Did the skill stay in scope? Were recommendations accurate? Any hallucinated files or APIs?
2. **Completeness** — Were edge cases handled? Was output format consistent? Missing escalation when needed?
3. **Efficiency** — Was the prompt too long to follow? Did the agent repeat work or ignore native tool features documented in Tool notes?

Improvement rules:

1. **Generalize** — fixes must help beyond the few eval examples
2. **Keep the skill file lean** — read transcripts, not just final outputs
3. **Edit the tool-neutral body first** — in `skills/<name>/SKILL.md` when bootstrap exists, else `.agents/skills/<name>/SKILL.md`; reinstall after bootstrap edits
4. **Edit Tool notes for tool-only gaps** — the `## Tool notes` section of the same file, per-tool subsections
5. **Explain why** — prefer reasoning over ALL-CAPS MUSTs
6. **Bundle repeated work** — if every run reinvented the same script, add it under `scripts/`

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

**Step 4 — Apply:** Update skill frontmatter in the authoritative edit location (`skills/<name>/SKILL.md` or `.agents/skills/<name>/SKILL.md`), reinstall if bootstrap. Show before/after when possible.

### How skill triggering works (general)

Agents match tasks against skill **name + description** in their available-skills list. Simple one-step tasks may not invoke a skill even when the description fits, because the base model handles them directly. Write eval queries substantial enough that consulting a skill would genuinely help.

---

## Packaging

Validate, then package the installed skill:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .agents/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/package_skill.py .agents/skills/<skill-name>
```

Direct the user to the resulting `.skill` file for installation elsewhere.

---

### Related skills

| Task | Skill |
| --- | --- |
| Custom agents with shared-first layout | [../agent-creator/SKILL.md](../agent-creator/SKILL.md) |
| Slash commands and Copilot prompts | [../command-creator/SKILL.md](../command-creator/SKILL.md) |
| Settling an ambiguous request before authoring | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) |

---

## Reference files

**agents/**

- `agents/grader.md` — assertion grading
- `agents/comparator.md` — blind A/B comparison
- `agents/analyzer.md` — benchmark analysis

**references/**

- `references/portable-skill-layout.md` — paths, bootstrap layout, worked examples
- `references/schemas.md` — evals, grading, benchmark JSON
- `references/description-eval-queries.md` — trigger eval query format and examples for description tuning
- `references/output-patterns.md` — output templates
- `references/workflows.md` — workflow patterns

**scripts/** — see **Bundled scripts** above.

---

## Core loop (summary)

1. Capture intent and **choose authoring path** (bootstrap vs direct)
2. Author the body (tool-neutral above `## Tool notes`) — bootstrap: `skills/<name>/` then `install_portable_skill.py`; direct: `create_skill.py` then expand Tool notes
3. Validate (bootstrap source path or the installed path)
4. Run test prompts on the target tool (per its Tool notes)
5. Review for correctness, completeness, and efficiency; use eval viewer when running full benchmarks
6. Improve at the authoritative edit location (see **Where to edit**); reinstall if bootstrap; re-validate
7. Repeat until satisfied; offer description optimization
8. Package the skill with `package_skill.py` when distributing

## Tool notes

### Claude Code

Claude Code supports **subagents** — use the full benchmark loop from the shared workspace spec.

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

**Step 2 — Assertions while runs execute.** Draft assertions per the body guidance; update `eval_metadata.json` and `evals/evals.json`; explain them to the user.

**Step 3 — Capture timing.** When subagent completion notifications include `total_tokens` and `duration_ms`, write `timing.json` in each run directory immediately.

**Step 4 — Grade, aggregate, viewer.** Grade with `agents/grader.md` → `grading.json` per run; aggregate with `python -m scripts.aggregate_benchmark`; analyst pass with `agents/analyzer.md`; then **always** launch the viewer and show results to the human **before** revising the skill yourself. For iteration 2+, pass `--previous-workspace`.

**Step 5 — Feedback loop.** Read `feedback.json` when the user is done. Empty feedback means accepted. Kill any background viewer.

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

Use the **Task tool** to spawn subagents; the full benchmark loop (with-skill + baseline, grading, aggregation) is supported.

**Step 1:** for each test case, launch **two** Task subagents in the **same turn** — with-skill and baseline — so they finish together. With-skill prompt:

```
Execute this task:
- Skill path: .agents/skills/<skill-name>/
- Task: <eval prompt>
- Input files: <eval files or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what matters — e.g. final CSV, generated file>
```

Baseline for a new skill: same prompt, no skill path → `without_skill/outputs/`. For an improvement: snapshot the skill first (`cp -r .agents/skills/<name> <workspace>/skill-snapshot/`), point the baseline at the snapshot → `old_skill/outputs/`.

**Steps 2–5:** as in the Claude Code notes above (assertions while runs execute; `timing.json` when Task notifications include `total_tokens`/`duration_ms`; grade → aggregate → viewer; read `feedback.json`, kill background viewer `kill $VIEWER_PID`).

**No browser / remote dev:** pass `--static <output.html>` and share the file path; the user downloads `feedback.json` from the static page — copy it into the workspace for the next iteration.

**Description optimization:** automated shared Step 3 (`run_loop.py`) is **not available** — it requires the Claude Code CLI. Use the shared manual path: draft queries, review with `assets/eval_review.html`, revise the description, sync it, and ask the user to test with realistic prompts.

Optional frontmatter: add `disable-model-invocation: true` if the skill should load only when explicitly requested rather than via description matching.

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
