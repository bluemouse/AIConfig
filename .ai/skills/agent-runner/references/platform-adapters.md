# Platform adapters

Host-specific dispatch mechanics live in your **tool wrapper** — read it after the shared skill. This file defines the common contract and capability checks that apply on every host.

Select the native concurrency mechanism that is actually available in the current host. Tool names and UI labels can change; inspect the exposed tools rather than assuming a command exists.

## Common contract

The host adapter must support all of these:

1. Create multiple isolated agent sessions or tasks.
2. Submit all task packets without waiting for earlier packets to finish.
3. Associate each result with its packet.
4. Preserve separate context for every subagent.

If the available feature cannot satisfy this contract, report that concurrent isolated dispatch is unavailable. Do not emulate it with sequential prompts.

## Capability detection

Before dispatching:

- inspect available tools for agent, subagent, task, session, worktree, sandbox, or branch primitives
- prefer a documented native primitive over shelling out to another assistant
- verify whether multiple calls in one turn are concurrent
- verify whether isolation is automatic or must be configured
- avoid undocumented flags or invented tool names

## Repository instruction precedence

Load and obey host and repository instructions before creating packets. Common locations include:

- `CLAUDE.md` and nested Claude instruction files
- `.cursor/rules/`, `.cursorrules`, or project Cursor instructions
- `.github/copilot-instructions.md`, `AGENTS.md`, and custom agent definitions

More specific repository instructions override generic recommendations in this skill unless they would violate the user's explicit request or safety constraints.
