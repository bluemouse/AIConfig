#!/usr/bin/env python3
"""Tests for run_loop.py single-instance lock and run metadata.

Covers the concurrent-run failure mode seen 2026-11-20: many agents each
launched run_loop against the same skill, duplicating API spend. The lock
must make the second launcher fail fast (exit 2, no API calls) and the
metadata must make every results dir attributable.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "run_loop.py"

# Import as a package (requires skill-creator root on sys.path, matching the
# "python -m scripts.run_loop" module form used in real invocations).
sys.path.insert(0, str(SCRIPT.parent.parent))
from scripts import run_loop  # noqa: E402


def make_skill_dir(root: Path, name: str = "demo-skill") -> Path:
    skill_dir = root / name
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: demo skill for lock tests\n---\n\nBody.\n"
    )
    return skill_dir


class LoopLockTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.lock_dir = self.root / "locks"
        self.skill_dir = make_skill_dir(self.root)

    def tearDown(self):
        # Release any lock this test left held so later tests start clean.
        if run_loop._held_lock_fd is not None:
            run_loop.release_lock()
        self._tmp.cleanup()

    def test_acquire_creates_lock_then_second_acquire_raises(self):
        lock_path = run_loop.acquire_lock(self.skill_dir, self.lock_dir)
        self.assertTrue(lock_path.exists())
        holder = json.loads(lock_path.read_text())
        self.assertEqual(holder["pid"], run_loop.os.getpid())
        # flock is per open file description, so even this same process is
        # refused on a second open — the race-safety property we need.
        with self.assertRaises(run_loop.LoopLockError) as ctx:
            run_loop.acquire_lock(self.skill_dir, self.lock_dir)
        # Error must point the duplicate at the existing holder.
        self.assertIn(str(holder["pid"]), str(ctx.exception))

    def test_release_allows_reacquire(self):
        lock_path = run_loop.acquire_lock(self.skill_dir, self.lock_dir)
        run_loop.release_lock()
        run_loop.acquire_lock(self.skill_dir, self.lock_dir)  # no raise
        run_loop.release_lock()

    def test_lock_from_dead_process_is_reacquirable(self):
        # flock is released by the kernel on holder death — the stale-lock
        # overwrite case is gone by construction. Verify it end to end.
        code = (
            "import sys; from pathlib import Path; "
            f"sys.path.insert(0, {str(SCRIPT.parent.parent)!r}); "
            "from scripts import run_loop; "
            f"run_loop.acquire_lock(Path({str(self.skill_dir)!r}), Path({str(self.lock_dir)!r}))"
        )
        child = subprocess.Popen([sys.executable, "-c", code])
        child.wait()
        lock_files = list(self.lock_dir.glob("*.lock"))
        self.assertEqual(len(lock_files), 1)
        # Dead holder: acquisition succeeds (kernel already released it).
        run_loop.acquire_lock(self.skill_dir, self.lock_dir)  # no raise
        run_loop.release_lock()

    def test_corrupt_lock_content_does_not_block_acquisition(self):
        # Advisory JSON is unreadable but the flock arbiter still works:
        # refusal depends only on the flock, and acquisition rewrites the
        # content through the held fd.
        lock_path = run_loop.acquire_lock(self.skill_dir, self.lock_dir)
        run_loop.release_lock()
        lock_path.write_text("{not json")  # corrupt leftover, no holder
        lock_path2 = run_loop.acquire_lock(self.skill_dir, self.lock_dir)  # no raise
        self.assertEqual(json.loads(lock_path2.read_text())["pid"], run_loop.os.getpid())
        run_loop.release_lock()

    def test_update_held_lock_results_dir_is_best_effort(self):
        lock_path = run_loop.acquire_lock(self.skill_dir, self.lock_dir)
        run_loop.update_held_lock_results_dir(self.root / "results")
        holder = json.loads(lock_path.read_text())
        self.assertEqual(holder["results_dir"], str(self.root / "results"))
        # Not-held case: update without an acquire is a silent no-op.
        run_loop.update_held_lock_results_dir(self.root / "results")  # no raise

    def test_locks_are_per_skill_path(self):
        other_skill = make_skill_dir(self.root, "other-skill")
        # Hold one skill's lock; a different skill must map to a different
        # lock file and acquire without contention.
        import hashlib
        def lock_name(p: Path) -> str:
            return hashlib.sha256(str(p.resolve()).encode()).hexdigest()[:16] + ".lock"
        self.assertNotEqual(lock_name(self.skill_dir), lock_name(other_skill))
        run_loop.acquire_lock(self.skill_dir, self.lock_dir)
        run_loop.release_lock()
        run_loop.acquire_lock(other_skill, self.lock_dir)  # no raise
        run_loop.release_lock()


class RunMetadataTest(unittest.TestCase):
    def test_metadata_records_pid_host_args_and_git_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "results"
            results_dir.mkdir()
            args = run_loop.argparse.Namespace(
                eval_set="eval.json", skill_path="skills/demo", model="claude-sonnet-5-5",
                force=False,
            )
            run_loop.write_run_metadata(results_dir, args)
            meta = json.loads((results_dir / "run_metadata.json").read_text())
            self.assertEqual(meta["pid"], run_loop.os.getpid())
            self.assertEqual(meta["args"]["model"], "claude-sonnet-5-5")
            self.assertTrue(meta["hostname"])
            # This test runs inside the AIConfig git repo — head must resolve.
            self.assertRegex(meta["git_head"] or "", r"^[0-9a-f]{7,}$")


class MainRefusesDuplicateTest(unittest.TestCase):
    """main() must exit 2 before any API call when the lock is held."""

    def test_second_invocation_exits_2_without_running(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = make_skill_dir(root)
            eval_set = root / "eval-queries.json"
            eval_set.write_text(json.dumps([
                {"query": "demo query", "should_trigger": True},
            ]))
            # Hold the lock with a live PID (this test process).
            lock_path = run_loop.acquire_lock(skill_dir, run_loop.LOCK_DIR)
            try:
                # Real usage runs the module form from the skill-creator root.
                proc = subprocess.run(
                    [
                        sys.executable, "-m", "scripts.run_loop",
                        "--eval-set", str(eval_set),
                        "--skill-path", str(skill_dir),
                        "--model", "claude-sonnet-5-5",
                        "--report", "none",
                    ],
                    capture_output=True, text=True, timeout=30,
                    cwd=SCRIPT.parent.parent,
                )
                self.assertEqual(proc.returncode, 2, proc.stderr)
                self.assertIn("already tuning", proc.stderr)
                self.assertIn("demo-skill", proc.stderr)
                # Refusal message points at this holder's results dir.
                self.assertIn("--force", proc.stderr)
            finally:
                run_loop.release_lock()


if __name__ == "__main__":
    unittest.main()
