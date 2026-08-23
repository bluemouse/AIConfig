# C#/.NET toolchain usage

Use this file for .NET SDK, CLI, MSBuild, NuGet, analyzer, formatting, packaging, publishing, and project-configuration work.

## Table of contents

1. Toolchain discovery
2. Project and solution files
3. CLI command map
4. NuGet and dependency hygiene
5. Build configuration and MSBuild
6. Formatting and analyzers
7. Source generators and incremental generators
8. Test toolchain
9. Debugging and diagnostics tools
10. Publish, trimming, single-file, Native AOT
11. CI command templates
12. Common command recipes

## 1. Toolchain discovery

Start with:

```bash
dotnet --info
dotnet --list-sdks
dotnet --list-runtimes
```

Then inspect repo config:

```bash
find . -maxdepth 3 \( -name global.json -o -name '*.sln' -o -name '*.slnx' -o -name '*.csproj' -o -name Directory.Build.props -o -name Directory.Build.targets -o -name .editorconfig -o -name NuGet.config \)
```

Key files:
- `global.json`: SDK pinning and, in newer SDKs, test runner selection.
- `*.sln`/`*.slnx`: solution composition.
- `*.csproj`: target frameworks, nullable, language version, packages, analyzers, test SDK.
- `Directory.Build.props`/`.targets`: shared settings. Props load early; targets load late.
- `.editorconfig`: style, analyzer severity, generated-code settings.
- `packages.lock.json`: NuGet lock mode/reproducibility.

## 2. Project and solution files

Prefer SDK-style project files unless maintaining legacy projects.

Common properties:

```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
  <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  <AnalysisLevel>latest</AnalysisLevel>
  <EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>
</PropertyGroup>
```

Use `TargetFrameworks` only when multi-targeting is necessary. Conditionalize packages and APIs by framework when required.

Project references are preferred over NuGet references for same-repo code:

```bash
dotnet reference add ../MyLib/MyLib.csproj
```

## 3. CLI command map

Basic commands:

```bash
dotnet new console|classlib|webapi|worker|xunit|nunit|mstest
dotnet restore
dotnet build
dotnet run --project path/to/App.csproj
dotnet test
dotnet format
dotnet pack
dotnet publish -c Release
```

Useful modifiers:

```bash
-c Release
-f net8.0
-r linux-x64
--no-restore
--no-build
-v minimal|normal|diag
-p:Property=Value
```

Use `--no-restore` after a successful restore to make build/test failures clearer.

## 4. NuGet and dependency hygiene

Commands:

```bash
dotnet package list
dotnet package list --outdated
dotnet package add <PACKAGE>
dotnet package remove <PACKAGE>
dotnet nuget locals all --clear
dotnet restore --locked-mode
```

Rules:
- Do not add packages for trivial helpers.
- Prefer maintained packages with compatible licenses and known security posture.
- Respect central package management (`Directory.Packages.props`) when present.
- Do not update broad dependency ranges during a targeted bug fix unless necessary.
- For libraries, avoid exposing third-party types in public APIs unless intentionally part of the contract.

## 5. Build configuration and MSBuild

Use `dotnet build` for standard SDK projects. Use `dotnet msbuild` for advanced property/target diagnostics.

Useful MSBuild diagnostics:

```bash
dotnet build -bl
dotnet build -v diag
dotnet msbuild -pp:preprocessed.xml
```

Rules:
- Use conditions for target-specific settings:

```xml
<ItemGroup Condition="'$(TargetFramework)' == 'net8.0'">
  <PackageReference Include="Some.Package" Version="1.2.3" />
</ItemGroup>
```

- Avoid custom targets when SDK properties solve the problem.
- Do not hide build logic in scripts if MSBuild can express it reproducibly.

## 6. Formatting and analyzers

Roslyn analyzers are included in modern .NET SDKs. They report compiler, IDE, and CA diagnostics according to project settings.

Verification:

```bash
dotnet format --verify-no-changes
dotnet build -warnaserror
```

Modification when requested:

```bash
dotnet format
dotnet format analyzers
dotnet format style
```

EditorConfig examples:

```ini
root = true

[*.cs]
indent_style = space
indent_size = 4
dotnet_style_qualification_for_field = false:suggestion
csharp_style_namespace_declarations = file_scoped:suggestion
dotnet_diagnostic.CA2007.severity = none
```

Rules:
- Do not mass-format unrelated files in a targeted fix.
- Prefer analyzer configuration over suppressions.
- Use suppressions only for false positives or documented trade-offs; include justification.

## 7. Source generators and incremental generators

When a project uses generators:
- Inspect `EmitCompilerGeneratedFiles`, `Analyzer` item groups, and generated artifacts.
- Debug generated-code errors by identifying the original generator input, not by editing generated output.
- Prefer incremental generators for performance and deterministic caching.
- Keep generated code nullable-aware and deterministic.

Useful property:

```xml
<PropertyGroup>
  <EmitCompilerGeneratedFiles>true</EmitCompilerGeneratedFiles>
  <CompilerGeneratedFilesOutputPath>$(BaseIntermediateOutputPath)Generated</CompilerGeneratedFilesOutputPath>
</PropertyGroup>
```

## 8. Test toolchain

Common frameworks: xUnit, NUnit, MSTest. Do not mix framework-specific command-line options globally across mixed test projects.

Commands:

```bash
dotnet test
dotnet test --no-build
dotnet test --filter FullyQualifiedName~MyTest
dotnet test --logger trx
dotnet test /p:CollectCoverage=true
```

Newer SDKs support Microsoft.Testing.Platform mode through `global.json`; older/default behavior uses VSTest. Check the repository before changing test runner mode.

## 9. Debugging and diagnostics tools

Use the right diagnostic level:
- Compile error: inspect exact diagnostic ID, file, line, generated code, target framework.
- Runtime exception: capture exception type, message, stack trace, input, environment, and recent changes.
- Test failure: run the single failing test with normal verbosity, then inspect arrange/act/assert assumptions.
- Performance issue: measure before optimizing.

CLI tools commonly useful in .NET environments:

```bash
dotnet tool install --global dotnet-counters
dotnet tool install --global dotnet-trace
dotnet tool install --global dotnet-dump
dotnet tool install --global dotnet-gcdump
dotnet tool install --global dotnet-monitor
```

Use these only if available/appropriate in the environment.

## 10. Publish, trimming, single-file, Native AOT

Publish:

```bash
dotnet publish -c Release -o ./artifacts/publish
```

Self-contained/runtime-specific:

```bash
dotnet publish -c Release -r linux-x64 --self-contained true
```

Trimming/AOT properties require compatibility checks:

```xml
<PropertyGroup>
  <PublishTrimmed>true</PublishTrimmed>
  <PublishAot>true</PublishAot>
  <IsAotCompatible>true</IsAotCompatible>
</PropertyGroup>
```

Rules:
- Treat trimming and AOT as behavior changes. Reflection, serializers, dynamic loading, expression compilation, source generators, and P/Invoke can break.
- Add tests that exercise serialization, DI activation, reflection, configuration binding, and plugin loading.
- Do not enable trimming/AOT casually in libraries; mark compatibility only after validation.

## 11. CI command templates

Conservative CI loop:

```bash
dotnet restore --locked-mode
dotnet build --no-restore -c Release
dotnet test --no-build -c Release
dotnet format --verify-no-changes --no-restore
```

When warning-as-error is not already configured:

```bash
dotnet build --no-restore -c Release -warnaserror
```

## 12. Common command recipes

Create a solution with app and tests:

```bash
dotnet new sln -n MyApp
dotnet new classlib -n MyApp.Core -o src/MyApp.Core
dotnet new xunit -n MyApp.Core.Tests -o tests/MyApp.Core.Tests
dotnet sln add src/MyApp.Core/MyApp.Core.csproj tests/MyApp.Core.Tests/MyApp.Core.Tests.csproj
dotnet add tests/MyApp.Core.Tests/MyApp.Core.Tests.csproj reference src/MyApp.Core/MyApp.Core.csproj
dotnet test
```

Find package vulnerabilities/outdated packages where supported:

```bash
dotnet package list --vulnerable
dotnet package list --outdated
```

Reproduce CI locally:

```bash
dotnet clean
dotnet restore
dotnet build -c Release --no-restore
dotnet test -c Release --no-build
```
