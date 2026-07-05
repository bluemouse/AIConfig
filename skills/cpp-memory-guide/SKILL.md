---
name: cpp-memory-guide
description: "Guide C++20 memory design: RAII, unique_ptr/shared_ptr, std::span borrows, caller-owned buffers, arena/bump/pool allocators, std::pmr, ownership and lifetimes, virtual-memory reserve/commit, leak/use-after-free prevention. Use when implementing or reviewing C++ allocation, custom allocators, move semantics, API buffer ownership, or debugging memory bugs with sanitizers — even if the user says 'memory leak' without naming an allocator."
---

# C++ Memory Guide (C++20)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` from that directory.

C++20 memory design: ownership, allocators, RAII, smart pointers, `span`, PMR, and sanitizer workflows. For general C++ style (naming, concurrency, build), see [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md).

## Language Standard

- Target **C++20** (`-std=c++20` or CMake `cxx_std_20`).
- Use `std::span`, `std::pmr`, concepts where they clarify ownership APIs.
- Do **not** use C++23-only features (`std::expected` in std, `std::print`) unless the project explicitly allows — use `std::optional`, error codes, or project-specific expected types instead.

## When to Use

- Designing C++ APIs with clear buffer ownership (caller-provided storage, no hidden `new`)
- Choosing allocators: heap, arena, pool, PMR scratch, virtual-memory reserve/commit
- Fixing or preventing leaks, double-free, use-after-free, iterator invalidation
- Implementing move semantics and Rule of 0/3/5 for resource-owning classes
- Setting up ASan/LSan/UBSan for memory debugging

## When NOT to Use

- Non-C++ code — out of scope (use a language-specific memory/allocator skill)
- GPU device memory (Vulkan/D3D12 tiers, staging, VRAM sub-allocation) — use **gpu-rendering-guide**
- General C++ style without a memory/ownership focus — use **cpp-coding**

## Essentials

- **Caller owns memory** - APIs take caller-provided storage; never allocate internally on hot paths, see [references/caller-owns-memory.md](references/caller-owns-memory.md)
- **Group by lifetime** - Allocate together what dies together; reset as a unit, see [references/ownership-and-lifetimes.md](references/ownership-and-lifetimes.md)
- **One owner** - `unique_ptr` or explicit single owner frees; everyone else borrows via `span`/reference, see [references/ownership-and-lifetimes.md](references/ownership-and-lifetimes.md)
- **Handles over pointers** - Reference relocatable storage by index/handle, not pointer into a growing or reset allocation; reserve/commit blocks are the exception (stable base until reset), see [references/ownership-and-lifetimes.md](references/ownership-and-lifetimes.md)

## Allocation Strategy

- **Arena / bump** - Pointer-bump from a block; reset frees everything at once, see [references/arenas-and-pools.md](references/arenas-and-pools.md)
- **Object pool** - Fixed-size slots + free list; O(1) alloc/free, stable addresses, see [references/arenas-and-pools.md](references/arenas-and-pools.md)
- **Scratch / temp** - Per-frame/per-request PMR or arena reset each cycle, see [references/arenas-and-pools.md](references/arenas-and-pools.md), [references/pmr-and-verification.md](references/pmr-and-verification.md)
- **Virtual-memory reserve/commit** - Stable-address growable storage, see [references/virtual-memory.md](references/virtual-memory.md)

## C++ Idioms

- **RAII** - Bind cleanup to scope; no naked `delete`, see [references/raii-and-smart-pointers.md](references/raii-and-smart-pointers.md)
- **`unique_ptr` default, `shared_ptr` exception** - Move to transfer ownership; Core Guidelines R.11, I.11
- **`std::span` / `string_view` borrows** - Non-owning parameters; document lifetime in comments or types
- **`std::pmr::monotonic_buffer_resource`** - Standard scratch arena for parse/build temporaries
- **Rule of 0/3/5** - Let RAII members manage resources; see decision table in [references/raii-and-smart-pointers.md](references/raii-and-smart-pointers.md)

## Reference Routing

| Task | Read |
|------|------|
| API buffer ownership, non-allocating libraries | [references/caller-owns-memory.md](references/caller-owns-memory.md) |
| Who frees, move vs copy, handles vs pointers | [references/ownership-and-lifetimes.md](references/ownership-and-lifetimes.md) |
| Arena, pool, placement new, frame scratch | [references/arenas-and-pools.md](references/arenas-and-pools.md) |
| Cap-free arrays, gapless rings, page tricks | [references/virtual-memory.md](references/virtual-memory.md) |
| Smart pointers, Rule of 0/3/5, custom deleters | [references/raii-and-smart-pointers.md](references/raii-and-smart-pointers.md) |
| std::pmr, ASan/LSan/UBSan, clang-tidy memory checks | [references/pmr-and-verification.md](references/pmr-and-verification.md) |

## Gotchas

- An arena cannot free individual objects — anything outliving reset is use-after-free; match lifetimes.
- Bump allocation has no bounds safety unless you check capacity; assert or return error on overflow.
- Two owners means double-free or leak; encode ownership in types, do not infer it.
- Pointers into a `vector` or reset arena dangle — prefer indices/handles across boundaries (reserve/commit virtual-memory blocks are the exception: stable base until reset).
- `vector` reallocation invalidates all pointers/references into it — `reserve` early or use stable storage.
- Mixing `new`/`delete` with `malloc`/`free` is undefined behavior — pick one strategy.
- Exception-throwing code paths must not leak — RAII or scope guards, never manual cleanup only on success path.

## Progressive Disclosure

- Read [references/caller-owns-memory.md](references/caller-owns-memory.md) - Load when designing an API's allocation boundary or a non-allocating library
- Read [references/ownership-and-lifetimes.md](references/ownership-and-lifetimes.md) - Load when deciding who owns/frees memory and how long it lives
- Read [references/arenas-and-pools.md](references/arenas-and-pools.md) - Load when choosing arena, pool, scratch, or virtual-memory-backed allocation
- Read [references/virtual-memory.md](references/virtual-memory.md) - Load when using address-space reservation for cap-free arrays or ring buffers
- Read [references/raii-and-smart-pointers.md](references/raii-and-smart-pointers.md) - Load when implementing resource-owning classes or choosing smart pointers
- Read [references/pmr-and-verification.md](references/pmr-and-verification.md) - Load when wiring PMR scratch or running memory sanitizers

## Companion Skills

| Skill | Path |
|-------|------|
| General C++20 style, Core Guidelines R.* overview | [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md) |
| GPU device memory strategy | [../gpu-rendering-guide/SKILL.md](../gpu-rendering-guide/SKILL.md) |
