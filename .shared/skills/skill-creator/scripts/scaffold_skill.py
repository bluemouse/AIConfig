#!/usr/bin/env python3
"""
Shared scaffolding helpers for portable and standalone skills.
"""

from __future__ import annotations

import re
from pathlib import Path


class SkillScaffoldError(Exception):
    """Raised for user-correctable scaffold errors."""


TOOL_SKILL_PATHS = {
    "claude": ".claude/skills/{name}",
    "cursor": ".cursor/skills/{name}",
    "github": ".github/skills/{name}",
}

RELATIVE_SHARED_SKILL_PATH = "../../../.shared/skills/{name}/SKILL.md"
RELATIVE_SHARED_SKILL_ROOT = "../../../.shared/skills/{name}"


SKILL_TEMPLATE = """---
name: {skill_name}
description: "[TODO: Complete and informative explanation of what the skill does and when the coding agent should use it. Include WHEN to use this skill - specific scenarios, file types, or tasks that trigger it.]"
---

# {skill_title}

Resolve `<SKILL_ROOT>` as the directory containing **this** skill's `SKILL.md` (the installed `{skill_name}` folder). Use these paths — do not guess or invent alternatives.

## Overview

[TODO: 1-2 sentences explaining what this skill enables]

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" → "Reading" → "Creating" → "Editing"
- Structure: ## Overview → ## Workflow Decision Tree → ## Step 1 → ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" → "Merge PDFs" → "Split PDFs" → "Extract Text"
- Structure: ## Overview → ## Quick Start → ## Task Category 1 → ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" → "Colors" → "Typography" → "Features"
- Structure: ## Overview → ## Guidelines → ## Specifications → ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" → numbered capability list
- Structure: ## Overview → ## Core Capabilities → ### 1. Feature → ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by the agent for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context when needed.

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that the agent should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output the agent produces.

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
"""

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""
Example helper script for {skill_name}

This is a placeholder script that can be executed directly.
Replace with actual implementation or delete if not needed.
"""

def main():
    print("This is an example script for {skill_name}")
    # TODO: Add actual script logic here

if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# Reference Documentation for {skill_title}

This is a placeholder for detailed reference documentation.
Replace with actual reference content or delete if not needed.

## When Reference Docs Are Useful

Reference docs are ideal for:
- Comprehensive API documentation
- Detailed workflow guides
- Complex multi-step processes
- Information too lengthy for main SKILL.md
- Content that's only needed for specific use cases
"""

EXAMPLE_ASSET = """# Example Asset File

This placeholder represents where asset files would be stored.
Replace with actual asset files (templates, images, fonts, etc.) or delete if not needed.

Asset files are NOT intended to be loaded into context, but rather used within
the output the agent produces.
"""

WRAPPER_DESCRIPTION_TEMPLATE = (
    '"[TODO: Same trigger description as the shared skill in '
    '.shared/skills/{skill_name}/SKILL.md]"'
)


def title_case_skill_name(skill_name: str) -> str:
    """Convert hyphenated skill name to Title Case for display."""
    return " ".join(word.capitalize() for word in skill_name.split("-"))


def slugify_name(value: str) -> str:
    """Normalize a skill name to lowercase hyphen-case."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise SkillScaffoldError("Skill name cannot be empty after normalization.")
    if len(value) > 64:
        raise SkillScaffoldError("Skill name must be 64 characters or fewer.")
    return value


def shared_skill_content(skill_name: str) -> str:
    skill_title = title_case_skill_name(skill_name)
    return SKILL_TEMPLATE.format(skill_name=skill_name, skill_title=skill_title)


def wrapper_skill_content(tool: str, skill_name: str, note: str | None) -> str:
    shared_skill_path = RELATIVE_SHARED_SKILL_PATH.format(name=skill_name)
    shared_skill_root = RELATIVE_SHARED_SKILL_ROOT.format(name=skill_name)
    tool_titles = {
        "claude": "Claude Code",
        "cursor": "Cursor",
        "github": "GitHub Copilot",
    }
    title = tool_titles[tool]
    note = (note or "No additional tool-specific instructions were provided.").strip()
    description = WRAPPER_DESCRIPTION_TEMPLATE.format(skill_name=skill_name)

    body = f"""\
# {skill_name} wrapper for {title}

This is a tool-specific wrapper. The canonical shared skill is:

`{shared_skill_path}`

Before following this skill, read that shared `SKILL.md` and treat it as the source of truth for workflows, output formats, and bundled resources. Resolve `<SKILL_ROOT>` as `{shared_skill_root}` and resolve paths to `scripts/`, `references/`, and `assets/` from that shared skill directory.

## {title}-specific information

{note}

## Wrapper policy

- Do not treat this wrapper as the full skill specification.
- Prefer the shared skill whenever this wrapper and the shared skill conflict.
- Keep edits to common behavior in `{shared_skill_root}/`.
- Keep only {title}-specific information in this wrapper.
"""
    return (
        f"---\nname: {skill_name}\ndescription: {description}\n---\n\n"
        + body
    )


def write_file(path: Path, content: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise SkillScaffoldError(f"Refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_shared_skill_dir(skill_dir: Path, skill_name: str, overwrite: bool) -> None:
    """Create a full skill directory with SKILL.md and placeholder resources."""
    if skill_dir.exists() and not overwrite:
        raise SkillScaffoldError(f"Refusing to overwrite existing directory: {skill_dir}")

    skill_dir.mkdir(parents=True, exist_ok=overwrite)
    write_file(skill_dir / "SKILL.md", shared_skill_content(skill_name), overwrite)

    skill_title = title_case_skill_name(skill_name)

    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    example_script = scripts_dir / "example.py"
    write_file(example_script, EXAMPLE_SCRIPT.format(skill_name=skill_name), overwrite)
    example_script.chmod(0o755)

    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True, exist_ok=True)
    write_file(
        references_dir / "api_reference.md",
        EXAMPLE_REFERENCE.format(skill_title=skill_title),
        overwrite,
    )

    assets_dir = skill_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    write_file(assets_dir / "example_asset.txt", EXAMPLE_ASSET, overwrite)


def scaffold_standalone_skill(parent_dir: Path, skill_name: str, overwrite: bool) -> Path:
    """Scaffold a standalone skill at parent_dir/skill_name."""
    skill_dir = parent_dir.resolve() / skill_name
    scaffold_shared_skill_dir(skill_dir, skill_name, overwrite)
    return skill_dir


def scaffold_portable_skill(
    root: Path,
    skill_name: str,
    overwrite: bool,
    claude_note: str | None = None,
    cursor_note: str | None = None,
    github_note: str | None = None,
) -> list[Path]:
    """Scaffold shared skill plus tool-specific wrappers."""
    root = root.resolve()
    skill_name = slugify_name(skill_name)
    written: list[Path] = []

    shared_dir = root / ".shared" / "skills" / skill_name
    scaffold_shared_skill_dir(shared_dir, skill_name, overwrite)
    written.append(shared_dir)

    notes = {
        "claude": claude_note,
        "cursor": cursor_note,
        "github": github_note,
    }
    for tool, pattern in TOOL_SKILL_PATHS.items():
        wrapper_dir = root / pattern.format(name=skill_name)
        write_file(
            wrapper_dir / "SKILL.md",
            wrapper_skill_content(tool, skill_name, notes[tool]),
            overwrite,
        )
        written.append(wrapper_dir)

    return written
