---
name: agent-creator
description: Create portable custom agents for GitHub Copilot, Cursor, and Claude Code using a shared-first layout, and iteratively improve them. Use when users want to create an agent from scratch, scaffold `.shared/agents` with tool wrappers in `.cursor/agents`, `.claude/agents`, or `.github/agents`, edit or optimize an existing agent, tune an agent's description for better triggering, or explain portable agent structure — even if they do not say "portable agent" explicitly.
---

# Agent Creator

A skill for creating portable custom agent definitions and iteratively improving them.

At a high level, creating an agent goes like this:

- Decide what the agent should do, when it should trigger, and how success is measured
- **Scaffold** the shared agent in `.shared/agents/<name>.md` and generate tool wrappers with `create_agent.py`
- Write a draft of the shared agent body (tool-neutral) and tool-specific notes in each wrapper
- Create a few realistic test prompts and run the agent on the target tool
- Help the user evaluate results for **correctness**, **completeness**, and **efficiency** on that tool
- Rewrite the shared agent and wrappers based on feedback
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

Check the target repository for existing agent conventions before generating files. If `.shared/agents/` or tool-specific agent folders already exist, match their style.

Use available research tools (MCP, docs search, similar agents in `agents-ref/` or the repo) when helpful — in parallel when your environment allows.

### Bundled scripts

Resolve `<AGENT_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `scripts/` and `references/` from that directory.

| Script | Path |
| --- | --- |
| Create portable agent | `<AGENT_CREATOR_ROOT>/scripts/create_agent.py` |
| Validate | `<AGENT_CREATOR_ROOT>/scripts/quick_validate.py` |

Bootstrap source for this meta-skill may live at `skills/agent-creator/`; installed copies live under `.shared/skills/agent-creator/`.

**Module scripts:** when additional scripts are added, run `python -m scripts.*` with `<AGENT_CREATOR_ROOT>` as the working directory so imports resolve.

### Anatomy of a portable agent

```
repo/
├── .shared/agents/<agent-name>.md       # Canonical, tool-neutral agent definition
├── .cursor/agents/<agent-name>.md       # Cursor wrapper
├── .claude/agents/<agent-name>.md       # Claude Code wrapper
└── .github/agents/<agent-name>.agent.md # GitHub Copilot wrapper
```

**Progressive disclosure:** metadata (frontmatter) → shared agent body → tool-specific wrapper notes on demand.

Keep behavior that applies everywhere in `.shared/agents/<agent-name>.md`. Put tool-native integration in wrappers only. Repo-root `agents-ref/` holds reference templates, not user portable agents.

### Scaffold a new agent (project, shared-first)

**Always** use `create_agent.py` for repository projects. Do **not** hand-create agent directories or placeholder files.

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

- Shared agent path (`.shared/agents/<agent-name>.md`)
- Wrapper paths (`.cursor/`, `.claude/`, `.github/agents/<agent-name>.agent.md`)
- Assumptions made about instructions or triggers
- Whether layouts are reference wrappers or standalone copies

### Updating an existing agent

- Preserve the original `name` unless the user wants a rename
- Edit the shared agent first for cross-tool behavior; wrappers for tool-only notes or frontmatter
- Re-run `quick_validate.py` after substantive edits; sync `description` across all four files when it changes
- Re-run `create_agent.py --overwrite` only when regenerating from a new instructions file is safer than hand-editing and the user confirms

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
3. **Edit shared first** — cross-tool behavior belongs in `.shared/agents/<name>.md`
4. **Edit wrappers for tool-only gaps** — spawn mechanics, frontmatter, reload steps
5. **Explain why** — prefer reasoning over ALL-CAPS MUSTs

Re-run test prompts after edits until the user is satisfied or progress stalls.

---

## Description optimization

The `description` field drives agent discovery. After creating or improving an agent, offer to tune it.

### Shared steps (all tools)

**Step 1 — Trigger eval queries:** Draft ~10–20 realistic queries (should-trigger / should-not-trigger), concrete and edge-case heavy. Mix explicit agent requests ("use the code reviewer agent") with implicit task phrasing that should still match.

**Step 2 — User review:** Walk through queries with the user. Mark false positives (would trigger but shouldn't) and false negatives (should trigger but might not).

**Step 3 (automated — tool-specific):** Some tools support automated description loops. Follow your wrapper if documented; otherwise skip to Step 4.

**Step 4 — Apply:** Update shared agent frontmatter and sync `description` into every wrapper. Show before/after when possible.

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

1. Capture intent and scaffold with `create_agent.py`
2. Write tool-neutral shared agent body; put native execution in wrappers
3. Validate all four paths with `quick_validate.py`
4. Run realistic test prompts on the target tool (per tool wrapper)
5. Review for correctness, completeness, and efficiency
6. Improve shared agent and wrappers; sync `description` across files; re-validate
7. Repeat until satisfied; offer description optimization
