# Portable Skill Layout

Use this guide when creating or reviewing skills that should work across GitHub Copilot and Claude Code.

## Two-phase workflow

Portable skills use **two phases**:

1. **Bootstrap** — Author tool-neutral content under `skills/<name>/`. This is the source of truth when bootstrap exists.
2. **Install** — Run `install_portable_skill.py` to copy the bootstrap package to `.agents/skills/<name>/` and create the Claude Code bridge symlink (`.claude/skills -> ../.agents/skills`).

Do not hand-edit `.agents/skills/` for bootstrapped skills — edit bootstrap and reinstall.

For one-off skills without bootstrap source, use `create_skill.py` to scaffold directly into the installed layout (direct path).

## Single-root install

One real copy of each skill lives at `.agents/skills/<name>/`. Claude Code discovers skills through the `.claude/skills` bridge symlink (auto-created on install); GitHub Copilot reads `.agents/skills/` directly. There are no per-tool wrapper copies and no category subfolders — a skill directory must be a direct child of a skills root (the validator rejects `skills/<category>/<name>/`).

Tool-specific guidance lives in `## Tool notes` sections of the `SKILL.md` body, not in separate files:

```markdown
## Tool notes

### Claude Code

- Restart or reload the session after install so the skill is rediscovered.
```

## Directory structure

**Installed layout (single root):**

```text
repo/
  .agents/
    skills/
      code-reviewer/
        SKILL.md
        scripts/
        references/
        assets/
  .claude/
    skills -> ../.agents/skills
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
```

`.agents/skills/<name>/` is the install output — a verbatim copy of the bootstrap package. Bundled resources (`scripts/`, `references/`, `assets/`) live in the skill directory after install (copied from bootstrap).

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

Keep the body tool-neutral above `## Tool notes`. Use `<SKILL_ROOT>` for bundled script and reference paths inside the skill.

## Tool-specific paths

| Tool | Read path |
| --- | --- |
| Claude Code | `.claude/skills/<name>/SKILL.md` via the bridge symlink to `.agents/skills/` |
| GitHub Copilot | `.agents/skills/<name>/SKILL.md` |

## Worked example: bootstrap and install

Create bootstrap source:

```text
skills/code-reviewer/
  SKILL.md
  references/review-checklist.md
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

This copies the bootstrap package to `.agents/skills/code-reviewer/` and creates the `.claude/skills -> ../.agents/skills` bridge symlink when it does not yet exist. If `.claude/skills` is a real directory (legacy install), the installer refuses and asks you to purge the legacy tree first.

Validate the installed skill:

```bash
python skills/skill-creator/scripts/quick_validate.py .agents/skills/code-reviewer
```

## Worked example: direct scaffold

When bootstrap is not used:

```bash
python skills/skill-creator/scripts/create_skill.py \
  --root /path/to/repo \
  --name code-reviewer \
  --overwrite
```

This scaffolds `.agents/skills/code-reviewer/` with placeholders. Edit its `SKILL.md` directly; put tool-specific mechanics in a `## Tool notes` section.

## Packaging

Validate, then package the installed skill:

```bash
python skills/skill-creator/scripts/quick_validate.py .agents/skills/code-reviewer
python skills/skill-creator/scripts/package_skill.py .agents/skills/code-reviewer
```

## Notes on portability

- If the user needs a standalone copy outside the single-root layout, use `init_skill.py <skill-name> --path <skills-root>` to create a full copy in one location.
- Tool-specific frontmatter such as `disable-model-invocation` marks a **command-skill** (slash-invoked only); see command-creator for that flow.

## Quality checklist

Before finishing, confirm the skill meets the three bars from the shared skill:

| Bar | Question |
| --- | --- |
| Correctness | Is the scope accurate? Are capabilities realistic? Are success criteria verifiable? |
| Completeness | Are edge cases, output format, and boundaries documented? Are long sections in `references/`? |
| Efficiency | Is the body lean? Are tool-native shortcuts in `## Tool notes`, not duplicated in the tool-neutral body? |
