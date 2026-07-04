# Create agent-creator

Install the **agent-creator** meta-skill into this repository's portable layout so it is available in Cursor, GitHub Copilot, and Claude Code.

## What to do

1. Confirm the workspace root is the repository root (where `.cursor/`, `.shared/`, and `skills/` live).

2. Run the install script from the repository root:

```bash
python skills/skill-creator/scripts/install_portable_skill.py \
  --root . \
  --name agent-creator \
  --source skills/agent-creator \
  --overwrite
```

3. If the script exits with code 0, report success with these paths:
   - **Shared skill (canonical):** `.shared/skills/agent-creator/`
   - **Cursor wrapper:** `.cursor/skills/agent-creator/SKILL.md`
   - **Claude Code wrapper:** `.claude/skills/agent-creator/SKILL.md`
   - **GitHub Copilot wrapper:** `.github/skills/agent-creator/SKILL.md`
   - **Bootstrap source (unchanged):** `skills/agent-creator/` — used for future updates and re-installs

4. Tell the user to reload their tools so the skill is discovered:
   - **Cursor:** reload the window
   - **VS Code + Copilot:** reload the window
   - **Claude Code:** restart or reload the session

## On failure

- Print the script's stderr/stdout.
- Do **not** claim the install succeeded.
- If validation failed, list which path failed and suggest re-running with `--overwrite` if stale files exist.

## Do not

- Edit the bootstrap source at `skills/agent-creator/` during install (the script copies it).
- Manually create skill directories or wrapper files — use the script only.
