# Evidence and citation rules

- Distinguish **observed** (directly present in source, configuration, tests, or command
  output), **validated** (observed dynamically through a successful build, test,
  reproduction, or controlled experiment), **inferred** (strongly implied by multiple
  observations but not directly asserted), **hypothesis** (needs a discriminating test),
  and **unknown** (insufficient evidence). Never present a hypothesis as established
  behavior.
- Cite every substantive architecture, execution-flow, invariant, or debugging conclusion
  with repository-relative `path:line` (or `path:start-end`) references, placed
  immediately after the supported sentence. High-level summaries of already-cited
  explanations may omit references when they introduce no new substantive claim.
- Evidence quality, preferred order: permanent implementation and public interfaces →
  focused tests → configuration and build definitions → maintained design docs →
  comments near the implementation → history/issue text. Do not use generated output or
  vendored code as the primary explanation of repository intent.
- For runtime observations record the exact command, environment, observed result, and the
  permanent source locations governing the behavior. Do not cite line numbers from
  temporary instrumentation after removal — re-read permanent files and refresh
  references before the final document.
- When code, tests, comments, and documentation disagree: describe the contradiction,
  identify which evidence reflects current executable behavior, and state whether the
  mismatch is stale documentation, a missing test, or a possible defect.
