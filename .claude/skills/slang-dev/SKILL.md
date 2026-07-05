---
name: slang-dev
description: "Develop, review, port, compile, test, debug, and optimize Slang shaders and C++ host integration for Vulkan SPIR-V and Metal MSL renderers: modules, import/__include, capabilities, ParameterBlock, generics/interfaces, slangc, IGlobalSession/ISession, ProgramLayout reflection, descriptor/argument-buffer layout, and cross-backend portability. Use for .slang files, slang compiler API, SPIR-V/MSL emission, shader entry points, or shader correctness/performance \u2014 even when the user does not say 'Slang'."
---

# slang-dev (Claude Code)

Read the shared skill first — it is the source of truth for Slang workflow, reference
routing, and review checklists:

`../../../.shared/skills/slang-dev/SKILL.md`

Resolve `<SKILL_ROOT>` as `../../../.shared/skills/slang-dev/`. Resolve paths to
`references/` and `scripts/` from that directory.

This wrapper adds **Claude Code-native** execution. When this wrapper and the shared skill
disagree on mechanics, follow this wrapper for Claude Code.

## Discovery and reload

- Project skills: `.claude/skills/<name>/SKILL.md` + shared under `.shared/skills/<name>/`
- **Restart or reload** the Claude Code session after installing or editing skills

## Install or refresh slang-dev

```bash
python .shared/skills/skill-creator/scripts/install_portable_skill.py \
  --root . --name slang-dev --source skills/slang-dev --overwrite
```

If bootstrap source exists at `skills/slang-dev/`, use that path for `--source` only.

## Compile matrix

For repeatable SPIR-V and MSL builds across entry points, run the bundled script from the
shared skill root:

```bash
python .shared/skills/slang-dev/scripts/slang_compile_matrix.py manifest.json [--print-only]
```

Use `--print-only` to emit commands without executing; `--allow-missing-slangc` when
`slangc` is not on PATH.

## Companion skills

| Task | Path |
|------|------|
| Vk* pipeline, descriptors, swapchain after SPIR-V | `.shared/skills/vulkan-dev/SKILL.md` |
| API-agnostic binding model, render graph | `.shared/skills/gpu-rendering-guide/SKILL.md` |
| C++20 style and build verification | `.shared/skills/cpp-coding/SKILL.md` |

Install companions with `install_portable_skill.py` when bootstrap sources exist under `skills/<name>/`.

## Wrapper policy

- Edit cross-tool Slang behavior in `../../../.shared/skills/slang-dev/`
- Edit Claude Code mechanics here
- Do not duplicate the full shared skill body in this file
