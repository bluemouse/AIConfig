# C++20 Core Guidelines

Rule-ID checklist derived from the [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines). Use it as a lookup when writing or reviewing; the external link holds the full rule text and rationale.

## Rule index

Key rule IDs per area — check the lines for the area under edit:

- **Philosophy & interfaces (P, I):** P.1 (express ideas directly), P.4 (statically type safe), P.5 (compile-time over run-time checks), P.8 (no leaks), P.10 (prefer immutable); I.2 (no non-const globals), I.4 (strongly typed interfaces), I.11 (never transfer ownership by raw pointer/reference), I.23 (few arguments)
- **Functions (F):** F.2/F.3 (single logical operation, short and simple), F.4 (constexpr when evaluable at compile time), F.6 (noexcept when it must not throw), F.16 (in-params: cheap by value, else `const&`; sinks by value), F.20/F.21 (return values or struct, not output parameters), F.43 (never return a pointer/reference to a local), F.53 (no reference captures in cross-thread lambdas), F.55 (no C-style variadics)
- **Classes (C):** C.2 (`class` if invariant, `struct` otherwise), C.20 (Rule of Zero), C.21 (Rule of Five when any special member is defined), C.35 (base dtor: public virtual or protected non-virtual), C.41 (constructor establishes invariants), C.46 (single-argument ctors `explicit`), C.67 (polymorphic classes suppress copy), C.128 (exactly one of `virtual`/`override`/`final`)
- **Resource management (R):** R.1 (RAII), R.3 (raw pointer = non-owning observer), R.5 (prefer scoped objects), R.11 (no explicit `new`/`delete`), R.20/R.21 (`unique_ptr` by default, `shared_ptr` only for shared ownership), R.22 (`make_shared`), R.13 (one resource allocation per expression)
- **Expressions & statements (ES):** ES.5 (small scopes, guard clauses), ES.20 (always initialize), ES.23 (`{}` initialization), ES.25 (`const`/`constexpr` by default), ES.45 (no magic constants), ES.46 (no narrowing), ES.47 (`nullptr`, never `0`/`NULL`), ES.48/ES.50 (no C-style casts, never cast away `const`), ES.100 (no signed/unsigned mixing)
- **Error handling (E):** E.2 (throw to signal a function cannot perform its task), E.6 (RAII to prevent leaks), E.12 (`noexcept` when throwing is impossible), E.14/E.15 (custom exception types; throw by value, catch by reference), E.16 (destructors/deallocation never fail), E.17 (don't catch everything everywhere)
- **Constants & immutability (Con):** Con.1 (immutable by default), Con.2 (const member functions), Con.3 (const pointer/ref parameters), Con.4 (const after construction), Con.5 (`constexpr` for compile-time values)
- **Concurrency (CP):** CP.2 (no data races), CP.3 (minimize shared writable data), CP.4 (tasks over threads), CP.8 (never `volatile` for synchronization), CP.20 (RAII locks, never manual `lock()`/`unlock()`), CP.21 (`scoped_lock` for multiple mutexes), CP.22 (no unknown code under a lock), CP.42 (always wait with a condition), CP.44 (name every guard), CP.100 (no lock-free without proven need)
- **Templates (T):** T.10 (concepts for all template arguments), T.11 (standard concepts first), T.13 (shorthand concept syntax), T.43 (`using` over `typedef`), T.120 (metaprogramming only when needed), T.144 (overload, don't specialize function templates)
- **Standard library (SL):** SL.con.1/SL.con.2 (`std::vector`/`std::array` over C arrays), SL.str.1/SL.str.2 (`std::string` owns, `string_view` observes), SL.io.50 (`'\n'`, not `std::endl`)
- **Enumerations (Enum):** Enum.1 (enums over macros), Enum.3 (`enum class`), Enum.5 (no ALL_CAPS enumerators), Enum.6 (no unnamed enums)
- **Source files & naming (SF, NL):** SF.1 (`.h`/`.cpp`), SF.7 (no `using namespace` at global scope in headers), SF.8 (include guards), SF.11 (self-contained headers), NL.5 (no Hungarian notation), NL.8 (consistent style), NL.9 (ALL_CAPS macros only), NL.10 (`underscore_style`)

## Performance (Per.*)

- **Per.1/Per.2** — don't optimize without reason or prematurely
- **Per.6** — no performance claims without measurements
- **Per.7** — design to enable optimization (clear hot paths, measurable structure)
- **Per.10** — rely on the static type system
- **Per.11** — move computation from run time to compile time
- **Per.19** — access memory predictably (contiguous data over pointer chasing)

For profiling and measurement workflow, see [build-and-verification.md](build-and-verification.md).

## Quick Reference Checklist

Before marking C++ work complete:

- [ ] No raw `new`/`delete` -- use smart pointers or RAII (R.11)
- [ ] Objects initialized at declaration (ES.20)
- [ ] Variables are `const`/`constexpr` by default (Con.1, ES.25)
- [ ] Member functions are `const` where possible (Con.2)
- [ ] `enum class` instead of plain `enum` (Enum.3)
- [ ] `nullptr` instead of `0`/`NULL` (ES.47)
- [ ] No narrowing conversions (ES.46)
- [ ] No C-style casts (ES.48)
- [ ] Single-argument constructors are `explicit` (C.46)
- [ ] Rule of Zero or Rule of Five applied (C.20, C.21)
- [ ] Base class destructors are public virtual or protected non-virtual (C.35)
- [ ] Templates are constrained with concepts (T.10)
- [ ] No `using namespace` in headers at global scope (SF.7)
- [ ] Headers have include guards and are self-contained (SF.8, SF.11)
- [ ] Locks use RAII (`scoped_lock`/`lock_guard`) (CP.20)
- [ ] Exceptions are custom types, thrown by value, caught by reference (E.14, E.15)
- [ ] `'\n'` instead of `std::endl` (SL.io.50)
- [ ] No magic numbers (ES.45)

Also complete the build and verification checklist in
[build-and-verification.md](build-and-verification.md#verification-checklist).
