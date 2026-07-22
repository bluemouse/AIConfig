---
name: skill-creator
description: Create portable skills for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create a skill from scratch, bootstrap under the skills directory and install to .shared/skills with tool wrappers, edit or optimize an existing skill, run evals to test a skill, benchmark skill performance, or optimize a skill's description for better triggering accuracy — even if they do not say "portable skill" explicitly.
---

# Skill Creator

A skill for creating portable skill definitions and iteratively improving them.

At a high level, creating a skill goes like this:

- Decide what the skill should do, when it should trigger, and how success is measured
- **Choose an authoring path** — bootstrap under `skills/<name>/` (preferred) or direct scaffold with `create_skill.py` (see below)
- Write a tool-neutral shared `SKILL.md` and tool-specific wrapper notes
- **Install** when using bootstrap (`install_portable_skill.py`); direct scaffold writes installed paths immediately
- Create a few realistic test prompts and run them with an agent that has access to the skill
- Help the user evaluate results qualitatively and, when supported, quantitatively
- Rewrite shared content and wrappers based on feedback (in bootstrap or installed paths, per path)
- Repeat until satisfied, then expand the test set

**Tool-specific execution** (how to spawn eval runs, baselines, description optimization, and reload steps) lives in your **tool wrapper** — read it after this shared skill. Do not assume subagents, a particular CLI, or a browser unless your wrapper documents them.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft skill, go straight to eval/iterate. If they prefer a lightweight pass without formal evals, follow their lead.

---

## Communicating with the user

Users may range from experts to people new to terminals and config files. Match their vocabulary. Briefly explain terms like "wrapper", "eval", or "assertion" when unsure they know them.

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
5. Should wrappers reference the shared skill, or does the user need a standalone copy in one tool folder?
6. What's the expected output format?
7. Should we set up test cases? Objective outputs (transforms, extraction, fixed workflows) benefit from tests; subjective outputs (tone, design) often don't.

### Interview and research

Ask about edge cases, formats, examples, success criteria, and dependencies before writing test prompts.

Check the target repository for existing skill conventions before generating files. If `skills/`, `.shared/skills/`, or tool-specific skill folders already exist, match their style.

Use available research tools (MCP, docs search, similar skills in the repo) when helpful — in parallel when your environment allows.

### Choose authoring path

Pick **one** path before writing files. Do not hand-edit installed layers (`.shared/skills/`, tool skill folders) when bootstrap source exists — edit bootstrap and reinstall.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained skill shipped like a product; repo already uses or wants `skills/<name>/`; skill will be revised and reinstalled over time | `skills/<name>/SKILL.md` + optional `references/`, `scripts/`, `assets/`, and `wrappers/<tool>/SKILL.md` | `install_portable_skill.py` |
| **Direct** | One-off or new skill in a project without `skills/` bootstrap; quick scaffold into installed layout | `.shared/skills/<name>/` (via script) | `create_skill.py` |

**Prefer bootstrap when:**

- The skill is part of this repo's portable config (maintained alongside other skills)
- You need custom tool wrappers with eval mechanics, reload steps, or frontmatter per tool
- The user asks to bootstrap, migrate, or reinstall a skill from `skills/<name>/`

**Prefer direct scaffold when:**

- The target project has no `skills/` directory and no plan to add bootstrap source
- You need all three tool wrappers generated immediately with default templates
- The user wants a fast first draft before deciding whether to adopt bootstrap later

**Partial custom wrappers:** Bootstrap may ship custom wrappers for only some tools under `wrappers/`. Install always generates all three tool skill paths — missing custom wrappers get minimal default templates.

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Cross-tool behavior | `skills/<name>/SKILL.md` → reinstall | `.shared/skills/<name>/SKILL.md` |
| Tool-only notes / frontmatter | `skills/<name>/wrappers/<tool>/SKILL.md` → reinstall | `.cursor/skills/<name>/SKILL.md`, etc. |
| Bundled resources | `skills/<name>/scripts/`, `references/`, `assets/` → reinstall | Same under `.shared/skills/<name>/` |
| Runtime read target | `.shared/skills/<name>/` (install output; do not hand-edit) | Same |

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

Bootstrap source for this meta-skill lives at `skills/skill-creator/`; installed copies live under `.shared/skills/skill-creator/`.

**Module scripts:** run `python -m scripts.*` with `<SKILL_CREATOR_ROOT>` as the working directory so imports resolve.

### Anatomy of a portable skill

**Installed layout:**

```
repo/
├── .shared/skills/<skill-name>/       # Tool-neutral skill (install output)
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
├── .cursor/skills/<skill-name>/       # Cursor wrapper (SKILL.md only)
├── .claude/skills/<skill-name>/       # Claude Code wrapper
└── .github/skills/<skill-name>/       # GitHub Copilot wrapper
```

**Bootstrap layout** (when the skill ships bootstrap source):

```
repo/
├── skills/<skill-name>/
│   ├── SKILL.md                       # Shared skill body (author here)
│   ├── scripts/                       # Optional bundled helpers
│   ├── references/                    # Optional on-demand docs
│   ├── assets/                        # Optional templates / output files
│   └── wrappers/                      # Optional custom tool templates
│       ├── cursor/SKILL.md
│       ├── claude/SKILL.md
│       └── github/SKILL.md
```

**Progressive disclosure:** metadata (frontmatter) → shared `SKILL.md` body → bundled resources on demand.

Keep behavior that applies everywhere in the shared skill (`skills/<name>/SKILL.md` at bootstrap, `.shared/skills/<name>/` after install). Put tool-native integration in wrappers only. Repo-root `skills-ref/` holds reference templates; bootstrapped portable skills belong in `skills/<name>/`.

### Bootstrap a new skill

When bootstrap is the chosen path, create or edit `skills/<skill-name>/`:

1. Add `SKILL.md` with tool-neutral frontmatter (`name`, `description`) and body. Resolve `<SKILL_ROOT>` in the shared body so paths work after install.
2. Add optional `scripts/`, `references/`, and `assets/` as needed.
3. Add optional custom wrappers under `wrappers/{cursor,claude,github}/SKILL.md` that point to `../../../.shared/skills/<name>/SKILL.md`, include reload notes, and document tool-specific mechanics (eval spawn, description optimization limits, optional frontmatter). If omitted, install generates minimal default wrappers.
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

Install copies the bootstrap package to `.shared/skills/<name>/` (excluding `wrappers/`) and generates tool skills — using custom wrappers from `wrappers/` when present, otherwise default templates.

Validate each installed path:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .shared/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .cursor/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .claude/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .github/skills/<skill-name>
```

Do not hand-edit `.shared/skills/` or tool skill folders for bootstrapped skills — reinstall from bootstrap instead.

### Scaffold a new skill (direct path)

Use `create_skill.py` for **direct** scaffold when bootstrap under `skills/<name>/` is not the chosen path. Do **not** hand-create `.shared/skills/` or tool wrapper directories — let the script generate them.

For **bootstrap** authoring, create or edit `skills/<name>/` (see **Bootstrap a new skill** and **Install a bootstrap skill**) instead of running `create_skill.py`.

```bash
python <SKILL_CREATOR_ROOT>/scripts/create_skill.py \
  --root <repo_root> \
  --name <skill-name> \
  --overwrite
```

Use `--claude-note`, `--cursor-note`, and `--github-note` for tool-specific wrapper hints. Use `--overwrite` only when regenerating and the user confirms.

**Validate immediately** — do not skip this step after scaffold or substantive edits:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .shared/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .cursor/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .claude/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .github/skills/<skill-name>
```

Fix validation errors before handing off to the user. Edit the shared skill, sync `description` into wrappers when it changes, remove unused placeholders, and expand wrapper sections per tool.

### Scaffold a standalone skill

When the user needs a full copy in one tool location (not the portable wrapper layout):

```bash
python <SKILL_CREATOR_ROOT>/scripts/init_skill.py <skill-name> --path <install-path>
```

### Shared skill rules

Shared `SKILL.md` must be **tool-neutral**: workflows, formats, bundled resources, security expectations. No subagent product names, no single-vendor CLI assumptions, no reload instructions for one IDE.

Resolve `<SKILL_ROOT>` in the shared body as the directory containing the shared skill's `SKILL.md` (the installed `.shared/skills/<name>/` folder).

### Wrapper rules

Wrappers contain **only** `SKILL.md`. They must:

- Use the tool's expected path (see `references/portable-skill-layout.md`)
- Share `name` and `description` with the shared skill (sync on changes)
- Point to `.shared/skills/<skill-name>/SKILL.md` as canonical
- Tell the agent to read the shared skill first and resolve `<SKILL_ROOT>` from the shared directory
- Hold all tool-native execution details (eval mechanics, reload steps, optional frontmatter like `disable-model-invocation`)

Do not duplicate the full shared body into wrappers unless the user requires copy-based portability.

Reference-based wrappers reduce duplication but depend on the tool following the wrapper instruction to read the shared skill. If the user needs maximum standalone behavior, use `init_skill.py` or generate copy-based wrappers instead.

After scaffold or install of a **new** skill, help the user draft **native wrapper sections** per tool. Use `--cursor-note`, `--claude-note`, and `--github-note` for one-line hints at direct scaffold time; expand in bootstrap `wrappers/` or installed tool skill files afterward. Do not leave TODO-only wrappers for production skills.

### Output summary

After creating or installing files, summarize for the user:

- Authoritative edit path (`skills/<skill-name>/` or `.shared/skills/<skill-name>/`)
- Shared skill path (`.shared/skills/<skill-name>/`)
- Wrapper paths (`.cursor/`, `.claude/`, `.github/skills/<skill-name>/`)
- Assumptions made about instructions or triggers
- Whether layouts are reference wrappers or standalone copies

### Updating an existing skill

- Preserve the original `name` unless the user wants a rename
- If `skills/<name>/` exists, edit bootstrap files first (see **Where to edit**), then reinstall with `install_portable_skill.py` — do not patch `.shared/skills/` or tool folders by hand
- If no bootstrap source, edit `.shared/skills/<name>/SKILL.md` first for cross-tool behavior; wrappers for tool-only notes
- Re-run `quick_validate.py` after substantive edits (bootstrap source path before install, or per installed path after)
- Sync `description` across shared content and every installed wrapper when it changes
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

- Keep shared instructions lean — every line should earn its place in context
- Put tool-specific shortcuts in wrappers (e.g. Task subagents in Cursor, Claude `-p` patterns, Copilot frontmatter)
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

See `references/portable-skill-layout.md` for path conventions, wrapper templates, relative paths, and a worked example.

---

## Test prompts

Draft 2–3 realistic user prompts that should invoke this skill. Confirm with the user before running.

For each prompt, note:

- **Expected behavior** — what a correct, complete response looks like
- **Efficiency signal** — unnecessary steps, over-long output, or wrong tool usage to watch for
- **Tool** — which wrapper/environment to test in

Save eval prompts to `skills/<skill-name>/evals/evals.json` when bootstrapping, or `.shared/skills/<skill-name>/evals/evals.json` on the direct path (prompts first; assertions later):

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

Follow your **tool wrapper** for how to execute eval runs (Task subagent, parallel baselines, etc.).

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

## Reviewing and improving the skill

After test runs:

1. **Correctness** — Did the skill stay in scope? Were recommendations accurate? Any hallucinated files or APIs?
2. **Completeness** — Were edge cases handled? Was output format consistent? Missing escalation when needed?
3. **Efficiency** — Was the prompt too long to follow? Did the agent repeat work or ignore native tool features documented in the wrapper?

Improvement rules:

1. **Generalize** — fixes must help beyond the few eval examples
2. **Keep the shared file lean** — read transcripts, not just final outputs
3. **Edit shared first** — cross-tool behavior in `skills/<name>/SKILL.md` when bootstrap exists, else `.shared/skills/<name>/SKILL.md`; reinstall after bootstrap edits
4. **Edit wrappers for tool-only gaps** — bootstrap: `skills/<name>/wrappers/<tool>/SKILL.md`; direct: tool skill folders under `.cursor/`, `.claude/`, `.github/`
5. **Explain why** — prefer reasoning over ALL-CAPS MUSTs
6. **Bundle repeated work** — if every run reinvented the same script, add it under `scripts/`

After edits: rerun evals into `iteration-<N+1>/`, regenerate the viewer, collect feedback, repeat until the user is satisfied or progress stalls.

---

## Advanced: Blind comparison

Optional rigor when comparing two skill versions. Read `agents/comparator.md` and `agents/analyzer.md`. Requires independent parallel runs — see your tool wrapper.

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

**Step 3 (automated — tool-specific):** run `run_loop.py` only when your tool wrapper documents it (Claude Code / Cowork). Otherwise skip to Step 4 after Steps 1–2.

**Step 4 — Apply:** Update shared skill frontmatter in the authoritative edit location (`skills/<name>/SKILL.md` or `.shared/skills/<name>/SKILL.md`), sync `description` into every wrapper, reinstall if bootstrap. Show before/after when possible.

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

- `references/portable-skill-layout.md` — paths, bootstrap layout, wrapper templates, worked examples
- `references/schemas.md` — evals, grading, benchmark JSON
- `references/description-eval-queries.md` — trigger eval query format and examples for description tuning
- `references/output-patterns.md` — output templates
- `references/workflows.md` — workflow patterns

**scripts/** — see **Bundled scripts** above.

---

## Core loop (summary)

1. Capture intent and **choose authoring path** (bootstrap vs direct)
2. Author shared body and wrappers — bootstrap: `skills/<name>/` then `install_portable_skill.py`; direct: `create_skill.py` then expand wrappers
3. Validate (bootstrap source path or per installed path)
4. Run test prompts on the target tool (per tool wrapper)
5. Review for correctness, completeness, and efficiency; use eval viewer when running full benchmarks
6. Improve at the authoritative edit location (see **Where to edit**); sync `description`; reinstall if bootstrap; re-validate
7. Repeat until satisfied; offer description optimization
8. Package shared skill with `package_skill.py` when distributing
