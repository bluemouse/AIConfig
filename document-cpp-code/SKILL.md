---
name: document-cpp-code
description: Create or rewrite a single Markdown documentation file for a C/C++ codebase or a specific module. Use when asked to document C++ architecture, explain a subsystem, produce a design doc, or write implementation notes. Output MUST be exactly one doc file; any useful tool/script output must be rewritten and embedded into that same document in the most relevant sections (diagrams and summaries inline; optional verbatim snippets in <details>). Temporary helper files/folders may be created during analysis but must be removed before finishing. Encourages Mermaid diagrams (component diagram for project scope; sequence diagram for 1–2 key flows). Optionally runs ./scripts/code_doc_helper.py (libclang when available) for API index + include graph and ./scripts/build_system_probe.py for build metadata.
---


# Document C/C++ Code

## When to Use This Skill

Use this skill when the user asks to:

- Create a design doc for the whole project.
- Document a module/subsystem.
- Explain implementation details of a library, subsystem, or component.
- Update existing documentation files.
- Add Mermaid diagrams to clarify structure or flow.

This skill is intended for C/C++ projects and assumes common conventions:

- Public API defined in headers (.h/.hpp) and implemented in sources (.c/.cpp)
- Namespaces, classes/structs, templates, and macros
- RAII / ownership and lifetime patterns
- Compile-time configuration via defines and build system options

## Inputs to Confirm Up Front

Before writing anything, ask the user to confirm:

1. Scope extent (required):
   - Whole project (high-level structure only)
   - Single module/subsystem (deeper)
   - Multiple modules/subsystems
2. Topic/title and target doc filename (required):
   - **Single-file rule**: exactly one target Markdown file will be created/updated.
   - If updating: which existing doc to rewrite (preferred)
   - If creating: propose one file (default: doc/<slug>.md; for engine/framework topics, doc/vulk-<topic>.md)
3. Audience:
   - Engine contributors
   - App/testbed developers
   - AI code assistants such as Copilot or Cursor
4. Depth:
   - Overview
   - Deep dive
5. Diagrams:
   - Mermaid encouraged when it clarifies

6. Markdown front matter (required by repo rules):
   - Confirm required fields and accepted values for any repo-specific rules.
   - Current workspace rule requires: `title`, `author`, `tags`, `summary`,
     `date` in YAML front matter.

6. Tool/script embedding policy (required):
   - Any useful information produced via scripts/tools that you rely on must be embedded into the one document.
   - Default: integrate it where it naturally belongs (e.g., build probe results in Build/Artifacts; include graph in Architecture).
   - Use `<details>` only for optional verbatim snippets (debugging / provenance), not as the primary presentation.

7. Language focus (default: C++):
   - C
   - C++
   - Mixed

8. Whole-project docs only: include build/run/test instructions?
   - Default: **yes** for build + run (whole-project docs should be runnable).
   - Tests: include test instructions only when the repo appears to have unit tests (e.g., CTest targets, `tests/` folder, `ctest`, or an explicit test runner).
   - If tests are not present, omit the Test section (do not invent one).

## Output Rules (Single-File + Embed + Cleanup)

Hard rules:

1. **Exactly one doc file**
   - The final output of the task MUST be a single Markdown file.
   - Do not create additional documentation files (no doc/generated/, no extra design docs) unless the user explicitly asks.

2. **Embed tool/script output into that doc**
   - Any information you generated via scripts/tools and found helpful enough to inform the doc must be embedded into the same file.
   - Prefer integrating it naturally as narrative sections and diagrams in-place.
   - It is allowed (often preferred) to **rewrite** raw tool output into a cleaner summary.
   - If keeping provenance is useful, include a small “verbatim” snippet in `<details>` near the section that uses it.

3. **Cleanup temporary artifacts**
   - You may create temporary helper files/folders during analysis (e.g., scratch outputs, intermediate reports), but you MUST remove them before finishing.
   - If you redirected script output to a file for convenience, either embed it and then delete it, or avoid creating the file by capturing stdout.

Quality rules:

- Prefer rewriting an existing best-match doc when it exists (to preserve repo conventions).
- When rewriting: read the existing doc first and use it as a primary reference (terminology, invariants, links).
- Preserve verified facts; avoid speculation. If uncertain, add a short "Open Questions / TODOs" section.

## How to Choose the Target Doc File

1. Scan existing documentation locations and prefer updating an existing doc.
   - Prefer in order: docs/ , doc/ , then README.md or module-level READMEs.
2. Match candidates in order:
   - Exact match: docs/<slug>.md or doc/<slug>.md
   - Prefixed match (if the repo uses a prefix convention): doc/<prefix>-<slug>.md
   - Keyword overlap match: pick the existing doc filename with the highest overlap with the requested topic
3. If no match:
   - Propose one new doc under doc/ or docs/ using the repo's naming conventions.
   - If no convention exists, prefer doc/<slug>.md.
4. Ask the user to confirm the final target filename.
5. **Single-file reminder**: do not create any additional doc files unless explicitly requested.

## Scope → Analysis Outputs (Decision Table)

Choose analysis outputs based on the requested scope.

- Whole project (high-level only)
   - Primary: component/include graph that shows major modules and boundaries.
   - Secondary (optional): lightweight build-system summary and subsystem index to structure headings.
   - Mermaid: prefer a component-style diagram.
   - Include build + run instructions by default.
   - Include test instructions only if unit tests exist.
   - Embedding: integrate build probe + component graph into the relevant sections.
   - Avoid API details: do not include an API index in a whole-project overview unless the user explicitly asks.

- Single module/subsystem
   - Primary: API index for that module (categorized into public headers vs internal headers vs sources; lists namespaces, key types, key functions).
  - Secondary: a small include/dependency graph limited to that module boundary.
  - Mermaid: prefer a sequence diagram only for 1–2 key runtime flows.
   - Embedding: keep module doc readable; put long indices in `<details>`.

- Multiple modules/subsystems
  - Primary: one API index per module plus one shared component diagram tying them together.
  - Secondary: per-module include graphs only when needed for clarity.
   - Embedding: keep each module section readable; put long indices in `<details>`.

## Recommended Workflow

1. Select scope and confirm the **single** target filename.
2. If updating an existing doc: read the current doc end-to-end.
   - Treat it as a reference input for the rewrite (terminology, intended audience, existing structure, and links).
   - Identify what must be kept (verified facts) vs what should be reworked (structure, clarity, missing details).
3. Collect truth sources from the repo:
   - Public API surface (headers, installed/public include directories)
   - Implementations (.c/.cpp) and internal headers
   - Existing docs under docs/ or doc/ (prefer rewriting them)
   - Repo constraints files (e.g., AGENTS.md, contributing docs, style guides)
   - Build metadata (compile_commands.json, CMakeLists.txt, toolchain files)
4. Optional: run helpers for structured analysis (preferred when available):
   - API index: `./scripts/code_doc_helper.py index`
   - Component/include graph: `./scripts/code_doc_helper.py includes`
   - Build-system summary: `./scripts/build_system_probe.py --diagrams`
   - IMPORTANT: Any useful output from these runs must be embedded into the single target doc (integrated inline; optional verbatim in `<details>`).
5. Generate a draft using a template:
   - Whole project: `./templates/project-overview.template.md`
   - Module: `./templates/module-design.template.md`
6. Rewrite the target doc for consistency:
   - Keep it scannable.
   - Add Mermaid diagrams where they clarify.
   - Integrate tool/script outputs inline where they belong; use `<details>` only optionally for short verbatim snippets near the relevant section.
7. Cleanup:
   - Remove any temporary helper files/folders created during analysis.
8. Accuracy pass:
   - Ensure statements match the code.
   - Clearly label approximate results (if fallback parsing was used).

## Optional Tooling: code_doc_helper.py (Libclang Preferred)

Prefer using .claude/skills/document-cpp-code/scripts/code_doc_helper.py in
auto mode for this repository layout.

Before running Python scripts, ensure the Python environment is configured by
the host tooling (required in this workspace).

- Whole project component/include graph example:
   - python .claude/skills/document-cpp-code/scripts/code_doc_helper.py --root . includes --backend auto --component-depth 2 --inputs src include testbed glsl-lib

- Module API index example:
   - python .claude/skills/document-cpp-code/scripts/code_doc_helper.py --root . index --backend auto --inputs include src

If libclang or compile_commands.json is not available, the helper should fall back and clearly label outputs as approximate.

The `index` output is structured to help documentation separate public API from internal implementation:

- Public API: symbols found in headers under include/
- Internal headers: symbols found in non-include/ headers
- Sources: symbols found in .c/.cpp files

## Optional Tooling: build_system_probe.py (CMake + Visual Studio + Xcode)

Use .claude/skills/document-cpp-code/scripts/build_system_probe.py to capture
build-system facts without guessing:

- Run example (Markdown to stdout):
   - python .claude/skills/document-cpp-code/scripts/build_system_probe.py --root . --diagrams > /tmp/build-system.md

CMake note (Optional “richer but may require running configure”):

- The richest CMake target/dependency information comes from the CMake File API reply, which only exists after configuring a build directory.
- If the project is not configured yet (no File API reply present), instruct the user to run configure first (do not do it automatically):
   - Example: cmake -S . -B build
- Then re-run the probe to pick up the File API reply.

## Templates and References

- Project template: templates/project-overview.template.md
- Module template: templates/module-design.template.md
- Doc conventions: references/doc-conventions.md
- Rewrite checklist: references/rewrite-checklist.md

## Embedding Pattern (Recommended)

Integrate generated information into the **main sections** of the single doc:

- Architecture: include/component Mermaid diagram (curated; limited scope)
- Build + Artifacts: build-system probe summary and (optionally) CMake target dependency Mermaid
- Module docs: API index (curated summary) and (optionally) a verbatim index in `<details>`

Use `<details>` only when it improves readability (provenance / debugging), and place it next to the section that uses it.

Example `<details>` wrapper:

```markdown
<details>
<summary>build_system_probe.py (verbatim)</summary>

```text
...tool output...
```

</details>
```
