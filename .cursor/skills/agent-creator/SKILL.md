---
name: agent-creator
description: Create portable custom agents for GitHub Copilot, Cursor, and Claude
  Code using a shared-first layout, and iteratively improve them. Use when users want
  to create an agent from scratch, bootstrap under the agents directory and install
  to .shared/agents with tool wrappers, edit or optimize an existing agent, tune an
  agent's description for better triggering, or explain portable agent structure —
  even if they do not say "portable agent" explicitly.
---

# agent-creator (Cursor)

Read the shared skill first — it is the source of truth for portable layout, authoring rules, validation, and the agent quality bars (correctness, completeness, efficiency):

`../../../.shared/skills/agent-creator/SKILL.md`

Resolve `<AGENT_CREATOR_ROOT>` as `../../../.shared/skills/agent-creator`. Resolve paths to `scripts/` and `references/` from that directory.

This wrapper adds **Cursor-native** execution. When this wrapper and the shared skill disagree on mechanics, follow this wrapper for Cursor; follow the shared skill for content structure and portable conventions.

## Discovery and reload

- Project skills: `.cursor/skills/<name>/SKILL.md` (this file) + shared package under `.shared/skills/<name>/`
- Reload the **Cursor window** after adding, editing, or re-installing skills so the agent rediscovers them
- Custom agents you create live under `.cursor/agents/<name>.md` (wrappers pointing to `.shared/agents/`)

## Install or refresh agent-creator

From repo root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name agent-creator --source skills/agent-creator --overwrite
```

If bootstrap source exists at `skills/agent-creator/`, use that path for `--source` only.

## Scaffolding and validation

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

**Always** run `quick_validate.py` after scaffold, install, or substantive edits. Fix errors before handing off to the user.

Use `--cursor-note` at direct scaffold time for one-line Cursor hints; expand `agents/<agent-name>/wrappers/cursor/AGENT.md` (bootstrap) or `.cursor/agents/<agent-name>.md` (direct) afterward with spawn mechanics and optional frontmatter (`model`, `readonly`, etc.).

## Testing agents in Cursor

Use the **Task tool** to spawn the custom agent under test. There is no formal eval JSON schema yet — use qualitative test prompts from the shared skill.

### Recommended flow

1. Draft 2–3 realistic prompts with the user (shared **Test prompts** section).
2. For each prompt, launch a **Task** subagent with `subagent_type` appropriate to the agent role (often `generalPurpose` or a named custom agent when Cursor supports selecting `.cursor/agents/<name>.md`).
3. In the Task prompt, include:
   - Path to the agent wrapper: `.cursor/agents/<agent-name>.md`
   - Instruction to read `.shared/agents/<agent-name>.md` first
   - The user's test prompt
   - Expected behavior and efficiency signals to watch for
4. Review the transcript against **correctness**, **completeness**, and **efficiency** (shared skill).
5. Edit bootstrap files (`agents/<agent-name>/`) for cross-tool fixes, or `.shared/agents/<agent-name>.md` on the direct path; edit `.cursor/agents/<agent-name>.md` for Cursor-only gaps. Reinstall after bootstrap edits.
6. Re-run `quick_validate.py` and re-test until the user is satisfied.

### Spawn example (Task prompt)

```
You are running as the custom agent defined in .cursor/agents/<agent-name>.md.
Read .shared/agents/<agent-name>.md first and follow it as the source of truth.

Task: <user test prompt>

Report your result in the output format defined in the shared agent file.
```

When Task notifications include `total_tokens` and `duration_ms`, note them when comparing efficiency across iterations.

## Description optimization in Cursor

No automated description loop is bundled for agents. Use the shared manual path:

1. Draft ~10–20 trigger eval queries (shared **Description optimization**)
2. Review should-trigger / should-not-trigger cases with the user in chat
3. Revise `description` in the authoritative edit location (`agents/<agent-name>/AGENT.md` or `.shared/agents/<agent-name>.md`) and sync into all installed wrapper files; reinstall if bootstrap
4. Ask the user to invoke the agent with realistic prompts in Cursor chat or via Task

## TodoList

When creating or testing agents, add todos so steps are not skipped — e.g. "Run quick_validate.py after scaffold" and "Run test prompts before marking agent complete."

## Wrapper policy

- Edit cross-tool behavior in `../../../.shared/skills/agent-creator/` and user agents in `.shared/agents/`
- Edit Cursor-only mechanics here and in user `.cursor/agents/` wrappers
- Do not duplicate the full shared skill body in this file
