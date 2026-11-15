# Portable Agent Layout

Use this guide when creating or reviewing agents that should work across GitHub Copilot, Cursor, and Claude Code.

## Two-phase workflow

Portable agents use **two phases**:

1. **Bootstrap** — Author tool-neutral content under `agents/<name>/`. This is the source of truth when bootstrap exists.
2. **Install** — Run `install_portable_agent.py` to write two real copies: `.claude/agents/<name>.md` (AGENT.md verbatim, which Cursor compat-reads) and `.github/agents/<name>.agent.md` (a Copilot transform).

Do not hand-edit installed agent files for bootstrapped agents — edit bootstrap and reinstall.

For one-off agents without bootstrap source, use `create_agent.py` to scaffold directly into the installed layout (direct path).

## Dual-target install

There is no shared wrapper layer. Each agent installs as two real files:

- **Claude Code** — `.claude/agents/<name>.md`, verbatim from `AGENT.md` (frontmatter + body). Cursor compat-reads this file.
- **GitHub Copilot** — `.github/agents/<name>.agent.md`, a transform keeping only `name` and `description` frontmatter plus the body.

Tool-specific guidance lives in `## Tool notes` sections of the agent body, not in separate files:

```markdown
## Tool notes

### Claude Code

- Restart or reload the session after install so the agent is rediscovered.

### GitHub Copilot

- Reload the window after adding or editing this agent.
```

## Directory structure

**Installed layout (dual target):**

```text
repo/
  .claude/
    agents/
      code-reviewer.md
  .github/
    agents/
      code-reviewer.agent.md
```

**Bootstrap layout** (when the agent ships bootstrap source):

```text
repo/
  agents/
    code-reviewer/
      AGENT.md
```

`.claude/agents/<name>.md` and `.github/agents/<name>.agent.md` are the install outputs. When bootstrap source exists at `agents/<name>/`, edit there and reinstall — do not hand-edit installed files.

## Agent template

```markdown
---
name: code-reviewer
description: Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request.
---

You are a senior code reviewer.

When invoked:

1. Read the relevant changes and surrounding context.
2. Evaluate against the criteria below.
3. Report findings in the output format specified.

Review focus:

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
- Do not rewrite large files unless explicitly asked.
- Do not comment on style-only preferences unless they affect readability or maintainability.

If no significant issues are found, say so and list any minor observations separately.
```

Keep the agent body tool-neutral above `## Tool notes`. Do not embed reload steps, subagent spawn commands, or vendor-specific frontmatter in the tool-neutral body.

## Tool-specific paths

| Tool | Install path |
| --- | --- |
| Claude Code (and Cursor compat-read) | `.claude/agents/<name>.md` |
| GitHub Copilot | `.github/agents/<name>.agent.md` |

## Worked example: bootstrap and install

Create bootstrap source:

```text
agents/code-reviewer/
  AGENT.md
```

Validate and install:

```bash
python skills/agent-creator/scripts/quick_validate.py --bootstrap-source agents/code-reviewer

python skills/agent-creator/scripts/install_portable_agent.py \
  --root /path/to/repo \
  --name code-reviewer \
  --source agents/code-reviewer \
  --overwrite
```

Do not skip bootstrap validation before install.

This writes `AGENT.md` verbatim to `.claude/agents/code-reviewer.md` and the Copilot transform to `.github/agents/code-reviewer.agent.md`. With `--overwrite`, stale legacy outputs from older installs (a shared-layer file or a `.cursor/agents/` copy) are removed.

Validate the installed set:

```bash
python skills/agent-creator/scripts/quick_validate.py --root /path/to/repo --name code-reviewer
```

Then edit bootstrap files for cross-tool behavior and expand `## Tool notes` subsections with tool-native spawn mechanics, reload steps, and per-tool frontmatter notes. Re-run validation after substantive edits.

## Worked example: direct scaffold

When bootstrap is not used:

```bash
python skills/agent-creator/scripts/create_agent.py \
  --root /path/to/repo \
  --name code-reviewer \
  --description "Reviews code changes for correctness, safety, maintainability, and test coverage. Use after implementation or before opening a pull request." \
  --instructions-file /tmp/code-reviewer-body.md \
  --overwrite
```

This writes `.claude/agents/code-reviewer.md` and `.github/agents/code-reviewer.agent.md` with identical content. Edit the Claude copy for Claude behavior and the GitHub copy for Copilot behavior; put shared guidance in the tool-neutral body.

Validate:

```bash
python skills/agent-creator/scripts/quick_validate.py --root /path/to/repo --name code-reviewer
```

## Notes on portability

- The two installed copies are real files; edits made in one do not propagate to the other. Prefer bootstrap + reinstall as the single edit point.
- Bootstrapped portable agents belong in `agents/<name>/`.
- Tool-specific frontmatter such as `model`, `tools`, or `readonly` is not portable; keep it as prose in `## Tool notes` when the user wants per-tool variants.

## Quality checklist

Before finishing, confirm the agent meets the three bars from the shared skill:

| Bar | Question |
| --- | --- |
| Correctness | Is the role accurate? Are capabilities realistic? Are success criteria verifiable? |
| Completeness | Are edge cases, output format, and boundaries documented? |
| Efficiency | Is the tool-neutral body lean? Are tool-native shortcuts in `## Tool notes`, not duplicated in the body? |
