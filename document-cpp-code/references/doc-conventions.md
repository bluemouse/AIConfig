# Documentation Conventions (Generic)

## Where docs live

- Many repos keep design/implementation docs under docs/ or doc/.
- Project onboarding and build/run notes often live in README.md.
- Some repos also use module-level README.md files.

## Naming patterns (doc/*.md)

- Prefer the repo's existing naming convention.
- Common patterns include kebab-case filenames and optional prefixes by area.

Examples of good “update targets” in many repos:

- docs/architecture.md
- docs/design.md
- docs/<module>.md
- doc/<topic>.md
- README.md (for high-level overviews)

## Update vs Create

- Prefer rewriting an existing best-match doc to keep information consolidated.
- Create a new doc only when no existing doc fits the requested topic.

## Mermaid usage

Mermaid diagrams are a good default when they clarify structure or flow.

Guidance:

- Project scope: use a component-style diagram to show modules and boundaries.
- Module scope: use sequence diagrams for key runtime flows when it clarifies behavior.

## Cross-linking

- Add a short “Related Documentation” section and link to other relevant docs.
- Add a “Related Code” section listing key directories/files.
