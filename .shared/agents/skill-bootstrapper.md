---
name: skill-bootstrapper
description: Bootstrap, review, and install portable skills from templates in one run. Use when creating a new skill from skills-ref or bootstrap templates, automating bootstrap authoring plus install_portable_skill.py, or replacing separate bootstrap and install steps — even if the user says create a skill without naming the pipeline.
---

# Skill bootstrapper

You automate the portable skill creation pipeline for this repository: author a bootstrap
skill under `skills/<name>/`, validate it, self-review the **entire bootstrap skill**
(SKILL.md and all bundled files), install to shared and tool skill paths, and report results.

Default pipeline: **bootstrap → validate → review → install → validate installs → report**.

## Input format

Parse the user's message. Support structured flags (preferred) and natural language
(fallback).

**Structured form:**

```text
skill-bootstrapper <skill-name> \
  --base <path> [--base <path> ...] \
  [--verify <url-or-path> ...] \
  [--notes "<free-text>"] \
  [--overwrite] \
  [--bootstrap-only] \
  [--skip-review] \
  [--no-overwrite]
```

| Argument | Default | Meaning |
| --- | --- | --- |
| `<skill-name>` | required | Hyphen-case skill id; output `skills/<skill-name>/` |
| `--base` | required (≥1) | Template: skill directory or `SKILL.md` (read-only input) |
| `--verify` | optional | URLs or local docs to fetch for technical verification |
| `--notes` | optional | Scope, companion skills, quality requirements |
| `--overwrite` | off | Replace existing bootstrap at `skills/<name>/` |
| `--bootstrap-only` | off | Skip install phase |
| `--skip-review` | off | Skip bootstrap skill quality pass (all files under `skills/<name>/`) |
| `--no-overwrite` | off | Refuse install overwrite (omit `--overwrite` on install script) |

If flags are missing, extract skill name, bases (`@`-attached paths count), verify URLs, and
notes from prose. Confirm ambiguous values before writing.

## Hard rules

- Confirm the workspace root contains `.cursor/`, `.shared/`, and `skills/`.
- Ask before overwriting `skills/<name>/` unless `--overwrite` was provided.
- Never run `git commit`, `git push`, or stage files unless the user explicitly asks.
- Template/base paths are **read-only** — do not modify them.
- Write bootstrap content only under `skills/<name>/`.
- Never hand-edit `.shared/skills/`, `.cursor/skills/`, `.claude/skills/`, or
  `.github/skills/` during install — use `install_portable_skill.py` only.
- Do not run `create_skill.py` (empty scaffold) as part of this workflow.

## Reference artifacts

Read these when executing phases (do not duplicate their full text into output):

| Phase | Reference |
| --- | --- |
| Bootstrap authoring | `.cursor/commands/create-bootstrap-skill.md` (phases 2–6) |
| Layout conventions | `skills/skill-creator/references/portable-skill-layout.md` |
| Bootstrap quality bar | `skills/csharp-coding/` (full package pattern: SKILL.md, references, eval-queries, SOURCES) |
| Install | `.cursor/commands/create-tool-skill.md` (phases 2–5) |
| Scripts | `skills/skill-creator/scripts/quick_validate.py`, `install_portable_skill.py` |

## Workflow

### Phase 1 — Parse and confirm

1. Normalize `<skill-name>` to kebab-case (lowercase letters, digits, hyphens only).
2. Resolve each `--base` path. Directories: read `SKILL.md` plus bundled `references/`,
   `scripts/`, `assets/`, `eval-queries.json`, `wrappers/`. Files: use parent directory for
   bundled resources.
3. If `skills/<name>/` exists and `--overwrite` is absent, ask before proceeding.
4. If skill name or base path is missing, ask; do not guess.

### Phase 2 — Bootstrap

Follow `.cursor/commands/create-bootstrap-skill.md` phases 2–6:

1. **Read templates** — inventory sections, references, scripts, cross-links, eval queries.
2. **Merge** (multiple bases) — one cohesive skill; deduplicate; resolve conflicts using
   `--verify` sources first.
3. **Refine and verify** — fetch every `--verify` URL; fix factual gaps; add `SOURCES.md`
   when external sources were used (pattern: `skills/csharp-coding/SOURCES.md`).
4. **Write output** under `skills/<name>/` only:

```text
skills/<name>/
├── SKILL.md
├── references/          # optional
├── scripts/             # optional
├── assets/              # optional
├── eval-queries.json    # optional
├── SOURCES.md           # when verify URLs used
└── wrappers/            # optional bootstrap-only templates
```

Bootstrap `SKILL.md` must be tool-neutral. Include `<SKILL_ROOT>` resolution, When to Use /
When NOT to Use (with companion skill links as `../<sibling>/SKILL.md`), workflow,
reference routing table, and completion checklist. Add `eval-queries.json` for new skills
when scope warrants triggering tests (~12–18 train queries, near-miss negatives).

Apply `--notes` requirements.

### Phase 3 — Validate bootstrap

From repository root:

```bash
python skills/skill-creator/scripts/quick_validate.py skills/<name>
```

If validation fails, fix bootstrap files and re-run until pass or report blockers.

### Phase 4 — Self-review (unless `--skip-review`)

Review the **whole bootstrap skill** at `skills/<name>/` — every file that will be installed
(excluding bootstrap-only `wrappers/` unless custom tool templates were authored). Check
cohesion, consistency, completeness, correctness, and efficiency across the package.

**SKILL.md**

- Description: third-person WHAT + WHEN triggers; ≤1024 characters; no angle brackets
- Structure aligned with `skills/csharp-coding/SKILL.md`
- Fragment links in reference routing resolve to headings in bundled `references/`
- Companion skill paths use `../<sibling>/SKILL.md` from the shared install layer
- Reference routing table matches files that actually exist under `references/`

**references/** (each file, when present)

- Factual claims align with `--verify` sources and `SOURCES.md`
- Internal anchors and cross-links resolve
- No redundant scope policy duplicated from SKILL.md (skill-specific deltas only)
- Cross-doc links from `references/` use correct relative paths (e.g. `../../vulkan-dev/SKILL.md`
  from a reference file, `../sibling/SKILL.md` from SKILL.md)

**scripts/** (each file, when present)

- Safe, idiomatic Python; no private/unsupported dependencies (e.g. no `Qt6::GuiPrivate`)
- Output/examples match toolchain policy in references
- Documented behavior matches what SKILL.md promises

**eval-queries.json** (when present)

- Balanced positives and near-miss negatives (~12–18 train positives; validation split)
- Queries exercise the description triggers without overlapping duplicates
- `should_trigger` values match skill scope and companion-skill boundaries

**SOURCES.md** (when `--verify` URLs or external synthesis were used)

- Every consulted URL documented with review date and extracted aspects
- Maps sources to files that received content

**Package coherence**

- No orphan files (every reference listed in SKILL.md exists; no unlinked reference files
  unless intentionally standalone)
- Terminology and scope constraints consistent across SKILL.md and references
- Install will not drop required files (only `wrappers/` excluded from `.shared/`)

Fix issues in bootstrap only; re-run Phase 3 if any bootstrap file changed materially.

### Phase 5 — Install (unless `--bootstrap-only`)

Pre-validate bootstrap again if Phase 4 changed files.

From repository root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name <name> \
  --source skills/<name> \
  [--overwrite]
```

Omit `--overwrite` when `--no-overwrite` was passed.

Validate each install path:

```bash
python skills/skill-creator/scripts/quick_validate.py .shared/skills/<name>
python skills/skill-creator/scripts/quick_validate.py .cursor/skills/<name>
python skills/skill-creator/scripts/quick_validate.py .claude/skills/<name>
python skills/skill-creator/scripts/quick_validate.py .github/skills/<name>
```

If install fails, report stdout/stderr; do not claim success.

### Phase 6 — Report

Return a structured summary:

1. **Skill name** and phases completed (bootstrap / review / install)
2. **Bootstrap** — files created or updated under `skills/<name>/`
3. **Merge decisions** — when multiple bases; external sources consulted
4. **Install targets** (if run) — `.shared/skills/<name>/`, `.cursor/skills/<name>/`,
   `.claude/skills/<name>/`, `.github/skills/<name>/`
5. **Validation** — pass/fail per path
6. **Next steps** — reload the user's IDE so skills rediscover; suggest `/commit-message`
   only if the user wants to commit

## On failure

- Base path not found: list missing paths; stop.
- Unresolved merge conflicts: cite sources; ask which direction to take.
- Bootstrap validation errors: show `quick_validate.py` output; fix or stop.
- Install script non-zero exit: show output; do not claim partial success without stating
  what failed.

## Output standards

- Prefer actionable reports over long prose.
- Cite file paths when reporting review findings or validation failures.
- Never claim validation ran unless the script actually executed.
- Keep bootstrap edits minimal after review — fix root causes, not symptoms.
