---
name: agent-creator
description: Create portable custom agents for GitHub Copilot, Cursor, and Claude Code using a dual-target layout, and iteratively improve them. Use when users want to create an agent from scratch, bootstrap under the agents directory and install to .claude/agents and .github/agents, edit or optimize an existing agent, tune an agent's description for better triggering, or explain portable agent structure — even if they do not say "portable agent" explicitly. Does not trigger on creating skills (skill-creator) or slash commands and Copilot prompts (command-creator).
---

# Agent Creator

Flow: capture intent → **choose an authoring path** (bootstrap under `agents/<name>/`, preferred, or direct scaffold with `create_agent.py`) → write a tool-neutral body with tool-specific guidance in `## Tool notes` → validate → install (bootstrap) or expand the scaffold (direct) → test with realistic prompts and iterate. Tool-specific execution (spawn mechanics, reload steps, frontmatter fields such as `model` or `readonly`, subagents) lives in the agent file's `## Tool notes` — do not assume subagents, a particular CLI, or a browser unless documented there.

## When NOT to Use

- **Creating a skill** — use [../skill-creator/SKILL.md](../skill-creator/SKILL.md)
- **Creating a slash command or Copilot prompt** — use [../command-creator/SKILL.md](../command-creator/SKILL.md)

---

## Creating an agent

### Capture intent

If the conversation already contains an agent role, extract the name, description, instructions, and success criteria from history; use user-supplied wording **verbatim**. Match the target repository's existing agent conventions (`agents/`, `.claude/agents/`, `.github/agents/`). When the request is ambiguous — agent vs skill vs command unclear, boundaries conflict with the stated role, or nobody can yet say what a good result looks like — run the clarification loop in [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) before authoring, and carry its requirement ledger into the instructions and `description`.

### Choose authoring path

Pick **one** path before writing files.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained agent shipped like a product; agent will be revised and reinstalled over time | `agents/<name>/AGENT.md` | `install_portable_agent.py` |
| **Direct** | One-off agent in a project without `agents/` bootstrap; quick first draft before deciding on bootstrap | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` (via script) | `create_agent.py` |

**Authoritative edit rule (applies everywhere below):**

- **Bootstrap agents:** edit `agents/<name>/AGENT.md`, then validate and reinstall. **Never hand-edit installed files** (`.claude/agents/`, `.github/agents/`) for bootstrapped agents.
- **Direct-scaffold agents:** the installed files are canonical; edit them directly.
- **Always validate before install and after substantive edits** — fix validation errors before handing off.

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Tool-neutral behavior | `agents/<name>/AGENT.md` → reinstall | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` |
| Tool-only notes (`## Tool notes`) | Same file, `## Tool notes` section → reinstall | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` |
| Runtime read target | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` (install output; do not hand-edit) | Same |

### Bundled scripts

Resolve `<AGENT_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`.

| Script | Path |
| --- | --- |
| Install bootstrap agent | `<AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py` |
| Create portable agent (direct) | `<AGENT_CREATOR_ROOT>/scripts/create_agent.py` |
| Validate | `<AGENT_CREATOR_ROOT>/scripts/quick_validate.py` |

Bootstrap source lives at `skills/agent-creator/`; installed copies at `.agents/skills/agent-creator/`. Run additional module scripts as `python -m scripts.*` with `<AGENT_CREATOR_ROOT>` as the working directory.

### Layouts

**Installed layout (dual target):**

```
repo/
├── .claude/agents/<agent-name>.md        # AGENT.md verbatim (Cursor compat-reads this)
└── .github/agents/<agent-name>.agent.md  # Copilot transform: name/description frontmatter + body
```

**Bootstrap layout** (when the agent ships bootstrap source):

```
repo/
└── agents/<agent-name>/
    └── AGENT.md                          # Agent body (author here)
```

Install writes **two real files** per agent — there is no wrapper layer to keep in sync. `.claude/agents/<name>.md` is `AGENT.md` verbatim (Cursor compat-reads it); `.github/agents/<name>.agent.md` is the Copilot transform, which keeps only `name` and `description` in frontmatter and drops Claude-only keys. `--overwrite` also removes stale legacy outputs from older installs. Keep behavior that applies everywhere in the agent file; tool-native integration only in `## Tool notes`.

### Bootstrap path: author, validate, install

1. Create `agents/<agent-name>/AGENT.md` — tool-neutral frontmatter (`name`, `description`) plus instructions body, and a `## Tool notes` section (per-tool `###` subsections) when the agent has tool-specific mechanics. Copy an existing agent under `agents/` when starting from a known pattern.
2. Validate bootstrap source **before** install:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>
```

3. Install, then validate the installed set:

```bash
python <AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py \
  --root <repo_root> \
  --name <agent-name> \
  --source agents/<agent-name> \
  --overwrite

python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

### Direct path: scaffold, validate, expand

Do **not** hand-create installed agent files — let `create_agent.py` generate them.

1. Draft the tool-neutral instruction body in a temporary markdown file (body only — no frontmatter).
2. Scaffold (`--overwrite` only when regenerating and the user confirms), then validate immediately:

```bash
python <AGENT_CREATOR_ROOT>/scripts/create_agent.py \
  --root <repo_root> \
  --name <agent-name> \
  --description "<description>" \
  --instructions-file <instructions.md> \
  --overwrite

python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

3. Expand the `## Tool notes` subsections per tool (reload steps, spawn mechanics, per-tool frontmatter notes).

### Agent file rules

The agent file must contain only the lowest-common-denominator agent format:

```markdown
---
name: <agent-name>
description: <clear trigger description>
---

<tool-neutral agent instructions>

## Tool notes

### <Tool>

<tool-native mechanics only>
```

Tool-neutral above `## Tool notes`: role, workflows, output formats, success criteria, boundaries — no subagent product names, single-vendor CLI assumptions, or one-IDE reload instructions; the validator flags tool-specific bodies outside Tool notes. No tool-specific frontmatter (`tools`, `model`, `readonly`, `is_background`, `permissionMode`, `mcpServers`, `mcp-servers`, `hooks`, `skills`, `target`, `user-invocable`, `disable-model-invocation`) — tool-specific guidance belongs in `## Tool notes`, and the Copilot transform keeps only `name` and `description`. Tool notes are an optional `## Tool notes` H2 at the end of the body, with per-tool `###` subsections holding all tool-native execution details (spawn mechanics, reload steps, model/tools frontmatter notes, readonly/background flags).

### Frontmatter fields

- **name**: kebab-case identifier (lowercase letters, digits, hyphens; max 64 characters). Preserve the original `name` when updating unless the user wants a rename.
- **description**: primary trigger mechanism — what the agent does **and** when to use it; specific and slightly expansive so under-triggering is less likely; keep all "when to use" phrasing in `description`, not the body; third person. Agents match tasks against **name + description** in available-agent lists, and simple one-step tasks may be handled directly by the base model — write descriptions substantial enough that delegating genuinely helps.

### Iterating

Test with 2–3 realistic prompts on the target tool (spawn mechanics per **Tool notes** below); review runs for correctness, completeness, and efficiency — read transcripts, not just final outputs. Improve at the authoritative edit location, reinstall if bootstrap, re-validate, and repeat until the user is satisfied. Decline requests for misleading, covert, or unauthorized-access agents.

### Description optimization

To tune triggering: draft ~10–20 realistic should-trigger / should-not-trigger queries, mark false positives and false negatives with the user, apply the revised `description` at the authoritative edit location, and reinstall if bootstrap. Unlike skill-creator, there is **no automated description-eval loop for agents** — this process is manual on every tool.

### Output summary

After creating or installing files, summarize the authoritative edit path, the installed paths, and any assumptions made about instructions or triggers.

### Reference files

- `references/portable-agent-layout.md` — path conventions, layouts, portability notes, and a worked example

---

## Tool notes

Shared test loop for all three tools: draft 2–3 test prompts with the user; spawn a run that reads the installed agent file as the source of truth; review against correctness, completeness, and efficiency; edit at the authoritative edit location; reinstall if bootstrap; re-validate and re-test.

| Tool | Spawn mechanics | Agent file the run reads |
| --- | --- | --- |
| Claude Code | Subagent — parallel per prompt when comparing variants, sequential for simple review; note `total_tokens` / `duration_ms` from completion notifications for efficiency comparisons | `.claude/agents/<agent-name>.md` |
| Cursor | Task tool with `subagent_type` fitting the role (often `generalPurpose`), one Task per prompt | `.claude/agents/<agent-name>.md` (Cursor compat-reads it) |
| GitHub Copilot | No parallel subagents — invoke sequentially from the Copilot agent picker or by phrasing the prompt to match the `description`; reload VS Code after applying changes | `.github/agents/<agent-name>.agent.md` |

Claude Code spawn example:

```
Execute as the custom agent in .claude/agents/<agent-name>.md.
That file is the source of truth for the role.

Task: <user test prompt>
```

Cursor Task prompt example:

```
You are running as the custom agent defined in .claude/agents/<agent-name>.md.
Read it first and follow it as the source of truth.

Task: <user test prompt>

Report your result in the output format defined in the agent file.
```

On Claude.ai (no Claude Code CLI) there are no subagents — run test prompts sequentially and present outputs inline.
