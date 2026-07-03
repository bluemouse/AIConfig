---
name: skill-creator
description: Create new Cursor agent skills, improve existing skills, validate structure, and package skills for sharing. Use when the user wants to author a SKILL.md, scaffold a skill folder, refine a skill description for better triggering, validate frontmatter, package a .skill file, or iterate on skill quality through manual testing in Cursor.
---

# Skill Creator

A skill for creating and improving **Cursor agent skills**.

At a high level:

1. Decide what the skill should do and when the Cursor agent should use it
2. **Scaffold** with `init_skill.py` (never create skill folders manually)
3. **Validate** immediately with `quick_validate.py`, then edit the draft
4. Test in Cursor with realistic prompts
5. Improve based on user feedback
6. Re-validate and package with `package_skill.py` when ready

Figure out where the user is in this loop and help them move forward. If they only want a quick draft without formal testing, follow their preference.

---

## Cursor specifics

### Install locations

| Scope | Path |
| --- | --- |
| Project (recommended) | `.cursor/skills/<skill-name>/` |
| Personal | `~/.cursor/skills/<skill-name>/` |

**Never** create user skills in `~/.cursor/skills-cursor/` — that directory is reserved for Cursor's built-in skills.

The skill directory name must match the `name` field in frontmatter (kebab-case).

After adding or editing a skill, reload the Cursor window so the agent rediscovers skills.

### Skills vs rules vs commands

| Asset | Location | Purpose |
| --- | --- | --- |
| **Skills** | `.cursor/skills/` | Specialized workflows loaded when relevant |
| **Rules** | `.cursor/rules/` | Persistent guidance via globs or `alwaysApply` |
| **Commands** | `.cursor/commands/` | User-invoked slash commands |

Use a **skill** when the agent needs a multi-step workflow, bundled scripts, or domain playbooks. Use a **rule** for always-on or file-scoped conventions. Use a **command** when the user explicitly invokes a named action.

### How triggering works

Cursor loads skill **metadata** (`name` + `description`) into the agent's available skills list. The agent reads and follows a skill when the user's task matches the description.

Practical implications:

- Put **what** the skill does and **when** to use it in `description`, not buried in the body
- Write descriptions in **third person** (they are injected into the system prompt)
- Include trigger phrases, file types, domains, and adjacent scenarios
- Skills can be under-triggered — descriptions should be specific and slightly expansive, but stay honest
- Test with realistic, substantive prompts — not one-word requests

### Frontmatter fields

| Field | Required | Notes |
| --- | --- | --- |
| `name` | Yes | Kebab-case, max 64 chars, matches directory name |
| `description` | Yes | Max 1024 chars, no angle brackets, third person, includes WHEN |
| `disable-model-invocation` | No | If `true`, skill loads only when explicitly invoked; omit for automatic discovery |
| `license` | No | License name or reference |
| `compatibility` | No | Environment requirements, max 500 chars |
| `metadata` | No | Arbitrary key-value map |
| `allowed-tools` | No | Space-separated pre-approved tools (when supported) |

Run `scripts/quick_validate.py` to check frontmatter before packaging.

---

## Communicating with the user

Users may range from expert developers to people new to the terminal. Match their vocabulary. Briefly explain terms like "frontmatter" or "kebab-case" when unsure they know them.

If the user provides exact wording for the skill, use it **verbatim** in `SKILL.md`.

---

## Creating a skill

### Capture intent

Start by understanding intent. If the current conversation already shows a workflow to capture, extract steps, tools, corrections, and output formats from history first. Confirm gaps with the user.

Ask:

1. What should this skill enable the Cursor agent to do?
2. When should it trigger? (phrases, file types, contexts)
3. Project skill (`.cursor/skills/`) or personal skill (`~/.cursor/skills/`)?
4. What output format is expected?
5. Should you set up test prompts? Objective outputs benefit from test cases; subjective outputs often need qualitative review only.

### Interview and research

Ask about edge cases, input/output formats, example files, success criteria, and dependencies before writing test prompts.

Use available tools (search, docs, repo exploration, MCP) to reduce burden on the user.

### Bundled scripts

Resolve `<SKILL_CREATOR_ROOT>` as the directory containing **this** skill's `SKILL.md` (the installed `skill-creator` folder). Use these paths — do not guess or invent alternatives:

| Script | Path |
| --- | --- |
| Scaffold | `<SKILL_CREATOR_ROOT>/scripts/init_skill.py` |
| Validate | `<SKILL_CREATOR_ROOT>/scripts/quick_validate.py` |
| Package | `<SKILL_CREATOR_ROOT>/scripts/package_skill.py` |

If this skill lives at `.cursor/skills/skill-creator/`, then `<SKILL_CREATOR_ROOT>/scripts/init_skill.py` is `.cursor/skills/skill-creator/scripts/init_skill.py`.

### Scaffold a new skill

**Always** scaffold with `init_skill.py`. Do **not** manually create skill directories, `SKILL.md`, or placeholder `scripts/` / `references/` / `assets/` folders.

1. Confirm target from the interview:
   - **Project**: `.cursor/skills/`
   - **Personal**: `~/.cursor/skills/`

2. Run (replace `<skill-name>` and `<install-path>`):

```bash
python <SKILL_CREATOR_ROOT>/scripts/init_skill.py <skill-name> --path <install-path>
```

Example for a project skill in this repository:

```bash
python .cursor/skills/skill-creator/scripts/init_skill.py my-skill --path .cursor/skills
```

3. **Immediately** validate the scaffold before editing content:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py <install-path>/<skill-name>
```

4. Edit the generated `SKILL.md`, remove unused placeholder files, then **re-run** `quick_validate.py` after substantive edits and before packaging.

### Write the SKILL.md

Based on the interview, fill in:

- **name**: Skill identifier (matches directory)
- **description**: Primary triggering mechanism — third person, what + when
- **disable-model-invocation**: Set `true` only if the skill should run when explicitly named, not auto-discovered
- **Body**: Instructions, workflows, examples, pointers to bundled resources

#### Anatomy of a skill

```
skill-name/
├── SKILL.md          # Required: frontmatter + instructions
├── scripts/          # Optional: executable helpers
├── references/       # Optional: docs loaded on demand
├── assets/           # Optional: templates/files used in output
└── evals/            # Optional: test prompts (excluded from .skill packages)
    └── evals.json
```

#### Progressive disclosure

1. **Metadata** — always in context (~100 words)
2. **SKILL.md body** — loaded when the skill triggers (<500 lines ideal)
3. **Bundled resources** — loaded or executed as needed

Patterns:

- Keep `SKILL.md` focused; move long reference material to `references/`
- Link clearly from `SKILL.md` to reference files and when to read them
- Keep references **one level deep** from `SKILL.md`
- For files >300 lines, add a table of contents
- For multiple domains, use separate reference files (e.g., `references/aws.md`, `references/gcp.md`)

See `references/workflows.md` and `references/output-patterns.md`.

#### Principle of lack of surprise

Skills must not contain malware, exploit code, or content that compromises security. Do not create misleading skills or skills for unauthorized access or data exfiltration.

#### Writing style

- Prefer imperative instructions
- Explain **why** important steps matter instead of heavy-handed MUST/NEVER unless safety requires it
- Generalize patterns; avoid overfitting to one example
- Use forward slashes in paths (`scripts/helper.py`), not Windows backslashes
- Choose consistent terminology throughout
- Draft, then revise with fresh eyes

**Description example (good):**

```yaml
description: Analyze Excel spreadsheets, create pivot tables, and generate charts. Use when working with .xlsx files, spreadsheet analysis, tabular data, pivot tables, or when the user mentions Excel, CSV exports, or workbook formulas.
```

**Description example (bad):**

```yaml
description: Helps with spreadsheets.
```

#### Anti-patterns

- Vague names like `helper`, `utils`, `tools`
- Too many equivalent library options without a default
- Time-sensitive instructions that will go stale
- Windows-style paths (`scripts\helper.py`)

---

## Testing and improving

Cursor does not include Claude Code's automated subagent benchmark pipeline. Use a **manual review loop** in Cursor agent mode.

### Step 1: Define test prompts

Create 2–3 realistic prompts — what a real user would type in Cursor Chat. Optionally save them in `evals/evals.json` (see `references/schemas.md`).

Share with the user: "Here are test cases I'd like to try. Do these look right?"

### Step 2: Run tests in Cursor

For each prompt:

1. Ensure the skill is installed under `.cursor/skills/<skill-name>/` (or `~/.cursor/skills/`)
2. Reload the Cursor window or start a fresh agent session
3. Run the prompt in **agent mode**
4. Confirm the skill was loaded (check that instructions were followed)
5. Save outputs the user needs to inspect (files, diffs, summaries)

If the skill does not trigger, revise the `description` before changing the body.

**Optional:** For rigorous comparison, use Cursor's Task/subagent tools to run the same prompt with and without the skill, then compare outputs with the user. This is optional — human review is usually enough.

### Step 3: Review with the user

Present each result in conversation:

- The prompt used
- What the agent produced
- Paths to any generated files
- Your assessment against expectations (if defined)

Ask what to change. Record notes in `feedback.json` or `iteration-notes.md` if helpful.

### Step 4: Improve the skill

When revising:

1. **Generalize from feedback** — fix root causes, not single-example quirks
2. **Keep the skill lean** — remove instructions that do not help
3. **Explain the why** — the agent follows reasoning better than rigid caps-lock rules
4. **Bundle repeated work** — if every test run reinvented the same script, add it to `scripts/`

Repeat until the user is satisfied or feedback is consistently positive.

### Optional: description tuning

After the skill works well, offer to tune the description:

1. Draft 8–10 **should-trigger** queries (varied phrasing, realistic detail)
2. Draft 8–10 **should-not-trigger** near-misses (adjacent but wrong domain)
3. Test in Cursor — note false negatives and false positives
4. Update `description` and retest

Good negative cases are genuinely tricky — not obviously unrelated topics.

---

## Validate and package

Run validation from `<SKILL_CREATOR_ROOT>/scripts/`. **Always** pass validation before packaging.

### Validate

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py <install-path>/<skill-name>
```

Example:

```bash
python .cursor/skills/skill-creator/scripts/quick_validate.py .cursor/skills/my-skill
```

Requires Python 3 and `PyYAML` (`pip install pyyaml`).

### Package

Only after `quick_validate.py` passes:

```bash
python <SKILL_CREATOR_ROOT>/scripts/package_skill.py <install-path>/<skill-name> ./dist
```

Example:

```bash
python .cursor/skills/skill-creator/scripts/package_skill.py .cursor/skills/my-skill ./dist
```

Produces `dist/my-skill.skill` (zip archive) after validation. The `evals/` directory is excluded from packages.

### Install elsewhere

Copy the skill folder into another repo's `.cursor/skills/` or a user's `~/.cursor/skills/`.

---

## Updating an existing skill

When editing an installed skill:

- **Preserve the original `name`** and directory name
- Edit in the project skill path (e.g., `.cursor/skills/<name>/`)
- Revalidate and retest after changes
- If the installed path is read-only, copy to a writable location, edit, then copy back

---

## Reference files

| File | Purpose |
| --- | --- |
| `references/workflows.md` | Sequential, conditional, and feedback-loop patterns |
| `references/output-patterns.md` | Templates and example formatting patterns |
| `references/schemas.md` | Optional eval and feedback JSON schemas |
| `scripts/init_skill.py` | Scaffold a new skill directory |
| `scripts/quick_validate.py` | Validate frontmatter and naming rules |
| `scripts/package_skill.py` | Package a validated skill into `.skill` |

---

## Quick checklist

- [ ] Scaffolded with `init_skill.py` (not created manually)
- [ ] `name` matches directory, kebab-case, ≤64 chars
- [ ] `description` is third person, states what + when, ≤1024 chars, no `>` or `<`
- [ ] Body is focused; long content in `references/`
- [ ] Scripts are referenced from `SKILL.md` with clear usage
- [ ] Not installed under `~/.cursor/skills-cursor/`
- [ ] Validated with `quick_validate.py` immediately after scaffold and before packaging
- [ ] Tested with realistic prompts in Cursor agent mode
- [ ] Packaged with `package_skill.py` if sharing
