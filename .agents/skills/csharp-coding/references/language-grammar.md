# C# language grammar quick reference

Use this file when the task depends on exact C# syntax, language-version behavior, or grammar-driven reasoning. This is a compact engineering grammar, not a replacement for the full C# language specification. Always check the project's `LangVersion` before using newer syntax.

## Table of contents

1. Compilation and versioning
2. Lexical grammar
3. Compilation-unit grammar
4. Namespaces and using directives
5. Types and type parameters
6. Type declarations
7. Member declarations
8. Statements
9. Expressions and operator precedence
10. Pattern matching
11. LINQ query expressions
12. Async, iterators, and unsafe code
13. Nullability grammar and flow rules
14. Feature-version gates to check

## 1. Compilation and versioning

C# source is compiled by Roslyn from one or more compilation units. The effective language version comes from `LangVersion`, SDK defaults, and target framework. Do not assume a feature is available just because it is documented in current Microsoft Learn.

Useful project-file probes:

```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <LangVersion>latest</LangVersion>
  <Nullable>enable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
</PropertyGroup>
```

Avoid `LangVersion=latest` in shared libraries unless the repository already uses it. Prefer explicit language versions for reproducible CI.

## 2. Lexical grammar

### Input elements

```ebnf
compilation_unit_text := input_element*
input_element := whitespace | comment | token
comment := single_line_comment | delimited_comment | documentation_comment
```

Whitespace separates tokens but usually has no semantic meaning. Comments do not nest, except that XML documentation comments are parsed for documentation tooling.

### Identifiers and keywords

```ebnf
identifier := regular_identifier | verbatim_identifier
regular_identifier := identifier_start_character identifier_part_character*
verbatim_identifier := '@' identifier_or_keyword
```

Reserved keywords cannot be used as normal identifiers. Prefix with `@` for interop or generated code: `@class`, `@event`. Contextual keywords (`async`, `await`, `record`, `required`, `init`, `file`, `scoped`, `where`, `from`, etc.) are keywords only in specific grammar positions.

### Literals

```ebnf
literal := null_literal | boolean_literal | integer_literal | real_literal | character_literal | string_literal
string_literal := regular_string | verbatim_string | interpolated_string | raw_string | interpolated_raw_string
```

Rules of thumb:
- Use raw string literals for multi-line text, JSON, regex, and generated code.
- Use verbatim strings for Windows paths or simpler multi-line text.
- Use interpolated strings for formatting; prefer structured logging placeholders over eager string interpolation when logging APIs do not optimize interpolation.
- Numeric literals can use `_` separators and binary/hex prefixes where supported.

### Special tokens

Important non-operator token modifiers:
- `@` starts a verbatim identifier or verbatim string.
- `$` starts an interpolated string.
- `"""` starts a raw string literal.
- `_` can be a discard in declarations, patterns, deconstruction, and lambda parameters.
- `#nullable`, `#pragma`, `#if`, `#else`, `#endif`, `#line`, `#region` are directives, not runtime statements.

## 3. Compilation-unit grammar

Modern C# has two common compilation-unit shapes.

### Traditional

```ebnf
compilation_unit := extern_alias_directive* using_directive* global_attribute* namespace_member_declaration*
namespace_member_declaration := namespace_declaration | type_declaration
```

### Top-level statements

```ebnf
compilation_unit := using_directive* global_attribute* statement* namespace_member_declaration*
```

Top-level statements are valid in one compilation unit per executable program. Use them for small console tools and samples; prefer explicit `Program`/host setup when the app has DI, logging, lifecycle, tests, or multiple entrypoint concerns.

## 4. Namespaces and using directives

```ebnf
using_directive := using_alias_directive | using_namespace_directive | using_static_directive
using_namespace_directive := 'using' namespace_name ';'
using_alias_directive := 'using' identifier '=' namespace_or_type_name ';'
using_static_directive := 'using' 'static' type_name ';'
namespace_declaration := file_scoped_namespace | block_scoped_namespace
file_scoped_namespace := 'namespace' qualified_identifier ';'
block_scoped_namespace := 'namespace' qualified_identifier namespace_body
```

Prefer file-scoped namespaces for new files when the repository uses them. Use `global using` in shared project infrastructure only when it reduces repeated imports without hiding important dependencies.

## 5. Types and type parameters

```ebnf
type := value_type | reference_type | type_parameter | pointer_type | function_pointer_type
value_type := struct_type | enum_type | nullable_value_type | tuple_type
reference_type := class_type | interface_type | array_type | delegate_type | dynamic | nullable_reference_type
nullable_value_type := non_nullable_value_type '?'
nullable_reference_type := reference_type '?'
tuple_type := '(' tuple_element (',' tuple_element)+ ')'
```

### Generic type parameters and constraints

```ebnf
type_parameter_list := '<' type_parameter (',' type_parameter)* '>'
constraint_clause := 'where' type_parameter ':' constraint (',' constraint)*
constraint := primary_constraint | secondary_constraint | constructor_constraint
primary_constraint := 'class' | 'class?' | 'struct' | 'notnull' | 'unmanaged' | type_name
constructor_constraint := 'new()'
```

Constraint ordering matters: primary constraint first, `new()` last. Use constraints to encode requirements instead of runtime type checks.

## 6. Type declarations

```ebnf
type_declaration := class_declaration | struct_declaration | interface_declaration | enum_declaration | delegate_declaration | record_declaration
class_declaration := attributes? modifiers? 'class' identifier type_parameter_list? base_list? constraint_clause* class_body ';'?
struct_declaration := attributes? modifiers? ('struct' | 'readonly' 'struct' | 'ref' 'struct' | 'readonly' 'ref' 'struct') identifier ...
record_declaration := attributes? modifiers? 'record' ('class' | 'struct')? identifier parameter_list? base_list? constraint_clause* record_body ';'?
interface_declaration := attributes? modifiers? 'interface' identifier type_parameter_list? interface_base? constraint_clause* interface_body ';'?
enum_declaration := attributes? modifiers? 'enum' identifier enum_base? enum_body ';'?
delegate_declaration := attributes? modifiers? 'delegate' return_type identifier type_parameter_list? parameter_list constraint_clause* ';'
```

Guidance:
- Use `class` for identity, mutable lifecycle, DI services, framework objects, and inheritance hierarchies.
- Use `record class` for immutable DTOs/value objects with reference semantics.
- Use `record struct` or `readonly record struct` for small values where copying is acceptable and measured.
- Use `readonly struct` for immutable value types to avoid defensive copies.
- Avoid mutable public fields. Use properties or methods.
- Use `file` types for helper implementation details local to one file when supported.

## 7. Member declarations

Common member forms:

```ebnf
member_declaration := constant | field | method | property | event | indexer | operator | conversion_operator | constructor | static_constructor | finalizer | nested_type
field := attributes? modifiers? type variable_declarators ';'
method := attributes? modifiers? return_type identifier type_parameter_list? parameter_list constraint_clause* method_body
property := attributes? modifiers? type identifier '{' accessor_declarations '}' | expression_body ';'
constructor := attributes? modifiers? identifier parameter_list constructor_initializer? body
```

Accessor grammar:

```ebnf
accessor_declarations := get_accessor? set_or_init_accessor?
get_accessor := attributes? accessor_modifier? 'get' accessor_body
set_or_init_accessor := attributes? accessor_modifier? ('set' | 'init') accessor_body
```

Use `required` for properties that must be assigned during object initialization. Use `init` when mutation after initialization should be disallowed. Do not put heavy work in `get` accessors.

Parameter modifiers:

```ebnf
parameter_modifier := 'ref' | 'out' | 'in' | 'params' | 'this' | 'scoped'
```

Use `in`/`ref readonly` only for large structs or measured hot paths. Do not expose `ref` returns unless lifetime and aliasing are obvious.

## 8. Statements

```ebnf
statement := labeled_statement | declaration_statement | embedded_statement
embedded_statement := block | empty_statement | expression_statement | selection_statement | iteration_statement | jump_statement | try_statement | checked_statement | unchecked_statement | lock_statement | using_statement | yield_statement | unsafe_statement | fixed_statement
selection_statement := if_statement | switch_statement
iteration_statement := while_statement | do_statement | for_statement | foreach_statement
jump_statement := break | continue | goto | return | throw
```

Guidance:
- Use guard clauses for invalid arguments and early exits.
- Use `using` declarations for deterministic disposal in a clear scope.
- Use `await using` for `IAsyncDisposable` resources.
- Use exception filters (`catch (Exception ex) when (...)`) when the filter is side-effect free and improves clarity.
- Avoid swallowing exceptions. Catch only when you can add context, recover, retry, translate, or intentionally suppress.

## 9. Expressions and operator precedence

Highest to lowest precedence:

1. Primary: member access `x.y`, invocation `f(x)`, element access `a[i]`, null-conditional `?.`/`?[]`, postfix `x++`, `x--`, null-forgiving `x!`, `new`, `typeof`, `checked`, `unchecked`, `default`, `nameof`, `delegate`, `sizeof`, `stackalloc`, pointer member access `x->y`.
2. Unary: `+x`, `-x`, `!x`, `~x`, prefix `++x`, `--x`, index-from-end `^x`, cast `(T)x`, `await`, address-of `&x`, pointer indirection `*x`, `true`, `false`.
3. Range: `x..y`.
4. `switch` and `with` expressions.
5. Multiplicative: `*`, `/`, `%`.
6. Additive: `+`, `-`.
7. Shift: `<<`, `>>`, `>>>`.
8. Relational/type: `<`, `>`, `<=`, `>=`, `is`, `as`.
9. Equality: `==`, `!=`.
10. Logical/bitwise AND: `&`.
11. Logical/bitwise XOR: `^`.
12. Logical/bitwise OR: `|`.
13. Conditional AND: `&&`.
14. Conditional OR: `||`.
15. Null-coalescing: `??`.
16. Conditional: `?:`.
17. Assignment and lambda: `=`, compound assignments, `??=`, `=>`.

Associativity: binary operators are left-associative except assignment, `??`, lambdas, and `?:`, which are right-associative. Operand evaluation is left to right, with conditional evaluation for `&&`, `||`, `??`, `??=`, `?.`, `?[]`, and `?:`.

## 10. Pattern matching

```ebnf
pattern := declaration_pattern | type_pattern | constant_pattern | relational_pattern | property_pattern | positional_pattern | var_pattern | discard_pattern | list_pattern | logical_pattern | parenthesized_pattern
logical_pattern := pattern 'and' pattern | pattern 'or' pattern | 'not' pattern
property_pattern := type? '{' subpattern_list? '}'
positional_pattern := type? '(' subpattern_list? ')'
list_pattern := '[' pattern_list? ']'
```

Use pattern matching to express shape checks, null checks, and simple discriminated logic. Avoid very large switch expressions with complex guards; move logic into named methods.

## 11. LINQ query expressions

```ebnf
query_expression := from_clause query_body
from_clause := 'from' type? identifier 'in' expression
query_body := query_body_clause* select_or_group_clause query_continuation?
query_body_clause := from_clause | let_clause | where_clause | join_clause | orderby_clause
```

Query expressions translate to method calls (`Select`, `Where`, `GroupBy`, `Join`, etc.). Prefer method syntax for short transformations and query syntax for multi-clause joins/grouping. Avoid multiple enumeration of deferred queries; materialize intentionally with `ToArray`, `ToList`, or `ToDictionary` when needed.

## 12. Async, iterators, and unsafe code

Async methods:

```ebnf
async_method := 'async'? return_type identifier parameter_list method_body
async_return_type := void | Task | Task<T> | ValueTask | ValueTask<T> | custom_task_like
```

Rules:
- `async void` is for event handlers only.
- Propagate cancellation and do not ignore returned tasks.
- Use `ConfigureAwait(false)` in libraries only when repository policy requires it; it is usually unnecessary in modern ASP.NET Core.

Iterators:

```ebnf
iterator_method := return_type identifier parameter_list block_with_yield
yield_statement := 'yield' 'return' expression ';' | 'yield' 'break' ';'
```

Unsafe grammar (`unsafe`, pointers, `fixed`, `stackalloc`, function pointers) must be justified and usually requires `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>`. Prefer `Span<T>`, `Memory<T>`, `MemoryMarshal`, and safe APIs before unsafe code.

## 13. Nullability grammar and flow rules

Nullable reference annotations are compile-time contracts, not runtime wrappers.

```csharp
string nonNull = "x";
string? maybe = GetMaybe();
if (maybe is null) return;
Console.WriteLine(maybe.Length); // flow state is not-null here
```

Use attributes from `System.Diagnostics.CodeAnalysis` when simple flow analysis cannot express the contract: `[NotNull]`, `[MaybeNull]`, `[NotNullWhen(true)]`, `[MemberNotNull]`, `[DoesNotReturn]`.

Do not use `!` to silence warnings unless an invariant is guaranteed outside compiler flow and a nearby comment states that invariant.

## 14. Feature-version gates to check

Check `LangVersion` before using:
- C# 9: records, init-only setters, top-level statements, pattern enhancements.
- C# 10: file-scoped namespaces, global usings, record structs, lambda improvements.
- C# 11: raw string literals, required members, generic math/static abstract interface members, list patterns.
- C# 12: collection expressions, primary constructors, alias any type, default lambda parameters.
- C# 13+: params collections, lock improvements, partial properties/indexers, ref/unsafe improvements.
- C# 14 preview/current docs: extension members and other newer syntax may require preview tooling.

Use older syntax when targeting older frameworks, older SDKs, Unity, Xamarin/legacy platforms, source generators, or repositories that pin compiler versions.
