# Create bootstrap skill

Create or refine a **bootstrap skill** under `skills/<name>/` from one or more template paths. Review, merge, verify, and write tool-neutral skill content only — do **not** install shared or tool skills.

## Input format

Parse the user's message after `/create-bootstrap-skill`. Support structured flags (preferred) and natural language (fallback).

**Structured form:**

```text
/create-bootstrap-skill <skill-name> \
  --base <path> [--base <path> ...] \
  [--verify <url-or-path> ...] \
  [--notes "<free-text requirements>"] \
  [--overwrite]
```

| Argument | Required | Meaning |
| --- | --- | --- |
| `<skill-name>` | yes | Hyphen-case skill id; output directory `skills/<skill-name>/` |
| `--base` | yes (≥1) | Template source: a `SKILL.md` file or skill directory (`SKILL.md` + bundled `references/`, `scripts/`, `assets/`, `eval-queries.json`) |
| `--verify` | no | URLs, spec links, or local docs to fetch for technical verification |
| `--notes` | no | Extra scope, constraints, companion skills, or quality requirements |
| `--overwrite` | no | Explicit consent to replace an existing bootstrap skill |

**Natural language fallback:** if flags are missing, extract the skill name, base paths (`@`-attached files count), verification URLs, and notes from prose. Confirm parsed values with the user before writing.

**Examples:**

```text
/create-bootstrap-skill slang-dev \
  --base skills-ref/slang-dev/SKILL.md \
  --verify https://github.com/shader-slang/spec \
  --verify https://docs.shader-slang.org/en/latest/external/slang/docs/user-guide/
```

```text
/create-bootstrap-skill renderer-stack \
  --base skills/gpu-rendering-guide \
  --base skills/vulkan-dev \
  --notes "Single skill for architecture + Vulkan implementation"
```

```text
/create-bootstrap-skill plan-guide \
  --base skills-ref/plan-guide \
  --notes "Add eval-queries for plan validation"
```

## What to do

### Phase 1 — Parse and confirm

1. Confirm the workspace root is the repository root (where `.cursor/`, `.shared/`, and `skills/` live).
2. Normalize `<skill-name>` to hyphen-case (lowercase letters, numbers, hyphens only).
3. Require at least one `--base` path. Resolve `@`-attached paths and workspace-relative paths.
4. If `skills/<name>/` already exists and `--overwrite` is absent, **ask the user before proceeding**.
5. If any required input is missing or ambiguous, ask before writing files.

### Phase 2 — Read templates

For each `--base` path:

- **Directory:** treat as a skill root — read `SKILL.md` and bundled `references/`, `scripts/`, `assets/`, `eval-queries.json`, `wrappers/`.
- **File:** use as the primary template; also read sibling `references/`, `scripts/`, and other bundled resources from the same directory.

Build an inventory: sections, references, scripts, cross-links, eval queries, and wrapper templates.

Template paths are **read-only inputs**. Do not modify them.

### Phase 3 — Merge (when multiple bases)

Produce **one cohesive bootstrap skill**, not a concatenation:

- Unify terminology and section structure across all bases.
- Deduplicate overlapping guidance; keep the stronger, more precise version.
- Resolve conflicts using `--verify` sources first, then other authoritative external docs.
- Consolidate `references/` and `scripts/` with consistent filenames; update all links in `SKILL.md`.
- Merge or rewrite the `description` frontmatter to cover the combined scope and trigger terms.

When bases disagree on facts, prefer normative specs and official docs over informal notes.

### Phase 4 — Refine and verify

Review, update, refine, and/or extend the skill so it is **cohesive, consistent, correct, complete, and efficient**.

- Use web search or doc fetch for every `--verify` URL and for gaps in technical accuracy.
- Prefer normative specs over user guides when they conflict; note the resolution in `SOURCES.md`.
- Follow bootstrap skill conventions (see `skills/skill-creator/references/portable-skill-layout.md`):
  - Tool-neutral `SKILL.md` body — no Cursor, Claude, or Copilot mechanics.
  - Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`.
  - Bundled resources only under `references/`, `scripts/`, or `assets/`.
  - Cross-link installed sibling skills via `../<sibling>/SKILL.md` when relevant.
  - Third-person `description` with both WHAT the skill does and WHEN to use it (trigger terms).
  - Progressive disclosure: keep `SKILL.md` concise; move depth to `references/`.
- When external sources were consulted, add `SOURCES.md` documenting URLs, review date, what each source was used for, and which files received extracted content (follow the pattern in `skills/slang-dev/SOURCES.md`).
- Optionally add `wrappers/{cursor,claude,github}/SKILL.md` under the bootstrap skill if bases include them or the skill needs custom tool-skill notes — bootstrap only, not installed.

Apply any extra requirements from `--notes`.

### Phase 5 — Write output (bootstrap only)

Create or update **only** under `skills/<name>/`:

```text
skills/<name>/
├── SKILL.md
├── references/          # optional
├── scripts/             # optional
├── assets/              # optional
├── eval-queries.json    # optional
├── SOURCES.md           # when external verification was used
└── wrappers/            # optional bootstrap-only tool skill templates
    ├── cursor/SKILL.md
    ├── claude/SKILL.md
    └── github/SKILL.md
```

### Phase 6 — Validate and report

1. Run validation from the repository root:

```bash
python skills/skill-creator/scripts/quick_validate.py skills/<name>
```

2. If validation fails, fix issues and re-run until it passes or report what could not be fixed.

3. Report to the user:
   - Files created or updated under `skills/<name>/`
   - Merge decisions (when multiple bases were used)
   - External sources consulted
   - Validation result

4. Tell the user the next step when they are satisfied with the bootstrap skill:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name <name> \
  --source skills/<name> \
  --overwrite
```

Do **not** run the install command in this workflow.

## On failure

- Missing skill name or base path: ask the user; do not guess.
- Base path not found: list the missing paths and stop.
- Unresolved conflicts between bases: state the conflict, cite sources, ask the user which direction to take.
- Validation errors: show `quick_validate.py` output and fix what you can before reporting.

## Do not

- Write to `.shared/skills/`, `.cursor/skills/`, `.claude/skills/`, or `.github/skills/`.
- Run `install_portable_skill.py` or `create_skill.py` — those produce shared and tool skills.
- Modify template/base paths — they are read-only inputs.
- Overwrite an existing `skills/<name>/` without user consent (unless `--overwrite` was provided).

## After success

The bootstrap skill is ready for review. When the user approves, they can install it to generate the shared skill and tool skills, then reload their tools. Installation is a separate step — not part of this command.
