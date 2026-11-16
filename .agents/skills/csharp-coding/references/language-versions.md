# C# language-version gates

Check `LangVersion` before using a feature — do not assume availability from current
Microsoft Learn documentation. The effective language version comes from `LangVersion`,
SDK defaults, and the target framework.

Probes in `*.csproj` / `Directory.Build.props`:

```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <LangVersion>latest</LangVersion>
  <Nullable>enable</Nullable>
</PropertyGroup>
```

Avoid `LangVersion=latest` in shared libraries unless the repository already uses it —
prefer explicit language versions for reproducible CI.

## Feature-version gates

- C# 9: records, init-only setters, top-level statements, pattern enhancements.
- C# 10: file-scoped namespaces, global usings, record structs, lambda improvements.
- C# 11: raw string literals, required members, generic math/static abstract interface
  members, list patterns.
- C# 12: collection expressions, primary constructors, alias any type, default lambda
  parameters.
- C# 13+: params collections, lock improvements, partial properties/indexers,
  ref/unsafe improvements.
- C# 14 preview: extension members and other newer syntax may require preview tooling.

Use older syntax when targeting older frameworks, older SDKs, Unity, Xamarin/legacy
platforms, source generators, or repositories that pin compiler versions.
