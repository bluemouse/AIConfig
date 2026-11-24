---
name: skill-creator
description: "Create, evaluate, and iteratively improve portable skills for GitHub Copilot and Claude Code using the single-root layout (bootstrap under skills/ and install to .agents/skills/). Use to author a skill from scratch, edit or benchmark an existing skill, run evals, or tune a skill description for triggering accuracy. Does not trigger on custom agents (agent-creator) or slash commands (command-creator)."
---

# Skill Creator

Flow: capture intent → choose bootstrap (`skills/<name>/`, preferred) or direct scaffold (`create_skill.py`) → write a tool-neutral `SKILL.md` body with host mechanics in `## Tool notes` → validate and install → run realistic test prompts → evaluate qualitatively/quantitatively → iterate, then tune `description`. Meet the user where they are (jump straight to eval/iterate on an existing draft, or skip formal evals if they want a quick pass); preserve user-supplied exact wording **verbatim**.

Shared authoring rules — bootstrap vs direct choice, authoritative-edit rule, intake, manual description tuning, output summary, and the iterate loop — live in [references/creation-common.md](references/creation-common.md); this file carries only the skill-specific delta.

## When NOT to Use

- **Creating a custom agent** → [../agent-creator/SKILL.md](../agent-creator/SKILL.md)
- **Creating a slash command or Copilot prompt** → [../command-creator/SKILL.md](../command-creator/SKILL.md)

---

## Creating a skill

### Intake and edit paths

Follow [references/creation-common.md](references/creation-common.md). Skill-specific intake: target capability, trigger phrases, output format, per-host `## Tool notes` (eval/reload mechanics), and whether objective test cases are warranted. Edit bootstrap skills in `skills/<name>/` and reinstall via `install_portable_skill.py` (never hand-edit `.agents/skills/<name>/` when bootstrap exists); runtime discovery always reads `.agents/skills/<name>/`.

### Bundled scripts

`<SKILL_CREATOR_ROOT>` is the directory containing **this** skill's `SKILL.md`; `<SKILL_ROOT>` is the installed target skill's directory.

- **Module form** (`python -m scripts.<name>` from `<SKILL_CREATOR_ROOT>`): `quick_validate`, `aggregate_benchmark`, `run_eval`, `improve_description` (plus `eval-viewer/generate_review.py` by path).
- **Direct form** (`python <SKILL_CREATOR_ROOT>/scripts/<name>.py` — flat sibling imports): `install_portable_skill`, `create_skill`, `init_skill`, `package_skill`.

### Anatomy, frontmatter, and installation

Installed single-root layout: `.agents/skills/<skill-name>/` (`SKILL.md` + optional `scripts/`, `references/`, `assets/`), read directly by GitHub Copilot and via the `.claude/skills -> ../.agents/skills` symlink by Claude Code (layout/examples/checklist in `references/portable-skill-layout.md`).

- **Progressive disclosure:** frontmatter (`name` kebab-case ≤64 chars; `description` ≤1,024 chars with no `<`/`>`, stating both **what** the skill does and **when** to trigger; optional `compatibility`) → lean tool-neutral `SKILL.md` body → `## Tool notes` H2 + on-demand `references/` and `scripts/`.
- **Bootstrap:** author `skills/<skill-name>/SKILL.md` (resolving `<SKILL_ROOT>` for bundled paths), then validate and install:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/install_portable_skill.py \
  --root <repo_root> --name <skill-name> --source skills/<skill-name> --overwrite
```

- **Direct / standalone:** scaffold into `.agents/skills/` via `create_skill.py --root <repo_root> --name <skill-name> --overwrite`, or standalone via `init_skill.py <skill-name> --path <skills-root>` (flat skills root only — category subfolders are rejected).

---

## Test prompts and evaluation

Draft 2–3 realistic prompts with expected behavior and efficiency signals, confirm with the user, and save to `skills/<skill-name>/evals/evals.json` (or `.agents/skills/<skill-name>/evals/evals.json` on the direct path) per `references/schemas.md`. Read `references/schemas.md` before running a full eval:

- Complete the planned iteration without stopping midway or invoking unrelated testing skills.
- Cap eval-loop concurrency self-contained: ≤4 with-skill/baseline pairs = 8 short-lived read-only subagents in flight (the host-safe ceiling; lower if the host requires) and spawn each case's with-skill + baseline (`without_skill/` or snapshotted `old_skill/`) in the **same turn**.
- Grade with `agents/grader.md` → `grading.json`; aggregate with `python -m scripts.aggregate_benchmark` (pass `--primary/--baseline` explicitly when >2 arms exist); analyze with `agents/analyzer.md` (and `agents/comparator.md` for optional blind A/B comparison); then launch the viewer (`--previous-workspace` on iteration 2+) and show the user **before** revising.
- Record infra failures via `run_status.json` (`{"status": "completed"|"errored"|"timeout"}`); read `feedback.json` when done, stop any viewer server, and never eval on a dirty tree (clean up residue after runs).
- Iterate on correctness, completeness, and efficiency per [references/creation-common.md](references/creation-common.md) into `iteration-<N+1>/`.

---

## Simplification and retirement decisions

When trimming, simplifying, or retiring guidance, compare frozen, hashed arms rather than arguing from length alone:

1. **Arms:** `baseline` (target removed), `current` (today's bytes), `candidate` (proposed simplification).
2. **Order:** grade correctness and safety first, efficiency only when correctness holds on paired cases.
3. **Pairing & uncertainty:** pair by task and repeat; treat missing/errored runs as incomplete (never a pass), and report small-sample ties as uncertain rather than equivalent.
4. **Scope:** report the exact tested host/model (plus consumer/cross-link impact when retiring a skill on a new model release).

---

## Description optimization and packaging

Description tuning uses the subagent-driven loop in `## Tool notes` (the scripts never spawn a CLI). Follow [references/creation-common.md](references/creation-common.md) + `references/description-eval-queries.md`, and use `assets/eval_review.html` (`__EVAL_DATA_PLACEHOLDER__`, `__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`) to review results.

Package an installed skill after validation:

```bash
python <SKILL_CREATOR_ROOT>/scripts/quick_validate.py .agents/skills/<skill-name>
python <SKILL_CREATOR_ROOT>/scripts/package_skill.py .agents/skills/<skill-name>
```

---

## Tool notes

### Subagent-driven description optimization (all hosts)

The scripts build prompts and score answers; the host agent does the model calls. Use native subagents when available. Each subagent gets a fresh context and answers one task only, so no subagent sees another's answer. The trigger result is a proxy: it shows whether a model would route the query to the description, not Claude Code's real routing.

1. **Trigger eval.** Run `python -m scripts.run_eval --eval-set <trigger-eval.json> --skill-path <SKILL_ROOT> --emit-tasks tasks.json`. Dispatch each task's `prompt` to its own no-tools subagent, one per task. Save the answers as `responses.json` (task id → answer text). Then run `python -m scripts.run_eval --eval-set <trigger-eval.json> --skill-path <SKILL_ROOT> --score tasks.json --responses responses.json > results.json`. A query with a missing or unparseable answer is listed under `summary.incomplete` and is never counted as a pass; re-dispatch those tasks and score again.
Use `[]` as `history.json` on the first round.
2. **Improve.** Run `python -m scripts.improve_description --eval-results results.json --skill-path <SKILL_ROOT> --history history.json --emit-prompt improve.txt`. Dispatch `improve.txt` to one subagent, save its reply to `reply.txt`, and run `python -m scripts.improve_description --eval-results results.json --skill-path <SKILL_ROOT> --history history.json --response reply.txt > next.json`. If `over_limit` is true in `next.json`, dispatch its `shorten_prompt` and parse the new reply the same way. Use `next.json`'s `history` as the next `history.json`.
3. Repeat steps 1–2 up to about 5 rounds, then pick the best description by train score. Confirm the final description with one more trigger eval before shipping.

Step 1 scoring uses `--trigger-threshold` (default 0.5). A should-trigger query passes when its trigger rate is at least the threshold; a should-not query passes when it is below it.

### Claude Code

Supports **subagents**: run the parallel with-skill + baseline eval loop, then the subagent-driven description optimization above.

- **Cowork / headless:** subagents work; pass `generate_review.py --static <path>` (before self-grading) when no browser is available.
- **Claude.ai (no CLI, no subagents):** run prompts sequentially inline and tune descriptions manually.

### GitHub Copilot

- **Agent surfaces with concurrent subagent/task dispatch** (e.g. VS Code Copilot agent/SDK): run independent with-skill + baseline eval pairs concurrently per **Test prompts and evaluation**, saving artifacts under `<workspace>/iteration-1/eval-<ID>/` and generating `<workspace>/<skill-name>-review.html` via `eval-viewer/generate_review.py --static` when Python is available. Then use the subagent-driven description optimization above.
- **Single-session chat surfaces** (no subagent dispatch): run a **qualitative, sequential** loop — write `evals/evals.json` and `eval_metadata.json`, send each prompt sequentially in chat (saving file outputs under `with_skill/outputs/`), optionally compare informally in a fresh session without the skill (`without_skill/outputs/`), and review in chat or via `generate_review.py --static <workspace>/<skill-name>-review.html` (skip `aggregate_benchmark` unless both arms exist). Tune descriptions manually.
