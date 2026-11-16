---
name: cpp-memory-guide
description: "Guide C++20 memory design: RAII, unique_ptr/shared_ptr, std::span borrows, caller-owned buffers, arena/bump/pool allocators, std::pmr, ownership and lifetimes, virtual-memory reserve/commit, leak/use-after-free prevention. Use when implementing or reviewing C++ allocation, custom allocators, move semantics, API buffer ownership, or debugging memory bugs with sanitizers — even if the user says 'memory leak' without naming an allocator."
---

# C++ Memory Guide (C++20)

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md`. Resolve paths to `references/` from that directory.

C++20 memory design: ownership, allocators, RAII, smart pointers, `span`, PMR, and sanitizer workflows. For general C++ style (naming, concurrency, build) and the C++20 language-standard policy, see [`../cpp-coding/SKILL.md`](../cpp-coding/SKILL.md).

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

## Reference routing

Load the matching reference before designing or reviewing in that area:

| Task | Read |
|------|------|
| Caller-owned API buffers — caller-provided storage, no hidden allocation on hot paths, non-allocating libraries | [references/caller-owns-memory.md](references/caller-owns-memory.md) |
| Ownership and lifetimes — who frees, one owner + `span`/reference borrows, move vs copy, group-by-lifetime reset, handles over pointers, `unique_ptr`/`shared_ptr` choice, RAII | [references/ownership-and-lifetimes.md](references/ownership-and-lifetimes.md) |
| Arena/bump, object pools (fixed-size slots + free list), placement new, per-frame/per-request scratch reset | [references/arenas-and-pools.md](references/arenas-and-pools.md) |
| Virtual-memory reserve/commit — cap-free arrays, gapless ring buffers, page tricks | [references/virtual-memory.md](references/virtual-memory.md) |
| `std::pmr` scratch (`monotonic_buffer_resource`), ASan/LSan/UBSan, clang-tidy memory checks | [references/pmr-and-verification.md](references/pmr-and-verification.md) |

## Gotchas

- Two owners means double-free or leak; encode ownership in types, do not infer it.
- Mixing `new`/`delete` with `malloc`/`free` is undefined behavior — pick one strategy.

Reference-level gotchas (dangling borrows across `vector` growth or arena reset, bump-capacity checks, OS reserve/commit contracts) live in the reference they belong to.

## Companion Skills

| Skill | Path |
|-------|------|
| General C++20 style, Core Guidelines R.* overview | [../cpp-coding/SKILL.md](../cpp-coding/SKILL.md) |
| GPU device memory strategy | [../gpu-rendering-guide/SKILL.md](../gpu-rendering-guide/SKILL.md) |

## Tool notes

Host-neutral: the body and references apply to any coding agent.
