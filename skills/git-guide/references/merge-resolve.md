# merge-resolve: Simple Merge/Rebase Conflict Triage

## Guideline

Detect, classify, and resolve **simple mechanical** merge/rebase conflicts. Stage the
result and validate with project checks. Do **not** create merge/rebase completion commits
during an active integration — hand off final commits to
[commit.md](commit.md) and [commit-message-writer](../../commit-message-writer/SKILL.md).

For semantic, API, behavioral, multi-file, or integration-verification work, hand off to
[../../git-merge-guide/SKILL.md](../../git-merge-guide/SKILL.md).

## Scope

| In scope (`git-guide`) | Out of scope → `git-merge-guide` |
| --- | --- |
| Lockfile, import, formatting, or obvious pick-ours/theirs | Function bodies, types, API contracts, behavioral logic |
| Single-file mechanical triage | Multi-file architectural conflicts |
| Stage resolved files during active merge/rebase | Integration review, affected-test verification, merge reports |
| Final merge commit **after** integration is already staged | End-to-end integration from conflict markers through verification |

## Rationale

Simple conflicts like import lists and lockfiles can be resolved mechanically. Semantic
conflicts need intent reconstruction and combined-tree review — that belongs to
`git-merge-guide`.

During an active merge or rebase, this skill resolves and stages only. Creating the merge
commit or finishing a rebase sequence after complex integration is separate mechanics
once the tree is correct and staged.

## Example: simple lockfile conflict

```bash
# Detect conflicts
$ git status --porcelain
UU package-lock.json

# Mechanical resolution — merge dependency versions or regenerate lockfile
# Validate with project checks
$ <project install or typecheck command>

# Stage only — no commit during active merge/rebase integration
$ git add package-lock.json
$ git rebase --continue    # or leave staged for git-merge-guide / final commit step
```

## Example: hand off semantic conflict

```bash
$ git status --porcelain
UU src/services/auth.ts
UU src/services/auth.test.ts

# Multi-file behavioral conflict — stop triage here
# Hand off to git-merge-guide for semantic resolution and verification
```

## Example: final merge commit (integration already staged)

When merge conflicts are resolved, files are staged, and the user asks to finish the
merge commit:

```bash
$ git status
All conflicts fixed but you are still merging.

$ git commit -m "<user-supplied or pre-drafted message>"
```

Use [commit-message-writer](../../commit-message-writer/SKILL.md) when the user needs
message drafting.

## Techniques

- Detect conflicts via `git status --porcelain` (UU, AA, DD markers)
- Classify as **simple** (auto-resolvable: lockfiles, imports, formatting, obvious
  pick-ours/theirs) or **complex** (functions, types, logic, multi-file behavior)
- Auto-resolve imports by merging lists; lockfiles by regenerate or newer-version policy;
  additions by including both when safe
- For complex conflicts: **stop** and hand off to
  [../../git-merge-guide/SKILL.md](../../git-merge-guide/SKILL.md) — do not guess semantic
  intent here
- Validate with the project's typecheck/lint/build commands before staging — discover them
  from `package.json` scripts, `Makefile`, `CMakeLists.txt` + CTest, `build.gradle.kts`
  + `check`, or repo docs; do not assume `npm`
- Stage resolved files with `git add` only after validation passes
- During active merge/rebase: **stage only** — do not run `git commit` unless the user
  explicitly wants the final merge commit and integration is complete
