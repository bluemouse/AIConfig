---
name: agent-creator
description: Create portable custom agents for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create an agent from scratch, bootstrap under the agents directory and install to .shared/agents with tool wrappers, edit or optimize an existing agent, tune an agent's description for better triggering, or explain portable agent structure — even if they do not say "portable agent" explicitly.
---

# Agent Creator

A skill for creating portable custom agent definitions and iteratively improving them.

At a high level, creating an agent goes like this:

- Decide what the agent should do, when it should trigger, and how success is measured
- **Choose an authoring path** — bootstrap under `agents/<name>/` (preferred) or direct scaffold with `create_agent.py` (see below)
- Write a tool-neutral shared agent body and tool-specific wrapper notes
- **Install** when using bootstrap (`install_portable_agent.py`); direct scaffold writes installed paths immediately
- Create a few realistic test prompts and run the agent on the target tool
- Help the user evaluate results for **correctness**, **completeness**, and **efficiency** on that tool
- Rewrite shared content and wrappers based on feedback (in bootstrap or installed paths, per path)
- Repeat until satisfied, then expand the test set

**Tool-specific execution** (how to spawn agent runs, reload steps, frontmatter fields such as `model` or `readonly`, and subagent mechanics) lives in your **tool wrapper** — read it after this shared skill. Do not assume subagents, a particular CLI, or a browser unless your wrapper documents them.

Your job is to figure out where the user is in this process and help them progress. If they already have a draft agent, go straight to review and iterate. If they prefer a lightweight pass without formal test runs, follow their lead.

---

## Communicating with the user

Users may range from experts to people new to agent configuration. Match their vocabulary. Briefly explain terms like "wrapper", "frontmatter", or "kebab-case" when unsure they know them.

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
5. Should wrappers reference the shared file, or does the user need a standalone copy in one tool folder?
6. What's the expected output format?
7. Should we set up test prompts? Objective agents (reviews, checklists, fixed workflows) benefit from tests; subjective agents (tone, design taste) often rely on qualitative review.

### Interview and research

Ask about edge cases, success criteria, output format, boundaries (what the agent must not do), readonly/background behavior, and whether the agent needs tool-specific frontmatter such as `model`, `tools`, `readonly`, `is_background`, or MCP settings.

Check the target repository for existing agent conventions before generating files. If `agents/`, `.shared/agents/`, or tool-specific agent folders already exist, match their style.

Use available research tools (MCP, docs search, similar agents in the repo) when helpful — in parallel when your environment allows.

### Choose authoring path

Pick **one** path before writing files. Do not hand-edit installed layers (`.shared/agents/`, tool agent folders) when bootstrap source exists — edit bootstrap and reinstall.

| Path | When to use | Author here | Install / scaffold |
| --- | --- | --- | --- |
| **Bootstrap** | Repo-maintained agent shipped like a product; repo already uses or wants `agents/<name>/`; agent will be revised and reinstalled over time | `agents/<name>/AGENT.md` + optional `wrappers/<tool>/AGENT.md` | `install_portable_agent.py` |
| **Direct** | One-off or new agent in a project without `agents/` bootstrap; quick scaffold into installed layout | `.shared/agents/<name>.md` (via script) | `create_agent.py` |

**Prefer bootstrap when:**

- The agent is part of this repo's portable config (maintained alongside skills)
- You need partial tool wrappers only (e.g. Cursor without Claude/GitHub) — bootstrap install skips missing wrappers; `create_agent.py` always creates all three
- The user asks to bootstrap, migrate, or reinstall an agent from `agents/<name>/`

**Prefer direct scaffold when:**

- The target project has no `agents/` directory and no plan to add bootstrap source
- You need all three tool wrappers generated immediately with default templates
- The user wants a fast first draft before deciding whether to adopt bootstrap later

**Partial wrappers:** Not every agent needs Claude, Cursor, and GitHub layers. Bootstrap supports any subset under `wrappers/`; validate only the paths that exist after install.

### Where to edit (by path)

| Concern | Bootstrap path | Direct path |
| --- | --- | --- |
| Cross-tool behavior | `agents/<name>/AGENT.md` → reinstall | `.shared/agents/<name>.md` |
| Tool-only notes / frontmatter | `agents/<name>/wrappers/<tool>/AGENT.md` → reinstall | `.cursor/agents/<name>.md`, etc. |
| Runtime read target | `.shared/agents/<name>.md` (install output; do not hand-edit) | Same |

After bootstrap edits, run `install_portable_agent.py` before testing in the IDE.

### Bundled scripts

Resolve `<AGENT_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `scripts/` and `references/` from that directory.

| Script | Path |
| --- | --- |
| Install bootstrap agent | `<AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py` |
| Create portable agent (direct) | `<AGENT_CREATOR_ROOT>/scripts/create_agent.py` |
| Validate | `<AGENT_CREATOR_ROOT>/scripts/quick_validate.py` |

Bootstrap source for this meta-skill may live at `skills/agent-creator/`; installed copies live under `.shared/skills/agent-creator/`.

**Module scripts:** when additional scripts are added, run `python -m scripts.*` with `<AGENT_CREATOR_ROOT>` as the working directory so imports resolve.

### Anatomy of a portable agent

**Installed layout:**

```
repo/
├── .shared/agents/<agent-name>.md       # Tool-neutral agent definition (install output)
├── .cursor/agents/<agent-name>.md       # Cursor wrapper
├── .claude/agents/<agent-name>.md       # Claude Code wrapper
└── .github/agents/<agent-name>.agent.md # GitHub Copilot wrapper
```

**Bootstrap layout** (when the agent ships bootstrap source):

```
repo/
├── agents/<agent-name>/
│   ├── AGENT.md                         # Shared agent body (author here)
│   └── wrappers/                        # Optional custom tool templates
│       ├── cursor/AGENT.md
│       ├── claude/AGENT.md
│       └── github/AGENT.md
```

**Progressive disclosure:** metadata (frontmatter) → shared agent body → tool-specific wrapper notes on demand.

Keep behavior that applies everywhere in the shared agent file (`agents/<name>/AGENT.md` at bootstrap, `.shared/agents/<name>.md` after install). Put tool-native integration in wrappers only. Bootstrapped portable agents belong in `agents/<name>/`; agents without bootstrap source belong in `.shared/agents/`.

### Bootstrap a new agent

When bootstrap is the chosen path, create or edit `agents/<agent-name>/`:

1. Add `AGENT.md` with tool-neutral frontmatter (`name`, `description`) and instructions body.
2. Add optional custom wrappers under `wrappers/{cursor,claude,github}/AGENT.md` that point to `../../.shared/agents/<name>.md`, include reload notes, and document tool-specific mechanics (spawn commands, model/tools frontmatter, readonly/background flags). If omitted, those tool layers are not installed until you add wrappers and reinstall.
3. **Validate bootstrap source before install** — do not skip this step:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>
```

Copy from an existing agent under `agents/` or adapt a similar agent in the repo when starting from a known pattern.

### Install a bootstrap agent

When bootstrap source exists at `agents/<agent-name>/`:

**Always validate bootstrap source immediately before install** — install syncs `description` (and rebuilds frontmatter) on custom wrappers from shared `AGENT.md`, but bootstrap validation catches name/description drift between bootstrap wrapper files and `AGENT.md` before anything is written.

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --bootstrap-source agents/<agent-name>

python <AGENT_CREATOR_ROOT>/scripts/install_portable_agent.py \
  --root <repo_root> \
  --name <agent-name> \
  --source agents/<agent-name> \
  --overwrite
```

Install copies `AGENT.md` to `.shared/agents/<name>.md` and installs only the tool wrappers present under `wrappers/`. It does **not** auto-generate missing wrappers. Custom wrappers get `name` and `description` synced from shared `AGENT.md` during install (including folded-block YAML descriptions).

**Overwrite behavior:**

- `--overwrite` (default): installs wrappers listed in bootstrap and **removes** installed tool wrappers that are no longer present under `wrappers/`. Use this when shrinking the wrapper set (dropping a tool) or migrating from a direct scaffold.
- `--no-overwrite`: refuses if any install target already exists. When install succeeds for new paths only, it **does not** delete stale wrappers left from a prior partial install.

Validate each installed path individually when the agent ships a partial wrapper set:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py .shared/agents/<agent-name>.md
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py .cursor/agents/<agent-name>.md
```

Do not hand-edit `.shared/agents/` or tool agent folders for bootstrapped agents — reinstall from bootstrap instead.

### Scaffold a new agent (direct path)

Use `create_agent.py` for **direct** scaffold when bootstrap under `agents/<name>/` is not the chosen path. Do **not** hand-create `.shared/agents/` or tool wrapper files — let the script generate them.

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

Use `--claude-note`, `--cursor-note`, and `--github-note` for tool-specific wrapper hints. Use `--overwrite` only when regenerating and the user confirms.

3. **Validate immediately** — do not skip this step after scaffold or substantive edits:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py --root <repo_root> --name <agent-name>
```

Or validate each file individually:

```bash
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py .shared/agents/<agent-name>.md
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py .cursor/agents/<agent-name>.md
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py .claude/agents/<agent-name>.md
python <AGENT_CREATOR_ROOT>/scripts/quick_validate.py .github/agents/<agent-name>.agent.md
```

Fix validation errors before handing off to the user. Re-run validation after editing shared agent or wrapper files.

4. Edit the shared agent and expand wrapper sections per tool (reload steps, spawn mechanics, optional frontmatter). Do not leave TODO-only wrappers for production agents.

### Shared agent rules

The shared file must contain only the lowest-common-denominator agent format:

```markdown
---
name: <agent-name>
description: <clear trigger description>
---

<tool-neutral agent instructions>
```

Shared agents must be **tool-neutral**: role, workflows, output formats, success criteria, and boundaries. No subagent product names, no single-vendor CLI assumptions, no reload instructions for one IDE.

Avoid tool-specific frontmatter in `.shared/agents/<agent-name>.md`, including `tools`, `model`, `readonly`, `is_background`, `permissionMode`, `mcpServers`, `mcp-servers`, `hooks`, `skills`, `target`, `user-invocable`, and `disable-model-invocation`.

Add those fields to a wrapper only when the user explicitly wants per-tool variants.

### Wrapper rules

Wrappers must:

- Use the tool's expected path and filename (see `references/portable-agent-layout.md`)
- Share `name` and `description` with the shared agent (sync on changes)
- Point to `.shared/agents/<agent-name>.md` as canonical
- Tell the agent to read the shared file first before acting
- Hold all tool-native execution details (spawn mechanics, reload steps, model/tools frontmatter, readonly/background flags)

Do not duplicate the full shared body into wrappers unless the user requires copy-based portability.

Reference-based wrappers reduce duplication but depend on the tool following the wrapper instruction to read the shared file. If the user needs maximum standalone behavior, generate copy-based wrappers instead.

After `create_agent.py` scaffolds a **new** agent, help the user draft **native wrapper sections** per tool. Use `--cursor-note`, `--claude-note`, and `--github-note` for one-line hints at scaffold time; expand in wrapper files afterward.

### Output summary

After creating or installing files, summarize for the user:

- Authoritative edit path (`agents/<agent-name>/` or `.shared/agents/<agent-name>.md`)
- Shared agent path (`.shared/agents/<agent-name>.md`)
- Wrapper paths (`.cursor/`, `.claude/`, `.github/agents/<agent-name>.agent.md`)
- Assumptions made about instructions or triggers
- Whether layouts are reference wrappers or standalone copies

### Updating an existing agent

- Preserve the original `name` unless the user wants a rename
- If `agents/<name>/` exists, edit bootstrap files first (see **Where to edit**), then reinstall with `install_portable_agent.py` — do not patch `.shared/agents/` or tool folders by hand
- If no bootstrap source, edit `.shared/agents/<name>.md` first for cross-tool behavior; wrappers for tool-only notes or frontmatter
- Re-run `quick_validate.py` after substantive edits (`--bootstrap-source` before install, or per installed path after)
- Sync `description` across shared content and every installed wrapper when it changes
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

- Keep shared instructions lean — every line should earn its place in context
- Put tool-specific shortcuts in wrappers (e.g. Task subagents in Cursor, Claude `-p` patterns, Copilot agent frontmatter)
- Avoid duplicating repo-wide rules the base model already follows
- Prefer imperative instructions; explain *why* when it helps generalization
- Do not embed long reference material in the shared file — point to repo docs or `references/` when the agent-creator skill bundles them

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

See `references/portable-agent-layout.md` for path conventions, wrapper templates, relative paths, and a worked example.

---

## Test prompts

Draft 2–3 realistic user prompts that should invoke this agent. Confirm with the user before running.

For each prompt, note:

- **Expected behavior** — what a correct, complete response looks like
- **Efficiency signal** — unnecessary steps, over-long output, or wrong tool usage to watch for
- **Tool** — which wrapper/environment to test in

Save prompts in the project (for example `<agent-name>-agent-tests.md` at repo root or in a user-chosen location) when the user wants a persistent test set. There is no required JSON schema yet; keep prompts concrete and tied to real tasks.

Follow your **tool wrapper** for how to spawn agent runs (Task subagent, slash command, Copilot agent picker, etc.).

---

## Reviewing and improving the agent

After test runs:

1. **Correctness** — Did the agent stay in scope? Were recommendations accurate? Any hallucinated files or APIs?
2. **Completeness** — Were edge cases handled? Was output format consistent? Missing escalation when needed?
3. **Efficiency** — Was the prompt too long to follow? Did the agent repeat work or ignore native tool features documented in the wrapper?

Improvement rules:

1. **Generalize** — fixes must help beyond the few test examples
2. **Keep the shared file lean** — read transcripts, not just final outputs
3. **Edit shared first** — cross-tool behavior in `agents/<name>/AGENT.md` when bootstrap exists, else `.shared/agents/<name>.md`; reinstall after bootstrap edits
4. **Edit wrappers for tool-only gaps** — bootstrap: `agents/<name>/wrappers/<tool>/AGENT.md`; direct: tool agent folders under `.cursor/`, `.claude/`, `.github/`
5. **Explain why** — prefer reasoning over ALL-CAPS MUSTs

Re-run test prompts after edits until the user is satisfied or progress stalls.

---

## Description optimization

The `description` field drives agent discovery. After creating or improving an agent, offer to tune it.

### Shared steps (all tools)

**Step 1 — Trigger eval queries:** Draft ~10–20 realistic queries (should-trigger / should-not-trigger), concrete and edge-case heavy. Mix explicit agent requests ("use the code reviewer agent") with implicit task phrasing that should still match.

**Step 2 — User review:** Walk through queries with the user. Mark false positives (would trigger but shouldn't) and false negatives (should trigger but might not).

**Step 3 (automated — tool-specific):** Some tools support automated description loops. Follow your wrapper if documented; otherwise skip to Step 4.

**Step 4 — Apply:** Update shared agent frontmatter in the authoritative edit location (`agents/<name>/AGENT.md` or `.shared/agents/<name>.md`), sync `description` into every wrapper, reinstall if bootstrap. Show before/after when possible.

### How agent triggering works (general)

Agents match tasks against **name + description** in available-agent lists. Simple one-step tasks may not invoke a custom agent even when the description fits, because the base model handles them directly. Write descriptions substantial enough that delegating to a specialized agent would genuinely help.

---

## Reference files

**references/**

- `references/portable-agent-layout.md` — paths, wrapper templates, relative paths, portability notes, and worked example

**scripts/** — see **Bundled scripts** above.

- `scripts/quick_validate.py` — Validate shared agent files, wrappers, or a full portable set (`--root` + `--name`)

---

## Core loop (summary)

1. Capture intent and **choose authoring path** (bootstrap vs direct)
2. Author shared body and wrappers — bootstrap: `agents/<name>/` then `install_portable_agent.py`; direct: `create_agent.py` then expand wrappers
3. Validate (`--bootstrap-source` or per installed path / full `--root` + `--name` set)
4. Run realistic test prompts on the target tool (per tool wrapper)
5. Review for correctness, completeness, and efficiency
6. Improve at the authoritative edit location (see **Where to edit**); sync `description`; reinstall if bootstrap; re-validate
7. Repeat until satisfied; offer description optimization
