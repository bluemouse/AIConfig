# ownership-and-lifetimes: Ownership and Lifetimes in C++

## Guideline

Every allocation has exactly one owner responsible for freeing it, and a clearly bounded lifetime; everyone else borrows via `std::span`, references, or raw non-owning pointers with documented scope. Decide both explicitly — never leave ownership implicit.

## Rationale

Most memory bugs are ownership bugs: a leak (nobody freed), a double-free (two owners freed), or a use-after-free (freed while still borrowed). C++ gives you tools to encode ownership in types (`std::unique_ptr`, move semantics); use them instead of conventions alone. Grouping by lifetime turns N free decisions into one (reset the arena at the boundary), which is both faster and harder to get wrong.

## How to Apply

1. For each resource, answer: _who frees it_ and _until when does it live_. Encode in types (`unique_ptr` = owner, `span`/`T&` = borrow).
2. Prefer **single ownership**: `std::unique_ptr` by default; `std::shared_ptr` only when sharing is required and lifetimes cannot be scope-bound.
3. **Transfer ownership** with move (`return std::move(ptr)` or return by value from `make_unique`) — never by raw pointer (Core Guidelines **I.11**).
4. **Tie lifetime to a phase** (frame, level, request) and reclaim via arena/PMR reset rather than individual deletes.
5. When storage may relocate (`std::vector` reallocation), reference by **index/handle**, not pointer into the container.
6. Follow **Rule of 0** (compiler-generated special members) when possible; Rule of 3/5 when you own a raw resource — see [references/raii-and-smart-pointers.md](./raii-and-smart-pointers.md).

## Example

```cpp
#include <memory>
#include <span>

using Handle = std::uint32_t;

class Pool {
public:
    [[nodiscard]] Handle alloc();
    std::span<Entity> borrow(Handle h);  // non-owning; valid until reset/free
    void free(Handle h);                 // single owner reclaims slot
    void reset();                        // end-of-phase: everything dies together
};

// Good: ownership in the return type.
[[nodiscard]] std::unique_ptr<Graph> load_graph(std::string_view path);

// Bad: ambiguous — caller or callee frees?
Entity* get_node(Graph& g, int i);
```

## Gotchas

- Returning a raw pointer rarely documents ownership; prefer `unique_ptr`, `optional<T&>`, or `_borrow`/`_take` naming.
- A `span` or reference cached across `vector` push_back or arena reset dangles — re-fetch or hold a handle.
- `shared_ptr` cycles leak; do not use it to paper over unclear ownership. Prefer explicit parent/child lifetimes.
- `std::move` on a `const` object copies — only move from non-const sources.

## Related

[references/arenas-and-pools.md](./arenas-and-pools.md), [references/caller-owns-memory.md](./caller-owns-memory.md), [references/raii-and-smart-pointers.md](./raii-and-smart-pointers.md)
