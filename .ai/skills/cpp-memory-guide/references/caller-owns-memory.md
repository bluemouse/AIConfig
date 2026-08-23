# caller-owns-memory: Caller-Owns-Memory in C++

## Guideline

A library never allocates heap memory; the caller provides all storage and the library operates on it. Functions take non-owning views (`std::span`, references) plus capacities and return status or `std::expected` — never freshly allocated owning pointers.

## Rationale

Hidden allocations are the root of leaks, ownership confusion, and surprise allocator cost on a hot path. When the caller owns the memory, it picks the strategy (stack buffer, `std::vector`, arena, PMR scratch), there is nothing to leak, and batch processing needs no per-item `new`. It also makes the library trivially testable and embeddable (no global allocator dependency). Maps to C++ Core Guidelines **I.11** (never transfer ownership by raw pointer).

## How to Apply

1. Init functions bind library state to caller-provided storage (`std::span<T>`, `std::vector&`) — not internally `new`'d buffers.
2. Operations check capacity/bounds and return an error on overflow instead of growing silently.
3. Complex operations that need scratch space take a caller-provided work buffer (size via a `required_scratch_bytes()` query).
4. Return values are status codes, indices, or handles — never `T*` or `unique_ptr` the caller must remember to free.
5. Mark ownership-sensitive returns `[[nodiscard]]`.

## Example

```cpp
#include <span>
#include <expected>

struct EntitySystem {
    std::span<float> x, y;
    std::size_t count = 0;
};

[[nodiscard]] std::expected<void, std::errc>
entity_system_init(EntitySystem& s, std::span<float> x, std::span<float> y) {
    if (x.size() != y.size()) return std::unexpected(std::errc::invalid_argument);
    s.x = x; s.y = y; s.count = 0;
    return {};
}

[[nodiscard]] std::expected<void, std::errc>
entity_add(EntitySystem& s, float x, float y) {
    if (s.count >= s.x.size()) return std::unexpected(std::errc::no_buffer_space);
    s.x[s.count] = x; s.y[s.count] = y; ++s.count;
    return {};
}

// Bad: hidden allocation — who owns it? leaks on exception paths, heap on hot path.
auto make_buffer(std::size_t n) { return std::make_unique<float[]>(n); }
```

## Gotchas

- A scratch-size query must stay in lockstep with the code that consumes the buffer; a mismatch is a buffer overflow.
- "Caller owns" is a whole-API contract — one function that secretly `new`s breaks the leak-free guarantee for everyone.
- Returning `std::string` or `std::vector` by value transfers ownership to the caller — that is fine for cold paths, not for per-frame hot loops.

## Related

[references/arenas-and-pools.md](./arenas-and-pools.md), [references/ownership-and-lifetimes.md](./ownership-and-lifetimes.md), [references/pmr-and-verification.md](./pmr-and-verification.md)
