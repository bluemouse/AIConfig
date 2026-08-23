# arenas-and-pools: Arenas, Pools, and Bulk Allocators in C++

## Guideline

Allocate from arena/bump and pool allocators over contiguous blocks and reclaim by lifetime reset, instead of per-object `new`/`delete` or unscoped `malloc`/`free`.

## Rationale

Per-object general-purpose allocation is slow (lock + free-list search), fragments the heap, scatters objects across random addresses, and adds header overhead. An arena allocates by bumping a pointer (a few instructions, no search) and places objects contiguously; reclaiming a whole lifetime is one O(1) reset and leak-proof by construction. Pools give O(1) allocate/free of same-size objects with stable addresses and no fragmentation.

## Techniques

- **Arena / bump / linear** - One block + an offset; allocate by advancing the offset (aligned); "free" by resetting the offset to zero. No individual frees.
- **Placement new** - Construct objects in arena storage: `new (ptr) T(args)`; call destructors manually before reset if non-trivial.
- **Object pool** - Fixed-size slots for one type; a free list threads through dead slots. O(1) alloc/free, stable storage.
- **Lifetime by reset** - Group allocations by lifetime (per-frame, per-level); reset at the boundary.
- **Scratch / temp arena** - Per-cycle arena for transient buffers, reset every cycle.
- **`std::pmr::monotonic_buffer_resource`** - Standard bump allocator backed by caller buffer or upstream resource; see [references/pmr-and-verification.md](./pmr-and-verification.md).
- **Virtual-memory reserve/commit** - Reserve a huge virtual range once, commit pages lazily; block never moves. See [references/virtual-memory.md](./virtual-memory.md).

## How to Apply

1. Identify allocations that share a lifetime; route them through one arena or PMR resource.
2. Implement aligned bump (`align_up(offset, align)`); check capacity; return null or error on overflow.
3. Reset at the lifetime boundary — no per-object `delete`.
4. For long-lived same-type objects with individual lifetimes, use a pool with a free list.

## Example

```cpp
#include <cstdint>
#include <memory>
#include <new>
#include <span>

struct Arena {
    std::span<std::byte> block;
    std::size_t used = 0;

    [[nodiscard]] void* alloc(std::size_t size, std::size_t align) {
        std::size_t off = (used + align - 1) & ~(align - 1);
        if (off + size > block.size()) return nullptr;
        used = off + size;
        return block.data() + off;
    }
    void reset() { used = 0; }
};

template<class T, class... Args>
T* arena_create(Arena& a, Args&&... args) {
    void* p = a.alloc(sizeof(T), alignof(T));
    return p ? new (p) T(std::forward<Args>(args)...) : nullptr;
}

// PMR scratch (C++17/20): stack buffer + monotonic resource
alignas(std::max_align_t) std::byte buf[64 * 1024];
std::pmr::monotonic_buffer_resource scratch{buf, sizeof(buf)};
std::pmr::vector<int> temp{&scratch};  // all temp allocations die with scratch reset
```

## Gotchas

- Arenas cannot free individual objects; anything outliving reset is use-after-free — match lifetimes.
- Placement-new objects with non-trivial destructors need explicit `ptr->~T()` before arena reset.
- Pointers into a growing `std::vector` invalidate on reallocation — prefer indices/handles. Reserve/commit arenas are the exception (stable base address until reset).
- PMR monotonic resources do not call destructors on reset — same rule as manual arenas.

## Related

[references/caller-owns-memory.md](./caller-owns-memory.md), [references/ownership-and-lifetimes.md](./ownership-and-lifetimes.md), [references/pmr-and-verification.md](./pmr-and-verification.md), [references/virtual-memory.md](./virtual-memory.md)
