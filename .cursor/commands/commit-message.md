# Commit message

Draft commit message(s) for specified changes. **Do not run `git commit`** unless the user explicitly asks to commit after reviewing the message.

Produce two versions:

1. **Compact** — one line, suitable for `git commit -m`
2. **Verbose** — subject line plus body with rationale, notable details, and test/evidence notes when relevant

Focus on **why** the change exists, not a file-by-file inventory. Match the repository's commit style when recent history is available.

## Input format

Parse the user's message after `/commit-message`. Support structured flags (preferred) and natural language (fallback).

**Structured form:**

```text
/commit-message \
  [--staged | --working | --commit <sha> | --range <rev-range>] \
  [--context <path-or-text> ...] \
  [--jira <ticket-id> ...] \
  [--notes "<free-text context>"]
```

| Argument | Default | Meaning |
| --- | --- | --- |
| *(none)* | `--staged` | Changes currently in the index |
| `--staged` | — | Staged changes only (`git diff --cached`) |
| `--working` | — | All tracked changes vs `HEAD` — staged and unstaged (`git diff HEAD`) |
| `--commit <sha>` | — | One existing commit (`git show <sha>`) |
| `--range <rev-range>` | — | Combined diff and log for a commit range (e.g. `abc123..def456`, `main..HEAD`, `HEAD~3..HEAD`) |
| `--context` | — | Extra context: `@`-attached file path, URL, design doc, implementation plan, ticket link, or inline text |
| `--jira` | — | Jira ticket id(s) (e.g. `PROJ-123`); fetch details via Atlassian MCP when available |
| `--notes` | — | Free-text context (intent, constraints, rollout notes) not captured elsewhere |

**Natural language fallback:** infer scope from prose ("staged changes", "everything I've changed", "last commit", "commits since main"). Treat `@`-attached files as `--context`. Confirm ambiguous scope before analyzing.

**Examples:**

```text
/commit-message
```

```text
/commit-message --working
```

```text
/commit-message --commit abc1234
```

```text
/commit-message --range main..HEAD
```

```text
/commit-message \
  --staged \
  --context @docs/plans/auth-flow.md \
  --jira PROJ-456 \
  --notes "Part 2 of JWT migration; no API break"
```

## What to do

### Phase 1 — Parse and confirm

1. Confirm the workspace root is a git repository (`git rev-parse --is-inside-work-tree`).
2. Resolve scope to exactly one mode: `--staged`, `--working`, `--commit`, or `--range`. Default: `--staged`.
3. Collect context from:
   - **Session history** — design decisions, implementation steps, tradeoffs, and test results from the current conversation
   - **`--context`** paths (read attached or referenced files)
   - **`--jira`** tickets (use Atlassian MCP to load title, description, acceptance criteria when the plugin is available)
   - **`--notes`** and any remaining user prose after flags
4. If scope is missing, conflicting, or the target has no changes, say so and stop.

### Phase 2 — Gather git evidence

Run the commands for the chosen scope from the repository root. Prefer parallel reads where independent.

| Scope | Primary commands |
| --- | --- |
| `--staged` | `git diff --cached --stat`, `git diff --cached`, `git diff --cached --name-status` |
| `--working` | `git diff HEAD --stat`, `git diff HEAD`, `git diff HEAD --name-status` |
| `--commit <sha>` | `git show <sha> --stat`, `git show <sha> --format=fuller`, `git show <sha>` |
| `--range <rev-range>` | `git log --oneline <range>`, `git diff <range> --stat`, `git diff <range>`, `git log <range> --format=fuller` |

Also run (all scopes except single `--commit` when redundant):

- `git status --short` — sanity check for unstaged/untracked noise
- `git log -5 --oneline` — recent message style on this branch
- `git branch --show-current` — branch name may hint at feature scope

For `--range`, summarize how many commits are included and whether the range is empty.

For very large diffs, prioritize: stat summary, name-status, hunk headers, and session/context over reading every line. Note in output when the diff was sampled due to size.

### Phase 3 — Analyze

Synthesize **intent** from git evidence plus all context sources. Do not list every file unless the change is inherently a bulk rename/move.

1. **Type** — infer conventional-commit type when it fits: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `build`, `perf`. Prefer the most specific accurate type.
2. **Subject** — imperative, lowercase after the type prefix, ≤ ~72 characters, no trailing period.
3. **Body (verbose only)** — complete sentences: motivation, approach, user-visible impact, breaking changes, follow-ups. Mention tests run or recommended when relevant.
4. **Session alignment** — when the conversation explains *why* something was done, that belongs in the message even if the diff alone looks mechanical.
5. **External context** — weave in plan/ticket acceptance criteria when `--context`, `--jira`, or `--notes` apply; reference ticket ids in the verbose body (e.g. `Refs PROJ-456`).

Follow recent repo style from `git log` when it clearly prefers a pattern (e.g. scope prefixes, no type prefix). Do not invent scopes or tickets.

### Phase 4 — Output

Return exactly this structure (markdown):

```markdown
## Compact

`<one-line message>`

## Verbose

<subject line>

<body paragraphs and bullet lists as needed>
```

Optional third block when useful:

```markdown
## Suggested command

git commit -m "$(cat <<'EOF'
<verbose subject + body>
EOF
)"
```

Include **Suggested command** only when scope is `--staged` or `--working` and the user might commit immediately. Omit for `--commit` / `--range` (historical or multi-commit).

After the messages, add a short **Context used** line listing: scope, commit count (if range), session context (yes/no), files/ tickets cited.

### Phase 5 — Optional commit

If the user says to commit (in the same or follow-up message), use the **verbose** message (or compact if they choose) and follow the user's git commit rules: stage only if needed, HEREDOC for multi-line messages, never `--no-verify` unless asked.

## On failure

- Not a git repo → say so; do not fabricate a message.
- Invalid `<sha>` or empty range → show git error output.
- No changes for `--staged` / `--working` → report clean tree / empty index; do not invent a message.
- Context path missing → list missing paths; continue with available context if the user agrees.
- Jira MCP unavailable → use ticket id in text only; note that live ticket details were not fetched.

## Do not

- Run `git commit`, `git push`, or stage files unless the user explicitly requests a commit afterward.
- Use `--no-verify`, amend, or force-push while drafting.
- Dump a raw file list as the commit message.
- Contradict session context or supplied plan/ticket intent when the diff is ambiguous.

## Quality bar

- **Compact** stands alone and would make sense in `git log --oneline`.
- **Verbose** explains *why*, not only *what*.
- Both describe one coherent logical change; if the diff mixes unrelated work, say so and suggest splitting commits instead of blending.
