---
name: agent-creator
description: "Create portable custom agents for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create an agent from scratch, scaffold `.shared/agents` with tool wrappers in `.cursor/agents`, `.claude/agents`, or `.github/agents`, edit or optimize an existing agent, tune an agent's description for better triggering, or explain portable agent structure \u2014 even if they do not say \"portable agent\" explicitly."
---

# agent-creator (Claude Code)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, validation, and the agent quality bars (correctness, completeness, efficiency):

`../../../.shared/skills/agent-creator/SKILL.md`

Resolve `<AGENT_CREATOR_ROOT>` as `../../../.shared/skills/agent-creator`. Resolve paths to `scripts/` and `references/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills
- Custom agents you create live under `.claude/agents/<name>.md` (wrappers pointing to `.shared/agents/`)

## Install or refresh agent-creator

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name agent-creator --source skills/agent-creator --overwrite
```

If bootstrap source exists at `skills/agent-creator/`, use that path for `--source` only.

## Scaffolding and validation

```bash
python <AGENT_CREATOR_ROOT>/scripts/create_agent.py \
  --root . \
  --name <agent-name> \
  --description "<description>" \
  --instructions-file <instructions.md> \
  --overwrite

python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root . --name <agent-name>
```

**Always** run `quick_validate.py` after scaffold or substantive edits.

Use `--claude-note` at scaffold time; expand `.claude/agents/<agent-name>.md` with Claude-specific frontmatter (`tools`, `model`, etc.) when the user wants per-tool variants.

## Testing agents in Claude Code

Claude Code supports **subagents** — use them to test custom agents qualitatively.

### Recommended flow

1. Draft 2–3 test prompts with the user.
2. For each prompt, spawn a subagent in the same turn when comparing variants, or sequentially for simple review.
3. Subagent prompt should reference `.claude/agents/<agent-name>.md` and instruct reading `.shared/agents/<agent-name>.md` first.
4. Review against correctness, completeness, and efficiency (shared skill).
5. Edit shared agent first; then `.claude/agents/` wrapper for Claude-only details.
6. Re-validate and re-test.

### Spawn example

```
Execute as the custom agent in .claude/agents/<agent-name>.md.
Read .shared/agents/<agent-name>.md first — it is the source of truth.

Task: <user test prompt>
```

When subagent completion notifications include `total_tokens` and `duration_ms`, note them for efficiency comparisons.

## Description optimization

No automated loop is bundled for agents. Use shared Steps 1–2 and 4 manually:

1. Draft trigger eval queries with the user
2. Mark false positives / false negatives
3. Skip automated Step 3 (no `run_loop.py` for agents)
4. Apply revised `description` to `.shared/agents/<agent-name>.md` and sync all wrappers

Triggering note: custom agents appear in available agent lists; Claude selects them when the description matches and specialized behavior would help.

## Claude.ai (no Claude Code CLI)

If you are on Claude.ai rather than Claude Code: no subagents. Run test prompts sequentially yourself, present outputs inline, and use manual description optimization only.

## Updating in read-only environments

Copy to `/tmp/agent-creator/`, edit, validate, then copy artifacts back if needed.

## Wrapper policy

- Edit cross-tool behavior in `../../../.shared/skills/agent-creator/` and user `.shared/agents/`
- Edit Claude Code mechanics here and in user `.claude/agents/` wrappers
