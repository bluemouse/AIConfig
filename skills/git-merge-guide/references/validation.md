# Structural and final-state validation

Use this after integration code review and impact-based testing/verification. This reference validates Git structure and final local state; it does not replace semantic review or affected testing.

## 1. Structural Git checks

Use commands such as:

```bash
git diff --check
git diff --name-only --diff-filter=U
git ls-files -u
git status
git diff
git diff --cached
```

Ensure no unmerged entries remain. Search intended text/source files for accidental conflict markers such as `<<<<<<<`, `=======`, and `>>>>>>>`, while avoiding false positives in fixtures/docs where those strings are deliberate.

## 2. Final diff integrity

Inspect the final current/staged diff for accidental structural mistakes:

- unintended deletions or file resurrecting;
- duplicated blocks introduced by conflict editing;
- missing/duplicate imports, declarations, build entries, or generated artifacts;
- whitespace/error markers reported by `git diff --check`;
- integration fixes that were accidentally left unstaged when they are intended to be part of the local result;
- unrelated user changes accidentally staged or modified.

Do not repeat the full semantic integration code review here; this is a final integrity pass.

## 3. Completed rebase checks

For a completed rebase:

- confirm no rebase metadata remains;
- confirm branch and new `HEAD` are expected;
- compare the recorded pre-rebase replay list to the resulting logical history;
- confirm no commit was unexpectedly dropped or silently skipped;
- use local `git range-diff`/logs when useful to verify replay intent;
- identify staged post-rebase integration fixes separately from rewritten commits;
- confirm unrelated local work remains untouched.

If an expected commit appears dropped, do not silently accept it. Investigate and apply the permission gate for history-discarding behavior.

## 4. Resolved merge checks

For a no-commit merge:

- confirm merge metadata remains only because the final merge commit is intentionally not created;
- confirm all intended merge and integration fixes are staged;
- confirm no unmerged entries remain;
- confirm unrelated local work is not mixed into the staged merge result;
- do not run `git merge --continue` or `git commit`;
- report that the final merge commit remains a user action.

For a fast-forward merge, confirm the ref advanced as expected and no merge metadata remains.

## 5. Final state capture

Record for reporting:

- current branch;
- current `HEAD`;
- operation metadata remaining;
- staged changes;
- unstaged changes;
- untracked files;
- unmerged entries;
- whether post-rebase integration fixes remain staged;
- confirmation that no remote operation was performed.

## Final gate

Structural validation passes only when the local Git state matches the intended operation and no unintended work/history loss is detected.

The overall integration may be called `VERIFIED SUCCESS` only if all three are true:

1. integration code review passed with no unresolved semantic decision;
2. all required directly/indirectly affected tests and applicable checks passed;
3. this structural/final-state validation passed.
