#!/usr/bin/env python3
"""
Skill Initializer - Creates a standalone skill directory from template.

Usage:
    init_skill.py <skill-name> --path <path> [--overwrite]

Examples:
    init_skill.py my-new-skill --path .cursor/skills
    init_skill.py my-api-helper --path ~/.cursor/skills
"""

import sys
from pathlib import Path

from scaffold_skill import SkillScaffoldError, scaffold_standalone_skill, slugify_name


def main() -> int:
    overwrite = "--overwrite" in sys.argv
    argv = [arg for arg in sys.argv if arg != "--overwrite"]

    if len(argv) < 4 or argv[2] != "--path":
        print("Usage: init_skill.py <skill-name> --path <path> [--overwrite]")
        print("\nSkill name requirements:")
        print("  - Hyphen-case identifier (e.g., 'data-analyzer')")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 64 characters")
        print("  - Must match directory name exactly")
        print("\nExamples:")
        print("  init_skill.py my-new-skill --path .cursor/skills")
        print("  init_skill.py my-api-helper --path ~/.cursor/skills")
        print("\nFor portable shared-first skills in a repository, use create_skill.py instead.")
        sys.exit(1)

    raw_name = argv[1]
    path = argv[3]

    print(f"Initializing standalone skill: {raw_name}")
    print(f"   Location: {path}")
    print()

    try:
        skill_name = slugify_name(raw_name)
        skill_dir = scaffold_standalone_skill(Path(path), skill_name, overwrite)
    except SkillScaffoldError as exc:
        print(f"Error: {exc}")
        return 1

    print(f"\nSkill '{skill_name}' initialized successfully at {skill_dir}")
    print("\nNext steps:")
    print("1. Edit SKILL.md to complete the TODO items and update the description")
    print("2. Customize or delete the example files in scripts/, references/, and assets/")
    print("3. Run quick_validate.py when ready to check the skill structure")
    print("4. Reload your coding agent so the new skill is discovered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
