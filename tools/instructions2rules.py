"""Convert Copilot .instructions.md files to Cursor .mdc rule files."""

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


def normalize_globs(apply_to: Any) -> List[str]:
    """Normalize applyTo into a list of glob patterns."""

    if apply_to is None:
        return []

    if isinstance(apply_to, list):
        items = [str(item).strip() for item in apply_to]
    else:
        items = [part.strip() for part in str(apply_to).split(",")]

    return [item for item in items if item]


def yaml_quote(value: str) -> str:
    """Quote a string for YAML output."""

    escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
    return f"\"{escaped}\""


def build_rule_content(
    description: str,
    globs: List[str],
    always_apply: bool,
    body: str,
) -> str:
    """Construct the Cursor rule file content."""

    normalized_description = (
        description.replace("GitHub Copilot", "Cursor AI")
        .replace("Visual Studio Code", "Cursor")
        .replace("VS Code", "Cursor")
        .replace("VSCode", "Cursor")
    )
    normalized_body = (
        body.replace("GitHub Copilot", "Cursor AI")
        .replace("Visual Studio Code", "Cursor")
        .replace("VS Code", "Cursor")
        .replace("VSCode", "Cursor")
    )

    lines: List[str] = ["---"]
    lines.append(f"description: {yaml_quote(normalized_description)}")

    if globs:
        lines.append("globs:")
        for glob in globs:
            lines.append(f"  - {yaml_quote(glob)}")
    else:
        lines.append("globs: []")

    lines.append(f"alwaysApply: {'true' if always_apply else 'false'}")
    lines.append("---")

    body_text = normalized_body
    if body_text.startswith("\n"):
        body_text = body_text[1:]

    if body_text:
        return "\n".join(lines) + "\n" + body_text + "\n"

    return "\n".join(lines) + "\n"


def convert_file(source_path: Path, destination_dir: Path) -> ConversionResult:
    """Convert a single .instructions.md file into a .mdc rule file."""

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

    metadata, body, parse_warnings = parse_frontmatter(text)
    warnings.extend(parse_warnings)

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        description = source_path.stem.replace(".instructions", "")

    apply_to = metadata.get("applyTo")
    globs = normalize_globs(apply_to)
    always_apply = any(glob in {"*", "**"} for glob in globs)

    rule_content = build_rule_content(description, globs, always_apply, body)

    output_name = source_path.name.replace(".instructions.md", ".mdc")
    destination_path = destination_dir / output_name

    try:
        destination_path.write_text(rule_content, encoding="utf-8")
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


def collect_instruction_files(source_dir: Path) -> List[Path]:
    """Collect all .instructions.md files from the source directory."""

    return sorted(source_dir.glob("*.instructions.md"))


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(
        description="Convert Copilot .instructions.md files to Cursor .mdc rules.",
    )
    parser.add_argument(
        "instruction_file",
        nargs="?",
        help="Specific .instructions.md file to convert.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point for conversion."""

    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    source_dir = repo_root / "copilot" / "instructions"
    destination_dir = repo_root / "cursor" / "rules"
    destination_dir.mkdir(parents=True, exist_ok=True)

    if args.instruction_file:
        source_path = Path(args.instruction_file).resolve()
        if not source_path.is_file():
            print(f"Error: file not found: {source_path}")
            return 1
        if not source_path.name.endswith(".instructions.md"):
            print("Error: input must be a .instructions.md file.")
            return 1
        sources = [source_path]
    else:
        sources = collect_instruction_files(source_dir)

    if not sources:
        print("No .instructions.md files found to convert.")
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
