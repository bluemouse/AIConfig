---
name: cpp-memory-guide
description: "Guide C++20 memory design: RAII, unique_ptr/shared_ptr, std::span borrows, caller-owned buffers, arena/bump/pool allocators, std::pmr, ownership and lifetimes, virtual-memory reserve/commit, leak/use-after-free prevention. Use when implementing or reviewing C++ allocation, custom allocators, move semantics, API buffer ownership, or debugging memory bugs with sanitizers — even if the user says 'memory leak' without naming an allocator."
---

# cpp-memory-guide (GitHub Copilot)

Read the shared skill first — it is the source of truth for C++20 memory workflow, reference
routing, and allocator patterns:

`../../../.shared/skills/cpp-memory-guide/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/cpp-memory-guide/`. Resolve paths to
`references/` from that directory.

This wrapper adds **GitHub Copilot / VS Code-native** execution.

## Discovery and reload

- Project skills: `.github/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Reload VS Code** after installing or editing skills so Copilot rediscovers them

## Install or refresh cpp-memory-guide

From repo root (or ask the user to run in a terminal):

```bash
python .shared/skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name cpp-memory-guide --source skills/cpp-memory-guide --overwrite
```

If bootstrap source exists at `skills/cpp-memory-guide/`, use that path for `--source` only.

## Companion skills

| Task | Path |
|------|------|
| General C++20 style, Core Guidelines | `.shared/skills/cpp-coding/SKILL.md` |
| GPU device memory strategy (VRAM tiers, staging) | `.shared/skills/gpu-rendering-guide/SKILL.md` |

Install companions with `install_portable_skill.py` when bootstrap sources exist under `skills/<name>/`.

## Wrapper policy

- Edit cross-tool memory behavior in `../../../.shared/skills/cpp-memory-guide/`
- Edit Copilot-specific mechanics here
- Do not duplicate the full shared skill body in this file
