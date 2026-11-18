# Study depth

Choose the lightest depth that answers the user's question. Record the selected depth in
the guide header or scope section. Infer from phrasing ("quick overview" / "high level" →
overview; "deep dive" / "exhaustive" / "every stage" → deep); default to **standard** when
unclear; in interactive mode, ask the user to pick before starting.

- **Overview** — first contact or time-boxed onboarding: purpose and mental model, major
  repository areas, entry points, top abstractions, narrowest verified build/test
  commands, a short reading order, explicit unknowns. Omit full traces, deep concurrency
  analysis, and exhaustive invariant lists.
- **Standard** (default) — full deliverable template, evidence-backed claims with
  `path:line` citations, tests mapped to behavior, validation commands actually run or
  clearly labeled as inferred, practical reading path.
- **Deep** — security-critical paths, heavy concurrency, intermittent failures, or the user
  asks for exhaustive analysis: everything in standard, plus error and cleanup paths,
  concurrency/timing/ordering assumptions with evidence, contradiction analysis, runtime
  validation when static evidence is insufficient, and test gap analysis. Never skip the
  quality gate, instrumentation cleanup verification, or explicit unknowns.
