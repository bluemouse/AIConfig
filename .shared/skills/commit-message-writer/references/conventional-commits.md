# Conventional Commits

## Contents

- [Format](#format)
- [Types](#types)
- [Subject rules](#subject-rules)
- [Body and footers](#body-and-footers)
- [Breaking changes](#breaking-changes)
- [Type selection](#type-selection)
- [Examples](#examples)
- [Repo alignment](#repo-alignment)

## Format

Conventional Commits structure (v1.0.0):

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

This skill produces two outputs from one analysis:

| Output | Contents |
| --- | --- |
| **Compact** | Single line: `<type>[scope]: <description>` — suitable for `git commit -m` |
| **Verbose** | Same subject line, blank line, then body (and footers when needed) |

## Types

Pick the **most specific accurate** type:

| Type | Use when |
| --- | --- |
| `feat` | New user-facing feature or capability |
| `fix` | Bug fix in application or library code |
| `refactor` | Behavior-preserving restructure |
| `docs` | Documentation only |
| `test` | Tests only |
| `ci` | CI/CD configuration |
| `chore` | Maintenance, deps, tooling with no production logic change |
| `build` | Build system or external dependency changes |
| `perf` | Performance improvement |

Default to `chore` only when no more specific type fits.

## Subject rules

- Imperative mood ("add", "fix", "remove" — not "added" or "adds")
- Lowercase after the type prefix (consistent with repo style when it differs)
- ≤ ~72 characters
- No trailing period
- Optional scope in parentheses when it clarifies intent: `feat(auth): add jwt refresh`

## Body and footers

**Verbose body only** — complete sentences covering:

- Motivation (*why*)
- Approach or notable design choice
- User-visible impact
- Breaking changes (or defer to footer)
- Tests run or recommended when relevant

Reference ticket ids in the verbose body when provided (e.g. `Refs PROJ-456`).

Footers follow git trailer convention when needed (`Reviewed-by:`, `Refs:`, etc.).

## Breaking changes

Indicate breaking changes by either:

- `!` after type/scope: `feat(api)!: remove legacy endpoint`
- `BREAKING CHANGE:` footer in the verbose body

Describe the breaking change clearly in the body when using `!`.

## Type selection

Infer type from diff **and** context — not filename patterns alone:

| Signal | Likely type |
| --- | --- |
| New feature behavior, new public API | `feat` |
| Corrects incorrect behavior | `fix` |
| Test files only | `test` |
| Markdown/docs only | `docs` |
| Workflow YAML, CI scripts | `ci` |
| CMake, package manifests, lockfiles without logic change | `build` or `chore` |
| Large internal restructure, same behavior | `refactor` |
| Hot-path optimization with measured gain | `perf` |

When the diff mixes unrelated types, suggest splitting commits instead of blending types.

## Examples

**Compact:**

```text
feat(auth): add jwt refresh token rotation
```

**Verbose:**

```text
feat(auth): add jwt refresh token rotation

Rotate refresh tokens on each use to limit replay window. Session
context drove this after the audit noted stale tokens survived logout.

Tests: pytest tests/auth/test_refresh.py
Refs PROJ-456
```

**Breaking change:**

```text
feat(api)!: remove v1 user endpoints

BREAKING CHANGE: v1 /users routes removed; clients must migrate to v2.
```

## Repo alignment

When recent `git log` shows a clear local pattern:

- Match presence or absence of type prefixes
- Match scope conventions
- Match body/footer habits

When the repo does not use Conventional Commits consistently, still produce valid
Conventional Commit drafts unless the user asks to match a non-standard legacy style exactly.
