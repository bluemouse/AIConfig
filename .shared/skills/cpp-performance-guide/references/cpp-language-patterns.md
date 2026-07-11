# C++ Language Patterns and Anti-patterns

## Table of contents
- Hot path review mindset
- Algorithms and recomputation
- Containers and lookups
- Ownership and type erasure
- Strings and formatting
- Virtual dispatch and inlining
- Exceptions, RTTI, and logging
- I/O

## Hot path review mindset

First decide whether code is hot. Startup-only, configuration, error handling, and rare admin flows usually should optimize for clarity. Hot paths, tight loops, frame loops, request paths, kernels, and frequently called callbacks need stricter scrutiny.

## Algorithms and recomputation

Flag:

- accidental `O(n^2)` loops,
- repeated sorting of mostly unchanged data,
- recomputing rolling values from scratch,
- repeated parsing or validation inside item loops,
- repeated map lookups that could be hoisted,
- creating intermediate vectors just to iterate once.

Prefer:

- incremental algorithms,
- precomputation with clear invalidation,
- direct indexing or stable IDs,
- streaming/batched processing,
- range/view pipelines only when they do not obscure allocations or repeated work.

## Containers and lookups

Smells and fixes:

- `std::map` in hot lookups -> consider `std::unordered_map` or a flat hash map if ordering is not needed.
- `std::list` traversal -> prefer `std::vector`/`std::deque` unless splice/stable iterator requirements dominate.
- `std::unordered_map<std::string, V>` lookup by `string_view` -> use heterogeneous lookup with transparent hash/equality where supported.
- linear search on sorted data -> use `lower_bound`/`binary_search`.
- push loops without `reserve()` -> reserve capacity.
- vector of polymorphic heap objects -> group by type, use `std::variant`, or store indices/SoA when appropriate.

## Ownership and type erasure

Smells:

- `std::shared_ptr` in hot loops or per-item structures when unique ownership works,
- `std::function` allocated or invoked in inner loops,
- lambdas created inside hot loops,
- capturing large objects by value,
- refcount increments on every item.

Alternatives:

- values or `std::unique_ptr`,
- template callables for compile-time dispatch,
- lightweight `function_ref`-style non-owning callable views when lifetime is clear,
- hoisted callbacks,
- references or spans for non-owning access.

## Strings and formatting

Smells:

- repeated `operator+` concatenation in a loop,
- `std::to_string` per item in hot logging/formatting,
- temporary `std::string` just for lookup,
- parsing JSON/text repeatedly in a hot path.

Fixes:

- reserve and append,
- use `std::format_to` or formatter APIs into an existing buffer,
- use `std::string_view` where lifetime is safe,
- parse once and reuse structured data,
- batch logs or use async logging outside hot loops.

## Virtual dispatch and inlining

Virtual calls are fine at coarse boundaries. They become suspicious inside tiny per-item kernels.

Options when measured hot:

- move dispatch outside the loop,
- devirtualize by storing concrete types,
- use CRTP or templates when type is known,
- use `std::variant` + `std::visit` when alternatives are closed,
- mark tiny helpers inline only when profiling/codegen shows call overhead or missed optimization.

## Exceptions, RTTI, and logging

Do not remove error handling for speed unless invariants are enforced elsewhere. In hot paths, avoid:

- throwing for ordinary control flow,
- `dynamic_cast` per item,
- logging per iteration,
- building expensive diagnostic strings unless enabled.

## I/O

Smells:

- open/close per item,
- unbuffered writes in hot loops,
- `std::endl` flushing repeatedly,
- database query per item,
- text stream extraction in a large parse loop.

Fixes:

- hold handles,
- batch and flush intentionally,
- stream once,
- memory-map huge read-only files when it simplifies measured I/O,
- prefer parse APIs that avoid per-field allocation.
