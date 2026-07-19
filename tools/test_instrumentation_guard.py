#!/usr/bin/env python3
"""Smoke tests for code-professor instrumentation_guard.py."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GUARD_PATH = REPO_ROOT / "skills" / "code-professor" / "scripts" / "instrumentation_guard.py"


def load_guard_module():
    spec = importlib.util.spec_from_file_location("instrumentation_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module from {GUARD_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["instrumentation_guard"] = module
    spec.loader.exec_module(module)
    return module


guard = load_guard_module()


class InstrumentationGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = Path(tempfile.mkdtemp(prefix="code-professor-guard-"))
        self.repo = self.temp_root / "repo"
        self.repo.mkdir()
        self.state_dir = self.temp_root / "state"
        self.target = self.repo / "src" / "probe.py"
        self.target.parent.mkdir(parents=True)
        self.target.write_text("original\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_begin_restore_verify_cleanup_happy_path(self) -> None:
        guard.begin(str(self.repo), str(self.state_dir), ["src/probe.py"])
        self.target.write_text("instrumented\n", encoding="utf-8")

        guard.restore(str(self.state_dir))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "original\n")

        guard.verify(str(self.state_dir))
        guard.cleanup(str(self.state_dir))
        self.assertFalse(self.state_dir.exists())

    def test_verify_fails_when_file_still_modified(self) -> None:
        guard.begin(str(self.repo), str(self.state_dir), ["src/probe.py"])
        self.target.write_text("instrumented\n", encoding="utf-8")

        with self.assertRaises(guard.GuardError):
            guard.verify(str(self.state_dir))

    def test_cleanup_refuses_when_paths_differ(self) -> None:
        guard.begin(str(self.repo), str(self.state_dir), ["src/probe.py"])
        self.target.write_text("instrumented\n", encoding="utf-8")

        with self.assertRaises(guard.GuardError):
            guard.cleanup(str(self.state_dir))
        self.assertTrue(self.state_dir.exists())

    def test_state_dir_inside_repo_is_rejected(self) -> None:
        inside = self.repo / "snapshots"
        with self.assertRaises(guard.GuardError):
            guard.begin(str(self.repo), str(inside), ["src/probe.py"])

    def test_repeated_begin_preserves_first_snapshot(self) -> None:
        guard.begin(str(self.repo), str(self.state_dir), ["src/probe.py"])
        self.target.write_text("first edit\n", encoding="utf-8")
        guard.begin(str(self.repo), str(self.state_dir), ["src/probe.py"])

        guard.restore(str(self.state_dir))
        self.assertEqual(self.target.read_text(encoding="utf-8"), "original\n")

    def test_snapshot_missing_file_and_restore_removes_created_file(self) -> None:
        missing = self.repo / "src" / "new.py"
        guard.begin(str(self.repo), str(self.state_dir), ["src/new.py"])
        missing.write_text("created during experiment\n", encoding="utf-8")

        guard.restore(str(self.state_dir))
        self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
