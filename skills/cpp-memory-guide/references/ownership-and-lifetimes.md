# ownership-and-lifetimes: Ownership and Lifetimes in C++

## Guideline

Every allocation has exactly one owner responsible for freeing it, and a clearly bounded lifetime; everyone else borrows via `std::span`, references, or raw non-owning pointers with documented scope. Never transfer ownership by raw pointer (Core Guidelines **I.11**) — encode ownership in types (`unique_ptr` = owner, `span`/`T&` = borrow), and tie lifetimes to a phase (frame, level, request) reclaimed via arena/PMR reset rather than individual deletes.

## Gotchas

- A `span` or reference cached across `vector` push_back or arena reset dangles — re-fetch or hold an index/handle into the container.
- `shared_ptr` cycles leak; do not use it to paper over unclear ownership. Prefer explicit parent/child lifetimes.
- `std::move` on a `const` object copies — only move from non-const sources.
- Custom deleters and manual frees must match the actual allocator: `delete` vs `delete[]` vs `free` — the wrong one is undefined behavior.
- Arena placement-new objects still need an explicit destructor call before arena reset — wrap `~T()` in a scope guard; RAII members do not run automatically for raw placement-constructed storage.

## Related

[references/arenas-and-pools.md](./arenas-and-pools.md), [references/caller-owns-memory.md](./caller-owns-memory.md)
