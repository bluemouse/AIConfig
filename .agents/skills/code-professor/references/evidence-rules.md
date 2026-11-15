# Evidence and citation rules

## Evidence classes

Use these classes in notes and make the distinction clear in prose when it matters:

- **Observed**: directly present in source, configuration, tests, or command output.
- **Validated**: observed dynamically through a successful build, test, reproduction, debugger, trace, or controlled experiment.
- **Inferred**: strongly implied by multiple observations but not directly asserted in one place.
- **Hypothesis**: plausible explanation that still needs a discriminating test.
- **Unknown**: insufficient evidence or inaccessible environment.

## Citation format

Use repository-relative POSIX paths:

- one line: `src/render/frame.cc:74`
- range: `src/render/frame.cc:74-118`
- multiple sources: `include/render/frame.h:22-61`, `src/render/frame.cc:74-118`

Place references immediately after the supported sentence or paragraph. Do not create a detached source dump that forces readers to reconstruct the relationship.

## Claims that require path:line evidence

Always cite:

- component responsibilities and boundaries
- dependency direction and ownership
- initialization, shutdown, and lifetime behavior
- control-flow and data-flow steps
- state transitions and invariants
- threading, synchronization, and asynchronous behavior
- error handling, fallback, retry, and cleanup behavior
- root-cause and debugging conclusions
- claimed extension points or compatibility constraints

High-level summaries of an already cited explanation may omit references when they introduce no new substantive claim.

## Evidence quality

Prefer, in order:

1. permanent implementation and public interfaces
2. focused tests that encode intended behavior
3. configuration and build definitions
4. maintained design documentation
5. comments near the relevant implementation
6. history, issue text, or external documentation

Do not use generated output or vendored code as the primary explanation of repository intent unless the question is specifically about that code.

## Dynamic evidence

For runtime observations, include:

- exact command or reproduction steps
- relevant environment and configuration
- observed result
- permanent source locations that produce, consume, or govern the behavior

Do not cite line numbers from temporary instrumentation after it has been removed. Re-read permanent files after cleanup and refresh all references before writing the final document.

## Handling disagreement

When code, tests, comments, and documentation disagree:

- describe the contradiction
- identify which evidence reflects current executable behavior
- avoid silently choosing the most convenient source
- state whether the mismatch appears to be stale documentation, a missing test, or a possible defect
