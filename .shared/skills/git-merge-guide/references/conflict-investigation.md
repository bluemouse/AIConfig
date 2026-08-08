# Conflict investigation

Use this reference for every nontrivial logical conflict.

## Contents

- [Evidence hierarchy](#evidence-hierarchy)
- [Investigate the operation first](#investigate-the-operation-first)
- [Build an intent record](#build-an-intent-record)
- [Classify conflict risk](#classify-conflict-risk)
- [Flag likely non-conflicted interactions](#flag-likely-non-conflicted-interactions)

## Evidence hierarchy

Prefer evidence in roughly this order, while adapting to the repository:

1. Current repository invariants, tests, and public/internal API contracts expressed in code.
2. The exact commits whose changes collide, including commit messages and patches.
3. The common ancestor/base behavior.
4. Nearby commits that explain a refactor, migration, bug fix, or follow-up.
5. File history and blame for the affected functions/types.
6. Callers, implementations, tests, comments, repository documentation, configuration, and generated-source definitions.
7. Naming/style conventions only after behavioral evidence is exhausted.

Do not use remote PRs/issues or network sources. The skill is local-only.

## Investigate the operation first

Identify the actual commits behind each side. Do not reason from conflict-marker labels alone.

Useful commands include:

```bash
git status
git diff --name-only --diff-filter=U
git ls-files -u
git show <commit>
git show <commit> -- path/to/file
git log --oneline --decorate --graph --all -- path/to/file
git log -p --follow -- path/to/file
git blame <rev> -- path/to/file
git merge-base <a> <b>
git diff <base>..<side> -- path/to/file
```

During rebase, inspect `REBASE_HEAD` and the current rebase metadata when available to determine the commit being replayed. The already-rebased `HEAD` may contain previously replayed commits and earlier conflict resolutions, so compare behavior rather than assuming it equals the original upstream tip.

## Build an intent record

For each logical conflict, answer these questions before editing:

### Base

- What did this code do before either change?
- What invariants, lifetime rules, error behavior, threading assumptions, serialization format, API contracts, or test expectations already existed?

### Change A

- Which commit(s) introduced it?
- Was it a bug fix, feature, cleanup, migration, performance change, compatibility change, or mechanical refactor?
- What behavior intentionally changed?
- What old behavior was intentionally removed?
- Which tests/callers changed with it?

### Change B / replayed change

Ask the same questions independently. Do not assume later chronology automatically means supersession; branches can evolve independently.

### Interaction

Classify the intentions:

- **Independent:** affect different concerns and should usually coexist.
- **Complementary:** one enables/extends the other and integration is required.
- **Overlapping:** solve similar problems differently; determine whether one supersedes the other.
- **Sequential:** one was authored assuming an earlier state and needs adaptation to the newer architecture.
- **Incompatible:** encode contradictory requirements that require a user/product/architecture decision.

## Classify conflict risk

### Low-risk textual

Examples: nearby comments, import ordering, independent declarations, formatting-only overlap. Still inspect enough context to ensure no semantic interaction.

### Rename/move

Trace both old and new paths with `git log --follow`, inspect references/callers, and determine whether edits should follow the rename. Do not duplicate a file merely to clear the conflict.

### Modify/delete

Determine why deletion happened. If deletion was an intentional replacement/removal, transplant still-relevant behavior into the replacement rather than restoring the obsolete file. If deletion was accidental or unrelated, retaining the modified file may be correct. Ask if product intent cannot be established.

### Add/add

Determine whether the files represent the same conceptual component, parallel implementations, or coincidental names. Merge identities only when contracts align.

### Generated artifacts

Find the source of truth and generation command. Prefer resolving source inputs and regenerating deterministic outputs. Do not hand-merge generated output unless regeneration is unavailable and the repository's workflow clearly expects manual edits.

### Binary/submodule

Textual semantic merging may be impossible. Inspect history, build metadata, and references. Choose a side only when evidence is clear; otherwise ask.

### API/type/schema

Search all callers/implementations/serializers/tests. A conflict-free caller can still become wrong after two API changes are combined.

### Behavioral/algorithmic

Reconstruct preconditions, outputs, error paths, state transitions, concurrency/lifetime assumptions, and performance constraints. Write or adapt tests that distinguish the competing interpretations when possible.

### Cross-file architectural

Treat the conflict as one logical migration. Resolve interfaces, implementations, adapters, tests, generated code, and cleanup consistently rather than file by file.

## Flag likely non-conflicted interactions

While researching conflicts, note likely interactions with cleanly merged code, especially when one side changes an API, value meaning, lifetime, schema, synchronization rule, configuration, or dependency used by the other side. These observations may affect the immediate conflict resolution.

Do not treat this early inspection as the full integration review. After every Git conflict is resolved and focused-tested, perform the systematic non-conflicted review in `integration-code-review.md` across both complete original change sets.
