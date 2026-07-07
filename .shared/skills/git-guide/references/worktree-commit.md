# worktree-commit: Commit in Worktree with Plan Context

## Guideline

Commit worktree changes using a message drafted via
[commit-message-writer](../../commit-message-writer/SKILL.md), enhanced by plan context
when available.

## Rationale

Plan-aware commits document not just what changed, but how it aligns with the overall
feature plan. Message composition belongs to commit-message-writer; this reference covers
the git mechanics inside a feature worktree.

## Example

```bash
# In feature worktree: services-feature-auth-flow
cd ../services-feature-auth-flow

# Add implementation and tests
# services/auth/flow.ts (220 lines)
# services/auth/__tests__/flow.test.ts (180 lines)

git status --porcelain
# M  services/auth/flow.ts
# A  services/auth/__tests__/flow.test.ts

# Plan stored in git config: "Implement email+password flow with TOTP"
# Draft message via commit-message-writer, then commit:
git add -A
git commit -m "feat: implement email+password flow with TOTP

Add LoginFlow component with email validation and TOTP verification.
Test coverage: happy path, invalid email, expired TOTP."

# Optional push
git push origin HEAD:services/feature/auth-flow
# GitLab only: git push -o ci.skip origin HEAD:services/feature/auth-flow
```

## Techniques

- Detect worktree name from directory
- Check changes: `git status --porcelain`
- Read plan: `git config branch.<branch>.plan` — pass to commit-message-writer as context
- Draft message via [commit-message-writer](../../commit-message-writer/SKILL.md) — do not
  auto-generate types or descriptions in this reference
- Commit: `git add -A && git commit -m "<message>"`
- Optionally push: `git push origin HEAD:<branch>` (GitLab: add `-o ci.skip` only when
  CI should be skipped on that push)
