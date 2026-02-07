"""code_doc_helper.py

Optional documentation analysis helper for C/C++ projects.

This script prefers libclang (via Python bindings `clang.cindex`) when available,
and falls back to lightweight parsing when it is not.

Primary use cases:
- Generate a lightweight API index (namespaces, types, functions) from translation
  units referenced by compile_commands.json.
- Generate an include/component dependency graph and emit Mermaid.

The intent is to support documentation authoring (e.g., the `document-cpp-code`
skill), not to be a full documentation generator.
"""

from __future__ import annotations

import argparse
import ctypes.util
import json
import os
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple


@dataclass(frozen=True)
class CompileCommand:
    directory: Path
    file: Path
    arguments: List[str]


@dataclass(frozen=True)
class BackendSelection:
    backend: str
    reason: str


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


def _repo_root_from_here() -> Path:
    """Attempt to find repo root by walking up to find .git or fallback to cwd."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "CMakeLists.txt").exists():
            return parent
    # Fallback: assume script is at .github/skills/<skill>/scripts/<script>.py
    if len(here.parents) >= 5:
        return here.parents[4]
    return Path.cwd()


def _normalize_path(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def _load_compile_commands(compdb_path: Path) -> List[CompileCommand]:
    """Load compile_commands.json into structured commands."""

    if not compdb_path.exists():
        raise FileNotFoundError(str(compdb_path))

    data = json.loads(compdb_path.read_text(encoding="utf-8"))
    commands: List[CompileCommand] = []

    for entry in data:
        directory = Path(entry["directory"]).expanduser()
        file_path = Path(entry["file"]).expanduser()

        if "arguments" in entry and isinstance(entry["arguments"], list):
            arguments = [str(a) for a in entry["arguments"]]
        else:
            arguments = shlex.split(str(entry["command"]))

        commands.append(
            CompileCommand(
                directory=_normalize_path(directory),
                file=_normalize_path(directory / file_path)
                if not file_path.is_absolute()
                else _normalize_path(file_path),
                arguments=arguments,
            )
        )

    return commands


def _sanitize_compiler_args(arguments: Sequence[str]) -> List[str]:
    """Return a libclang-friendly args list."""

    args = list(arguments)
    if args:
        args = args[1:]

    sanitized: List[str] = []
    skip_next = False

    drop_with_value = {
        "-o",
        "-MF",
        "-MT",
        "-MQ",
        "-Xclang",
        "-include-pch",
        "-isysroot",
        "--sysroot",
    }

    for token in args:
        if skip_next:
            skip_next = False
            continue

        if token in {"-c"}:
            continue

        if token in drop_with_value:
            skip_next = True
            continue

        if token.startswith("-o") and token != "-o":
            continue

        if token.startswith("-MF") and token != "-MF":
            continue

        if token.startswith("-fdiagnostics"):
            continue

        sanitized.append(token)

    return sanitized


def _collect_compdb_targets(
    commands: Sequence[CompileCommand],
    inputs: Sequence[Path],
) -> List[CompileCommand]:
    normalized_inputs = [_normalize_path(p) for p in inputs]

    selected: List[CompileCommand] = []
    for cmd in commands:
        for inp in normalized_inputs:
            if inp.is_dir():
                try:
                    cmd.file.relative_to(inp)
                except ValueError:
                    continue
                selected.append(cmd)
                break

            if inp.is_file() and cmd.file == inp:
                selected.append(cmd)
                break

    selected.sort(key=lambda c: str(c.file))
    return selected


def _try_configure_libclang() -> BackendSelection:
    try:
        from clang import cindex  # type: ignore
    except ImportError:
        return BackendSelection(
            backend="fallback",
            reason=(
                "Python bindings for libclang not found (missing 'clang' module)."
            ),
        )

    lib_file = os.environ.get("LIBCLANG_FILE")
    lib_path = os.environ.get("LIBCLANG_PATH") or os.environ.get(
        "CLANG_LIBRARY_PATH"
    )

    try:
        if lib_file:
            cindex.Config.set_library_file(lib_file)
        elif lib_path:
            cindex.Config.set_library_path(lib_path)
        else:
            found = ctypes.util.find_library("clang")
            if found:
                cindex.Config.set_library_file(found)

        _ = cindex.Index.create()
    except Exception as exc:  # noqa: BLE001
        return BackendSelection(
            backend="fallback",
            reason=(
                "libclang bindings present but could not load libclang. "
                "Set LIBCLANG_FILE to an absolute path to libclang.so, or set "
                "LIBCLANG_PATH to the directory containing it. "
                f"Original error: {exc}"
            ),
        )

    return BackendSelection(backend="libclang", reason="libclang available")


def _select_backend(requested: str) -> BackendSelection:
    requested = requested.strip().lower()
    if requested not in {"auto", "libclang", "fallback"}:
        return BackendSelection(
            backend="fallback",
            reason=f"Unknown backend '{requested}', using fallback.",
        )

    if requested == "fallback":
        return BackendSelection(backend="fallback", reason="requested fallback")

    configured = _try_configure_libclang()
    if requested == "libclang" and configured.backend != "libclang":
        return configured

    if requested == "auto":
        return configured

    return BackendSelection(backend="libclang", reason="requested libclang")


def _compile_db_path(arg: Optional[str], root: Path) -> Path:
    if arg:
        return _normalize_path(Path(arg).expanduser())
    return _normalize_path(root / "compile_commands.json")


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _component_key(path: Path, root: Path, depth: int) -> str:
    rel = _rel(path, root)
    parts = [p for p in rel.split("/") if p and p != "."]
    if not parts:
        return "."
    return "/".join(parts[: max(1, depth)])


def _read_text_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1").splitlines()


def _is_header(path: Path) -> bool:
    return path.suffix.lower() in {".h", ".hh", ".hpp", ".hxx"}


def _is_source(path: Path) -> bool:
    return path.suffix.lower() in {".c", ".cc", ".cpp", ".cxx"}


def _classify_symbol_location(loc_path: Path, root: Path) -> str:
    """Classify a symbol location into a documentation-oriented bucket.

    Heuristics:
    - Headers under include/ are treated as "public".
    - Other headers are treated as "internal headers".
    - Sources are treated as "sources".

    This is intentionally simple and works reasonably well for many C/C++ repos.
    """

    loc_path = _normalize_path(loc_path)
    try:
        rel = loc_path.relative_to(root)
        rel_str = str(rel).replace("\\", "/")
    except ValueError:
        rel_str = str(loc_path).replace("\\", "/")

    if _is_header(loc_path):
        if rel_str.startswith("include/"):
            return "public-headers"
        return "internal-headers"

    if _is_source(loc_path):
        return "sources"

    return "other"


def _fallback_includes_edges(
    root: Path,
    targets: Sequence[CompileCommand],
    component_depth: int,
    include_system: bool,
) -> Dict[Tuple[str, str], int]:
    include_re = re.compile(r"^\s*#\s*include\s*([<\"])([^>\"]+)[>\"]")

    edges: Dict[Tuple[str, str], int] = {}

    for cmd in targets:
        lines = _read_text_lines(cmd.file)
        src_component = _component_key(cmd.file, root, component_depth)
        for line in lines:
            m = include_re.match(line)
            if not m:
                continue

            bracket, header = m.group(1), m.group(2).strip()
            if bracket == "<" and not include_system:
                continue

            key = (src_component, header if bracket == "<" else header)
            edges[key] = edges.get(key, 0) + 1

    return edges


def _emit_mermaid_component_graph(
    edges: Dict[Tuple[str, str], int],
    label_counts: bool,
) -> str:
    lines: List[str] = ["```mermaid", "flowchart LR"]

    nodes: Set[str] = set()
    for src, dst in edges.keys():
        nodes.add(src)
        nodes.add(dst)

    node_ids: Dict[str, str] = {}
    for i, node in enumerate(sorted(nodes)):
        node_ids[node] = f"n{i}"

    for node in sorted(nodes):
        node_id = node_ids[node]
        lines.append(f'  {node_id}["{node}"]')

    for (src, dst), count in sorted(
        edges.items(),
        key=lambda kv: (kv[0][0], kv[0][1]),
    ):
        src_id = node_ids[src]
        dst_id = node_ids[dst]
        if label_counts and count > 1:
            lines.append(f"  {src_id} -->|{count}| {dst_id}")
        else:
            lines.append(f"  {src_id} --> {dst_id}")

    lines.append("```")
    return "\n".join(lines) + "\n"


def _libclang_includes_edges(
    root: Path,
    targets: Sequence[CompileCommand],
    component_depth: int,
    include_system: bool,
) -> Dict[Tuple[str, str], int]:
    from clang import cindex  # type: ignore

    edges: Dict[Tuple[str, str], int] = {}
    index = cindex.Index.create()

    for cmd in targets:
        args = _sanitize_compiler_args(cmd.arguments)
        try:
            tu = index.parse(
                path=str(cmd.file),
                args=list(args) + ["-fparse-all-comments"],
                options=cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
            )
        except Exception as exc:  # noqa: BLE001
            _eprint(f"[code_doc_helper] Failed to parse {cmd.file}: {exc}")
            continue

        src_component = _component_key(cmd.file, root, component_depth)

        for inc in tu.get_includes():
            included = inc.include
            if included is None:
                continue

            included_path = Path(str(included.name))

            if included_path.exists():
                included_path = _normalize_path(included_path)
                try:
                    included_path.relative_to(root)
                    dst_component = _component_key(
                        included_path, root, component_depth
                    )
                except ValueError:
                    if not include_system:
                        continue
                    dst_component = _rel(included_path, root)
            else:
                if not include_system:
                    continue
                dst_component = f"<{included.name}>"

            key = (src_component, dst_component)
            edges[key] = edges.get(key, 0) + 1

    return edges


def _walk(cursor, visitor) -> None:
    visitor(cursor)
    for child in cursor.get_children():
        _walk(child, visitor)


def _qualified_namespace(cursor) -> str:
    parts: List[str] = []
    cur = cursor.semantic_parent

    while cur is not None:
        kind_name = getattr(cur.kind, "name", "")
        if kind_name in {"NAMESPACE", "NAMESPACE_ALIAS"}:
            if cur.spelling:
                parts.append(cur.spelling)
        cur = getattr(cur, "semantic_parent", None)

    parts.reverse()
    return "::".join(parts)


def _libclang_index_markdown(
    root: Path,
    targets: Sequence[CompileCommand],
    include_private: bool,
) -> str:
    from clang import cindex  # type: ignore

    index = cindex.Index.create()

    # group -> namespace -> set of items
    grouped: Dict[str, Dict[str, Set[str]]] = {}
    # Track seen symbols to avoid duplicates from forward declarations
    seen_symbols: Set[Tuple[str, str, str]] = set()  # (group, ns, fq)

    def visit(cursor: "cindex.Cursor") -> None:
        if cursor.location is None or cursor.location.file is None:
            return

        loc_path = _normalize_path(Path(str(cursor.location.file)))
        if not include_private:
            try:
                loc_path.relative_to(root)
            except ValueError:
                return

        kind = cursor.kind
        is_type = kind in {
            cindex.CursorKind.CLASS_DECL,
            cindex.CursorKind.STRUCT_DECL,
            cindex.CursorKind.ENUM_DECL,
            cindex.CursorKind.CLASS_TEMPLATE,
        }
        is_func = kind in {
            cindex.CursorKind.FUNCTION_DECL,
            cindex.CursorKind.CXX_METHOD,
            cindex.CursorKind.CONSTRUCTOR,
            cindex.CursorKind.DESTRUCTOR,
        }

        # Skip forward declarations for types (no definition body)
        if is_type and not cursor.is_definition():
            return

        if not (is_type or is_func):
            return

        name = cursor.spelling or ""
        if not name:
            return

        ns = _qualified_namespace(cursor)
        fq = f"{ns}::{name}" if ns else name

        group = _classify_symbol_location(loc_path, root)

        # Skip if we've already seen this symbol (avoids duplicates from multiple TUs)
        key = (group, ns or "(global)", fq)
        if key in seen_symbols:
            return
        seen_symbols.add(key)

        grouped.setdefault(group, {}).setdefault(ns or "(global)", set()).add(fq)

    for cmd in targets:
        args = _sanitize_compiler_args(cmd.arguments)
        try:
            tu = index.parse(
                path=str(cmd.file),
                args=list(args) + ["-fparse-all-comments"],
                options=cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES,
            )
        except Exception as exc:  # noqa: BLE001
            _eprint(f"[code_doc_helper] Failed to parse {cmd.file}: {exc}")
            continue

        for c in tu.cursor.get_children():
            _walk(c, visit)

    def render_group(title: str, group_key: str) -> List[str]:
        if group_key not in grouped:
            return []

        out: List[str] = []
        out.append(f"### {title}")
        out.append("")
        for ns in sorted(grouped[group_key].keys()):
            out.append(f"#### {ns}")
            out.append("")
            for item in sorted(grouped[group_key][ns]):
                out.append(f"- {item}")
            out.append("")
        return out

    lines: List[str] = []
    lines.append("## API Index (Generated)")
    lines.append("")
    lines.append(
        "This index is grouped by symbol location: public headers (include/), "
        "internal headers, and sources."
    )
    lines.append("")

    # Order matters for readability.
    lines.extend(render_group("Public API (Headers under include/)", "public-headers"))
    lines.extend(render_group("Internal Headers", "internal-headers"))
    lines.extend(render_group("Sources", "sources"))
    lines.extend(render_group("Other", "other"))

    if not grouped:
        lines.append("_No symbols found. Check stderr for parse errors._")
        lines.append("")

    return "\n".join(lines) + "\n"


def _fallback_index_markdown(
    root: Path,
    targets: Sequence[CompileCommand],
) -> str:
    lines: List[str] = []
    lines.append("## API Index (Generated)")
    lines.append("")
    lines.append("_Note: generated without libclang; results are approximate._")
    lines.append("")

    token_re = re.compile(
        r"\b(class|struct|enum)\s+([A-Za-z_][A-Za-z0-9_]*)|"
        r"\b([A-Za-z_][A-Za-z0-9_:<>]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
    )

    # group -> file -> set of items
    found: Dict[str, Dict[str, Set[str]]] = {}

    for cmd in targets:
        try:
            cmd.file.relative_to(root)
        except ValueError:
            continue

        for line in _read_text_lines(cmd.file):
            m = token_re.search(line)
            if not m:
                continue

            item = m.group(2) or m.group(4) or ""
            if not item:
                continue

            group = _classify_symbol_location(cmd.file, root)
            file_key = _rel(cmd.file, root)
            found.setdefault(group, {}).setdefault(file_key, set()).add(item)

    def render_group(title: str, group_key: str) -> None:
        if group_key not in found:
            return
        lines.append(f"### {title}")
        lines.append("")
        for file_key in sorted(found[group_key].keys()):
            lines.append(f"#### {file_key}")
            lines.append("")
            for item in sorted(found[group_key][file_key]):
                lines.append(f"- {item}")
            lines.append("")

    render_group("Public API (Headers under include/)", "public-headers")
    render_group("Internal Headers", "internal-headers")
    render_group("Sources", "sources")
    render_group("Other", "other")

    return "\n".join(lines) + "\n"


def _write_output(text: str, out_path: Optional[Path]) -> None:
    if out_path is None:
        sys.stdout.write(text)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def cmd_includes(args: argparse.Namespace) -> int:
    root = _normalize_path(Path(args.root).expanduser())
    compdb_path = _compile_db_path(args.compdb, root)

    backend = _select_backend(args.backend)
    if backend.backend != "libclang":
        _eprint(f"[code_doc_helper] Using fallback backend: {backend.reason}")

    try:
        commands = _load_compile_commands(compdb_path)
    except FileNotFoundError:
        _eprint(
            "[code_doc_helper] compile_commands.json not found. "
            "Configure CMake with export compile commands enabled, or provide "
            "--compdb PATH."
        )
        return 2

    targets = _collect_compdb_targets(commands, [Path(p) for p in args.inputs])
    if not targets:
        _eprint(
            "[code_doc_helper] No translation units matched inputs. "
            "Pass a directory containing .cpp files (or specific .cpp files) "
            "that exist in compile_commands.json."
        )
        return 3

    if backend.backend == "libclang":
        edges = _libclang_includes_edges(
            root=root,
            targets=targets,
            component_depth=args.component_depth,
            include_system=args.include_system,
        )
    else:
        edges = _fallback_includes_edges(
            root=root,
            targets=targets,
            component_depth=args.component_depth,
            include_system=args.include_system,
        )

    header = "## Include / Component Graph (Generated)\n\n"
    if backend.backend != "libclang":
        header += (
            "_Note: generated without libclang; results may be approximate._\n\n"
        )

    mermaid = _emit_mermaid_component_graph(
        edges=edges,
        label_counts=not args.no_label_counts,
    )

    _write_output(header + mermaid, Path(args.out) if args.out else None)
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    root = _normalize_path(Path(args.root).expanduser())
    compdb_path = _compile_db_path(args.compdb, root)

    backend = _select_backend(args.backend)
    if backend.backend != "libclang":
        _eprint(f"[code_doc_helper] Using fallback backend: {backend.reason}")

    try:
        commands = _load_compile_commands(compdb_path)
    except FileNotFoundError:
        _eprint(
            "[code_doc_helper] compile_commands.json not found. "
            "Configure CMake with export compile commands enabled, or provide "
            "--compdb PATH."
        )
        return 2

    targets = _collect_compdb_targets(commands, [Path(p) for p in args.inputs])
    if not targets:
        _eprint(
            "[code_doc_helper] No translation units matched inputs. "
            "Pass a directory containing .cpp files (or specific .cpp files) "
            "that exist in compile_commands.json."
        )
        return 3

    if backend.backend == "libclang":
        content = _libclang_index_markdown(
            root=root,
            targets=targets,
            include_private=args.include_private,
        )
    else:
        content = _fallback_index_markdown(
            root=root,
            targets=targets,
        )

    _write_output(content, Path(args.out) if args.out else None)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Optional documentation helper. Prefers libclang when available "
            "and falls back otherwise."
        )
    )

    parser.add_argument(
        "--root",
        default=str(_repo_root_from_here()),
        help="Repository root (used for relative paths and filtering).",
    )
    parser.add_argument(
        "--compdb",
        default=None,
        help="Path to compile_commands.json (default: <root>/compile_commands.json).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    includes = sub.add_parser(
        "includes",
        help="Generate a Mermaid include/component dependency graph.",
    )
    includes.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="File(s) or directory(ies) to select translation units from compdb.",
    )
    includes.add_argument(
        "--backend",
        default="auto",
        help="auto|libclang|fallback (default: auto).",
    )
    includes.add_argument(
        "--component-depth",
        type=int,
        default=2,
        help=(
            "Directory depth used to group files into components "
            "(default: 2, e.g. src/engine)."
        ),
    )
    includes.add_argument(
        "--include-system",
        action="store_true",
        help="Include system headers (may be noisy).",
    )
    includes.add_argument(
        "--no-label-counts",
        action="store_true",
        help="Do not label edges with include counts.",
    )
    includes.add_argument(
        "--out",
        default=None,
        help="Write output to a file instead of stdout.",
    )
    includes.set_defaults(func=cmd_includes)

    index = sub.add_parser(
        "index",
        help="Generate a lightweight API index as Markdown.",
    )
    index.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="File(s) or directory(ies) to select translation units from compdb.",
    )
    index.add_argument(
        "--backend",
        default="auto",
        help="auto|libclang|fallback (default: auto).",
    )
    index.add_argument(
        "--include-private",
        action="store_true",
        help="Include declarations outside --root (mostly for debugging).",
    )
    index.add_argument(
        "--out",
        default=None,
        help="Write output to a file instead of stdout.",
    )
    index.set_defaults(func=cmd_index)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    ns = parser.parse_args(argv)
    return int(ns.func(ns))


if __name__ == "__main__":
    raise SystemExit(main())
