---
name: android-ndk-dev
description: "android ndk and c++ integration guidance for kotlin android 16/api 36+ apps. use when designing, implementing, reviewing, or troubleshooting native libraries, cmake, externalnativebuild, jni bridges from kotlin, prebuilt libraries, abi packaging, native memory, native threads, image/media processing in c++, native debugging, sanitizers, symbols, and performance profiling. prefer android-dev for app-layer kotlin, compose, sdk camera/media, permissions, and release architecture. prefer android-vulkan-dev for vulkan renderer internals and gpu rendering through the ndk."
---

# android-ndk-dev wrapper for Cursor

This is a tool-specific wrapper. The canonical shared skill is:

`../../../.shared/skills/android-ndk-dev/SKILL.md`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `../../../.shared/skills/android-ndk-dev` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## Cursor-specific information

Reload the Cursor window after adding or editing this skill so the agent rediscovers it.

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `../../../.shared/skills/android-ndk-dev/`.
- Keep only Cursor-specific information in this wrapper.
