---
name: agent-creator
description: Create portable custom agents for GitHub Copilot, Cursor, and Claude Code using a dual-target layout, and iteratively improve them. Use when users want to create an agent from scratch, bootstrap under the agents directory and install to .claude/agents and .github/agents, edit or optimize an existing agent, tune an agent's description for better triggering, or explain portable agent structure — even if they do not say "portable agent" explicitly. Does not trigger on creating skills (skill-creator) or slash commands and Copilot prompts (command-creator).
---

# Agent Creator

A skill for creating portable custom agent definitions and iteratively improving them.

At a high level, creating an agent goes like this:

- Decide what the agent should do, when it should trigger, and how success is measured
- **Choose an authoring path** — bootstrap under `agents/<name>/` (preferred) or direct scaffold with `create_agent.py` (see below)
- Write a tool-neutral `AGENT.md` body; put tool-specific guidance in `## Tool notes` sections
- **Install** when using bootstrap (`install_portable_agent.py`); direct scaffold writes installed paths immediately
- Create a few realistic test prompts and run the agent on the target tool
- Help the user evaluate results for **correctness**, **completeness**, and **efficiency** on that tool
- Rewrite content based on feedback (in bootstrap or installed paths, per path)
- Repeat until satisfied, then expand the test set

**Tool-specific execution** (how to spawn agent runs, reload steps, frontmatter fields such as `model` or `readonly`, and subagent mechanics) lives in the `## Tool notes` section of the agent file — read it after the tool-neutral body. Do not assume subagents, a particular CLI, or a browser unless the Tool notes document them.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft agent, go straight to review and iterate. If they prefer a lightweight pass without formal test runs, follow their lead.

## When NOT to Use

- **Creating a skill** — use [../skill-creator/SKILL.md](../skill-creator/SKILL.md), which follows a shared-first layout for skills with bundled resources and eval loops
- **Creating a slash command or Copilot prompt** — use [../command-creator/SKILL.md](../command-creator/SKILL.md), which follows a shared-first layout for commands

---

## Communicating with the user

Users may range from experts to people new to agent configuration. Match their vocabulary. Briefly explain terms like "Tool notes", "frontmatter", or "kebab-case" when unsure they know them.

If the user provides exact wording for agent instructions or the description, use it **verbatim** in generated files.

---

## Creating an agent

### Capture intent

Start by understanding intent. If the conversation already contains an agent role to capture, extract the name, description, instructions, success criteria, and tool-specific notes from history first. Confirm gaps with the user.

Ask:

1. What should this agent enable the coding agent to do?
2. When should it trigger? (phrases, tasks, contexts)
3. Where should files be written? (repo root, output directory)
4. Are there tool-specific notes for Claude Code, Cursor, or GitHub Copilot?
5. Does the user need one host only, or dual-target Claude + Copilot output?
6. What's the expected output format?
7. Should we set up test prompts? Objective agents (reviews, checklists, fixed workflows) benefit from tests; subjective agents (tone, design taste) often rely on qualitative review.

### Interview and research

Ask about edge cases, success criteria, output format, boundaries (what the agent must not do), readonly/background behavior, and whether the agent needs tool-specific frontmatter such as `model`, `tools`, `readonly`, `is_background`, or MCP settings.

The questions above are a fixed intake. When the request is ambiguous beyond them — the user is unsure whether they need an agent, a skill, or a command; the agent's boundaries conflict with its stated role; or nobody can yet say what a good result looks like — run the clarification loop in [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) before authoring files, and carry its requirement ledger into the agent's instructions and `description`.

Check the target repository for existing agent conventions before generating files. If `agents/`, `.claude/agents/`, or `.github/agents/` already exist, match their style.

Use available research tools (MCP, docs search, similar agents in the repo) when helpful — in parallel when your environment allows.

### Choose authoring path

Pick **one** path before writing files. Do not hand-edit installed layers (`.claude/agents/`, `.github/agents/`) when bootstrap source exists — edit bootstrap and reinstall.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained agent shipped like a product; repo already uses or wants `agents/<name>/`; agent will be revised and reinstalled over time | `agents/<name>/AGENT.md` | `install_portable_agent.py` |
| **Direct** | One-off or new agent in a project without `agents/` bootstrap; quick scaffold into installed layout | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` (via script) | `create_agent.py` |

**Prefer bootstrap when:**

- The agent is part of this repo's portable config (maintained alongside skills)
- The user asks to bootstrap, migrate, or reinstall an agent from `agents/<name>/`

**Prefer direct scaffold when:**

- The target project has no `agents/` directory and no plan to add bootstrap source
- The user wants a fast first draft before deciding whether to adopt bootstrap later

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Tool-neutral behavior | `agents/<name>/AGENT.md` → reinstall | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` |
| Tool-only notes (`## Tool notes`) | Same file, `## Tool notes` section → reinstall | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` |
| Runtime read target | `.claude/agents/<name>.md` + `.github/agents/<name>.agent.md` (install output; do not hand-edit) | Same |

After bootstrap edits, run `install_portable_agent.py` before testing in the IDE.

### Bundled scripts

Resolve `<AGENT_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `scripts/` and `references/` from that directory.

| Script | Path |
| --- | --- |
| Install bootstrap agent | `<AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py` |
| Create portable agent (direct) | `<AGENT_CREATOR_ROOT>/scripts/create_agent.py` |
| Validate | `<AGENT_CREATOR_ROOT>/scripts/quick_validate.py` |

Bootstrap source for this meta-skill may live at `skills/agent-creator/`; installed copies live under `.agents/skills/agent-creator/`.

**Module scripts:** when additional scripts are added, run `python -m scripts.*` with `<AGENT_CREATOR_ROOT>` as the working directory so imports resolve.

### Anatomy of a portable agent

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

**Progressive disclosure:** metadata (frontmatter) → tool-neutral body → `## Tool notes` on demand.

Keep behavior that applies everywhere in the agent file (`agents/<name>/AGENT.md` at bootstrap, installed copies after install). Put tool-native integration only in `## Tool notes` sections. Bootstrapped portable agents belong in `agents/<name>/`; agents without bootstrap source are scaffolded directly by `create_agent.py`.

### Bootstrap a new agent

When bootstrap is the chosen path, create or edit `agents/<agent-name>/`:

1. Add `AGENT.md` with tool-neutral frontmatter (`name`, `description`) and instructions body.
2. Add a `## Tool notes` section (with `### Claude Code` / `### GitHub Copilot` subsections) when the agent has tool-specific mechanics — spawn commands, reload steps, per-tool frontmatter notes. Keep it out of the tool-neutral body.
3. **Validate bootstrap source before install** — do not skip this step:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>
```

Copy from an existing agent under `agents/` or adapt a similar agent in the repo when starting from a known pattern.

### Install a bootstrap agent

When bootstrap source exists at `agents/<agent-name>/`:

**Always validate bootstrap source immediately before install.**

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>

python <AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py \
  --root <repo_root> \
  --name <agent-name> \
  --source agents/<agent-name> \
  --overwrite
```

Install writes two real copies: `AGENT.md` verbatim to `.claude/agents/<name>.md` (Cursor compat-reads it) and a Copilot transform (name/description frontmatter + body, Claude-only keys dropped) to `.github/agents/<name>.agent.md`. `--overwrite` also removes stale legacy outputs left by older installs (a leftover shared-layer or per-tool agent file).

Validate the installed set:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

Do not hand-edit installed agent files for bootstrapped agents — reinstall from bootstrap instead.

### Scaffold a new agent (direct path)

Use `create_agent.py` for **direct** scaffold when bootstrap under `agents/<name>/` is not the chosen path. Do **not** hand-create installed agent files — let the script generate them.

For **bootstrap** authoring, create or edit `agents/<name>/` (see **Choose authoring path** and **Install a bootstrap agent**) instead of running `create_agent.py`.

1. Draft the shared, tool-neutral instruction body in a temporary markdown file (body only — no frontmatter).
2. Run:

```bash
python <AGENT_CREATOR_ROOT>/scripts/create_agent.py \
  --root <repo_root> \
  --name <agent-name> \
  --description "<description>" \
  --instructions-file <instructions.md> \
  --overwrite
```

Use `--overwrite` only when regenerating and the user confirms.

3. **Validate immediately** — do not skip this step after scaffold or substantive edits:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

Fix validation errors before handing off to the user. Re-run validation after editing the agent file.

4. Edit the agent body and expand `## Tool notes` subsections per tool (reload steps, spawn mechanics, per-tool frontmatter notes).

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

Agents must be **tool-neutral** above `## Tool notes`: role, workflows, output formats, success criteria, and boundaries. No subagent product names, no single-vendor CLI assumptions, no reload instructions for one IDE.

Avoid tool-specific frontmatter in the agent file, including `tools`, `model`, `readonly`, `is_background`, `permissionMode`, `mcpServers`, `mcp-servers`, `hooks`, `skills`, `target`, `user-invocable`, and `disable-model-invocation`.

Tool-specific guidance belongs in `## Tool notes` sections, not frontmatter — the validator flags tool-specific bodies outside Tool notes, and the GitHub Copilot install transform keeps only `name` and `description` in frontmatter.

### Tool notes rules

Tool notes live in a `## Tool notes` H2 section at the end of the agent body, with per-tool `###` subsections as needed. Tool notes must:

- Stay out of the tool-neutral body above them
- Hold all tool-native execution details (spawn mechanics, reload steps, model/tools frontmatter notes, readonly/background flags)
- Stay optional — omit the section entirely when the agent has no tool-specific mechanics

The installed copies are two real files per agent; there is no wrapper layer to keep in sync.

After `create_agent.py` scaffolds a **new** agent, help the user draft **Tool notes sections** per tool.

### Output summary

After creating or installing files, summarize for the user:

- Authoritative edit path (`agents/<agent-name>/` or the installed files)
- Installed paths (`.claude/agents/<agent-name>.md`, `.github/agents/<agent-name>.agent.md`)
- Assumptions made about instructions or triggers

### Updating an existing agent

- Preserve the original `name` unless the user wants a rename
- If `agents/<name>/` exists, edit bootstrap files first (see **Where to edit**), then reinstall with `install_portable_agent.py` — do not patch installed files by hand
- If no bootstrap source, edit `.claude/agents/<name>.md` for Claude behavior and `.github/agents/<name>.agent.md` for Copilot behavior
- Re-run `quick_validate.py` after substantive edits (`--bootstrap-source` before install, or the installed set after)
- Re-run `create_agent.py --overwrite` only on the **direct** path when regenerating from a new instructions file is safer than hand-editing and the user confirms

### Write the agent definition

- **name**: kebab-case identifier (lowercase letters, digits, hyphens; max 64 characters)
- **description**: Primary trigger mechanism — what the agent does **and** when to use it. Be specific and slightly expansive so under-triggering is less likely. Keep all "when to use" phrasing in `description`, not the body. Write in third person.

---

## Agent writing guide

Every agent you create should be **correct**, **complete**, and **efficient on the specified tool**. Use these as explicit quality bars during drafting and review.

### Correctness

- Define a clear role and scope — what the agent owns and what it must defer to the user or other agents
- State accurate capabilities; do not instruct behavior the target tool cannot perform
- Include concrete success criteria the agent can verify before finishing
- Prefer citing files, functions, or code regions over vague references
- When the agent must refuse or escalate, say when and how

### Completeness

- Cover the happy path and common edge cases (missing context, empty diffs, failed commands, ambiguous requirements)
- Specify output format (sections, severity groups, JSON shape, bullet structure)
- Define boundaries: what not to change, what not to assume, when to ask clarifying questions
- Include a short "when invoked" or workflow section when the agent has ordered steps
- For review or audit agents, list explicit check categories

### Efficiency (tool-native)

- Keep tool-neutral instructions lean — every line should earn its place in context
- Put tool-specific shortcuts in `## Tool notes` (e.g. Task subagents in Cursor, Claude `-p` patterns, Copilot agent frontmatter)
- Avoid duplicating repo-wide rules the base model already follows
- Prefer imperative instructions; explain *why* when it helps generalization
- Do not embed long reference material in the agent file — point to repo docs or `references/` when the agent-creator skill bundles them

### Anatomy (shared file body)

A strong shared agent body typically includes:

1. **Role** — one paragraph establishing expertise and tone
2. **Workflow** — ordered steps when sequence matters
3. **Criteria / checklist** — what to evaluate or produce
4. **Output format** — how to structure the response
5. **Boundaries** — scope limits and escalation rules

Split long domain content into a separate reference file only when the agent-creator skill or target repo already supports bundled references for agents. Default portable agents are single shared markdown files.

### Principle of lack of surprise

No malware or hidden behavior. Decline requests for misleading, unauthorized-access, or covert agents.

See `references/portable-agent-layout.md` for path conventions, layouts, and a worked example.

---

## Test prompts

Draft 2–3 realistic user prompts that should invoke this agent. Confirm with the user before running.

For each prompt, note:

- **Expected behavior** — what a correct, complete response looks like
- **Efficiency signal** — unnecessary steps, over-long output, or wrong tool usage to watch for
- **Tool** — which environment to test in

Save prompts in the project (for example `<agent-name>-agent-tests.md` at repo root or in a user-chosen location) when the user wants a persistent test set. There is no required JSON schema yet; keep prompts concrete and tied to real tasks.

Follow the skill's `## Tool notes` for how to spawn agent runs (Task subagent, slash command, Copilot agent picker, etc.).

---

## Reviewing and improving the agent

After test runs:

1. **Correctness** — Did the agent stay in scope? Were recommendations accurate? Any hallucinated files or APIs?
2. **Completeness** — Were edge cases handled? Was output format consistent? Missing escalation when needed?
3. **Efficiency** — Was the prompt too long to follow? Did the agent repeat work or ignore native tool features documented in Tool notes?

Improvement rules:

1. **Generalize** — fixes must help beyond the few test examples
2. **Keep the agent file lean** — read transcripts, not just final outputs
3. **Edit the tool-neutral body first** — in `agents/<name>/AGENT.md` when bootstrap exists, else the installed files; reinstall after bootstrap edits
4. **Edit Tool notes for tool-only gaps** — the `## Tool notes` section of the agent file, per-tool subsections
5. **Explain why** — prefer reasoning over ALL-CAPS MUSTs

Re-run test prompts after edits until the user is satisfied or progress stalls.

---

## Description optimization

The `description` field drives agent discovery. After creating or improving an agent, offer to tune it.

### Shared steps (all tools)

**Step 1 — Trigger eval queries:** Draft ~10–20 realistic queries (should-trigger / should-not-trigger), concrete and edge-case heavy. Mix explicit agent requests ("use the code reviewer agent") with implicit task phrasing that should still match.

**Step 2 — User review:** Walk through queries with the user. Mark false positives (would trigger but shouldn't) and false negatives (should trigger but might not).

**Step 3 (automated — tool-specific):** Some tools support automated description loops. Follow Tool notes if documented; otherwise skip to Step 4.

**Step 4 — Apply:** Update agent frontmatter in the authoritative edit location (`agents/<name>/AGENT.md` or the installed files), reinstall if bootstrap. Show before/after when possible.

### How agent triggering works (general)

Agents match tasks against **name + description** in available-agent lists. Simple one-step tasks may not invoke a custom agent even when the description fits, because the base model handles them directly. Write descriptions substantial enough that delegating to a specialized agent would genuinely help.

---

### Related skills

| Task | Skill |
| --- | --- |
| Passive discovery, bundled scripts, eval loops | [../skill-creator/SKILL.md](../skill-creator/SKILL.md) |
| Slash commands and Copilot prompts | [../command-creator/SKILL.md](../command-creator/SKILL.md) |
| Settling an ambiguous request before authoring | [../prompt-clarifier/SKILL.md](../prompt-clarifier/SKILL.md) |

---

## Reference files

**references/**

- `references/portable-agent-layout.md` — paths, layouts, portability notes, and worked example

**scripts/** — see **Bundled scripts** above.

- `scripts/quick_validate.py` — Validate a bootstrap AGENT.md, an installed agent file, or a full portable set (`--root` + `--name`)

---

## Core loop (summary)

1. Capture intent and **choose authoring path** (bootstrap vs direct)
2. Author the body (tool-neutral above `## Tool notes`) — bootstrap: `agents/<name>/` then `install_portable_agent.py`; direct: `create_agent.py` then expand Tool notes
3. Validate (`--bootstrap-source` or per installed path / full `--root` + `--name` set)
4. Run realistic test prompts on the target tool (per Tool notes)
5. Review for correctness, completeness, and efficiency
6. Improve at the authoritative edit location (see **Where to edit**); sync `description`; reinstall if bootstrap; re-validate
7. Repeat until satisfied; offer description optimization

## Tool notes

### Claude Code

Claude Code supports **subagents** — use them to test custom agents qualitatively:

1. Draft 2–3 test prompts with the user.
2. For each prompt, spawn a subagent in the same turn when comparing variants, or sequentially for simple review.
3. The subagent prompt should reference `.claude/agents/<agent-name>.md` and instruct reading it as the source of truth.
4. Review against correctness, completeness, and efficiency.
5. Edit bootstrap files (`agents/<agent-name>/`) for cross-tool fixes, or the installed files on the direct path; reinstall after bootstrap edits.
6. Re-validate and re-test.

Spawn example:

```
Execute as the custom agent in .claude/agents/<agent-name>.md.
That file is the source of truth for the role.

Task: <user test prompt>
```

When subagent completion notifications include `total_tokens` and `duration_ms`, note them for efficiency comparisons.

**Description optimization:** no automated loop is bundled for agents. Use shared Steps 1–2 and 4 manually (draft queries, mark false positives/negatives, apply the revised `description`, reinstall if bootstrap). Custom agents appear in available agent lists; Claude selects them when the description matches and specialized behavior would help.

On Claude.ai (no Claude Code CLI): no subagents — run test prompts sequentially yourself, present outputs inline, use manual description optimization only. For read-only environments, copy to `/tmp/agent-creator/`, edit, validate, then copy artifacts back if needed.

### Cursor

Use the **Task tool** to spawn the custom agent under test:

1. Draft 2–3 realistic prompts with the user.
2. Launch a **Task** subagent per prompt with `subagent_type` appropriate to the agent role (often `generalPurpose`).
3. In the Task prompt include: the path to the agent under test (`.claude/agents/<agent-name>.md`, which Cursor compat-reads), the instruction to read it first, the user's test prompt, and expected behavior / efficiency signals.
4. Review the transcript against correctness, completeness, and efficiency.
5. Edit bootstrap files (`agents/<agent-name>/`) for cross-tool fixes, or the installed files on the direct path; reinstall after bootstrap edits.
6. Re-run `quick_validate.py` and re-test until the user is satisfied.

Task prompt example:

```
You are running as the custom agent defined in .claude/agents/<agent-name>.md.
Read it first and follow it as the source of truth.

Task: <user test prompt>

Report your result in the output format defined in the agent file.
```

**Description optimization:** no automated loop — draft ~10–20 trigger eval queries, review should-trigger / should-not-trigger cases with the user in chat, revise `description` in the authoritative edit location, reinstall if bootstrap, and ask the user to invoke the agent with realistic prompts.

### GitHub Copilot

Copilot Chat does not expose parallel subagents — use a **qualitative, sequential** loop in Copilot Chat or the Copilot agent picker:

1. Draft 2–3 test prompts with the user.
2. Ensure the agent is installed at `.github/agents/<name>.agent.md`.
3. Invoke the custom agent from the Copilot agent picker or by phrasing the prompt to match the agent `description`.
4. Present each prompt + output to the user; review against correctness, completeness, and efficiency.
5. Edit bootstrap files (`agents/<agent-name>/`) for cross-tool fixes, or the installed files on the direct path; reinstall after bootstrap edits.
6. Re-validate in terminal; reload VS Code; re-test in chat.

**Description optimization:** manual path only (shared Steps 1–2 and 4); reload VS Code after applying. Write descriptions that state both **what** the agent does and **when** Copilot should use it.
