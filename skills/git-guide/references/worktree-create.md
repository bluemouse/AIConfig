# worktree-create: Create Feature Worktree

Create a new git worktree directory with a feature branch, allowing isolated development without affecting the current worktree.

## Goal

- Detect current worktree name from directory path
- Create a sibling worktree directory with a feature branch
- Follow the naming pattern: `<worktree>-feature-<name>` directory with `<worktree>/feature/<name>` branch
- Store source-branch association in git config for later merge back

## Preconditions

Create a feature branch **only when all are true**:

1. Current branch (`git branch --show-current`) is one of: `main`, `master`, or `dev`
2. The user has explicitly confirmed creation after seeing the proposed names

If the current branch is anything else, **do not create** a feature branch or worktree. Tell the user which branch you're on and continue on that branch unless they ask to switch first.

Never create a feature branch proactively or without confirmation — even when the current branch qualifies.

## Core Workflow

1. **Detect Worktree** — extract worktree name from current directory path
2. **Get Source Branch** — specified branch or current via `git branch --show-current`
3. **Gate on Source Branch** — proceed only if source branch is `main`, `master`, or `dev`
4. **Confirm with User** — show proposed worktree directory, feature branch name, and source branch; wait for explicit approval
5. **Create Worktree** — `git worktree add` with new directory + feature branch
6. **Store Association** — save source branch in git config (`branch.<branch>.mergeBackTo`)

## Naming Convention

- Worktree directory: `<worktree>-feature-<feature-name>`
- Branch name: `<worktree>/feature/<feature-name>`

Examples:

| In worktree | Feature        | Directory                   | Branch                      |
| ----------- | -------------- | --------------------------- | --------------------------- |
| `services`  | `auth-fix`     | `services-feature-auth-fix` | `services/feature/auth-fix` |
| `api`       | `new-endpoint` | `api-feature-new-endpoint`  | `api/feature/new-endpoint`  |

## Implementation Steps

1. Validate that a feature name was provided
2. `pwd` to get full path
3. Extract worktree name from basename (e.g. `/path/to/services` → `services`)
4. Source branch: specified or `git branch --show-current`
5. If source branch is not `main`, `master`, or `dev` → stop; report current branch and do not create
6. Sanitize feature name → kebab-case (strip special chars)
7. Construct paths:
   - Worktree dir: `../<worktree>-feature-<sanitized-name>`
   - Branch name: `<worktree>/feature/<sanitized-name>`
8. Ask the user to confirm creation — include worktree directory, feature branch, and source branch; do not run `git worktree add` until they approve
9. `git worktree add <worktree-dir> -b <branch-name> <source-branch>`
10. `cd <worktree-dir> && git config branch.<branch-name>.mergeBackTo <source-branch>`

## Output

```
Created feature worktree: services-feature-auth-fix

Detected worktree: services
Source branch: master

Created worktree: /home/user/projects/services-feature-auth-fix
Created branch: services/feature/auth-fix

Stored associations:
- Source branch: master

Next Steps:
1. Navigate: cd ../services-feature-auth-fix
2. Associate plan (if working with a plan): set git config branch.<branch>.plan
3. Start work in the new worktree
```

## Error Handling

- Error if feature name not provided
- Do not create if current/source branch is not `main`, `master`, or `dev`
- Do not create without explicit user confirmation
- Error if worktree directory already exists
- Error if branch already exists
- Error if specified source branch doesn't exist

## Gotchas

- The directory naming pattern `<worktree>-feature-<name>` is what downstream operations (merge, abandon) detect — non-conforming names break the workflow
- `branch.<branch>.mergeBackTo` and `branch.<branch>.plan` are custom config keys this workflow sets and reads; git itself ignores them, so don't expect any built-in behavior from them
- `mergeBackTo` git config is the only record of the source branch — without it, `worktree-merge` can't find where to merge back
- Creating a worktree from a dirty source branch carries those uncommitted changes into the feature worktree only if they're staged — verify clean state first
- A second worktree can't check out the same branch as another worktree — try a different source branch or move the existing worktree
