# LLM Coding Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Terminal Execution

**Run terminating commands sync. Never block on a missed completion notification.**

The agent does not actively wait — the terminal tool layer suspends the turn until a
result is ready. Stuck-agent incidents almost always trace to a terminating command run
in async mode (or backgrounded) whose early/silent exit produced no completion
notification. Follow these rules to avoid that gap:

- **Sync mode for terminating commands.** Builds, tests, lint, install, compile, git
  reads — all sync. Sync returns inline on any exit code (0 or non-zero); there is no
  "wait for notification" gap. This is the default and the strongly preferred mode.
- **Async mode only for long-running processes.** Servers, watchers, dev daemons.
  End the turn and let the completion notification arrive; do not poll, `sleep`, or
  loop on `get_terminal_output`.
- **Never background terminating commands.** No `&`, `nohup`, `disown`, or
  daemonizing wrappers for builds/tests. Backgrounding breaks exit detection — the
  parent exits but the child holds the pty, so the terminal never sees EOF and never
  considers the command finished.
- **Disable pagers and interactive readers.** Use `git --no-pager`, `GIT_PAGER=cat`,
  and pipe through `cat` (never `less`/`more`/`tail -f`). Never pipe an interactive
  prompt through `tail`/`head`/`grep` — it hides the prompt from the terminal and
  prevents the "needs input" signal from firing.
- **Prefer non-interactive flags.** `GIT_EDITOR=true`, `GIT_SEQUENCE_EDITOR=true`,
  `gh ... --body-file -`, `pip install --no-input`. Route any remaining interactive
  prompt (password, y/n confirm) to the user; never send secrets through the model.
- **Timeout as a safety net only.** Set a `timeout` for commands you suspect may hang.
  If it trips, the command moves to background — treat that as async and wait for the
  notification rather than polling.
- **If a command exits early with an error, do not keep waiting.** Sync mode returns
  the error inline; act on it. For async, if no notification arrives within a
  reasonable window, call `get_terminal_output` once to check status rather than
  ending the turn and stalling the conversation.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
