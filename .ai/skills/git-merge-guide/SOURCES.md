# Sources

## git-merge-guide (reference draft)

- **Path:** `references/skills/git-merge-guide/`
- **Last reviewed:** 2026-08-08
- **Used for:**
  - `SKILL.md` → end-to-end local merge/rebase integration workflow
  - `references/operation-semantics.md` → rebase stage semantics, baseline recording, empty commits
  - `references/conflict-investigation.md` → intent reconstruction and conflict classification
  - `references/semantic-resolution.md` → resolution modes and decision gate
  - `references/integration-code-review.md` → non-conflicted cross-branch semantic review
  - `references/testing-verification.md` → impact-based affected-test discovery and verification
  - `references/validation.md` → final structural Git and state validation
  - `references/merge-report.md` → compact and detailed reporting formats
  - `scripts/collect-git-context.sh` → read-only operation-state snapshot
- **Aspects extracted:**
  - Local-only merge/rebase contract (no fetch/push) → `SKILL.md`
  - No-commit merge workflow → `SKILL.md`, `references/operation-semantics.md`
  - Integration verification vs Git operation completion → `SKILL.md`
  - Rebase ours/theirs inversion → `references/operation-semantics.md`

## git-guide boundary (repository)

- **Path:** `skills/git-guide/`
- **Last reviewed:** 2026-08-08
- **Used for:**
  - Skill cluster boundary: general git mechanics vs deep merge integration
  - Reciprocal **When NOT to Use** and companion-skill cross-links
  - Eval-query differentiation for simple triage vs semantic integration
  - Final merge commit always deferred to `git-guide`
- **Aspects extracted:**
  - `git-guide` owns push/fetch/worktrees/staging/cherry-pick/revert/simple triage/final merge commit
  - this skill owns local merge/rebase integration depth

## dependent-skill handoffs (repository)

- **Path:** `skills/debugging-guide/`, `skills/implementation-auditor/`, `skills/code-reviewer/`, `skills/plan-executor/`, `skills/agent-runner/`, `skills/pull-request-guide/`, `skills/github-guide/`
- **Last reviewed:** 2026-08-08
- **Used for:**
  - reciprocal routing sections and companion-skill tables
- **Aspects extracted:**
  - debugging proves unclear failure cause, then returns here
  - auditor proves requirement coverage after integration verification
  - code-reviewer is optional read-only final review
  - plan-executor/agent-runner allow read-only work during active operations only

## Refresh Workflow

1. Re-read `references/skills/git-merge-guide/` if the reference draft is updated
2. Verify boundary with `git-guide`, `code-reviewer`, and `implementation-auditor` has not drifted
3. Re-run eval-queries against the skill description
4. Bump **Last reviewed** dates above
