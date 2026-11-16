---
name: github-guide
description: "Use when delivering a pull request and its review on GitHub (github.com or GitHub Enterprise Server) from the command line with the `gh` CLI and `gh api` — opening a PR with `gh pr create`, writing or self-reviewing the PR description or body (what/why/how, how-tested, tradeoffs, sizing and splitting), posting a structured review with line-anchored inline comments, resolving review threads, detecting that the host is GitHub from the git remote, and scoping a classic or fine-grained token. Triggers on a github.com / GHES remote, `gh pr create`, `gh api .../pulls/.../reviews`, writing a PR description / PR body, sizing or splitting a large change into reviewable PRs, self-reviewing a PR before requesting review, draft vs ready, an inline review comment by path+line, resolving a review thread (resolveReviewThread), REQUEST_CHANGES / branch-protection merge gating, or GH_TOKEN / GH_ENTERPRISE_TOKEN scopes — even when the user doesn't say 'gh' or 'PR', e.g. 'write the PR description'."
---

# GitHub PR & review delivery — quick reference

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` from that directory.

## Scope / handoffs

The host-**delivery** tier: take finished artifacts and land them on GitHub via `gh` / `gh api` — open a PR (`gh pr create`), post a structured review with line-anchored inline comments (`POST …/pulls/{n}/reviews`), resolve threads (GraphQL `resolveReviewThread`), scope a classic or fine-grained token, or set up auth / GHES env vars. The author-side PR description, sizing, and self-review defaults live in **PR authoring defaults** below; for everything else hand off: findings and severity → [code-reviewer](../code-reviewer/SKILL.md); commit, push, rebase, worktrees, final merge commit → [git-guide](../git-guide/SKILL.md); complex local merge/rebase integration → [git-merge-guide](../git-merge-guide/SKILL.md); non-GitHub hosts (GitLab, Azure DevOps) → that host's tooling.

## Core model

- **One atomic review object** — a single `POST .../pulls/{n}/reviews` carries the summary body, every line-anchored inline comment, AND the APPROVE / REQUEST_CHANGES / COMMENT verdict together.
- **`gh pr review` is summary-only** — it posts the review-level body and verdict but has no inline support.
- **Drop to `gh api` for inline and resolve** — inline comments use `gh api` REST; resolving a thread uses `gh api graphql` (GraphQL-only).
- **Merge blocking is policy, not API** — REQUEST_CHANGES blocks merge only under branch protection / rulesets, not from the review POST alone.

When this skill fires:

1. Confirm the host is GitHub and auth works — `gh auth status` then a real read call (`gh api user`) — before any write. If `gh auth status` reports the host is unauthenticated, **do not** run `gh auth login` inside the agent — it opens an interactive browser/device flow that blocks the terminal. Stop and ask the user to authenticate, then resume.
2. Reach for `gh api` the moment you need an inline comment or a thread resolve; the high-level `gh pr` verbs cannot do either.
3. Load the `references/*.md` file matching the task, not everything upfront.
4. Run all `gh` commands in **sync terminal mode**. Always pass `--body-file -` (never let `gh pr create` / `gh pr edit` open `$EDITOR`), and avoid `--web` (it launches a browser and blocks).

## Essentials

- **Confirm host and auth** — a `github.com` (or GHES) host on `git remote get-url origin` (resolved via `gh repo view --json nameWithOwner,url`) is the detection signal; for GHES set `GH_HOST` / `--hostname` and use `GH_ENTERPRISE_TOKEN`. First-time install + `gh auth login` + protocol + clone + verify: [references/onboarding.md](references/onboarding.md); token families, per-operation least-privilege scopes, and storage: [references/auth.md](references/auth.md).
- **Open a PR** — `gh pr create --base <target> --head <source> --title … --body-file -` auto-pushes the branch if it isn't on the remote and sets reviewers/labels/assignees in one call; the raw `POST /repos/{owner}/{repo}/pulls` does NOT push. See [references/create.md](references/create.md).
- **Push / rebase first** — the clean branch is [git-guide](../git-guide/SKILL.md)'s job; this skill assumes the source branch builds on the latest target. See [git-guide push reference](../git-guide/references/push.md).
- **Post a structured review** — `gh pr review` only carries the summary + verdict; batch the summary, every inline comment, and the verdict into one `gh api … /pulls/{n}/reviews` object. See [references/review-post.md](references/review-post.md).
- **Write the review content with code-reviewer** — findings, severity, and merge verdict are `code-reviewer`'s; this skill maps them to GitHub bodies and submits them (see **Handoff from code-reviewer** below).
- **Write the PR body from the authoring defaults** — `gh pr create --body-file` takes a description authored per the **PR authoring defaults** below.
- **Resolve a thread** — GraphQL-only `resolveReviewThread` by thread node id (`PRRT_…`), matched by id never by line; list threads with `pullRequest.reviewThreads`. See [references/review-resolve.md](references/review-resolve.md).
- **Scope the token per operation** — push needs Contents: write; open-PR / post-review need Pull requests: write; resolve also needs Contents: read & write on a fine-grained token. See [references/auth.md](references/auth.md).

## PR authoring defaults

Author-side defaults for the PR description, sizing, and self-review — apply them before `gh pr create`. Four are firm:

- **"Tested locally" tells the reviewer nothing** — name the scenario, the environment, and how the reviewer can re-run it (a command, a request, a deep link); list the automated tests added and the edge cases checked (empty, error, concurrency, large input).
- **50-200 changed lines per PR, ~400 as a soft cap** — line counts approximate the real target: review time under roughly an hour. Limit files touched, not just lines; a wide diff is hard to follow even when small.
- **Split a refactor out of a feature PR** — one concern per PR; break large changes into independently reviewable slices or stack dependent PRs and cross-link them. Line count measures volume, not risk, so call out legitimately big diffs (scaffolding, generated code, dependency bumps, renames) up front and the reviewer calibrates instead of skimming.
- **Keep the PR a draft until CI is green and you have self-reviewed the diff** — read your own diff file by file, remove debug logging, commented-out code, and stray files, confirm the diff matches the description, run the project checks (typecheck / lint / build / test), then flip to ready and assign reviewers.

Description shape:

- Lead with **What / Why / How** — the net effect, the goal with the linked work item, the approach plus any rejected alternative and the reason.
- Match depth to size — one sentence for a typo or version bump; ~300-400 words for a multi-area change. Link context (work items, related PRs, design docs) and attach screenshots for any UI change.
- Add a short **Tradeoffs / risks** section when the change has limitations or non-obvious decisions: each known limitation and why it is acceptable for now, alternatives considered, and anything affecting backwards compatibility, data, or config. Do not invent risks when there are none.
- A lean template of 4-6 prompts (What / Why / Changes / Testing / Tradeoffs / Related) beats a long checklist form — set it as `PULL_REQUEST_TEMPLATE.md` so every PR starts pre-filled.

For the surrounding work, hand off: **[git-guide](../git-guide/SKILL.md)** for mechanics (commit, push, rebase, worktrees), **[git-merge-guide](../git-merge-guide/SKILL.md)** for local merge/rebase integration, **[commit-message-writer](../commit-message-writer/SKILL.md)** for the commit message, **[code-reviewer](../code-reviewer/SKILL.md)** for diff review.

## Gotchas

- A fine-grained PAT must have **Contents: write** to push commits/refs (`POST/PATCH .../git/refs`, `PUT .../contents`) — Contents: read is enough only to OPEN a PR and POST a review, never to push.
- `gh pr edit --body` / `--body-file` **replaces** the whole description (never appends) — fetch first (`gh pr view N --json body -q .body`), recombine, then set; metadata is incremental via paired `--add-*` / `--remove-*` flags.
- `gh pr create` is **not** create-or-update — it aborts non-zero if an open PR already exists for the branch; guard with `|| gh pr view --json url -q .url`. Only `--web` proceeds anyway, and `--dry-run` "may still push git changes".
- `gh pr review` has **no inline support** (cli/cli#12396) and the standalone `.../pulls/{n}/comments` endpoint 422s on `line`/`side` payloads (cli/cli#13358) — put inline comments inside one `.../reviews` object.
- `line` in the reviews API is a **file line number** + `side`, NOT the deprecated diff `position` (never compute position); a multi-line range needs `start_line`/`start_side` preceding `line`/`side` in the same hunk. Anchor to the PR HEAD sha or comments go "outdated".
- You **cannot** APPROVE or REQUEST_CHANGES your own PR (HTTP 422) — self-reviews are COMMENT-only.
- REQUEST_CHANGES blocks merge only under branch-protection / ruleset required reviews, and clears only via the **same** reviewer approving or a write-access **dismiss** (`PUT .../dismissals`) — another person's approval does not override it.
- Thread resolution is GraphQL-only; on a fine-grained PAT / App token it also silently needs **Contents: read & write** or returns "Resource not accessible by integration" (community #44650). Classic `repo` suffices.
- `Closes #N` in the PR **body** auto-closes the issue only when the PR merges into the **default** branch; cross-repo needs `Closes owner/repo#N`. There is no `gh` flag for it.
- GitHub Enterprise Server uses **GH_ENTERPRISE_TOKEN** / GITHUB_ENTERPRISE_TOKEN, not GH_TOKEN — mixing them is the classic "works on github.com, 401 on GHES".
- Insufficient permission on a **private** repo returns 404 (not 403) — GitHub hides existence; read the `X-Accepted-GitHub-Permissions` header (`gh api -i <endpoint>`) for the exact required permission.

## Handoff from code-reviewer

When the user wants a PR reviewed **and posted on GitHub**, run the two skills in order:

1. **[code-reviewer](../code-reviewer/SKILL.md)** — review the PR diff (typically `git diff <base>...<head>` or the open PR's changed files) and produce the in-chat Output Contract.
2. **This skill** — map those findings to one atomic `POST .../pulls/{n}/reviews` call. Read [references/review-post.md](references/review-post.md) for the full anchor model and examples.

Do not re-review the diff here — only translate and post. If findings already exist in chat from a prior `code-reviewer` run, skip straight to mapping and posting.

### Severity → inline comment body

Prefix each inline `comments[].body` with the finding's severity label:

| `code-reviewer` severity | Inline prefix | Blocking? |
| --- | --- | --- |
| `blocker` | `**blocker (blocking):**` | Yes — drives `REQUEST_CHANGES` (not on self-review; use `COMMENT`) |
| `major` | `**major:**` | No |
| `minor` | `**minor:**` | No |

Compose the rest from the finding fields: `{What's wrong}. {Why it matters}. {Proposed fix}`. Optionally lead with the scope in brackets, e.g. `[security] **blocker (blocking):** …`.

Only findings with a resolvable **file + line** become inline comments. Findings without a line anchor belong in the review summary body only.

### Severity → review verdict (`event`)

| Condition | `event` |
| --- | --- |
| Any `blocker` finding (reviewing **someone else's** PR) | `REQUEST_CHANGES` |
| No findings; overall verdict is merge-ready | `APPROVE` |
| Only `major` / `minor` with actionable inline feedback | `COMMENT` (**default** when posting inline comments that need a response) |
| Only minor nits and reviewer **explicitly** approves | `APPROVE` (optional inline comments for nits) |

**`COMMENT` vs `APPROVE`:** when you post inline comments the author should address, default to `COMMENT` even if nothing is `blocker`. Use `APPROVE` only when the reviewer clearly wants to approve merge and inline notes are optional context, not requested changes.

**Self-review (your own PR):** GitHub allows `COMMENT` only — never `APPROVE` or `REQUEST_CHANGES` (HTTP 422). Use `event=COMMENT` regardless of severity. Keep `**blocker (blocking):**` prefixes on inline comments and state in the summary that formal merge blocking requires another reviewer.

`REQUEST_CHANGES` and `COMMENT` require a non-empty summary `body`.

### Summary body

Build the review-level `body` from the `code-reviewer` report:

- Lead with **Overall Verdict** (merge readiness, top risks).
- Add a **Findings** bullet list: severity, `path:line`, one-line summary, and "(see inline)" when anchored inline.
- Include **Open Questions Or Assumptions** only when they could change the review outcome.

## Example — open a PR, post a blocking inline review, resolve a thread

```bash
# 0. confirm the host is GitHub and you can read
gh repo view --json nameWithOwner,url -q '.url'   # github.com/... or your GHES host
gh auth status && gh api user -q '.login'

# 1. open the PR (gh pushes feat/x if it isn't on the remote); idempotency guard
gh pr create --base main --head feat/x \
  --title "feat: guard null user" --body-file pr-body.md \
  --reviewer org/team-slug --assignee @me --label enhancement \
  || gh pr view feat/x --json url -q .url

# 2. post ONE review object: summary + inline comment + verdict (gh pr review can't do inline)
HEAD=$(gh pr view 123 --json headRefOid -q .headRefOid)
gh api --method POST repos/{owner}/{repo}/pulls/123/reviews \
  -f commit_id="$HEAD" -f event=REQUEST_CHANGES \
  -f body=$'## Summary\nOne blocking issue, see inline.' \
  -f 'comments[][path]=src/app.ts' \
  -F 'comments[][line]=42' \
  -f 'comments[][side]=RIGHT' \
  -f 'comments[][body]=**blocker (blocking):** guard against a null `user` here.'

# 3. list threads, then resolve by node id (never by line) — GraphQL only
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{id isResolved path comments(first:1){nodes{databaseId body}}}}}}}' \
  -F o=OWNER -F r=REPO -F n=123
gh api graphql -f query='mutation($t:ID!){resolveReviewThread(input:{threadId:$t}){thread{id isResolved}}}' \
  -f t=PRRT_kwDOxxxxx
```

