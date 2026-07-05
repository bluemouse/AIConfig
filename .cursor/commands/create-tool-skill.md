# Create tool skill

Install one or more **bootstrap skills** from `skills/<name>/` into the portable layout: shared skill (`.shared/skills/<name>/`) plus tool skills for Cursor, Claude Code, and GitHub Copilot. This is the install step after authoring with `/create-bootstrap-skill`.

## Input format

Parse the user's message after `/create-tool-skill`. Support structured flags (preferred) and natural language (fallback).

**Structured form:**

```text
/create-tool-skill \
  --source <bootstrap-path> [--source <bootstrap-path> ...] \
  [--no-overwrite]
```

| Argument | Required | Meaning |
| --- | --- | --- |
| `--source` | yes (≥1) | Bootstrap skill: `skills/<name>/` directory or `skills/<name>/SKILL.md` file |
| `--no-overwrite` | no | Refuse to overwrite existing shared or tool install targets (default: overwrite) |

**Natural language fallback:** extract bootstrap paths from `@`-attached files or prose (e.g. "Create the tool skills from @skills/slang-dev/SKILL.md"). Confirm parsed values with the user before installing.

**Examples:**

```text
/create-tool-skill --source skills/slang-dev
```

```text
/create-tool-skill \
  --source skills/gpu-rendering-guide \
  --source skills/vulkan-dev \
  --source skills/slang-dev
```

```text
/create-tool-skill \
  --source skills/cpp-coding \
  --source skills/cpp-memory-guide \
  --source skills/cpp-testing
```

Use multiple `--source` flags when installing a cluster of cross-linked companion skills in one batch.

## What to do

### Phase 1 — Parse and confirm

1. Confirm the workspace root is the repository root (where `.cursor/`, `.shared/`, and `skills/` live).
2. Require at least one `--source` path. Resolve `@`-attached paths and workspace-relative paths.
3. If inputs are missing or ambiguous, ask before running install.
4. Confirm `skills/skill-creator/scripts/install_portable_skill.py` exists (requires skill-creator bootstrap or installed copy).

### Phase 2 — Resolve each bootstrap skill

For each `--source` path:

- **Directory** (`skills/slang-dev/`): use as bootstrap root; read `name` from `SKILL.md` frontmatter.
- **File** (`skills/slang-dev/SKILL.md`): use the parent directory as bootstrap root; derive skill name from frontmatter `name`.

Expected layout: bootstrap skills under `skills/<name>/`. If `--source` points elsewhere, still install with that path but warn the user it is outside the usual bootstrap location.

Deduplicate: if the same skill is listed twice (directory and file), install once.

### Phase 3 — Pre-validate bootstrap skills

Before install, validate each bootstrap skill from the repository root:

```bash
python skills/skill-creator/scripts/quick_validate.py skills/<name>
```

If validation fails, do **not** install. Tell the user to fix the bootstrap skill or run `/create-bootstrap-skill` first.

### Phase 4 — Install shared + tool skills

Run `install_portable_skill.py` once per skill, in the order the user listed `--source` flags (or the order parsed from the message):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name <name> \
  --source skills/<name> \
  --overwrite
```

Use `--no-overwrite` instead of `--overwrite` when the user passed `--no-overwrite`.

**Multiple skills / dependencies:** install every listed bootstrap skill in the batch. Cross-linked clusters (GPU stack, C++ cluster, etc.) can be installed in any order — sibling links (`../<sibling>/SKILL.md`) resolve after all targets exist under `.shared/skills/`.

For each skill, the script:

1. Copies bootstrap → `.shared/skills/<name>/` (excluding `wrappers/`)
2. Writes tool skills to `.cursor/skills/<name>/`, `.claude/skills/<name>/`, and `.github/skills/<name>/` (custom wrappers from `skills/<name>/wrappers/` when present)
3. Validates all four paths with `quick_validate.py`

Do **not** manually create wrapper files — use the script only.

If one skill in a multi-skill batch fails, report which succeeded and which failed; stop unless the user asks to continue with the remaining skills.

### Phase 5 — Report

For each successfully installed skill, report:

- **Bootstrap source (unchanged):** `skills/<name>/`
- **Shared skill:** `.shared/skills/<name>/`
- **Tool skills:** `.cursor/skills/<name>/`, `.claude/skills/<name>/`, `.github/skills/<name>/`

Tell the user to reload tools **once** after the full batch:

- **Cursor:** reload the window
- **VS Code + Copilot:** reload the window
- **Claude Code:** restart or reload the session

## On failure

- Bootstrap path not found: list missing paths; do not install a partial batch unless the user confirms.
- Script exit non-zero: print stdout/stderr; do not claim success for failed skills.
- Name/frontmatter mismatch: report the script error (e.g. skill name does not match frontmatter `name`).
- Validation errors: show `quick_validate.py` output before or after install as appropriate.

## Do not

- Edit bootstrap source during install — the script copies it; bootstrap remains the reinstall source.
- Run `create_skill.py` (scaffolds empty skills) or the `/create-bootstrap-skill` workflow (authoring, not install).
- Write skill content by hand into `.shared/` or tool skill folders.

## After success

Future edits to a bootstrap skill require re-running `/create-tool-skill` (or `install_portable_skill.py`) to refresh the shared skill and tool skills.
