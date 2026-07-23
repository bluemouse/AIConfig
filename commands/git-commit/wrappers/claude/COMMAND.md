---
name: git-commit
description: Draft a Conventional Commit for staged changes and commit without pushing.
argument-hint: [optional context or "push"]
allowed-tools: Bash, Read, Grep, Glob
---

Use `$ARGUMENTS` as optional extra context for the commit message body or to detect an explicit push request.
