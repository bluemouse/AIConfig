# Portable Skill Layout

Use this guide when creating or reviewing skills that should work across GitHub Copilot, Cursor, and Claude Code.

## Two-phase workflow

Portable skills use **two phases**:

1. **Bootstrap** — Author tool-neutral content under `skills/<name>/` (plus optional custom wrappers). This is the source of truth when bootstrap exists.
2. **Install** — Run `install_portable_skill.py` to copy the bootstrap package to `.shared/skills/<name>/` and generate tool skills under `.cursor/`, `.claude/`, and `.github/`.

Do not hand-edit `.shared/skills/` or tool skill folders for bootstrapped skills — edit bootstrap and reinstall.

For one-off skills without bootstrap source, use `create_skill.py` to scaffold directly into the installed layout (direct path).

## Skills vs agents (install differences)

| | Skills | Agents |
| --- | --- | --- |
| Tool wrappers on install | Always creates all three paths; missing custom wrappers get default templates | Installs only wrappers present under `wrappers/` |
| Partial custom wrappers | Custom per tool; defaults fill gaps | Omitted tools are not installed |
| Shrinking wrapper set | Re-install overwrites all three tool skills | Re-install with `--overwrite` removes stale tool wrappers |

## Directory structure

**Installed layout:**

```text
repo/
  .shared/
    skills/
      code-reviewer/
        SKILL.md
        scripts/
        references/
        assets/
  .claude/
    skills/
      code-reviewer/
        SKILL.md
  .cursor/
    skills/
      code-reviewer/
        SKILL.md
  .github/
    skills/
      code-reviewer/
        SKILL.md
```

**Bootstrap layout** (when the skill ships bootstrap source):

```text
repo/
  skills/
    code-reviewer/
      SKILL.md
      scripts/
      references/
      assets/
      wrappers/
        cursor/
          SKILL.md
        claude/
          SKILL.md
        github/
          SKILL.md
```

`.shared/skills/<name>/` is the tool-neutral install output. The three tool-specific folders contain wrappers that point back to the shared skill and add local integration notes. Bundled resources (`scripts/`, `references/`, `assets/`) live in the shared skill directory after install (copied from bootstrap). The bootstrap `wrappers/` tree is install-only and is not copied into `.shared/skills/`.

## Shared skill template

```markdown
---
name: code-reviewer
description: Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request.
---

# Code Review Plus

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`.

You are a senior code reviewer.

Review the relevant code changes and focus on:

1. Correctness bugs
2. API misuse
3. Resource leaks
4. Race conditions
5. Security issues
6. Missing tests or edge cases
7. Maintainability problems

When reporting findings:

- Group issues by severity: critical, high, medium, low.
- Cite the relevant file, function, or code region when possible.
- Explain why each issue matters.
- Suggest a concrete fix.

If no significant issues are found, say so and list any minor observations separately.
```

Keep shared `SKILL.md` tool-neutral. Use `<SKILL_ROOT>` for bundled script and reference paths inside the shared skill.

## Wrapper template

Use the same `name` and `description` frontmatter in each wrapper unless the user asks for tool-specific frontmatter.

```markdown
---
name: code-reviewer
description: Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request.
---

# code-reviewer wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/code-reviewer/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/code-reviewer/` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/code-reviewer/`.
- Keep only Cursor-specific information in this wrapper.
```

## Tool-specific paths

| Tool | Wrapper path |
| --- | --- |
| Claude Code | `.claude/skills/<name>/SKILL.md` |
| Cursor | `.cursor/skills/<name>/SKILL.md` |
| GitHub Copilot | `.github/skills/<name>/SKILL.md` |

Relative path from any wrapper to the shared skill:

`../../../.shared/skills/<name>/SKILL.md`

Relative path from any wrapper to the shared skill root:

`../../../.shared/skills/<name>/`

## Worked example: bootstrap and install

Create bootstrap source:

```text
skills/code-reviewer/
  SKILL.md
  references/review-checklist.md
  wrappers/cursor/SKILL.md   # optional custom wrapper
```

Validate and install:

```bash
python skills/skill-creator/scripts/quick_validate.py skills/code-reviewer

python skills/skill-creator/scripts/install_portable_skill.py \
  --root /path/to/repo \
  --name code-reviewer \
  --source skills/code-reviewer \
  --overwrite
```

This copies the bootstrap package to `.shared/skills/code-reviewer/` (excluding `wrappers/`) and generates tool skills — using custom wrappers from `wrappers/` when present, otherwise default templates.

Validate installed paths:

```bash
python skills/skill-creator/scripts/quick_validate.py .shared/skills/code-reviewer
python skills/skill-creator/scripts/quick_validate.py .cursor/skills/code-reviewer
```

## Worked example: direct scaffold

When bootstrap is not used:

```bash
python skills/skill-creator/scripts/create_skill.py \
  --root /path/to/repo \
  --name code-reviewer \
  --overwrite
```

This creates `.shared/skills/code-reviewer/` with placeholders and default tool wrappers. Edit `.shared/skills/code-reviewer/SKILL.md` for cross-tool behavior; edit tool skill files for tool-only notes.

## Packaging

Validate, then package the **shared** skill only (wrappers stay project-local):

```bash
python skills/skill-creator/scripts/quick_validate.py .shared/skills/code-reviewer
python skills/skill-creator/scripts/package_skill.py .shared/skills/code-reviewer
```

## Notes on portability

- Reference-based wrappers reduce duplication but depend on the tool following the wrapper instruction to read the shared skill.
- If the user needs maximum standalone behavior, use `init_skill.py --path <tool-skills-dir>` to create a full copy in one location instead of wrappers.
- Repo-root `skills-ref/` can hold reference templates. Bootstrapped portable skills belong in `skills/<name>/`.
- Add tool-specific frontmatter such as `disable-model-invocation` only in wrappers when the user explicitly wants per-tool variants.

## Quality checklist

Before finishing, confirm the skill meets the three bars from the shared skill:

| Bar | Question |
| --- | --- |
| Correctness | Is the scope accurate? Are capabilities realistic? Are success criteria verifiable? |
| Completeness | Are edge cases, output format, and boundaries documented? Are long sections in `references/`? |
| Efficiency | Is the shared file lean? Are tool-native shortcuts in wrappers, not duplicated in shared? |
