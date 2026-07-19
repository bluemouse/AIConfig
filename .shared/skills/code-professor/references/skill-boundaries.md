# Skill boundaries and handoffs

Use this reference when the user's request could match more than one workflow skill. Prefer the skill whose **terminal output** matches what the user asked for.

## Routing matrix

| User goal | Primary skill | Terminal output | Not this skill when |
| --- | --- | --- | --- |
| Learn, explain, or document existing code | **code-professor** | Evidence-backed guide (orientation, module, trace, or failure investigation) | Output is a diff review, research report, implementation plan, or verified fix |
| Fix a defect with minimal verified repair | [debugging-guide](../../debugging-guide/SKILL.md) | Root cause + patch + passing verification | User only wants a teaching document or ranked hypotheses |
| Review git diffs or commits | [code-reviewer](../../code-reviewer/SKILL.md) | Findings-first review report | User wants open-ended codebase learning without a change set |
| Research product ideas, requirements, or specs | [research-guide](../../research-guide/SKILL.md) | Agreed research report | User wants to understand how existing code works |
| Author or repair an implementation plan | [plan-guide](../../plan-guide/SKILL.md) | Executable TDD-first plan | User wants a learning guide, not a task breakdown |
| Execute an approved plan | [plan-executor](../../plan-executor/SKILL.md) | Implementation report | User wants to study code without implementing |
| Audit a research report | [research-reviewer](../../research-reviewer/SKILL.md) | Research review report | User wants a codebase architecture guide |
| Audit an implementation plan | [plan-reviewer](../../plan-reviewer/SKILL.md) | Plan review + Guide handoff | User wants repository onboarding |
| Optimize C/C++ performance with measurements | [cpp-performance-guide](../../cpp-performance-guide/SKILL.md) | Benchmark-driven optimization report | User wants to understand performance-related code paths without optimizing |

## Overlap resolutions

### code-professor vs debugging-guide

Both can investigate failures. Choose by **primary outcome**:

- **code-professor**: teach — reproduction, path trace, evidence, ranked hypotheses, optional **candidate fix** documented as a proposal. **Does not apply production fixes.**
- **debugging-guide**: repair — iron rule (symptom → root cause → evidence → failing test → minimal fix → verify).

Phrases like "investigate this crash", "why does this fail", or "explain this regression" → **code-professor** unless the user clearly wants a patch applied ("fix", "repair", "apply minimal fix", "verify the fix").

After a failure investigation guide, hand off to **debugging-guide** when the user asks to implement or verify a repair.

### code-professor vs plan-guide

Both may read the codebase. Choose by **terminal output**:

- **code-professor**: learning artifact — mental model, reading path, traced workflow, documented invariants.
- **plan-guide**: execution artifact — ordered tasks, TDD specs, verification commands, file targets.

"Explore the codebase and turn this feature ask into a **plan**" → **plan-guide**.  
"Teach me how the **auth module** works" → **code-professor**.

When **plan-guide** is discovery-gated, it may inspect code narrowly to unblock planning. That inline inspection is not a substitute for **code-professor** when the user wants a durable learning guide.

After orientation or a module deep dive, hand off to **plan-guide** when the user wants to implement a change.

### code-professor vs research-guide

Both may mention architecture. Choose by **subject**:

- **research-guide**: unsettled product/requirements — alternatives, scope, acceptance criteria, agreement gates.
- **code-professor**: settled implementation — what the repository **already does**, with `path:line` evidence.

"Brainstorm requirements for notifications" → **research-guide**.  
"How does the notification pipeline work in this repo?" → **code-professor**.

**research-guide** may inspect the codebase for feasibility claims; **code-professor** produces the full learning document when understanding the code is the goal.

### code-professor vs code-reviewer

- **code-reviewer** requires a **change set** (staged, unstaged, branch, commit, or range).
- **code-professor** studies **baseline code** to teach structure, behavior, or failure paths.

"Review my branch before I push" → **code-reviewer**.  
"Explain this module so I can change it safely" → **code-professor** (then **code-reviewer** after edits if asked).

### code-professor vs cpp-performance-guide

- **Failure investigation** for slow or flaky performance symptoms → **code-professor** (failure investigation deliverable).
- **Optimization** with profiling, benchmarks, and measured improvements → **cpp-performance-guide**.

"Why is this path slow?" (learning) → **code-professor**.  
"Profile and optimize this hot loop" → **cpp-performance-guide**.

## Typical handoff chains

```
Onboard → change code:
  code-professor (orientation) → plan-guide → plan-executor → code-reviewer

Understand module → fix bug:
  code-professor (module or failure guide) → debugging-guide → code-reviewer

Research feature → implement:
  research-guide → research-reviewer → plan-guide → plan-executor
  (code-professor optional when planner or user needs codebase literacy first)
```

## Upstream inputs code-professor accepts

- User question about the repository (most common)
- Pointers from **plan-guide** when discovery-gated ("inspect codebase" expanded into a learning guide — only when the user agrees)
- Follow-up after **research-guide** when feasibility work needs a code-grounded architecture map — only when understanding existing code is explicitly requested

## Downstream skills code-professor defers to

| User next asks for | Skill |
| --- | --- |
| Verified fix | [debugging-guide](../../debugging-guide/SKILL.md) |
| Implementation plan | [plan-guide](../../plan-guide/SKILL.md) |
| Execute plan | [plan-executor](../../plan-executor/SKILL.md) |
| Diff review | [code-reviewer](../../code-reviewer/SKILL.md) |
| Product/requirements research | [research-guide](../../research-guide/SKILL.md) |
| Stack-specific implementation | Domain skills (e.g. [cpp-coding](../../cpp-coding/SKILL.md), [python-coding](../../python-coding/SKILL.md)) |
