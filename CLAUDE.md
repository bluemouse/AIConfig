# CLAUDE.md

Claude Code-specific guidance for this repository. Read [AGENTS.md](AGENTS.md) first for repo layout, architecture, common scripts, and editing conventions.

## Always-on output shaping

Apply the `response-guidelines` guideline (`guidelines/response-guidelines.md`) to **every response**: lead with the result or decision, raise every ask via `AskUserQuestion` (never a question buried in prose), no preamble/recap/closers, matter-of-fact errors, close with the done/next/for-you status block, size work by shape not clock. Artifact files follow their templates and are exempt. This citation is the always-on load mechanism; the guideline is inert unless cited here.

## Discovery and reload

- **Project skills:** `.agents/skills/<name>/SKILL.md` — discovered through the `.claude/skills` bridge symlink (`.claude/skills -> ../.agents/skills`, auto-created on install)
- **Custom agents:** `.claude/agents/<name>.md` (one dual-target copy; the twin lives at `.github/agents/<name>.agent.md`)
- **Slash commands:** installed as command-skills at `.agents/skills/<name>/SKILL.md` with `disable-model-invocation: true` (installed from `commands/<name>/` bootstrap via command-creator). Available commands include `/dev-workflow` (full pipeline) and `/dev-workflow-{research,plan,implement,review}` (individual phase loops), plus `/git-commit`
- **Restart or reload** the Claude Code session after installing or editing skills, agents, or commands

## Skill and agent workflow

**Skills:** edit bootstrap under `skills/<name>/`, then install with `install_portable_skill.py`. Do not hand-edit `.agents/skills/` for bootstrapped skills — reinstall from bootstrap instead.

**Custom agents:** edit bootstrap under `agents/<name>/` when bootstrap source exists, then install with `install_portable_agent.py`. Do not hand-edit `.claude/agents/` or `.github/agents/` for bootstrapped agents — reinstall from bootstrap instead. For agents without bootstrap source, edit `.claude/agents/<name>.md` directly or regenerate with `create_agent.py`.

**Commands:** edit bootstrap under `commands/<name>/`, then install with `install_portable_command.py`. Do not hand-edit installed command-skills for bootstrapped commands — reinstall from bootstrap instead.

**Claude-specific mechanics** (subagents, reload, Cowork): edit the `### Claude Code` subsection under `## Tool notes` in the bootstrap `SKILL.md` / `AGENT.md`, then re-install from bootstrap. Edits under the installed copy alone are overwritten on the next install — copy durable changes back to the bootstrap body first.

## Running evals in Claude Code

Claude Code supports **subagents** — use the full benchmark loop in `.agents/skills/skill-creator/SKILL.md`.

Key rules:

- Spawn with-skill and baseline subagents in the **same turn** per test case
- Write `eval_metadata.json` and `timing.json` when completion data is available
- Grade with `.agents/skills/skill-creator/agents/grader.md`
- **Always** launch the eval viewer (`skills/skill-creator/eval-viewer/generate_review.py`) and show results to the human before revising the skill
- Read `feedback.json` when the user finishes review

For description optimization after content is stable, use `run_loop.py` from `skills/skill-creator/scripts/` (see the skill-creator skill's Claude Code Tool notes).

## Cowork / headless Claude Code

- Subagents work; fall back to serial runs if timeouts are severe
- No browser: use `skills/skill-creator/eval-viewer/generate_review.py --static <path>` and share the link; feedback downloads as `feedback.json`
- `run_loop.py` works (uses `claude -p`, not a browser)

## Claude.ai (no Claude Code CLI)

If you are on Claude.ai rather than Claude Code: no subagents, no `run_loop.py`. Run test prompts sequentially, skip baselines and quantitative benchmarks, and use manual description optimization only.

## Updating skills in read-only environments

Copy to `/tmp/<skill-name>/`, edit, validate, package, then copy artifacts back if needed.
