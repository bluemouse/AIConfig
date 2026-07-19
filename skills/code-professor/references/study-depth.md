# Study depth

Choose the lightest depth that answers the user's question. Record the selected depth in the guide header or scope section.

## Overview

**Use when:** first contact, time-boxed onboarding, or the user asks for a quick map.

**Include:**

- purpose and mental model
- repository map (major areas only)
- entry points and startup summary
- top three to five abstractions
- narrowest verified build/test commands
- short reading order (five to ten stops)
- explicit unknowns

**Omit or shorten:**

- full end-to-end traces
- deep concurrency analysis
- exhaustive invariant lists
- runtime instrumentation unless essential to answer the question

## Standard

**Use when:** default for module, workflow, or failure study when no depth is specified.

**Include:**

- full deliverable template for the selected document type
- evidence-backed claims with path:line citations
- tests mapped to behavior where relevant
- validation commands actually run or clearly labeled as inferred
- practical reading path and next actions

**Omit or shorten:**

- exhaustive edge-case catalogs
- platform-variant matrices unless the question spans them

## Deep

**Use when:** security-critical paths, heavy concurrency, intermittent failures, cross-system integration, or the user explicitly asks for exhaustive analysis.

**Include everything in standard, plus:**

- full workflow or failure trace including error and cleanup paths
- concurrency, timing, and ordering assumptions with evidence
- contradiction analysis when sources disagree
- runtime validation or controlled experiments when static evidence is insufficient
- test gap analysis and discriminating experiments for open hypotheses

**Do not skip:** quality gate, instrumentation cleanup verification, or explicit unknowns.

## Depth resolution

- Infer from phrasing: "quick overview", "high level" → overview; "deep dive", "exhaustive", "every stage" → deep.
- Default to **standard** when unclear.
- In **interactive mode**, ask the user to pick overview, standard, or deep before starting.
