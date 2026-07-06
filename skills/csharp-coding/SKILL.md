---
name: csharp-coding
description: Write, review, refactor, test, debug, and optimize modern C# and .NET code using project-local toolchain settings. Use when working on .cs, .csproj, .sln, NuGet, Roslyn analyzers, MSTest/NUnit/xUnit, ASP.NET, console, library, worker, or service code; explaining C# grammar or language-version behavior; choosing dotnet/MSBuild/NuGet commands; fixing compiler, analyzer, runtime, or test failures; or applying idiomatic nullable-safe async C# — even if the user says "C# help" or "fix this .NET code" without naming a framework.
---

# C# Coding

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve
paths to `references/` and `scripts/` from that directory.

Write and review C# code against project-local `TargetFramework`, `LangVersion`, nullable
settings, analyzers, and style configuration. Read bundled references on demand — do not
load all reference files unless the task requires them.

## When to Use

- Writing, reviewing, or refactoring C# and .NET code
- Explaining C# syntax, grammar, language-version behavior, or nullable rules
- Choosing dotnet, MSBuild, NuGet, analyzer, format, pack, or publish commands
- Fixing compiler, analyzer, runtime, async, or test failures
- Designing implementation plans, tests, or verification loops for C# changes
- Applying idiomatic nullable-safe async C# best practices

## When NOT to Use

- Non-C# projects (use language-specific skills instead)
- Pure infrastructure/DevOps work with no C# code changes (Kubernetes, Terraform, etc.)
- Unity/Xamarin/legacy platforms that pin older language versions — adapt selectively and
  check `LangVersion` before using newer syntax
- Infrastructure or CI work with no .NET build, test, or project-file changes (e.g. pure
  Terraform/Kubernetes provisioning)

## Operating model

Treat this as a production C# engineering skill. Optimize for correctness first, then
maintainability, then performance. Use the local project's `TargetFramework`, `LangVersion`,
nullable settings, analyzers, package versions, and style configuration as the source of
truth.

Before editing or generating nontrivial code:

1. Inspect `global.json`, `*.sln`, `*.slnx`, `*.csproj`, `Directory.Build.props`,
   `Directory.Build.targets`, `Directory.Packages.props`, `.editorconfig`, `NuGet.config`,
   lock files, and test projects when available.
2. Identify the target runtime and language version. If unspecified, assume the SDK default
   for the project, not the newest language feature.
3. Prefer changes that compile under the existing target framework and follow existing
   naming, file layout, dependency injection, logging, and test patterns.
4. After changes, run the smallest meaningful verification first, then broaden:
   format/analyze, build, targeted tests, full tests.

## Cross-cutting principles

These themes apply to every C# change:

1. **Nullable safety** — enable and respect nullable reference types; avoid `!` suppressions
2. **Project truth** — match `LangVersion`, target framework, and repo conventions
3. **Explicit async** — propagate `CancellationToken`; avoid blocking on async
4. **Test seams** — identify or add tests before changing observable behavior
5. **Verify before claiming** — run commands or state what was not verified

## Workflow

### 1. Assess

Before writing or reviewing:

- Restate the concrete outcome: new behavior, bug fix, refactor, performance improvement, or
  explanation.
- Complete the operating-model inspect steps above — confirm `TargetFramework`, `LangVersion`,
  nullable settings, analyzers, and test framework.
- Read every matching row in [Reference routing](#reference-routing) before editing.

### 2. Implement

- Apply [language-grammar.md](references/language-grammar.md) for syntax, patterns, and
  language-version gates.
- Apply [best-practices.md](references/best-practices.md) for API design, null safety, async,
  security, logging, and review standards.
- Apply [workflow-testing-debugging.md](references/workflow-testing-debugging.md) for test
  strategy, debugging, and failure triage.
- Apply [toolchain.md](references/toolchain.md) for project files, CLI commands, NuGet, and
  analyzers.
- Locate the owning type and tests. If no tests exist, identify a test seam before changing
  production code.
- Make the smallest idiomatic change. Avoid architectural rewrites unless the user asks or
  the current structure blocks the fix.
- Add or update tests at the appropriate level: unit for pure logic, integration for I/O and
  framework boundaries, benchmark only for performance-sensitive changes.

### 3. Verify

Run the quality bar in
[toolchain.md](references/toolchain.md#11-ci-command-templates) and the completion report in
[workflow-testing-debugging.md](references/workflow-testing-debugging.md#10-completion-report):

- Build clean at project warning level.
- Targeted tests first (`dotnet test --filter ...`), then broader scope.
- Format/analyzer verification when repo policy requires it.
- Report changed files, commands run, and remaining risks. Never claim code was tested unless
  a tool actually ran.

## Language rules to enforce

Default to these rules unless project conventions contradict them:

- Enable and respect nullable reference types. Use `?`, guards, and flow analysis instead of
  suppressing warnings with `!`.
- Prefer `record`/`record struct` for data/value semantics and `class` for identity/lifecycle
  semantics.
- Use `required` and `init` when object construction must be complete and immutable after
  initialization.
- Prefer pattern matching, switch expressions, target-typed `new`, collection expressions,
  `using` declarations, and file-scoped namespaces when supported by the project's language
  version.
- Keep properties cheap and side-effect free. Put expensive or asynchronous work in methods.
- Avoid `dynamic`, reflection, `unsafe`, and shared mutable state unless the problem
  justifies them.
- Use `async Task`/`Task<T>` for async APIs. Use `async void` only for event handlers. Use
  `ValueTask<T>` only in measured hot paths or APIs that often complete synchronously.
- Use `CancellationToken` on async I/O, long-running work, and public service APIs.
- Avoid blocking on async (`.Result`, `.Wait()`, `GetAwaiter().GetResult()`) except at proven
  safe process boundaries.

## Tool usage expectations

When a terminal or code execution tool is available, use it for real projects:

- Discover: `dotnet --info`, `dotnet workload list`, `dotnet sln list` (when available),
  `dotnet package list`, `dotnet test --list-tests` when useful.
- Restore/build: `dotnet restore`, `dotnet build --no-restore -warnaserror` where project
  policy allows.
- Test: `dotnet test --no-build`, targeted `--filter`, and framework-specific options only when
  the test framework supports them.
- Format/analyze: `dotnet format --verify-no-changes` for verification or `dotnet format` when
  asked to modify.
- Package/publish: `dotnet pack`, `dotnet publish -c Release`, and trimming/AOT options only
  after checking project support.

If command planning would help, run or inspect
`<SKILL_ROOT>/scripts/csharp_workflow.py` to generate a compact project command checklist.

## Reference routing

| Task | Read |
|------|------|
| Syntax, grammar, keywords, operators, patterns, nullable rules, generics, async, LINQ, language-version gates | [language-grammar.md](references/language-grammar.md) |
| dotnet CLI, MSBuild, NuGet, SDK selection, analyzers, formatting, packaging, publishing, AOT, trimming | [toolchain.md](references/toolchain.md) |
| Implementation loop, test strategy, debugging, failure triage, profiling, refactoring, completion report | [workflow-testing-debugging.md](references/workflow-testing-debugging.md) |
| API design, null safety, async, exceptions, performance, security, logging, style, review checklist | [best-practices.md](references/best-practices.md) |
| Source generators, incremental generators, generated-code compile errors | [toolchain.md](references/toolchain.md#7-source-generators-and-incremental-generators) |
| Runtime diagnostics, profiling, dotnet-trace/counters/dump | [toolchain.md](references/toolchain.md#9-debugging-and-diagnostics-tools) |

When a change spans multiple areas, read **every matching row** — e.g. async bug fixes need
both [workflow-testing-debugging.md](references/workflow-testing-debugging.md) and
[best-practices.md](references/best-practices.md); build failures need
[toolchain.md](references/toolchain.md) and possibly [language-grammar.md](references/language-grammar.md).

## Quick completion checklist

Complete **both** before marking C# work done:

1. **Code quality** — review checklist in
   [best-practices.md](references/best-practices.md#15-style-and-review-checklist)
   (nullability, async, resources, security, tests)
2. **Build and verification** — follow
   [toolchain.md](references/toolchain.md#11-ci-command-templates):
   - `dotnet build --no-restore` (with `-warnaserror` when project policy allows)
   - `dotnet test --no-build` (targeted filter first, then broader scope)
   - `dotnet format --verify-no-changes` when formatting/analyzers are part of repo policy

The Verify workflow step (above) is satisfied only when checklist part 2 commands ran or
unverified areas are explicitly stated.

## Output standards

For code answers:

- Provide complete, compilable snippets with required `using` statements, namespace context,
  and target framework assumptions when relevant.
- Explain why the chosen C# feature is appropriate when there are close alternatives.
- Keep examples idiomatic but not over-clever. Prefer readable control flow over dense LINQ
  when debugging, side effects, or error handling matter.
- Include tests or test guidance for behavior changes.

For reviews:

- Prioritize correctness, nullability, async/concurrency, resource lifetime, security,
  performance, API compatibility, and test gaps.
- Distinguish confirmed defects from style preferences.
- Provide concrete fixes and the command that would catch the issue next time.

## Resources

- [language-grammar.md](references/language-grammar.md) — C# syntax, grammar, and language-version gates
- [toolchain.md](references/toolchain.md) — .NET SDK, CLI, MSBuild, NuGet, analyzers, publish
- [workflow-testing-debugging.md](references/workflow-testing-debugging.md) — Engineering workflow and failure triage
- [best-practices.md](references/best-practices.md) — Idiomatic C# design, safety, and review standards
- [SOURCES.md](SOURCES.md) — Provenance and external references (read for attribution only)

External reference: [C# documentation](https://learn.microsoft.com/en-us/dotnet/csharp/)
