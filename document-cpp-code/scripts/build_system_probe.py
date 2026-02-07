"""build_system_probe.py

Build system probe for C/C++ documentation.

This script helps the `document-cpp-code` skill understand how a C/C++ project is
built without executing a build. It detects and parses common build systems:

- CMake (CMakePresets.json, CMakeCache.txt, and optionally CMake File API replies)
- Visual Studio MSBuild projects (.sln/.vcxproj)
- Xcode projects (.xcodeproj/project.pbxproj)

Output is a concise Markdown report designed to be pasted into a design doc.

Notes
-----
- Parsing is best-effort and intentionally conservative.
- For CMake, the richest structured data comes from the CMake File API reply,
  which exists only after configuring the build directory.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class DetectedFile:
    path: Path
    kind: str


@dataclass
class CMakeTarget:
    name: str
    type: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class VisualStudioProject:
    name: str
    path: Path
    guid: Optional[str] = None
    references: List[str] = field(default_factory=list)
    include_dirs: List[str] = field(default_factory=list)
    defines: List[str] = field(default_factory=list)


@dataclass
class XcodeTarget:
    name: str
    build_settings: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class BuildSystemReport:
    root: Path
    detected_files: List[DetectedFile] = field(default_factory=list)

    cmake_presets: List[Path] = field(default_factory=list)
    cmake_build_dirs: List[Path] = field(default_factory=list)
    cmake_file_api_build_dirs: List[Path] = field(default_factory=list)
    cmake_targets: List[CMakeTarget] = field(default_factory=list)

    vs_solutions: List[Path] = field(default_factory=list)
    vs_projects: List[VisualStudioProject] = field(default_factory=list)

    xcode_projects: List[Path] = field(default_factory=list)
    xcode_targets: List[XcodeTarget] = field(default_factory=list)

    compile_commands: Optional[Path] = None


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


def _normalize(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


# Directories to exclude from scanning (common dependency/build folders).
_EXCLUDED_DIRS = {
    "vcpkg",
    "external",
    "third_party",
    "thirdparty",
    "3rdparty",
    "vendor",
    "node_modules",
    ".git",
    ".hg",
    ".svn",
}


def _is_excluded_path(path: Path, root: Path) -> bool:
    """Return True if the path is under an excluded directory."""
    try:
        rel = path.relative_to(root)
        parts = rel.parts
        return any(p.lower() in _EXCLUDED_DIRS for p in parts)
    except ValueError:
        return False


def _find_first(root: Path, names: Sequence[str]) -> Optional[Path]:
    for name in names:
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


def _iter_files(
    root: Path, patterns: Sequence[str], max_hits: int, exclude: bool = True
) -> List[Path]:
    hits: List[Path] = []
    for pattern in patterns:
        for p in sorted(root.rglob(pattern)):
            if not p.is_file():
                continue
            if exclude and _is_excluded_path(p, root):
                continue
            hits.append(_normalize(p))
            if len(hits) >= max_hits:
                return hits
    return hits


def _detect_compile_commands(root: Path) -> Optional[Path]:
    direct = root / "compile_commands.json"
    if direct.exists():
        return _normalize(direct)

    # Common locations if the file is not copied to repo root.
    candidates = _iter_files(root, ["**/compile_commands.json"], max_hits=10)
    return candidates[0] if candidates else None


def _detect_cmake(report: BuildSystemReport, max_hits: int) -> None:
    # Only look for presets in non-excluded directories
    presets = _iter_files(report.root, ["CMakePresets.json"], max_hits=max_hits)
    report.cmake_presets.extend(presets)

    # Check for root-level CMakeLists.txt (not filtered)
    cmakelists = _find_first(report.root, ["CMakeLists.txt"])
    if cmakelists:
        report.detected_files.append(DetectedFile(cmakelists, "cmake"))

    # Heuristically detect build directories (only at root level, not recursive).
    build_dir_patterns = [
        "build",
        "build/*",
        "out/build",
        "out/build/*",
        "cmake-build-*",
    ]

    for pattern in build_dir_patterns:
        for d in sorted(report.root.glob(pattern)):
            if not d.is_dir():
                continue
            if _is_excluded_path(d, report.root):
                continue
            cache = d / "CMakeCache.txt"
            if cache.exists():
                report.cmake_build_dirs.append(_normalize(d))

            reply_dir = d / ".cmake" / "api" / "v1" / "reply"
            if reply_dir.exists():
                report.cmake_file_api_build_dirs.append(_normalize(d))

    # Prefer structured data from File API replies.
    for build_dir in report.cmake_file_api_build_dirs:
        targets = _parse_cmake_file_api(build_dir)
        report.cmake_targets.extend(targets)


def _parse_cmake_file_api(build_dir: Path) -> List[CMakeTarget]:
    """Parse CMake File API reply for codemodel targets.

    This expects an already-configured build directory.
    """

    reply_dir = build_dir / ".cmake" / "api" / "v1" / "reply"
    index_files = sorted(reply_dir.glob("index-*.json"))
    if not index_files:
        return []

    # Pick the newest index file.
    index_path = max(index_files, key=lambda p: p.stat().st_mtime)
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        _eprint(f"[build_system_probe] Failed to parse {index_path}: {exc}")
        return []

    # Find the codemodel reply.
    codemodel_rel: Optional[str] = None
    for obj in index.get("objects", []):
        if obj.get("kind") == "codemodel":
            codemodel_rel = obj.get("jsonFile")
            break

    if not codemodel_rel:
        return []

    codemodel_path = reply_dir / codemodel_rel
    try:
        codemodel = json.loads(codemodel_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        _eprint(f"[build_system_probe] Failed to parse {codemodel_path}: {exc}")
        return []

    targets_by_name: Dict[str, CMakeTarget] = {}

    for config in codemodel.get("configurations", []):
        for tgt_ref in config.get("targets", []):
            tgt_file = tgt_ref.get("jsonFile")
            if not tgt_file:
                continue

            tgt_path = reply_dir / tgt_file
            try:
                tgt = json.loads(tgt_path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                _eprint(f"[build_system_probe] Failed to parse {tgt_path}: {exc}")
                continue

            name = tgt.get("name") or ""
            if not name:
                continue

            item = targets_by_name.get(name) or CMakeTarget(name=name)
            item.type = tgt.get("type") or item.type

            for art in tgt.get("artifacts", []) or []:
                path = art.get("path")
                if path and path not in item.artifacts:
                    item.artifacts.append(path)

            for dep in tgt.get("dependencies", []) or []:
                dep_id = dep.get("id")
                # Dependency IDs can be "name::hash"; keep name prefix if possible.
                if dep_id:
                    dep_name = str(dep_id).split("::", 1)[0]
                    if dep_name and dep_name not in item.dependencies:
                        item.dependencies.append(dep_name)

            # Sources is a flat list of source group objects, each with a "path" key.
            # In CMake File API v1, sources can also be in "compileGroups" -> "sources".
            for src in tgt.get("sources", []) or []:
                path = src.get("path")
                if path and path not in item.sources:
                    item.sources.append(path)

            targets_by_name[name] = item

    out = list(targets_by_name.values())
    out.sort(key=lambda t: t.name)
    return out


def _detect_visual_studio(report: BuildSystemReport, max_hits: int) -> None:
    slns = _iter_files(report.root, ["*.sln"], max_hits=max_hits)
    report.vs_solutions.extend(slns)

    for sln in slns:
        projects = _parse_sln(sln)
        report.vs_projects.extend(projects)


def _parse_sln(sln_path: Path) -> List[VisualStudioProject]:
    """Parse a .sln to find referenced .vcxproj projects."""

    text = sln_path.read_text(encoding="utf-8", errors="replace")
    # Example:
    # Project("{GUID}") = "Name", "path\\proj.vcxproj", "{GUID}"
    project_re = re.compile(
        r'^Project\("\{[^}]+\}"\)\s*=\s*"([^"]+)",\s*"([^"]+\.vcxproj)",\s*"(\{[^}]+\})"',
        re.MULTILINE,
    )

    projects: List[VisualStudioProject] = []

    for m in project_re.finditer(text):
        name, rel_path, guid = m.group(1), m.group(2), m.group(3)
        proj_path = _normalize((sln_path.parent / rel_path).resolve())
        proj = VisualStudioProject(name=name, path=proj_path, guid=guid)
        if proj_path.exists():
            _augment_vcxproj(proj)
        projects.append(proj)

    projects.sort(key=lambda p: p.name)
    return projects


def _augment_vcxproj(project: VisualStudioProject) -> None:
    """Parse a .vcxproj for includes/defines and project references."""

    try:
        tree = ET.parse(project.path)
    except Exception as exc:  # noqa: BLE001
        _eprint(f"[build_system_probe] Failed to parse {project.path}: {exc}")
        return

    root = tree.getroot()

    # Namespace handling: vcxproj uses MSBuild XML namespaces.
    ns_match = re.match(r"\{([^}]+)\}", root.tag)
    ns = {"msb": ns_match.group(1)} if ns_match else {}

    def findall(path: str) -> List[ET.Element]:
        return list(root.findall(path, ns))

    # Project references
    for ref in findall(".//msb:ProjectReference") or findall(".//ProjectReference"):
        include = ref.attrib.get("Include")
        if include and include not in project.references:
            project.references.append(include)

    # Includes / defines (best-effort, aggregated across configurations)
    def collect_text(tag_name: str) -> List[str]:
        values: Set[str] = set()
        for el in root.iter():
            if el.tag.endswith(tag_name) and el.text:
                # MSBuild uses ';' separated lists.
                for part in el.text.split(";"):
                    part = part.strip()
                    if not part or part == "%(AdditionalIncludeDirectories)":
                        continue
                    if part == "%(PreprocessorDefinitions)":
                        continue
                    values.add(part)
        return sorted(values)

    project.include_dirs = collect_text("AdditionalIncludeDirectories")
    project.defines = collect_text("PreprocessorDefinitions")


def _detect_xcode(report: BuildSystemReport, max_hits: int) -> None:
    xcode_dirs = [
        p
        for p in sorted(report.root.rglob("*.xcodeproj"))
        if p.is_dir() and not _is_excluded_path(p, report.root)
    ]
    if len(xcode_dirs) > max_hits:
        xcode_dirs = xcode_dirs[:max_hits]

    for xcodeproj in xcode_dirs:
        pbxproj = xcodeproj / "project.pbxproj"
        if pbxproj.exists():
            report.xcode_projects.append(_normalize(xcodeproj))
            report.xcode_targets.extend(_parse_pbxproj(pbxproj))


def _parse_pbxproj(pbxproj_path: Path) -> List[XcodeTarget]:
    """Best-effort parser for project.pbxproj (OpenStep-like plist).

    We avoid external dependencies. This parser extracts:
    - PBXNativeTarget names
    - Basic dependencies (when discoverable)
    - A small subset of build settings from XCBuildConfiguration blocks

    This is not a full pbxproj parser.
    """

    text = pbxproj_path.read_text(encoding="utf-8", errors="replace")

    # Find target IDs of PBXNativeTarget blocks.
    native_target_re = re.compile(
        r"(?P<id>[A-F0-9]{24}) /\* (?P<label>[^*]+) \*/ = \{\s*isa = PBXNativeTarget;(?P<body>.*?)\n\s*\};",
        re.DOTALL,
    )

    targets: Dict[str, XcodeTarget] = {}

    for m in native_target_re.finditer(text):
        target_id = m.group("id")
        body = m.group("body")
        name_match = re.search(r"\bname = ([^;]+);", body)
        name = None
        if name_match:
            name = name_match.group(1).strip().strip('"')
        else:
            # Fallback: label from comment.
            name = m.group("label").strip()

        targets[target_id] = XcodeTarget(name=name)

        # Dependencies via 'dependencies = ( ... );'
        deps_match = re.search(r"\bdependencies = \((?P<deps>.*?)\);", body, re.DOTALL)
        if deps_match:
            deps_text = deps_match.group("deps")
            for dep_id in re.findall(r"([A-F0-9]{24})", deps_text):
                targets[target_id].dependencies.append(dep_id)

    # Map build configuration lists to settings.
    # Extract XCBuildConfiguration blocks keyed by ID.
    build_cfg_re = re.compile(
        r"(?P<id>[A-F0-9]{24}) /\* [^*]+ \*/ = \{\s*isa = XCBuildConfiguration;(?P<body>.*?)\n\s*\};",
        re.DOTALL,
    )
    cfg_settings: Dict[str, Dict[str, str]] = {}

    for m in build_cfg_re.finditer(text):
        cfg_id = m.group("id")
        body = m.group("body")
        settings_match = re.search(r"\bbuildSettings = \{(?P<settings>.*?)\n\s*\};", body, re.DOTALL)
        if not settings_match:
            continue

        settings_block = settings_match.group("settings")
        parsed = _parse_pbx_settings_block(settings_block)
        if parsed:
            cfg_settings[cfg_id] = parsed

    # Targets reference a buildConfigurationList ID; resolve it to config IDs.
    bcl_re = re.compile(
        r"(?P<id>[A-F0-9]{24}) /\* [^*]+ \*/ = \{\s*isa = XCConfigurationList;(?P<body>.*?)\n\s*\};",
        re.DOTALL,
    )
    bcl_to_cfgs: Dict[str, List[str]] = {}

    for m in bcl_re.finditer(text):
        bcl_id = m.group("id")
        body = m.group("body")
        cfgs_match = re.search(r"\bbuildConfigurations = \((?P<cfgs>.*?)\);", body, re.DOTALL)
        if not cfgs_match:
            continue

        cfg_ids = re.findall(r"([A-F0-9]{24})", cfgs_match.group("cfgs"))
        if cfg_ids:
            bcl_to_cfgs[bcl_id] = cfg_ids

    # Attach settings to targets: pick a representative configuration (first).
    for target_id, target in targets.items():
        # Find buildConfigurationList in the PBXNativeTarget body.
        tgt_block_re = re.compile(
            rf"{re.escape(target_id)} /\* [^*]+ \*/ = \{{\s*isa = PBXNativeTarget;(?P<body>.*?)\n\s*\}};",
            re.DOTALL,
        )
        m = tgt_block_re.search(text)
        if not m:
            continue

        body = m.group("body")
        bcl_match = re.search(r"\bbuildConfigurationList = ([A-F0-9]{24});", body)
        if not bcl_match:
            continue

        bcl_id = bcl_match.group(1)
        cfg_ids = bcl_to_cfgs.get(bcl_id, [])
        if not cfg_ids:
            continue

        rep_cfg = cfg_ids[0]
        target.build_settings = cfg_settings.get(rep_cfg, {})

    out = list(targets.values())

    # Resolve dependency IDs to names when possible.
    id_to_name = {tid: t.name for tid, t in targets.items()}
    for t in out:
        t.dependencies = [id_to_name.get(d, d) for d in t.dependencies]
        t.dependencies.sort()

    out.sort(key=lambda t: t.name)
    return out


def _parse_pbx_settings_block(block: str) -> Dict[str, str]:
    """Parse a very small subset of key = value; lines."""

    settings: Dict[str, str] = {}

    # Keep a few build settings useful for documentation.
    keys_of_interest = {
        "HEADER_SEARCH_PATHS",
        "USER_HEADER_SEARCH_PATHS",
        "GCC_PREPROCESSOR_DEFINITIONS",
        "CLANG_CXX_LANGUAGE_STANDARD",
        "CLANG_C_LANGUAGE_STANDARD",
        "OTHER_CFLAGS",
        "OTHER_CPLUSPLUSFLAGS",
        "OTHER_LDFLAGS",
        "PRODUCT_NAME",
    }

    line_re = re.compile(r"\s*([A-Z0-9_]+)\s*=\s*(.+?);\s*$")
    for raw in block.splitlines():
        m = line_re.match(raw)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if key in keys_of_interest:
            settings[key] = value

    return settings


def _render_mermaid_targets(
    targets: Iterable[Tuple[str, Sequence[str]]],
    title: str,
) -> str:
    nodes: Set[str] = set()
    edges: List[Tuple[str, str]] = []

    for src, deps in targets:
        nodes.add(src)
        for dep in deps:
            nodes.add(dep)
            edges.append((src, dep))

    node_ids = {name: f"n{i}" for i, name in enumerate(sorted(nodes))}

    lines: List[str] = ["```mermaid", "flowchart LR"]
    lines.append(f"  %% {title}")

    for name in sorted(nodes):
        lines.append(f'  {node_ids[name]}["{name}"]')

    for src, dep in sorted(edges):
        lines.append(f"  {node_ids[src]} --> {node_ids[dep]}")

    lines.append("```")
    return "\n".join(lines) + "\n"


def _render_markdown(report: BuildSystemReport, include_diagrams: bool) -> str:
    root = report.root
    lines: List[str] = []

    lines.append("## Build System Summary (Generated)")
    lines.append("")

    if report.compile_commands:
        lines.append(f"- compile_commands.json: `{_rel(report.compile_commands, root)}`")
    else:
        lines.append("- compile_commands.json: not found")

    lines.append("")

    if report.cmake_presets or report.cmake_build_dirs or report.cmake_targets:
        lines.append("### CMake")
        lines.append("")
        if report.cmake_presets:
            for p in report.cmake_presets:
                lines.append(f"- Presets: `{_rel(p, root)}`")
        if report.cmake_build_dirs:
            lines.append("- Detected build directories (CMakeCache.txt present):")
            for d in report.cmake_build_dirs:
                lines.append(f"  - `{_rel(d, root)}`")
        if report.cmake_file_api_build_dirs:
            lines.append("- Build directories with CMake File API reply:")
            for d in report.cmake_file_api_build_dirs:
                lines.append(f"  - `{_rel(d, root)}`")
        if report.cmake_targets:
            lines.append("")
            lines.append("Targets (from CMake File API):")
            for t in report.cmake_targets:
                kind = f" ({t.type})" if t.type else ""
                lines.append(f"- {t.name}{kind}")
        else:
            lines.append("")
            lines.append(
                "Richer CMake target information requires an already-configured build "
                "directory with CMake File API replies."
            )
            lines.append("")
            lines.append(
                "If the project is not configured yet, instruct the user to run configure, e.g.:"
            )
            lines.append("")
            lines.append("```sh")
            lines.append("cmake -S . -B build")
            lines.append("```")
        lines.append("")

    if report.vs_solutions or report.vs_projects:
        lines.append("### Visual Studio / MSBuild")
        lines.append("")
        for sln in report.vs_solutions:
            lines.append(f"- Solution: `{_rel(sln, root)}`")
        if report.vs_projects:
            lines.append("")
            lines.append("Projects:")
            for p in report.vs_projects:
                lines.append(f"- {p.name}: `{_rel(p.path, root)}`")
                if p.references:
                    lines.append("  - Project references:")
                    for r in p.references[:20]:
                        lines.append(f"    - `{r}`")
                if p.include_dirs:
                    lines.append("  - Include dirs (aggregated):")
                    for inc in p.include_dirs[:20]:
                        lines.append(f"    - `{inc}`")
                if p.defines:
                    lines.append("  - Defines (aggregated):")
                    for d in p.defines[:20]:
                        lines.append(f"    - `{d}`")
        lines.append("")

    if report.xcode_projects or report.xcode_targets:
        lines.append("### Xcode")
        lines.append("")
        for proj in report.xcode_projects:
            lines.append(f"- Project: `{_rel(proj, root)}`")
        if report.xcode_targets:
            lines.append("")
            lines.append("Targets:")
            for t in report.xcode_targets:
                lines.append(f"- {t.name}")
                if t.build_settings:
                    lines.append("  - Representative build settings:")
                    for k in sorted(t.build_settings.keys()):
                        lines.append(f"    - `{k}` = `{t.build_settings[k]}`")
        lines.append("")

    if include_diagrams:
        # Prefer graphs from structured systems if available.
        cmake_edges = [(t.name, t.dependencies) for t in report.cmake_targets if t.dependencies]
        vs_edges = [(p.name, p.references) for p in report.vs_projects if p.references]
        xcode_edges = [(t.name, t.dependencies) for t in report.xcode_targets if t.dependencies]

        if cmake_edges or vs_edges or xcode_edges:
            lines.append("### Build Target Dependency Graph (Mermaid)")
            lines.append("")

        if cmake_edges:
            lines.append(_render_mermaid_targets(cmake_edges, "CMake targets"))
        if vs_edges:
            lines.append(_render_mermaid_targets(vs_edges, "VS projects"))
        if xcode_edges:
            lines.append(_render_mermaid_targets(xcode_edges, "Xcode targets"))

    return "\n".join(lines) + "\n"


def _write_output(text: str, out_path: Optional[Path]) -> None:
    if out_path is None:
        sys.stdout.write(text)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def run_probe(root: Path, max_hits: int, include_diagrams: bool) -> BuildSystemReport:
    report = BuildSystemReport(root=_normalize(root))

    report.compile_commands = _detect_compile_commands(report.root)

    _detect_cmake(report, max_hits=max_hits)
    _detect_visual_studio(report, max_hits=max_hits)
    _detect_xcode(report, max_hits=max_hits)

    return report


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Probe common C/C++ build systems (CMake, Visual Studio, Xcode) and "
            "emit a Markdown summary for documentation."
        )
    )

    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory (default: .).",
    )
    parser.add_argument(
        "--max-hits",
        type=int,
        default=20,
        help="Limit how many project files are scanned (default: 20).",
    )
    parser.add_argument(
        "--diagrams",
        action="store_true",
        help="Include Mermaid dependency diagrams when possible.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Write Markdown output to a file instead of stdout.",
    )

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser()
    report = run_probe(root=root, max_hits=args.max_hits, include_diagrams=args.diagrams)
    text = _render_markdown(report, include_diagrams=args.diagrams)
    _write_output(text, Path(args.out) if args.out else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
