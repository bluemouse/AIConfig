# Modern C++20 — version gates and non-obvious rules

C++20 is the baseline standard; feature usage itself needs no reference — this file
holds only the version gates and the rules implementations tend to get wrong.

## Version gates

- **No C++23+ features** unless the project explicitly targets C++23 or later:
  `std::expected` / `std::unexpected`, `std::print` / `std::println` (use
  `std::format` in C++20), `#embed`, reflection proposals. For exception-free error
  handling in C++20, use `std::optional`, error codes, or a project result type —
  not `std::expected`.
- **Do not mandate modules** (`import std;`) — toolchain and ecosystem support
  varies. Stick with headers unless the project already uses modules.

## Non-obvious rules

- `std::jthread` over detached `std::thread` — joins on destruction, supports
  `std::stop_token` cooperative cancellation.
- `std::scoped_lock` for acquiring multiple mutexes (deadlock-free); RAII lock types
  only — never manual `lock()`/`unlock()`.
- Explicit memory orders and lock-free code only after profiling demands it
  (CP.100); lock-free code is a last resort.
- **Never `volatile` for inter-thread synchronization** (CP.8) — it is not a
  synchronization primitive; use `std::atomic` or locks.
- **No reference captures in lambdas that cross threads** (F.53) — capture by value,
  or use a pointer with clear ownership.
- Parallel execution policies (`std::execution::par`) only after profiling shows
  benefit.
- Coroutines: prefer futures/callbacks for simple one-shot async when coroutine
  infrastructure is not already in the project; keep coroutine types in dedicated
  files — they affect ABI and readability.
- `'\n'` over `std::endl` (the latter flushes on every call).
