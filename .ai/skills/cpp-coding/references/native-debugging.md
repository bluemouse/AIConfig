# Native C++ Debugging

C++ toolchain and runtime techniques for crashes, corrupted memory, undefined behavior, and
debugger-only state. Use this when the failure is clearly in native C++ runtime behavior
and you need symbols, sanitizers, or a platform debugger — not when you still lack a stable
reproduction or hypothesis workflow.

For language-neutral debugging method (repro, bisect, hypotheses, minimal fix, report), start
with [debugging-guide](../../debugging-guide/SKILL.md). Return there whenever the investigation
is still about *finding* root cause rather than *reading* native crash evidence.

## Contents

- [When to use this reference](#when-to-use-this-reference)
- [When to hand off](#when-to-hand-off)
- [Prerequisites](#prerequisites)
- [Workflow](#workflow)
  - [ThreadSanitizer for deadlocks and data races](#4b-threadsanitizer-for-deadlocks-and-data-races)
- [Common rationalizations](#common-rationalizations)
- [Red flags](#red-flags)
- [Verification](#verification)
- [Tips](#tips)

## When to use this reference

- Segmentation fault, access violation, or `abort()` in a C++ process
- Bug depends on object lifetime, ownership, or move/copy behavior
- Behavior differs between debug and release builds
- AddressSanitizer, UndefinedBehaviorSanitizer, or a debugger is needed to see the failure
- Native test hangs, deadlocks, or corrupts memory without a clear stack trace

## When to hand off

| Situation | Use instead |
|-----------|-------------|
| No stable reproduction or structured root-cause workflow yet | [debugging-guide](../../debugging-guide/SKILL.md) |
| Memory leak, ownership convention, allocator design, or LSan/ASan allocation-site diagnosis | [cpp-memory-guide](../../cpp-memory-guide/SKILL.md) |
| Compile, link, or CMake configuration failure | [build-and-verification.md](build-and-verification.md), [cmake-dev](../../cmake-dev/SKILL.md) |
| Performance-only issue, no correctness defect | [cpp-performance-guide](../../cpp-performance-guide/SKILL.md) |
| Regression test authoring after fix is confirmed | [cpp-testing](../../cpp-testing/SKILL.md), [test-driven-dev-guide](../../test-driven-dev-guide/SKILL.md) |

## Prerequisites

- Reproducible failing command, test, or executable
- Debug-capable build with symbols
- Access to the relevant debugger or sanitizer-enabled toolchain
- Enough context to tell whether the bug is runtime, lifetime, concurrency, or build-related

## Workflow

### 1. Rebuild for diagnosis, not speed

Start with a debuggable build before chasing the crash:

```bash
# CMake
cmake -S . -B build-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build build-debug -j

# Clang/GCC direct build
clang++ -std=c++20 -g -O0 -Wall -Wextra -Wpedantic main.cpp -o app
```

Guidelines:

- enable symbols (`-g`, MSVC `/Zi`)
- reduce or disable optimization while reproducing (`-O0`, MSVC `/Od`)
- keep warnings enabled
- reproduce with the same inputs that fail in CI or production-like runs

Sanitizer build flags and CI gating are also documented in
[build-and-verification.md](build-and-verification.md#sanitizers-and-runtime-checks).

### 2. Capture the exact failing surface

```bash
ctest --test-dir build-debug --output-on-failure

# Or run the specific executable directly
./build-debug/app args...
```

Record:

1. exact command line
2. failing input or fixture
3. crash signal or exit code
4. first bad log line, assertion, or stack frame

### 3. Inspect runtime state with a native debugger

Use the platform-native debugger your team standardizes on.

```bash
# GDB
gdb --args ./build-debug/app args...
# (gdb) run
# (gdb) bt
# (gdb) frame 0
# (gdb) info locals
# (gdb) p suspiciousVariable

# LLDB
lldb -- ./build-debug/app args...
# (lldb) run
# (lldb) bt
# (lldb) frame variable
```

Focus on:

- the first frame where state becomes invalid
- moved-from or already-destroyed objects
- container bounds and iterator validity
- null or dangling pointers
- cross-thread ordering when the state only fails under load

### 4. Turn on sanitizers early

Sanitizers catch bug classes that ordinary logging hides.

```bash
cmake -S . -B build-asan \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-fsanitize=address,undefined -fno-omit-frame-pointer"
cmake --build build-asan -j
ctest --test-dir build-asan --output-on-failure
```

On Windows, use MSVC AddressSanitizer when the toolchain supports it.

Use sanitizer output to answer:

- which access was invalid
- which allocation/free site owned the memory
- whether UB happened before the visible crash

### 4b. ThreadSanitizer for deadlocks and data races

When hangs, deadlocks, or data races are suspected (especially under load):

```bash
cmake -S . -B build-tsan \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-fsanitize=thread -fno-omit-frame-pointer"
cmake --build build-tsan -j
ctest --test-dir build-tsan --output-on-failure
```

ThreadSanitizer builds are slow — use for targeted repro runs, not every edit loop. Pair
TSan reports with debugger thread backtraces (`thread apply all bt` in GDB). For
intermittent repro or hypothesis workflow, use
[debugging-guide](../../debugging-guide/SKILL.md). For ownership and lifetime design,
use [cpp-memory-guide](../../cpp-memory-guide/SKILL.md).

### 5. Use core dumps or crash artifacts when the bug is post-mortem

If the crash only appears outside the current shell, collect the artifact and inspect it:

- preserve the crashing binary and symbols
- keep the exact build that produced the dump
- load the dump in the matching debugger
- compare the crashing frame with the last known good run

Do not "fix" a crash dump by guessing from the top frame alone. Trace ownership and state
backwards.

### 6. Fix the root cause and harden the boundary

Typical C++ root causes:

- lifetime mismatch between owner and borrower
- invalid iterator or reference after container mutation
- double free or use-after-free
- missing synchronization around shared mutable state
- undefined behavior surfaced by a newer compiler or optimizer

After the fix:

- rerun the failing reproduction
- rerun sanitizer-enabled tests
- add a regression test where practical (see [cpp-testing](../../cpp-testing/SKILL.md))
- check nearby code for the same lifetime or ownership pattern

Hand back to [debugging-guide](../../debugging-guide/SKILL.md) for the evidence report and
minimal-fix verification when the broader investigation is not finished.

## Common rationalizations

| Rationalization | Reality |
|-----------------|---------|
| "The debugger changes timing, so it is useless" | Timing-sensitive bugs still need debugger or sanitizer evidence. Use them to narrow the failure class, then confirm in a normal run. |
| "Release-only crash means the optimizer is broken" | Most release-only failures are UB, data races, or lifetime bugs that debug mode accidentally masks. |
| "The stack trace is enough" | Native crashes often happen far from the real cause. Ownership history matters more than the final frame. |
| "I'll just add null checks" | Null checks do not fix dangling references, iterator invalidation, or races. |

## Red flags

- The crash disappears when you add logging but no root cause is identified
- The only "fix" is changing optimization level
- You cannot say which object owns the failing memory
- The code mixes raw ownership, smart pointers, and borrowed references without clear boundaries
- No regression test or sanitizer rerun happened after the fix

## Verification

- [ ] A reproducible failing command or test exists
- [ ] A debug-symbol build was used during diagnosis
- [ ] Debugger or sanitizer output identifies the real failure class
- [ ] The final fix addresses ownership, bounds, synchronization, or UB at the source
- [ ] The targeted reproduction and relevant tests pass after the fix

## Tips

- Prefer smaller reproductions: isolate the failing target or test before debugging the whole system
- If the stack is noisy, break on the first thrown exception, failed assertion, or allocator error
- Compare debug and release compile flags when behavior diverges
- If the bug is build-related after all, use [build-and-verification.md](build-and-verification.md) and [cmake-dev](../../cmake-dev/SKILL.md)
