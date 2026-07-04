# Portable Skill Layout

Use this guide when creating or reviewing skills that should work across GitHub Copilot, Cursor, and Claude Code.

## Directory structure

```text
repo/
  .shared/
    skills/
      code-review-plus/
        SKILL.md
        scripts/
        references/
        assets/
  .claude/
    skills/
      code-review-plus/
        SKILL.md
  .cursor/
    skills/
      code-review-plus/
        SKILL.md
  .github/
    skills/
      code-review-plus/
        SKILL.md
```

`.shared/skills/<name>/` is the canonical source of truth. The three tool-specific folders contain wrappers that point back to the shared skill and add local integration notes. Bundled resources (`scripts/`, `references/`, `assets/`) live only in the shared skill directory.

## Shared skill template

```markdown
---
name: code-review-plus
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
name: code-review-plus
description: Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request.
---

# code-review-plus wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/code-review-plus/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/code-review-plus/` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/code-review-plus/`.
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

## Worked example

Scaffold a portable skill in a repository:

```bash
python skills/skill-creator/scripts/create_skill.py \
  --root /path/to/repo \
  --name code-review-plus \
  --overwrite
```

This creates:

- `.shared/skills/code-review-plus/` with `SKILL.md`, `scripts/`, `references/`, and `assets/`
- `.cursor/skills/code-review-plus/SKILL.md`
- `.claude/skills/code-review-plus/SKILL.md`
- `.github/skills/code-review-plus/SKILL.md`

Validate:

```bash
python skills/skill-creator/scripts/quick_validate.py .shared/skills/code-review-plus
python skills/skill-creator/scripts/quick_validate.py .cursor/skills/code-review-plus
```

Package the shared skill for distribution:

```bash
python skills/skill-creator/scripts/package_skill.py .shared/skills/code-review-plus
```

## Notes on portability

- Reference-based wrappers reduce duplication but depend on the tool following the wrapper instruction to read the shared skill.
- If the user needs maximum standalone behavior, use `init_skill.py --path <tool-skills-dir>` to create a full copy in one location instead of wrappers.
- Repo-root `skills/` can hold meta/bootstrap packages (for example `skill-creator` itself). User-created portable skills belong in `.shared/skills/`.
- Add tool-specific frontmatter such as `disable-model-invocation` only in wrappers when the user explicitly wants per-tool variants.
