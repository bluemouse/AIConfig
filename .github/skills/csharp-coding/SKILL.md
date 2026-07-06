---
name: csharp-coding
description: "Write, review, refactor, test, debug, and optimize modern C# and .NET code using project-local toolchain settings. Use when working on .cs, .csproj, .sln, NuGet, Roslyn analyzers, MSTest/NUnit/xUnit, ASP.NET, console, library, worker, or service code; explaining C# grammar or language-version behavior; choosing dotnet/MSBuild/NuGet commands; fixing compiler, analyzer, runtime, or test failures; or applying idiomatic nullable-safe async C# \u2014 even if the user says \"C# help\" or \"fix this .NET code\" without naming a framework."
---

# csharp-coding wrapper for GitHub Copilot

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/csharp-coding/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/csharp-coding` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## GitHub Copilot-specific information

Reload VS Code after adding or editing this skill so Copilot rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/csharp-coding/`.
- Keep only GitHub Copilot-specific information in this wrapper.
