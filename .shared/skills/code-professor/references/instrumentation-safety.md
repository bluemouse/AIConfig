# Temporary instrumentation safety

Temporary code edits are an investigative technique, not a shortcut around static analysis. Use them only when existing diagnostics, tests, debuggers, or tracing cannot answer the question efficiently.

Resolve `<SKILL_ROOT>` as the directory containing the shared `code-professor` skill's `SKILL.md`.

## Reversible experiment protocol

1. Inspect `git status --short` and record pre-existing changes.
2. Choose the smallest possible set of files.
3. Create a snapshot outside the repository before editing:

```bash
STATE_DIR="${TMPDIR:-/tmp}/code-professor-$$"
python "<SKILL_ROOT>/scripts/instrumentation_guard.py" begin \
  --repo "$PWD" --state-dir "$STATE_DIR" -- path/to/file1 path/to/file2
```

Replace `<SKILL_ROOT>` with the absolute path to the installed shared skill directory (e.g. `.shared/skills/code-professor/` after install, or `skills/code-professor/` during bootstrap development).

4. Add minimal instrumentation marked `CODE_PROFESSOR_TEMP`.
5. Do not log credentials, secrets, tokens, private payloads, or unnecessary user data.
6. Run a focused experiment and capture only the evidence needed.
7. Restore exact contents, symlink targets, and file modes:

```bash
python "<SKILL_ROOT>/scripts/instrumentation_guard.py" restore \
  --state-dir "$STATE_DIR"
```

8. Verify guarded paths:

```bash
python "<SKILL_ROOT>/scripts/instrumentation_guard.py" verify \
  --state-dir "$STATE_DIR"
```

9. Inspect `git status --short` and targeted diffs against the original baseline.
10. Remove the external snapshot only after verification succeeds:

```bash
python "<SKILL_ROOT>/scripts/instrumentation_guard.py" cleanup \
  --state-dir "$STATE_DIR"
```

## Safety rules

- Never snapshot the entire repository when only a few files will change.
- Never restore with broad Git commands that could erase user work.
- Do not overwrite an existing snapshot for a path; the script preserves the first captured state.
- Do not instrument generated, vendored, or third-party code unless that code is the target of the investigation.
- Avoid persistent schema changes, migrations, external writes, network side effects, and destructive tests.
- Use a safe local or test environment for experiments that can mutate data or external systems.
- If another process or user edits a guarded file during the experiment, stop and explain the conflict before restoration.
- If verification fails, keep the snapshot and report the exact paths and differences.
