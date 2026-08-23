# raii-and-smart-pointers: RAII and Smart Pointers

## Guideline

Bind every resource lifetime (memory, files, handles, locks) to object lifetime via RAII; express heap ownership with `std::unique_ptr` by default and `std::shared_ptr` only when sharing is required; prefer `std::make_unique` / `std::make_shared`.

## Rationale

Manual `delete` on every exit path (including exceptions) is error-prone. RAII makes cleanup automatic at scope end. Smart pointers encode ownership in the type system so leaks and double-frees are caught at compile time or by sanitizers, not in production.

## Rule of 0 / 3 / 5

| Situation | Rule |
|-----------|------|
| Class owns only RAII members (`unique_ptr`, `vector`, `mutex`) | **Rule of 0** — use compiler-generated special members |
| Raw owning pointer or manual `new`/`delete` | **Rule of 3/5** — define/copy/move/destructor explicitly, or replace raw pointer with smart pointer |
| Non-copyable resource (file handle, `unique_ptr`) | Delete copy; implement move |

When performance-critical code needs arenas or pools, ownership of the **block** stays in one RAII object; individual objects inside the arena are not individually heap-owned.

## Techniques

- **`std::make_unique<T>(...)`** - Default for exclusive ownership; exception-safe construction.
- **`std::make_shared<T>(...)`** - Shared ownership; watch for extra control-block allocation and cycles.
- **Custom deleter** - `unique_ptr<FILE, decltype(&fclose)>` or lambda deleter for C APIs.
- **Non-owning observers** - Raw pointer or `span` only when lifetime is documented and shorter than owner.
- **No raw `new`/`delete`** - Core Guidelines **R.11**; use smart pointers or stack/arena storage.

## Example

```cpp
#include <memory>
#include <mutex>

// Rule of 0: members manage themselves.
class Document {
    std::unique_ptr<Impl> impl_;
    std::vector<Section> sections_;
public:
    explicit Document(std::unique_ptr<Impl> impl) : impl_(std::move(impl)) {}
};

// Rule of 5 (only when you must wrap a C API):
class File {
    std::unique_ptr<FILE, int(*)(FILE*)> fp_;
public:
    explicit File(const char* path)
        : fp_(std::fopen(path, "rb"), &std::fclose) {}
    File(File&&) = default;
    File& operator=(File&&) = default;
    File(const File&) = delete;
    File& operator=(const File&) = delete;
};

// CP.20: never plain lock/unlock
void work(std::mutex& m) {
    std::lock_guard lock{m};
    // ...
}
```

## Gotchas

- `shared_ptr` where `unique_ptr` suffices adds atomic refcount cost (R.21).
- Returning `unique_ptr` from factory functions is the standard pattern — do not return raw `T*`.
- Custom deleters must match the actual free function (`delete` vs `delete[]` vs `free`).
- Arena placement-new objects still need explicit destructors before arena reset — RAII wrappers can call `~T()` in a scope guard.

## Related

[references/ownership-and-lifetimes.md](./ownership-and-lifetimes.md), [references/arenas-and-pools.md](./arenas-and-pools.md), [../../cpp-coding/SKILL.md](../../cpp-coding/SKILL.md) (Core Guidelines R.*, E.6, CP.20)
