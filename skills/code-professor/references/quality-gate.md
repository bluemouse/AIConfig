# Quality gate

Before delivering the final guide, verify every item below. Do not skip items because the answer is long or the user is waiting.

## Scope and evidence

- [ ] The requested scope was answered
- [ ] Architecture, execution-flow, invariant, and debugging conclusions have stable `path:line` evidence
- [ ] Line references point to restored permanent source, not removed instrumentation
- [ ] Facts, inferences, and hypotheses are distinguishable in prose
- [ ] Contradictory evidence is explained
- [ ] Generated or third-party code is labeled and not mistaken for primary design intent
- [ ] Unknowns are explicit — what remains unproven and what would establish it

## Commands and repository state

- [ ] Commands and observed results are accurate — no claimed passes without successful runs
- [ ] Verified commands are separated from commands inferred from configuration
- [ ] Temporary edits are fully removed and verified
- [ ] Pre-existing user changes remain intact
- [ ] `git status --short` matches the investigation baseline (aside from any changes the user explicitly requested)

## Recommendations and output

- [ ] Recommendations are separated from current behavior
- [ ] Candidate fixes are labeled as proposals, not confirmed repairs
- [ ] Study depth matches what was delivered (overview did not pretend to be exhaustive)
- [ ] File output (if any) follows [document-output.md](document-output.md)
