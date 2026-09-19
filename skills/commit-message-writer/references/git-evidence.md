# Git Evidence

## Contents

- [Goal](#goal)
- [Commands by scope](#commands-by-scope)
- [Supplementary commands](#supplementary-commands)
- [Large diffs](#large-diffs)
- [Repo style discovery](#repo-style-discovery)

## Goal

Gather factual evidence from git before composing messages. Run commands from the
repository root. Prefer parallel reads where independent.

## Commands by scope

Run all `git log` and `git show` commands with `--no-pager` (or `GIT_PAGER=cat`) per
`coding-behavior-guidelines.md` → Terminal execution — they invoke the default pager
(`less`) when stdout is a TTY and will block on stdin if paged. `git diff` is also paged
by default; use `--no-pager` there too, or pipe through `cat`.

| Scope | Primary commands |
| --- | --- |
| `--staged` | `git --no-pager diff --cached --stat`, `git --no-pager diff --cached`, `git --no-pager diff --cached --name-status` |
| `--working` | `git --no-pager diff HEAD --stat`, `git --no-pager diff HEAD`, `git --no-pager diff HEAD --name-status` |
| `--commit <sha>` | `git --no-pager show <sha> --stat`, `git --no-pager show <sha> --format=fuller`, `git --no-pager show <sha>` |
| `--range <rev-range>` | `git --no-pager log --oneline <range>`, `git --no-pager diff <range> --stat`, `git --no-pager diff <range>`, `git --no-pager log <range> --format=fuller` |

For `--range`:

- Summarize how many commits are included and whether the range is empty
- Note two-dot (`A..B`) vs three-dot (`A...B`) when the user's phrasing implies branch review

## Supplementary commands

Run for all scopes except single `--commit` when redundant:

| Command | Purpose |
| --- | --- |
| `git status --short` | Sanity check for unstaged/untracked noise |
| `git --no-pager log -10 --oneline` | Recent message style on this branch |
| `git --no-pager log -10 --format=fuller` | Body layout (prose vs bullets), scopes, footers |
| `git branch --show-current` | Branch name may hint at feature scope |

## Large diffs

For very large diffs, prioritize:

1. Stat summary and name-status
2. Hunk headers and file-level intent
3. Session/context over reading every line

Record in `Context used:` with `note=` when the diff was sampled due to size.

## Repo style discovery

Read `git --no-pager log -10 --oneline` and `--format=fuller` when types/scopes or body
layout are unclear to detect:

- Whether the repo uses Conventional Commit type prefixes
- Common scopes (e.g. `feat(skills):`, `docs(workflow):`)
- Subject casing and length habits
- Whether bodies use prose paragraphs or bullet lists
- Whether footers are common

Follow the detected pattern when clear, subject to
[message-style-contract.md](message-style-contract.md). Do not invent scopes or ticket ids
the user did not supply. Do not import host-specific commit templates when they conflict
with repo history.

Prior history is the best evidence of what a message may reference: past commit messages
cite committed paths, symbols, and ticket ids — not the planning documents that produced
them. Match that convention, and never introduce a plan, research, review, audit, or
manifest reference that prior history does not have.
