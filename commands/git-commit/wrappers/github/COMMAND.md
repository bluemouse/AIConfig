---
name: git-commit
description: Draft a Conventional Commit for staged changes and commit without pushing.
argument-hint: [optional context or "push"]
agent: agent
---

Use `${input:context:optional notes for the commit message}` when the user did not provide trailing context after the command name.
