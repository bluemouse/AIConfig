---
name: agent-creator
description: "Create and iteratively improve portable custom agents for GitHub Copilot, Cursor, and Claude Code using the dual-target layout (bootstrap under agents/ and install to .claude/agents and .github/agents). Use to author an agent from scratch, edit or validate an agent, tune its trigger description, or explain portable agent layout. Does not trigger on skills (skill-creator) or slash commands (command-creator)."
---

# Agent Creator

Flow: capture intent → choose bootstrap (`agents/<name>/AGENT.md`, preferred) or direct scaffold (`create_agent.py`) → write a tool-neutral body with host mechanics in `## Tool notes` → validate → install or expand → test with realistic prompts and iterate.

Shared authoring rules — bootstrap vs direct choice, authoritative-edit rule, intake, manual description tuning, output summary, and the iterate loop — live in [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md); this file carries only the agent-specific delta.

## When NOT to Use

- **Creating a skill** → [../skill-creator/SKILL.md](../skill-creator/SKILL.md)
- **Creating a slash command or Copilot prompt** → [../command-creator/SKILL.md](../command-creator/SKILL.md)

---

## Creating an agent

### Intake, paths, and bundled scripts

Follow [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md) to extract `name`, `description`, instructions, and success criteria matching existing `agents/`, `.claude/agents/`, and `.github/agents/` conventions.

| Path | Authoritative source | Install / scaffold | Installed targets (dual-target real copies) |
| --- | --- | --- | --- |
| **Bootstrap** | `agents/<name>/AGENT.md` | `install_portable_agent.py` | `.claude/agents/<name>.md` (verbatim; Cursor + modern VS Code Copilot compat-read) + `.github/agents/<name>.agent.md` (Copilot `name`/`description` transform) |
| **Direct** | Installed files (via script) | `create_agent.py` | Same dual-target paths (`--overwrite` purges legacy wrappers) |

Resolve `<AGENT_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`:
- `python -m scripts.quick_validate` / `python -m scripts.create_agent` (from `<AGENT_CREATOR_ROOT>`) or by full path.
- `python <AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py` (direct path only — flat sibling imports).

### Bootstrap and direct commands

- **Bootstrap (preferred):** author `agents/<agent-name>/AGENT.md`, validate bootstrap, install, and validate installed copies:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>
python <AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py \
  --root <repo_root> --name <agent-name> --source agents/<agent-name> --overwrite
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

- **Direct scaffold** (never hand-create installed files): draft body-only Markdown, then scaffold and validate:

```bash
python <AGENT_CREATOR_ROOT>/scripts/create_agent.py \
  --root <repo_root> --name <agent-name> --description "<description>" \
  --instructions-file <instructions.md> --overwrite
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

### Agent file and frontmatter rules

- **Frontmatter (`name` + `description` only):** `name` kebab-case ≤64 chars (preserve on edits unless renaming); `description` ≤1,024 chars with no `<`/`>`, third-person, stating **what** the agent does and **when** to delegate to it (all trigger phrasing belongs here, not the body). Do not add non-portable keys (`tools`, `model`, `readonly`, `is_background`, `permissionMode`, `mcpServers`, `mcp-servers`, `hooks`, `skills`, `target`, `user-invocable`, `disable-model-invocation`) — document host-specific frontmatter options inside `## Tool notes` (or see `references/portable-agent-layout.md` for read-only checker agents).
- **Body neutrality:** keep role, workflow, output format, and boundaries strictly tool-neutral above optional `## Tool notes` (per-tool `###` subsections at the end; validator rejects host-specific terms in the neutral body).

### Iterate, tune, and references

Follow [../skill-creator/references/creation-common.md](../skill-creator/references/creation-common.md) for testing, manual `description` tuning (there is no automated `run_loop.py` for agents), and the final output summary. Layout details and per-host read-only checker notes live in `references/portable-agent-layout.md`.

---

## Tool notes

Draft 2–3 test prompts, run against the installed agent, review correctness/completeness/efficiency, edit the authoritative source, reinstall if bootstrapped, and re-validate:

| Tool | Spawn mechanics | Agent file read |
| --- | --- | --- |
| Claude Code | Subagent (parallel per prompt when comparing variants; note `total_tokens` / `duration_ms`); sequential inline on Claude.ai | `.claude/agents/<agent-name>.md` |
| Cursor | Task tool (`subagent_type` matching role, e.g. `generalPurpose`), one Task per prompt | `.claude/agents/<agent-name>.md` (compat-read) |
| GitHub Copilot | Subagent/task dispatch when the active Copilot surface exposes it (e.g. VS Code Copilot agent/SDK); otherwise invoke sequentially from the agent picker or matching prompt; reload VS Code after changes | `.github/agents/<agent-name>.agent.md` (VS Code also compat-discovers `.claude/agents/<agent-name>.md`) |

Prompt wrapper when spawning via generic subagent/Task:

```text
You are running as the custom agent defined in .claude/agents/<agent-name>.md.
Read it first and follow it as the source of truth.

Task: <user test prompt>

Report your result in the output format defined in the agent file.
```
