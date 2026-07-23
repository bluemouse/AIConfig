# CLAUDE.md

Claude Code-specific guidance for this repository. Read [AGENTS.md](AGENTS.md) first for repo layout, architecture, common scripts, and editing conventions.

## Discovery and reload

- **Project skills:** `.claude/skills/<name>/SKILL.md` (wrapper) + `.shared/skills/<name>/` (shared content)
- **Custom agents:** `.claude/agents/<name>.md` (wrapper) + `.shared/agents/<name>.md` (shared content)
- **Slash commands:** `.claude/commands/<name>.md` (installed from `commands/<name>/` bootstrap via command-creator)
- **Restart or reload** the Claude Code session after installing or editing skills, agents, or commands

When a tool skill wrapper says to read the shared skill first, resolve paths from `.shared/skills/<name>/` — not from `.claude/skills/<name>/`.

## Skill and agent workflow

**Skills:** edit bootstrap under `skills/<name>/`, then install with `install_portable_skill.py`. Do not hand-edit `.shared/skills/` or `.claude/skills/` — reinstall from bootstrap instead.

**Custom agents:** edit bootstrap under `agents/<name>/` when bootstrap source exists, then install with `install_portable_agent.py`. Do not hand-edit `.shared/agents/` or `.claude/agents/` for bootstrapped agents — reinstall from bootstrap instead. For agents without bootstrap source, edit `.shared/agents/<name>.md` directly or regenerate with `create_agent.py`.

**Commands:** edit bootstrap under `commands/<name>/`, then install with `install_portable_command.py`. Do not hand-edit `.shared/commands/` or `.claude/commands/` for bootstrapped commands — reinstall from bootstrap instead.

**Claude-only wrapper mechanics** (subagents, reload, Cowork): edit `skills/<name>/wrappers/claude/SKILL.md`, then re-install from bootstrap. Edits under `.claude/skills/<name>/` alone are overwritten on the next install — copy durable changes back to the bootstrap wrapper first.

When a wrapper and the shared skill disagree on mechanics, follow the **Claude wrapper** for Claude Code execution.

## Running evals in Claude Code

Claude Code supports **subagents** — use the full benchmark loop in `.shared/skills/skill-creator/SKILL.md` and `.claude/skills/skill-creator/SKILL.md`.

Key rules:

- Spawn with-skill and baseline subagents in the **same turn** per test case
- Write `eval_metadata.json` and `timing.json` when completion data is available
- Grade with `.shared/skills/skill-creator/agents/grader.md`
- **Always** launch the eval viewer (`skills/skill-creator/eval-viewer/generate_review.py`) and show results to the human before revising the skill
- Read `feedback.json` when the user finishes review

For description optimization after content is stable, use `run_loop.py` from `skills/skill-creator/scripts/` (see the Claude skill-creator wrapper).

## Cowork / headless Claude Code

- Subagents work; fall back to serial runs if timeouts are severe
- No browser: use `skills/skill-creator/eval-viewer/generate_review.py --static <path>` and share the link; feedback downloads as `feedback.json`
- `run_loop.py` works (uses `claude -p`, not a browser)

## Claude.ai (no Claude Code CLI)

If you are on Claude.ai rather than Claude Code: no subagents, no `run_loop.py`. Run test prompts sequentially, skip baselines and quantitative benchmarks, and use manual description optimization only.

## Updating skills in read-only environments

Copy to `/tmp/<skill-name>/`, edit, validate, package, then copy artifacts back if needed.
