# Sources

## C# documentation (Microsoft Learn)

- **URL:** https://learn.microsoft.com/en-us/dotnet/csharp/
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → language rules, operating model
  - `references/language-grammar.md` → compilation units, namespaces, types, statements, expressions
- **Aspects extracted:**
  - Language-version and `LangVersion` behavior → `references/language-grammar.md`
  - Feature-version gates (C# 9–14) → `references/language-grammar.md`

## Nullable reference types

- **URL:** https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → language rules, cross-cutting principles
  - `references/best-practices.md` → null safety section
  - `references/language-grammar.md` → nullability grammar and flow rules
- **Aspects extracted:**
  - Nullable annotations as compile-time contracts → `references/language-grammar.md`
  - Guard clauses, flow analysis, attribute usage → `references/best-practices.md`

## .NET CLI overview

- **URL:** https://learn.microsoft.com/en-us/dotnet/core/tools/
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → tool usage expectations
  - `references/toolchain.md` → CLI command map, discovery
- **Aspects extracted:**
  - `dotnet restore`, `build`, `test`, `format`, `pack`, `publish` → `references/toolchain.md`
  - Common modifiers (`-c`, `-f`, `-r`, `--no-restore`, `--no-build`) → `references/toolchain.md`

## dotnet test

- **URL:** https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `references/toolchain.md` → test toolchain
  - `references/workflow-testing-debugging.md` → test strategy, verification loops
- **Aspects extracted:**
  - `--filter`, `--no-build`, `--logger` options → `references/toolchain.md`
  - Microsoft.Testing.Platform vs VSTest note → `references/toolchain.md`

## Code analysis / Roslyn analyzers

- **URL:** https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `references/toolchain.md` → formatting and analyzers
  - `references/workflow-testing-debugging.md` → analyzer failure triage
- **Aspects extracted:**
  - `dotnet format`, `AnalysisLevel`, `.editorconfig` severity → `references/toolchain.md`
  - Prefer code changes over suppressions → `references/workflow-testing-debugging.md`

## C# coding conventions

- **URL:** https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `references/best-practices.md` → naming, methods, properties, style checklist
- **Aspects extracted:**
  - PascalCase/camelCase conventions, async naming, property vs method guidance → `references/best-practices.md`

## CSharpGuidelines (synthesis metadata)

- **URL:** https://github.com/dennisdoomen/CSharpGuidelines
- **Last reviewed:** 2026-07-05
- **Used for:**
  - Design principles, layout rules, review discipline (synthesized, not verbatim)
- **Access limitation:** Individual `Skills/csharp-guidelines/SKILL.md` was not available at
  fetch time. Content is synthesized from repository metadata and Microsoft Learn sources above.

## antigravity-awesome-skills catalog (synthesis metadata)

- **URL:** https://github.com/sickn33/antigravity-awesome-skills
- **Last reviewed:** 2026-07-05
- **Used for:**
  - Catalog entry for `skills/super-code/csharp` — language-specific guideline scope
- **Access limitation:** Exact skill file was not available at fetch time. Integrated practices
  (nullable types, records, DI, analyzers, structured logging) were cross-checked against
  Microsoft Learn and encoded in `references/best-practices.md`.

## Community articles (synthesis metadata)

- Medium: "C# 12 Best Practices I Wish I Knew Earlier — Cleaner, Faster, Safer Code for 2025"
- DEV Community: "C# | Best Practices" by Hassan BOLAJRAF
- **Last reviewed:** 2026-07-05
- **Used for:**
  - Supplemental idioms where aligned with Microsoft Learn (collection expressions, `required`/`init`, `Span<T>`)
- **Aspects extracted:**
  - Integrated into `references/best-practices.md` only when consistent with official guidance
