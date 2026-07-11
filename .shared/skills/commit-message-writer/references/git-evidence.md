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

| Scope | Primary commands |
| --- | --- |
| `--staged` | `git diff --cached --stat`, `git diff --cached`, `git diff --cached --name-status` |
| `--working` | `git diff HEAD --stat`, `git diff HEAD`, `git diff HEAD --name-status` |
| `--commit <sha>` | `git show <sha> --stat`, `git show <sha> --format=fuller`, `git show <sha>` |
| `--range <rev-range>` | `git log --oneline <range>`, `git diff <range> --stat`, `git diff <range>`, `git log <range> --format=fuller` |

For `--range`:

- Summarize how many commits are included and whether the range is empty
- Note two-dot (`A..B`) vs three-dot (`A...B`) when the user's phrasing implies branch review

## Supplementary commands

Run for all scopes except single `--commit` when redundant:

| Command | Purpose |
| --- | --- |
| `git status --short` | Sanity check for unstaged/untracked noise |
| `git log -10 --oneline` | Recent message style on this branch |
| `git log -10 --format=fuller` | Body layout (prose vs bullets), scopes, footers |
| `git branch --show-current` | Branch name may hint at feature scope |

## Large diffs

For very large diffs, prioritize:

1. Stat summary and name-status
2. Hunk headers and file-level intent
3. Session/context over reading every line

Record in `Context used:` with `note=` when the diff was sampled due to size.

## Repo style discovery

Read `git log -10 --oneline` and `--format=fuller` when types/scopes or body layout are
unclear to detect:

- Whether the repo uses Conventional Commit type prefixes
- Common scopes (e.g. `feat(skills):`, `docs(workflow):`)
- Subject casing and length habits
- Whether bodies use prose paragraphs or bullet lists
- Whether footers are common

Follow the detected pattern when clear, subject to
[message-style-contract.md](message-style-contract.md). Do not invent scopes or ticket ids
the user did not supply. Do not import host-specific commit templates when they conflict
with repo history.
