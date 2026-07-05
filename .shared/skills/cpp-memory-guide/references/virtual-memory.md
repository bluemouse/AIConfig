# virtual-memory: Virtual-Memory Tricks Beyond Reserve/Commit

## Guideline

Treat address-space reservation as nearly free (especially on 64-bit) and exploit it: back cap-free arrays by reserving a huge range and committing on touch, grow buffers in page multiples, alias a second mapping for a gapless ring buffer, and use an end-of-page allocator to catch overruns. For reserve/commit basics see [references/arenas-and-pools.md](./arenas-and-pools.md); this is the toolbox built on top.

## Rationale

Reserving address space only consumes page-table entries, not physical RAM — and on 64-bit the address space is effectively unlimited, so virtual fragmentation is irrelevant. That decouples "how big could this get" from "how much memory does it use," which removes static caps, realloc-and-copy on growth, and split-on-wrap logic in ring buffers.

## How to Apply

1. **Cap-free arrays** - Reserve `MAX * sizeof(T)` up front; commit pages only as the array grows; pointers into committed range stay valid (no `vector` reallocation copy).
2. **Page-aligned growth** - Grow by whole pages instead of geometric doubling; cuts average internal fragmentation.
3. **Gapless ring buffer** - Map a second virtual region after the buffer onto the same physical pages; wraparound needs no split logic.
4. **End-of-page allocator (debug)** - Place allocation end flush against a page boundary with the next page unmapped; overrun faults immediately.
5. Wrap OS handles in **RAII guards** (`mmap`/`munmap`, `VirtualAlloc`/`VirtualFree`) — never leak reserved regions on exception paths.

## Example

```cpp
// Thin RAII wrapper (platform-specific impl omitted).
class VirtualBlock {
public:
    static std::optional<VirtualBlock> reserve(std::size_t bytes);
    bool commit(std::size_t additional_bytes);
    std::span<std::byte> bytes() const;
    ~VirtualBlock();  // releases reservation
};

// Cap-free push: commit next page when full; &items[i] never moves.
void push(VirtualBlock& block, std::size_t& count, Element e) {
    if (needs_commit(block, count))
        block.commit(PAGE_SIZE);
    static_cast<Element*>(block.bytes().data())[count++] = e;
}
```

## Counter-Example

On 32-bit or memory-tight embedded targets, large reservations trade away scarce address space — prefer capped containers or geometric growth there.

## Gotchas

- Linux overcommits; Windows separates reserve from commit — match the OS contract you target.
- Ring-buffer double-mapping can race if the adjacent region is taken — reserve alias space atomically or retry.
- End-of-page debug allocators must keep freed pages unmapped so use-after-free still faults.

## Related

[references/arenas-and-pools.md](./arenas-and-pools.md), [references/ownership-and-lifetimes.md](./ownership-and-lifetimes.md), [references/raii-and-smart-pointers.md](./raii-and-smart-pointers.md)
