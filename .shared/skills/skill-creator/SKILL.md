---
name: skill-creator
description: Create portable skills for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create a skill from scratch, scaffold `.shared/skills` with tool wrappers in `.cursor/skills`, `.claude/skills`, or `.github/skills`, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say "portable skill" explicitly.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- **Scaffold** the shared skill in `.shared/skills/<name>/` and generate tool wrappers with `create_skill.py`
- Write a draft of the shared `SKILL.md` (tool-neutral) and tool-specific notes in each wrapper
- Create a few test prompts and run them with an agent that has access to the skill
- Help the user evaluate the results qualitatively and, when supported, quantitatively
- Rewrite the skill based on feedback and benchmark results
- Repeat until satisfied, then expand the test set

**Tool-specific execution** (how to spawn eval runs, baselines, description optimization, and reload steps) lives in your **tool wrapper** — read it after this shared skill. Do not assume subagents, a particular CLI, or a browser unless your wrapper documents them.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft, go straight to eval/iterate. If they prefer a lightweight pass without formal evals, follow their lead.

---

## Communicating with the user

Users may range from experts to people new to terminals and config files. Match their vocabulary. Briefly explain terms like "wrapper", "eval", or "assertion" when unsure they know them.

- "evaluation" and "benchmark" are usually fine
- For "JSON" and "assertion", explain briefly unless the user clearly knows them

---

## Creating a skill

### Capture Intent

Start by understanding intent. If the conversation already contains a workflow to capture, extract tools used, steps, corrections, and formats from history first. Confirm gaps with the user.

1. What should this skill enable the coding agent to do?
2. When should it trigger? (phrases, contexts)
3. Where should files be written? (repo root, output directory)
4. Are there tool-specific notes for Claude Code, Cursor, or GitHub Copilot?
5. Should wrappers reference the shared skill, or does the user need a standalone copy in one tool folder?
6. What's the expected output format?
7. Should we set up test cases? Objective outputs (transforms, extraction, fixed workflows) benefit from tests; subjective outputs (tone, design) often don't.

### Interview and Research

Ask about edge cases, formats, examples, success criteria, and dependencies before writing test prompts.

Use available research tools (MCP, docs search, similar skills) when helpful — in parallel when your environment allows.

### Bundled scripts

Resolve `<SKILL_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve `<SKILL_ROOT>` the same way when paths refer to bundled resources.

| Script | Path |
| --- | --- |
| Create portable skill | `<SKILL_CREATOR_ROOT>/scripts/create_skill.py` |
| Install bootstrap skill | `<SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py` |
| Standalone scaffold | `<SKILL_CREATOR_ROOT>/scripts/init_skill.py` |
| Validate | `<SKILL_CREATOR_ROOT>/scripts/quick_validate.py` |
| Package | `<SKILL_CREATOR_ROOT>/scripts/package_skill.py` |
| Aggregate benchmark | `<SKILL_CREATOR_ROOT>/scripts/aggregate_benchmark.py` |
| Description eval loop | `<SKILL_CREATOR_ROOT>/scripts/run_loop.py` |
| Eval viewer | `<SKILL_CREATOR_ROOT>/eval-viewer/generate_review.py` |

Bootstrap source for this meta-skill may live at `skills/skill-creator/`; installed copies live under `.shared/skills/skill-creator/`.

**Module scripts:** run `python -m scripts.*` with `<SKILL_CREATOR_ROOT>` as the working directory so imports resolve.

### Anatomy of a portable skill

```
repo/
├── .shared/skills/<skill-name>/     # Canonical: SKILL.md + scripts/ references/ assets/
├── .cursor/skills/<skill-name>/     # Cursor wrapper (SKILL.md only)
├── .claude/skills/<skill-name>/     # Claude Code wrapper
└── .github/skills/<skill-name>/     # GitHub Copilot wrapper
```

**Progressive disclosure:** metadata (frontmatter) → shared `SKILL.md` body → bundled resources on demand.

Keep behavior that applies everywhere in `.shared/skills/<skill-name>/`. Put tool-specific integration in wrappers only. Repo-root `skills/` holds bootstrap/meta packages, not user portable skills.

### Scaffold a new skill (project, shared-first)

**Always** use `create_skill.py` for repository projects. Do **not** hand-create skill directories or placeholder folders.

```bash
python <SKILL_CREATOR_ROOT>/scripts/create_skill.py --root <repo_root> --name <skill-name>
```

Use `--claude-note`, `--cursor-note`, and `--github-note` for tool-specific wrapper hints. Use `--overwrite` only when regenerating and the user confirms.

Validate immediately:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .shared/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .cursor/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .claude/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .github/skills/<skill-name>
```

Edit the shared skill, sync `description` into wrappers when it changes, remove unused placeholders, re-validate before packaging.

### Scaffold a standalone skill

```bash
python <SKILL_CREATOR_ROOT>/scripts/init_skill.py <skill-name> --path <install-path>
```

### Shared skill rules

Shared `SKILL.md` must be **tool-neutral**: workflows, formats, bundled resources, security expectations. No subagent product names, no single-vendor CLI assumptions, no reload instructions for one IDE.

### Wrapper rules

Wrappers contain **only** `SKILL.md`. They must:

- Share `name` and `description` with the shared skill (sync on changes)
- Point to `.shared/skills/<skill-name>/SKILL.md` as canonical
- Tell the agent to read the shared skill first and resolve `<SKILL_ROOT>` from the shared directory
- Hold all tool-native execution details (eval mechanics, reload steps, optional frontmatter like `disable-model-invocation`)

Do not duplicate the full shared body into wrappers unless the user requires copy-based portability.

After `create_skill.py` scaffolds a **new** skill, help the user draft **native wrapper sections** per tool (reload steps, eval execution, description optimization limits). Do not leave TODO-only wrappers for production skills. Use `--cursor-note`, `--claude-note`, and `--github-note` for one-line hints at scaffold time; expand in wrapper files afterward.

### Output summary

After creating or installing files, summarize for the user:

- Shared skill path (`.shared/skills/<skill-name>/`)
- Wrapper paths (`.cursor/`, `.claude/`, `.github/skills/<skill-name>/`)
- Assumptions made about instructions or triggers
- Whether layouts are reference wrappers or standalone copies

### Updating an existing skill

- Preserve the original `name` unless the user wants a rename
- Edit shared skill first for cross-tool behavior; wrappers for tool-only notes
- Re-run `create_skill.py --overwrite` only when regenerating from scratch and the user confirms

### Write the SKILL.md

- **name**: kebab-case identifier
- **description**: Primary trigger mechanism — what the skill does **and** when to use it. Be specific and slightly expansive so under-triggering is less likely. Keep all "when to use" phrasing in `description`, not the body.
- **compatibility**: optional; rarely needed

### Skill Writing Guide

#### Anatomy

```
<skill-name>/
├── SKILL.md
├── scripts/      # Executable helpers
├── references/   # Docs loaded on demand
└── assets/       # Templates, files for output (not loaded as context)
```

#### Progressive disclosure

1. Metadata (~100 words) — always visible
2. `SKILL.md` body (<500 lines ideal)
3. Bundled resources — unlimited; scripts may run without loading

Split long content into `references/`. For files >300 lines, add a table of contents.

**Domain variants:** e.g. `references/aws.md`, `references/gcp.md` — agent reads the relevant file only.

#### Principle of Lack of Surprise

No malware or hidden behavior. Decline requests for misleading or unauthorized-access skills.

#### Writing Patterns

See `references/output-patterns.md` and `references/workflows.md`.

Prefer imperative instructions and explain *why* when it helps generalization.

### Test Cases

Draft 2–3 realistic user prompts. Confirm with the user before running.

Save to `.shared/skills/<skill-name>/evals/evals.json` (prompts first; assertions later):

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

---

## Running and evaluating test cases

Follow your **tool wrapper** for how to execute runs (parallel vs sequential, baselines, timing capture). This section defines the **shared workspace layout and artifacts** all tools should use when running full evals.

Do not stop partway through a planned eval iteration. Do not use unrelated testing skills.

Workspace: `<skill-name>-workspace/` sibling to `.shared/skills/`, organized by `iteration-N/` and per-eval directories. Create directories as you go.

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

## Improving the skill

1. **Generalize** — fixes must help beyond the few eval examples
2. **Keep the prompt lean** — read transcripts, not just outputs
3. **Explain why** — prefer reasoning over ALL-CAPS MUSTs
4. **Bundle repeated work** — if every run reinvented the same script, add it under `scripts/`

After edits: rerun evals into `iteration-<N+1>/`, regenerate the viewer, collect feedback, repeat until the user is satisfied or progress stalls.

---

## Advanced: Blind comparison

Optional rigor when comparing two skill versions. Read `agents/comparator.md` and `agents/analyzer.md`. Requires independent parallel runs — see your tool wrapper.

---

## Description Optimization

The `description` field drives skill discovery. After creating or improving a skill, offer to tune it.

### Shared steps (all tools)

**Step 1 — Trigger eval queries:** ~20 realistic queries (should-trigger / should-not-trigger), concrete and edge-case heavy. See `references/description-eval-queries.md` for format, examples, and coverage guidance.

**Step 2 — User review:** use `assets/eval_review.html`. Replace placeholders:

- `__EVAL_DATA_PLACEHOLDER__` → JSON array of eval items (no quotes around it — JS variable assignment)
- `__SKILL_NAME_PLACEHOLDER__` → skill name
- `__SKILL_DESCRIPTION_PLACEHOLDER__` → current description

Open in a browser; user edits queries, toggles should-trigger, exports JSON (often to Downloads as `eval_set.json`).

**Step 3 (automated — tool-specific):** run `run_loop.py` only when your tool wrapper documents it (Claude Code / Cowork). Otherwise skip to Step 4 after Steps 1–2.

**Step 4 — Apply:** update shared `SKILL.md` frontmatter and sync `description` into every wrapper. Show before/after when possible.

### How skill triggering works (general)

Agents match tasks against skill **name + description** in their available-skills list. Simple one-step tasks may not invoke a skill even when the description fits, because the base model handles them directly. Write eval queries substantial enough that consulting a skill would genuinely help.

---

## Packaging

Validate, then package the **shared** skill only (wrappers stay project-local):

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .shared/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/package_skill.py .shared/skills/<skill-name>
```

Direct the user to the resulting `.skill` file for installation elsewhere.

---

## Reference files

**agents/**

- `agents/grader.md` — assertion grading
- `agents/comparator.md` — blind A/B comparison
- `agents/analyzer.md` — benchmark analysis

**references/**

- `references/portable-skill-layout.md` — paths and wrapper templates
- `references/schemas.md` — evals, grading, benchmark JSON
- `references/description-eval-queries.md` — trigger eval query format and examples for description tuning
- `references/output-patterns.md` — output templates
- `references/workflows.md` — workflow patterns

**scripts/** — see **Bundled scripts** above.

---

## Core loop (summary)

1. Capture intent and scaffold with `create_skill.py`
2. Write tool-neutral shared `SKILL.md`; put native execution in wrappers
3. Validate all four paths with `quick_validate.py`
4. Run test prompts (per tool wrapper)
5. Review via `generate_review.py` and user feedback
6. Improve, re-validate, repeat
7. Package shared skill with `package_skill.py`
