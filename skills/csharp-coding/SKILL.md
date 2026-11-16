---
name: csharp-coding
description: Write, review, refactor, and verify modern C# (C# 9-14) language code — idioms, nullable-safe async, file-scoped namespaces, records, and pattern matching; LangVersion and SDK selection; and minimal dotnet build/test verification. Use when writing or reviewing .cs code (including reviewing C# libraries for IDisposable misuse, HttpClient lifetime, and other correctness pitfalls), explaining C# grammar or language-version behavior, checking what a project's LangVersion permits, fixing compiler or language-level errors, or applying idiomatic nullable-safe async C# — even if the user says "C# help" or "fix this C# code" without naming a version.
---

# C# Coding

Resolve `<SKILL_ROOT>` as the directory containing this skill's `SKILL.md`.

## Operating model

Before assuming language or toolchain features, inspect the project's `global.json`,
`*.csproj`, and `Directory.Build.props` / `Directory.Packages.props` (plus `.editorconfig`
when style matters). `LangVersion` — not the newest installed SDK — determines which
language features are available; see [language-versions.md](references/language-versions.md)
for the C# 9–14 feature gates. Unity, Xamarin, and legacy repos often pin an old
`LangVersion` — check it before using records, required members, or collection
expressions. Match the existing `TargetFramework`, nullable setting, and analyzer
configuration rather than the latest defaults.

## Verify

- `dotnet build --no-restore` (add `-warnaserror` when project policy allows)
- `dotnet test --no-build` (targeted `--filter` first, then broader scope)
- `dotnet format --verify-no-changes` when formatting/analyzers are part of repo policy
- Newer .NET SDKs support Microsoft.Testing.Platform alongside classic VSTest — check the repo's existing test runner mode (`global.json`, `Directory.Packages.props`) before changing runner options, since MTP and VSTest flags are not interchangeable

Never claim code was tested unless a command actually ran; state what was not verified.

## When NOT to Use

- Non-C# projects — use the language-specific skill instead.
- Infrastructure/DevOps work with no C# or project-file changes (pure Terraform,
  Kubernetes, CI provisioning).

## Reference routing

| Task | Read |
|------|------|
| Which language features a project's `LangVersion` permits; C# 9–14 feature-version gates; SDK/LangVersion interaction | [language-versions.md](references/language-versions.md) |

[SOURCES.md](SOURCES.md) records provenance for the surviving material.
