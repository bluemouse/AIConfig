# Source Notes

Normative and reference sources checked on 2026-07-08:

| Source | URL | Used for |
|--------|-----|----------|
| GLSL 4.60 specification | https://docs.vulkan.org/glsl/latest/index.html | Language grammar, stages, layout rules, built-ins |
| Overview of Shading | https://docs.vulkan.org/glsl/latest/chapters/overview.html | Stage responsibilities and invocation models |
| Introduction | https://docs.vulkan.org/glsl/latest/chapters/introduction.html | Version 4.60 baseline, SPIR-V targeting notes |
| Non-Normative SPIR-V Mappings | https://docs.vulkan.org/glsl/latest/chapters/spirvmappings.html | Vulkan vs OpenGL feature removals/additions/changes |
| Vulkan Specification — Shaders | https://docs.vulkan.org/spec/latest/chapters/shaders.html | Host-side shader module and pipeline context |
| Khronos OpenGL Wiki — GLSL | https://wikis.khronos.org/opengl/OpenGL_Shading_Language | OpenGL-oriented supplements |
| Khronos OpenGL Wiki — common mistakes | https://wikis.khronos.org/opengl/GLSL_:_common_mistakes | OpenGL uniform/link pitfalls |
| LearnOpenGL — Shaders | https://learnopengl.com/Getting-started/Shaders | Teaching-oriented stage introduction |

## Spec highlights encoded in this skill

- **GLSL 4.60.9** is the version documented at `docs.vulkan.org/glsl/latest`; `#version 460` is the documented baseline for that text.
- **SPIR-V targeting** is selected by the offline toolchain, not by in-shader `#version` profile keywords.
- **Vulkan SPIR-V removes** default uniforms (non-opaque), subroutines, `noise()`, compatibility profile, and `shared`/`packed` layouts.
- **Vulkan SPIR-V adds** push constants, descriptor `set`/`binding`, specialization constants, `gl_VertexIndex`/`gl_InstanceIndex`, and input attachments.
- **Vulkan default fragment origin** is upper-left; OpenGL historically used lower-left — engines must correct in projection/viewport policy.
- **OpenGL ES GLSL** is not a strict subset of desktop GLSL — precision and interface rules differ.

## Skill boundaries

| Topic | Owner skill |
|-------|-------------|
| GLSL language, layouts, SPIR-V compile validation | `glsl-coding` (this skill) |
| Creative effects (SDF, ray marching, recipes) | `shader-guide` |
| Slang modules and slangc | `slang-dev` |
| `Vk*` host setup after SPIR-V exists | `vulkan-dev` |
| Renderer architecture | `gpu-rendering-guide` |
