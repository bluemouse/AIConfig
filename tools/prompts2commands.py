"""Convert Copilot prompt markdown files to Cursor command markdown files."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ConversionResult:
    """Result of a single file conversion."""

    source: Path
    destination: Optional[Path]
    success: bool
    warnings: List[str]
    error: Optional[str]


def parse_yaml_value(raw_value: str) -> Any:
    """Parse a simple YAML value from a frontmatter line."""

    value = raw_value.strip()
    if not value:
        return ""

    if value.startswith("[") and value.endswith("]"):
        try:
            literal = ast.literal_eval(value)
            return literal
        except (SyntaxError, ValueError):
            return value

    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]

    return value


def extract_prompt_block(text: str) -> Tuple[str, List[str]]:
    """Extract the content from a ```prompt fenced block if present."""

    warnings: List[str] = []
    lines = text.splitlines()

    start_index = None
    for index, line in enumerate(lines):
        if line.strip().startswith("```prompt"):
            start_index = index
            break

    if start_index is None:
        return text, warnings

    end_index = None
    for index in range(start_index + 1, len(lines)):
        if lines[index].strip() == "```":
            end_index = index
            break

    if end_index is None:
        warnings.append("Prompt block start found without closing ```.")
        return text, warnings

    inner_lines = lines[start_index + 1 : end_index]
    return "\n".join(inner_lines), warnings


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str, List[str]]:
    """Extract frontmatter and body from a markdown document.

    Only the first YAML frontmatter block at the top of the file is parsed.
    """

    warnings: List[str] = []
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return {}, text, warnings

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        warnings.append("Frontmatter start found without closing '---'.")
        return {}, text, warnings

    frontmatter_lines = lines[1:end_index]
    body_lines = lines[end_index + 1 :]

    metadata: Dict[str, Any] = {}
    for line in frontmatter_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            warnings.append(f"Unrecognized frontmatter line: {line}")
            continue
        key, raw_value = line.split(":", 1)
        metadata[key.strip()] = parse_yaml_value(raw_value)

    body_text = "\n".join(body_lines)
    return metadata, body_text, warnings


def normalize_text(text: str) -> str:
    """Normalize product references for Cursor."""

    return (
        text.replace("GitHub Copilot", "Cursor AI")
        .replace("Visual Studio Code", "Cursor")
        .replace("VS Code", "Cursor")
        .replace("VSCode", "Cursor")
    )


def build_command_content(
    description: Optional[str],
    body: str,
    filename_stem: str,
) -> str:
    """Construct the Cursor command file content."""

    normalized_body = normalize_text(body)
    normalized_description = normalize_text(description) if description else ""

    title = filename_stem.replace("-", " ").replace("_", " ").title()

    parts: List[str] = [f"# {title}"]
    if normalized_description:
        parts.append(f"{normalized_description}")
    parts.append("")
    parts.append("Use any text after the command as additional context.")
    parts.append("")

    if normalized_body:
        parts.append(normalized_body)

    return "\n".join(parts).rstrip() + "\n"


def convert_file(source_path: Path, destination_dir: Path) -> ConversionResult:
    """Convert a single .prompt.md file into a Cursor command file."""

    warnings: List[str] = []
    try:
        text = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        return ConversionResult(
            source=source_path,
            destination=None,
            success=False,
            warnings=warnings,
            error=str(exc),
        )

    prompt_text, prompt_warnings = extract_prompt_block(text)
    warnings.extend(prompt_warnings)

    metadata, body, parse_warnings = parse_frontmatter(prompt_text)
    warnings.extend(parse_warnings)

    description = metadata.get("description")
    if description is not None and not isinstance(description, str):
        warnings.append("Description is not a string; using filename instead.")
        description = None

    output_name = source_path.name.replace(".prompt.md", ".md")
    destination_path = destination_dir / output_name

    filename_stem = source_path.stem.replace(".prompt", "")
    command_content = build_command_content(description, body, filename_stem)

    try:
        destination_path.write_text(command_content, encoding="utf-8")
    except OSError as exc:
        return ConversionResult(
            source=source_path,
            destination=destination_path,
            success=False,
            warnings=warnings,
            error=str(exc),
        )

    return ConversionResult(
        source=source_path,
        destination=destination_path,
        success=True,
        warnings=warnings,
        error=None,
    )


def collect_prompt_files(source_dir: Path) -> List[Path]:
    """Collect all .prompt.md files from the source directory."""

    return sorted(source_dir.glob("*.prompt.md"))


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Convert Copilot .prompt.md files to Cursor commands.",
    )
    parser.add_argument(
        "prompt_file",
        nargs="?",
        help="Specific .prompt.md file to convert.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point for conversion."""

    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    source_dir = repo_root / "copilot" / "prompts"
    destination_dir = repo_root / "cursor" / "commands"
    destination_dir.mkdir(parents=True, exist_ok=True)

    if args.prompt_file:
        source_path = Path(args.prompt_file).resolve()
        if not source_path.is_file():
            print(f"Error: file not found: {source_path}")
            return 1
        if not source_path.name.endswith(".prompt.md"):
            print("Error: input must be a .prompt.md file.")
            return 1
        sources = [source_path]
    else:
        sources = collect_prompt_files(source_dir)

    if not sources:
        print("No .prompt.md files found to convert.")
        return 0

    converted = 0
    failed = 0
    warning_count = 0

    for source in sources:
        result = convert_file(source, destination_dir)
        if result.success:
            converted += 1
            if result.destination is not None:
                print(f"Converted: {result.source} -> {result.destination}")
        else:
            failed += 1
            print(f"Failed: {result.source} ({result.error})")

        for warning in result.warnings:
            warning_count += 1
            print(f"Warning: {result.source}: {warning}")

    print(
        "Summary: "
        f"converted={converted}, failed={failed}, warnings={warning_count}"
    )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
