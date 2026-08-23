#!/usr/bin/env python3
"""Snapshot, restore, and verify files used for temporary instrumentation.

The state directory must be outside the repository. The first snapshot of a path
is retained, so repeated `begin` calls can add files without replacing their
original state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

METADATA_NAME = "metadata.json"
BACKUP_DIR_NAME = "backups"
FORMAT_VERSION = 1


class GuardError(RuntimeError):
    """Raised for a safe, user-actionable guard failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_repo(repo_arg: str) -> Path:
    repo = Path(repo_arg).expanduser().resolve()
    if not repo.is_dir():
        raise GuardError(f"Repository root is not a directory: {repo}")
    return repo


def resolve_state_dir(state_arg: str, repo: Path | None = None) -> Path:
    state_dir = Path(state_arg).expanduser().resolve()
    if repo is not None and is_relative_to(state_dir, repo):
        raise GuardError(
            "State directory must be outside the repository to avoid creating "
            f"repository changes: {state_dir}"
        )
    return state_dir


def metadata_path(state_dir: Path) -> Path:
    return state_dir / METADATA_NAME


def load_metadata(state_dir: Path) -> Dict[str, Any]:
    path = metadata_path(state_dir)
    if not path.is_file():
        raise GuardError(f"Snapshot metadata not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GuardError(f"Cannot read snapshot metadata: {exc}") from exc
    if data.get("format_version") != FORMAT_VERSION:
        raise GuardError(
            f"Unsupported snapshot format: {data.get('format_version')!r}"
        )
    if not isinstance(data.get("files"), dict):
        raise GuardError("Snapshot metadata has no valid files map")
    return data


def write_metadata(state_dir: Path, data: Dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    destination = metadata_path(state_dir)
    fd, temporary_name = tempfile.mkstemp(
        prefix="metadata-", suffix=".json", dir=str(state_dir)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, destination)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def normalize_target(repo: Path, raw: str) -> Tuple[str, Path]:
    supplied = Path(raw).expanduser()
    target = supplied if supplied.is_absolute() else repo / supplied
    target = Path(os.path.abspath(target))
    if not is_relative_to(target, repo):
        raise GuardError(f"Target is outside repository: {raw}")
    resolved_parent = target.parent.resolve()
    if not is_relative_to(resolved_parent, repo):
        raise GuardError(
            "Target reaches outside the repository through a symlinked parent: "
            f"{raw}"
        )
    if target == repo:
        raise GuardError("Repository root cannot be snapshotted as a file")
    relative = target.relative_to(repo).as_posix()
    return relative, target


def lstat_type(path: Path) -> str:
    mode = path.lstat().st_mode
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISDIR(mode):
        return "directory"
    return "special"


def remove_current_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.exists():
        raise GuardError(
            f"Refusing to remove a directory or special path during restore: {path}"
        )


def begin(repo_arg: str, state_arg: str, raw_paths: Iterable[str]) -> None:
    repo = resolve_repo(repo_arg)
    state_dir = resolve_state_dir(state_arg, repo)
    raw_list = list(raw_paths)
    if not raw_list:
        raise GuardError("At least one repository-relative file path is required")

    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / BACKUP_DIR_NAME).mkdir(parents=True, exist_ok=True)

    if metadata_path(state_dir).exists():
        data = load_metadata(state_dir)
        stored_repo = Path(data["repo_root"]).resolve()
        if stored_repo != repo:
            raise GuardError(
                f"Snapshot belongs to a different repository: {stored_repo}"
            )
    else:
        data = {
            "format_version": FORMAT_VERSION,
            "repo_root": str(repo),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": {},
        }

    added: List[str] = []
    skipped: List[str] = []
    for raw in raw_list:
        relative, target = normalize_target(repo, raw)
        if relative in data["files"]:
            skipped.append(relative)
            continue

        entry: Dict[str, Any] = {"relative_path": relative}
        if target.is_symlink():
            entry.update(
                {
                    "existed": True,
                    "kind": "symlink",
                    "link_target": os.readlink(target),
                    "mode": stat.S_IMODE(target.lstat().st_mode),
                }
            )
        elif target.exists():
            kind = lstat_type(target)
            if kind != "file":
                raise GuardError(
                    f"Only regular files and symlinks can be snapshotted: {target} ({kind})"
                )
            index = len(data["files"])
            backup_name = f"{index:06d}.bin"
            backup_path = state_dir / BACKUP_DIR_NAME / backup_name
            shutil.copyfile(target, backup_path)
            entry.update(
                {
                    "existed": True,
                    "kind": "file",
                    "mode": stat.S_IMODE(target.stat().st_mode),
                    "sha256": sha256_file(target),
                    "backup": f"{BACKUP_DIR_NAME}/{backup_name}",
                }
            )
        else:
            entry.update({"existed": False, "kind": "missing"})

        data["files"][relative] = entry
        write_metadata(state_dir, data)
        added.append(relative)

    print(f"Snapshot directory: {state_dir}")
    for relative in added:
        print(f"SNAPSHOTTED {relative}")
    for relative in skipped:
        print(f"ALREADY_SNAPSHOTTED {relative}")


def inspect_entry(repo: Path, entry: Dict[str, Any]) -> List[str]:
    relative = entry["relative_path"]
    path = repo / relative
    differences: List[str] = []

    if not entry["existed"]:
        if path.exists() or path.is_symlink():
            differences.append("path exists but did not exist at snapshot")
        return differences

    if not (path.exists() or path.is_symlink()):
        differences.append("path is missing")
        return differences

    expected_kind = entry["kind"]
    actual_kind = lstat_type(path)
    if actual_kind != expected_kind:
        differences.append(
            f"kind changed from {expected_kind} to {actual_kind}"
        )
        return differences

    actual_mode = stat.S_IMODE(path.lstat().st_mode)
    if actual_mode != entry.get("mode"):
        differences.append(
            f"mode changed from {entry.get('mode'):04o} to {actual_mode:04o}"
        )

    if expected_kind == "file":
        actual_hash = sha256_file(path)
        if actual_hash != entry["sha256"]:
            differences.append(
                f"content hash changed from {entry['sha256']} to {actual_hash}"
            )
    elif expected_kind == "symlink":
        actual_target = os.readlink(path)
        if actual_target != entry["link_target"]:
            differences.append(
                "symlink target changed from "
                f"{entry['link_target']!r} to {actual_target!r}"
            )
    return differences


def collect_differences(data: Dict[str, Any]) -> Dict[str, List[str]]:
    repo = Path(data["repo_root"]).resolve()
    return {
        relative: differences
        for relative, entry in sorted(data["files"].items())
        if (differences := inspect_entry(repo, entry))
    }


def restore(state_arg: str) -> None:
    state_dir = resolve_state_dir(state_arg)
    data = load_metadata(state_dir)
    repo = Path(data["repo_root"]).resolve()
    if not repo.is_dir():
        raise GuardError(f"Repository root no longer exists: {repo}")

    for relative, entry in sorted(data["files"].items()):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)

        if not entry["existed"]:
            if target.is_symlink() or target.is_file():
                target.unlink()
            elif target.exists():
                raise GuardError(
                    f"Refusing to remove directory created at guarded file path: {target}"
                )
            print(f"RESTORED_MISSING {relative}")
            continue

        remove_current_path(target)
        if entry["kind"] == "symlink":
            os.symlink(entry["link_target"], target)
        elif entry["kind"] == "file":
            backup = state_dir / entry["backup"]
            if not backup.is_file():
                raise GuardError(f"Backup file is missing: {backup}")
            fd, temporary_name = tempfile.mkstemp(
                prefix=f".{target.name}.code-professor-", dir=str(target.parent)
            )
            try:
                with os.fdopen(fd, "wb") as destination, backup.open("rb") as source:
                    shutil.copyfileobj(source, destination)
                    destination.flush()
                    os.fsync(destination.fileno())
                os.chmod(temporary_name, entry["mode"])
                os.replace(temporary_name, target)
            except Exception:
                try:
                    os.unlink(temporary_name)
                except FileNotFoundError:
                    pass
                raise
        else:
            raise GuardError(f"Unsupported snapshot kind for {relative}")
        print(f"RESTORED {relative}")

    differences = collect_differences(data)
    if differences:
        for relative, items in differences.items():
            for item in items:
                print(f"DIFFERENT {relative}: {item}", file=sys.stderr)
        raise GuardError("Restoration completed but verification failed")
    print("RESTORE_VERIFIED")


def verify(state_arg: str) -> None:
    state_dir = resolve_state_dir(state_arg)
    data = load_metadata(state_dir)
    differences = collect_differences(data)
    if differences:
        for relative, items in differences.items():
            for item in items:
                print(f"DIFFERENT {relative}: {item}")
        raise GuardError(f"Verification failed for {len(differences)} path(s)")
    print(f"VERIFIED {len(data['files'])} path(s)")


def status(state_arg: str) -> None:
    state_dir = resolve_state_dir(state_arg)
    data = load_metadata(state_dir)
    output = {
        "state_dir": str(state_dir),
        "repo_root": data["repo_root"],
        "created_at_utc": data["created_at_utc"],
        "guarded_paths": sorted(data["files"]),
        "differences": collect_differences(data),
    }
    print(json.dumps(output, indent=2, sort_keys=True))


def cleanup(state_arg: str) -> None:
    state_dir = resolve_state_dir(state_arg)
    data = load_metadata(state_dir)
    differences = collect_differences(data)
    if differences:
        for relative, items in differences.items():
            for item in items:
                print(f"DIFFERENT {relative}: {item}", file=sys.stderr)
        raise GuardError("Refusing cleanup because guarded paths differ from snapshots")
    shutil.rmtree(state_dir)
    print(f"REMOVED_SNAPSHOT {state_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Guard files modified for temporary code instrumentation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    begin_parser = subparsers.add_parser(
        "begin", help="Snapshot one or more repository paths before editing"
    )
    begin_parser.add_argument("--repo", required=True, help="Repository root")
    begin_parser.add_argument(
        "--state-dir", required=True, help="Snapshot directory outside the repository"
    )
    begin_parser.add_argument(
        "paths", nargs="+", help="Repository-relative files to guard"
    )

    for command, help_text in (
        ("restore", "Restore all guarded paths exactly"),
        ("verify", "Verify guarded paths match their snapshots"),
        ("status", "Print guarded paths and current differences as JSON"),
        ("cleanup", "Delete a verified snapshot directory"),
    ):
        command_parser = subparsers.add_parser(command, help=help_text)
        command_parser.add_argument("--state-dir", required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "begin":
            begin(args.repo, args.state_dir, args.paths)
        elif args.command == "restore":
            restore(args.state_dir)
        elif args.command == "verify":
            verify(args.state_dir)
        elif args.command == "status":
            status(args.state_dir)
        elif args.command == "cleanup":
            cleanup(args.state_dir)
        else:
            parser.error(f"Unknown command: {args.command}")
        return 0
    except GuardError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
