---
name: code-review-plus
description: "Review git diffs and commits \u2014 staged changes, unstaged changes, the full working tree, the last commit, a specific commit, or a commit range \u2014 and return a structured, findings-first report with proposed fixes. Use whenever the user asks to review code, review a diff, review staged/unstaged/working-tree changes, review a commit or commit range, do a code review, or asks for a security/performance/design/test review of recent changes \u2014 even if they don't say \"code review\" explicitly (e.g. \"check this diff\", \"look over my changes\", \"any issues in this commit\", \"is this ready to merge\", \"review my branch against main\"). Supports six selectable review scopes (design, correctness, maintainability, security, performance, tests), three effort levels (basic, standard, deep), and an interactive mode that asks up front what to review, in what scope, and how deep before starting \u2014 say \"review interactively\" or \"guided review\" to trigger it."
---

# code-review-plus (Claude Code)

Read the shared skill first — it is the source of truth for review workflow, scopes, effort
tiers, and output format:

`../../../.shared/skills/code-review-plus/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/code-review-plus/`. Resolve paths to
`references/`, `scripts/`, and `assets/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh code-review-plus

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name code-review-plus --source skills/code-review-plus --overwrite
```

If bootstrap source exists at `skills/code-review-plus/`, use that path for `--source`
only.

## Deep effort in Claude Code: subagent dispatch

At `deep` effort, use the shared **Deep Effort: Parallel Scope Passes** procedure with
Claude Code **subagents**:

1. Run Scope & Intent Alignment yourself (inline) before dispatching.
2. In a **single turn**, spawn one subagent per *selected* scope, all in parallel when
   possible.
3. Each subagent prompt must include the full resolved diff (or exact git commands to
   reproduce it), the intent summary, and checklist bullets copied verbatim from
   `<SKILL_ROOT>/references/scope-checklists.md` (plus matching Conditional Extensions).
4. Instruct each subagent to read surrounding code with its available tools before
   flagging anything, and to return up to 6 candidates in the shared markdown format.
5. Collect all subagent replies, then run cross-scope dedup, verify pass, and gap sweep
   yourself per the shared skill.

When subagent completion notifications include `total_tokens` and `duration_ms`, note
them if comparing efficiency across review runs.

## Claude.ai (no Claude Code CLI)

If you are on Claude.ai rather than Claude Code: no parallel subagents. At `deep` effort,
run scope passes sequentially yourself, keeping notes separate per scope, then dedup,
verify, and gap-sweep per the shared skill.

## Posting to GitHub

This skill produces the in-chat review report. When the user asks to post findings as PR
review comments on a **GitHub** repo, finish the review first, then follow the shared
skill's **Posting to GitHub** section and hand off to
[github-guide](../../../.shared/skills/github-guide/SKILL.md) (or the installed
`.claude/skills/github-guide/SKILL.md` wrapper).

## Wrapper policy

- Edit cross-tool review behavior in `../../../.shared/skills/code-review-plus/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
