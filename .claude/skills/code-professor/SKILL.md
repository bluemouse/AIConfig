---
name: code-professor
description: "Investigate unfamiliar repositories and produce evidence-based guides for learning, tracing, and documenting code. Use when asked to understand, explain, learn, or document a repo, module, library, feature, algorithm, execution path, data flow, failure, or dev workflow; create an orientation guide, reading path, architecture map, module deep dive, workflow trace, or failure investigation guide; or find grounded improvements and candidate fixes \u2014 even without saying 'code professor' (e.g. 'teach me this codebase', 'how does this work', 'trace this request end to end', 'help me onboard'). Supports four deliverables, study depths (overview, standard, deep), and interactive mode ('guided study'). Does not trigger on diff review (code-reviewer), product/requirements research (research-guide), implementation plan authoring or execution (plan-guide, plan-executor), verified defect repair (debugging-guide), or C++ performance optimization (cpp-performance-guide)."
---

# code-professor wrapper for Claude Code

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/code-professor/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/code-professor` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Claude Code-specific information

Restart or reload the Claude Code session after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/code-professor/`.
- Keep only Claude Code-specific information in this wrapper.
