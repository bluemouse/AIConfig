# pmr-and-verification: std::pmr and Memory Verification

## Guideline

Use `std::pmr` for polymorphic allocation (especially scratch and level-scoped work); verify memory correctness with AddressSanitizer, LeakSanitizer, and UBSan in CI and local debug builds.

## Rationale

`std::pmr` lets containers (`vector`, `string`, `unordered_map`) share a bump or pool resource without template allocator parameters everywhere. Sanitizers turn use-after-free, buffer overflow, and leaks into deterministic crashes with stack traces — cheaper than hunting corruption in production.

## std::pmr hierarchy

| Resource | Use |
|----------|-----|
| `monotonic_buffer_resource` | Bump/scratch; reset by destroying and recreating, or use fresh resource per frame |
| `unsynchronized_pool_resource` | Fixed/chunked sizes; faster than heap for many small allocs |
| `new_delete_resource()` | Fallback to global `::operator new` |
| Caller buffer + monotonic | Stack `byte buf[N]` backs scratch — zero heap for temporaries |

Wire into containers: `std::pmr::vector<T>` or `std::vector<T, std::pmr::polymorphic_allocator<T>>`.

## Verification

**Compile flags (GCC/Clang):**
```bash
-fsanitize=address,undefined -fno-omit-frame-pointer -g
# LeakSanitizer is included in ASan on Linux; macOS may need ASAN_OPTIONS=detect_leaks=1
```

**Run under sanitizers** for any change touching ownership, allocators, or raw pointers.

**clang-tidy checks:** `cppcoreguidelines-owning-memory`, `modernize-make-unique`, `modernize-make-shared`, `bugprone-unused-return-value`.

## Example

```cpp
#include <memory_resource>
#include <vector>

void parse_frame(std::string_view input) {
    alignas(std::max_align_t) std::byte scratch[256 * 1024];
    std::pmr::monotonic_buffer_resource pool{scratch, sizeof(scratch)};
    std::pmr::polymorphic_allocator<char> alloc{&pool};

    std::pmr::vector<std::pmr::string> tokens{alloc};
    // ... parse into tokens; all memory freed when pool goes out of scope
}

// CMake (pattern — match project conventions):
// target_compile_options(my_target PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
// target_link_options(my_target PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
```

## Gotchas

- PMR monotonic reset does not run destructors — same as manual arenas; do not store non-trivial types you forget to destroy.
- `unsynchronized_pool_resource` is not thread-safe — one resource per thread or external sync.
- Sanitizers slow execution 2–3× — use Debug/CI configs, not release shipping builds.
- False negatives: sanitizers do not catch all logic bugs; combine with tests and code review.

## Related

[references/arenas-and-pools.md](./arenas-and-pools.md), [references/caller-owns-memory.md](./caller-owns-memory.md), [../../cpp-coding/references/build-and-verification.md](../../cpp-coding/references/build-and-verification.md)
