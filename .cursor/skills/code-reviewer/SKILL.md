---
name: code-reviewer
description: "Review git diffs and commits \u2014 staged changes, unstaged changes, branch changes (pre-push vs default branch), the full working tree, the last commit, a specific commit, or a commit range \u2014 and return a structured, findings-first report with proposed fixes. Use whenever the user asks to review code, review a diff, review staged/unstaged/working-tree/branch changes, review a commit or commit range, do a code review, or asks for a security/performance/design/test review of recent changes \u2014 even if they don't say \"code review\" explicitly (e.g. \"check this diff\", \"look over my changes\", \"any issues before I push\", \"is this ready to merge\", \"review my branch against main\"). Supports six selectable review scopes (design, correctness, maintainability, security, performance, tests), three effort levels (basic, standard, deep), and an interactive mode that asks up front what to review, in what scope, and how deep before starting \u2014 say \"review interactively\" or \"guided review\" to trigger it."
---

# code-reviewer (Cursor)

Read the shared skill first — it is the source of truth for review workflow, scopes, effort
tiers, and output format:

`../../../.shared/skills/code-reviewer/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/code-reviewer/`. Resolve paths to
`references/`, `scripts/`, and `assets/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for review
content and output structure.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under
  `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the
  agent rediscovers them

## Install or refresh code-reviewer

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name code-reviewer --source skills/code-reviewer --overwrite
```

If bootstrap source exists at `skills/code-reviewer/`, use that path for `--source`
only.

## Deep effort in Cursor: Task tool dispatch

At `deep` effort, use the shared **Deep Effort: Parallel Scope Passes** procedure with
Cursor's **Task tool**:

1. Run Scope & Intent Alignment yourself (inline) before dispatching.
2. In a **single message**, issue one Task call per *selected* scope, all in parallel
   (multiple tool calls in one turn, not sequential calls).
3. Use `subagent_type: "generalPurpose"` — it has Read/Grep/Shell access to inspect
   surrounding code.
4. Paste the shared scope-pass prompt template with real diff content and the checklist
   bullets copied verbatim from `<SKILL_ROOT>/references/scope-checklists.md`.
5. Collect each subagent's **final text reply** (you do not receive its tool calls).
6. Run cross-scope dedup, verify pass, and gap sweep yourself per the shared skill.

### Task prompt additions (Cursor)

Append to each scope pass prompt:

```
Use Read/Grep/Shell as needed to inspect call sites, related tests, and existing patterns
before flagging anything.

If a ReportFindings tool is available in your environment, you may call it once at the end
with raw candidates (file, line, summary, failure_scenario, category: "<scope>") — but
your final reply text must still restate each candidate with Severity, Location, What's
wrong, Why it matters, and Proposed fix, because the orchestrator only receives your final
text message.
```

## Posting to GitHub

This skill produces the in-chat review report. When the user asks to post findings as PR
review comments on a **GitHub** repo, finish the review first, then follow the shared
skill's **Posting to GitHub** section and hand off to
[github-guide](../../../.shared/skills/github-guide/SKILL.md) (or the installed
`.cursor/skills/github-guide/SKILL.md` wrapper).

On Cursor, you may also suggest the built-in `/code-review --comment` for a quick native
post — but prefer `github-guide` when the user needs `REQUEST_CHANGES`, multi-comment
batching, or thread resolution via `gh api`.

## Wrapper policy

- Edit cross-tool review behavior in `../../../.shared/skills/code-reviewer/`
- Edit Cursor-only mechanics here
- Do not duplicate the full shared skill body in this file
