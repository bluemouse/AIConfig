# Sources

## C++ Core Guidelines (memory & ownership)

- **URL:** https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines — R.* (resource management), I.11 (never transfer ownership by raw pointer), E.6 (RAII), Per.19 (predictable allocation)
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → C++ idioms, Gotchas, Essentials
  - `references/raii-and-smart-pointers.md`, `references/ownership-and-lifetimes.md`, `references/caller-owns-memory.md`
- **Aspects extracted:**
  - RAII, `unique_ptr` default, non-owning borrows, Rule of 0/3/5, no hidden allocation in APIs

## std::pmr and std::span (cppreference)

- **URL:** https://en.cppreference.com/w/cpp/memory/memory_resource , https://en.cppreference.com/w/cpp/container/span
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `references/pmr-and-verification.md`, `references/arenas-and-pools.md`, `references/caller-owns-memory.md`
- **Aspects extracted:**
  - `monotonic_buffer_resource`, `polymorphic_allocator`, non-owning `span` parameters

## LLVM sanitizers

- **URL:** https://clang.llvm.org/docs/AddressSanitizer.html , https://clang.llvm.org/docs/LeakSanitizer.html , https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `references/pmr-and-verification.md`
- **Aspects extracted:**
  - ASan/LSan/UBSan flags, leak detection workflow, CI debug builds

## Region-based / arena memory management

- **URL:** https://en.wikipedia.org/wiki/Region-based_memory_management and Tofte & Talpin, "Region-Based Memory Management" (Information and Computation, 1997)
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Allocation strategy, Ownership
  - Lifetime-by-reset and arena semantics
- **Aspects extracted:**
  - Arena/bump/linear allocators, lifetime reset, scratch arenas → `references/arenas-and-pools.md`

## Custom allocators (pools, freelists, bump)

- **URL:** Game Engine Architecture (J. Gregory), Memory Management chapter; Andrei Alexandrescu, "std::allocator Is to Allocation what std::vector Is to Vexation" (CppCon 2015)
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Allocation strategy
- **Aspects extracted:**
  - Object pools, free lists, fragmentation, per-allocation overhead → `references/arenas-and-pools.md`
  - Caller-provided storage / non-allocating APIs → `references/caller-owns-memory.md`

## Virtual memory reserve/commit

- **URL:** OS virtual-memory APIs — `mmap`/`mprotect` (POSIX), `VirtualAlloc` (Windows); reserve-then-commit growable-array technique
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Allocation strategy
- **Aspects extracted:**
  - Reserve large / commit on demand, stable-address growable arrays → `references/virtual-memory.md`

## Ownership & lifetimes

- **URL:** Ownership models as in RAII (C++) and the Rust ownership/borrow model — https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html
- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Ownership, Essentials
- **Aspects extracted:**
  - Single-owner/borrow, lifetime-by-scope, leak/double-free/use-after-free avoidance, refcount as exception → `references/ownership-and-lifetimes.md`

## Game-engine development blog (archive)

- **Last reviewed:** 2026-07-05
- **Used for:**
  - `SKILL.md` → Allocation strategy
  - Practical virtual-memory techniques built on address-space reservation
- **Aspects extracted:**
  - "Virtual Memory Tricks" — reserve cheap address space vs commit physical, cap-free never-moving arrays, page-aligned growth to cut fragmentation, gapless ring buffer via double-mapping, end-of-page bounds-checking allocator → `references/virtual-memory.md`

## Refresh Workflow

1. Re-read the upstream source(s) above
2. Diff against the prior pull (or scan for newly added sections)
3. For each changed area, update the corresponding `references/<topic>.md`
4. Bump **Last reviewed** date above
