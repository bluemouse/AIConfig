# Repository orientation guide

Use this document for onboarding, first contact, or a broad request to explain a repository.

## Default structure

# Repository orientation: [repository name]

## 1. Purpose and mental model

Explain what the system does, who or what uses it, and the simplest useful mental model. Keep this section compact.

## 2. Prerequisites

List languages, tools, platforms, and domain familiarity the reader should have before diving deeper. State when the guide assumes none.

## 3. Learning objectives

After reading this guide, the reader should be able to:

- [objective 1 — e.g. locate the main entry point and start the application]
- [objective 2 — e.g. run the narrowest useful test suite]
- [objective 3 — e.g. identify where to add a feature in the dominant module]

Adapt objectives to the repository and study depth. At **overview** depth, keep to three concise objectives.

## 4. Repository map

Describe major directories and boundaries in a table:

| Area | Responsibility | Important entry points | Notes |
|---|---|---|---|

Cite responsibility and boundary claims.

## 5. How the system starts and runs

Explain executable or library entry points, initialization order, major runtime components, and shutdown at a useful level of detail.

## 6. Core abstractions

For each important abstraction, cover:

- responsibility
- ownership and lifetime
- key collaborators
- central invariants
- where to read next

At **overview** depth, cover only the top three to five abstractions.

## 7. Build, test, and development loop

List verified commands or clearly label commands inferred from repository configuration. Explain the test hierarchy and the narrowest useful checks.

## 8. Common change paths

Show where a developer would normally work to:

- add a feature
- change behavior
- add a test
- add diagnostics
- modify configuration

Adapt this list to the repository.

## 9. Recommended reading order

Provide a short ordered path through files or modules. Explain what each stop teaches.

## 10. Risks, unknowns, and follow-up topics

Identify generated boundaries, platform variants, external services, difficult runtime dependencies, stale documentation, or unresolved questions.

## 11. Optional opportunities

Suggest only evidence-backed improvements, extension points, or candidate fixes. Separate them from the description of current behavior.
