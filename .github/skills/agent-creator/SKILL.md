---
name: agent-creator
description: Create portable custom agents for GitHub Copilot, Cursor, and Claude
  Code using a shared-first layout, and iteratively improve them. Use when users want
  to create an agent from scratch, bootstrap under the agents directory and install
  to .shared/agents with tool wrappers, edit or optimize an existing agent, tune an
  agent's description for better triggering, or explain portable agent structure —
  even if they do not say "portable agent" explicitly.
---

# agent-creator (GitHub Copilot)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, validation, and the agent quality bars (correctness, completeness, efficiency):

`../../../.shared/skills/agent-creator/SKILL.md`

Resolve `<AGENT_CREATOR_ROOT>` as `../../../.shared/skills/agent-creator`. Resolve paths to `scripts/` and `references/` from that directory.

This wrapper adds **GitHub Copilot / VS Code-native** execution. Copilot Chat does not expose parallel subagents — adapt the test loop accordingly.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Reload VS Code** after installing or editing skills and agents so Copilot rediscovers them
- Custom agents you create live under `.github/agents/<name>.agent.md` (wrappers pointing to `.shared/agents/`)

## Install or refresh agent-creator

From repo root (or ask the user to run in a terminal):

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name agent-creator --source skills/agent-creator --overwrite
```

If bootstrap source exists at `skills/agent-creator/`, use that path for `--source` only.

## Scaffolding and validation

Run in the integrated terminal.

**Bootstrap path (preferred):** author under `agents/<agent-name>/`, then install:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>

python <AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py \
  --root . \
  --name <agent-name> \
  --source agents/<agent-name> \
  --overwrite
```

**Direct path:** when bootstrap is not used:

```bash
python <AGENT_CREATOR_ROOT>/scripts/create_agent.py \
  --root . \
  --name <agent-name> \
  --description "<description>" \
  --instructions-file <instructions.md> \
  --overwrite

python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root . --name <agent-name>
```

**Always** run `quick_validate.py` after scaffold, install, or substantive edits. Reload VS Code after creating new Copilot agents.

Use `--github-note` at direct scaffold time; expand `agents/<agent-name>/wrappers/github/AGENT.md` (bootstrap) or `.github/agents/<agent-name>.agent.md` (direct) with Copilot-specific frontmatter when needed.

## Testing agents in Copilot

Use a **qualitative, sequential** loop in Copilot Chat or the Copilot agent picker.

### Recommended flow

1. Draft 2–3 test prompts with the user.
2. Ensure the agent is installed (shared + `.github/agents/<name>.agent.md`).
3. Invoke the custom agent from the Copilot agent picker or by phrasing the prompt to match the agent `description`.
4. Present each prompt + output to the user; review against correctness, completeness, and efficiency.
5. Edit bootstrap files (`agents/<agent-name>/`) for cross-tool fixes, or `.shared/agents/<agent-name>.md` on the direct path; then the GitHub wrapper for Copilot-only details. Reinstall after bootstrap edits.
6. Re-validate in terminal; reload VS Code; re-test in chat.

Skip parallel baselines — Copilot has no subagent API for informal A/B in chat.

## Description optimization

Manual path only:

1. Shared Step 1 — draft trigger eval queries with the user
2. Shared Step 2 — review should-trigger / should-not-trigger in chat
3. Skip automated Step 3
4. Shared Step 4 — revise `description` in the authoritative edit location (`agents/<agent-name>/AGENT.md` or `.shared/agents/<agent-name>.md`); sync all installed wrappers; reinstall if bootstrap; reload VS Code

Write descriptions that state both **what** the agent does and **when** Copilot should use it.

## Wrapper policy

- Edit cross-tool behavior in `../../../.shared/skills/agent-creator/` and user bootstrap (`agents/<name>/`) or `.shared/agents/` on the direct path
- Edit Copilot-specific mechanics here and in user `.github/agents/` wrappers
