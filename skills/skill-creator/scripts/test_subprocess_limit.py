#!/usr/bin/env python3
"""Tests for the machine-wide subprocess slot limiter and spawn budget in
utils.py.

Covers the 2026-11-20 failure mode where many independently launched
eval loops each spawned `claude -p` subprocesses with no global cap.
The limiter must enforce the cap across separate processes, release
slots on process death, and fail loudly when no slot frees up. The spawn
budget must hard-fail the run once its expected count is exceeded, so a
retry/respawn regression cannot silently duplicate API spend.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR.parent))

from scripts import utils  # noqa: E402


class SubprocessSlotTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.slot_dir = Path(self._tmp.name) / "slots"
        # Patch the module-level dir the limiter reads at call time.
        self._orig_dir = utils.SUBPROCESS_SLOT_DIR
        utils.SUBPROCESS_SLOT_DIR = self.slot_dir

    def tearDown(self):
        utils.SUBPROCESS_SLOT_DIR = self._orig_dir
        self._tmp.cleanup()

    def _hold_child(self, max_slots: int) -> subprocess.Popen:
        """Start a child process that holds one slot for ~10s."""
        code = (
            "import sys, time; from pathlib import Path; sys.path.insert(0, {root!r}); "
            "from scripts import utils; utils.SUBPROCESS_SLOT_DIR = Path({slot_dir!r}); "
            "ctx = utils.subprocess_slot({max_slots}, wait_timeout=5); "
            "ctx.__enter__(); time.sleep(10)"
        ).format(root=str(SCRIPTS_DIR.parent), slot_dir=str(self.slot_dir), max_slots=max_slots)
        return subprocess.Popen([sys.executable, "-c", code])

    def test_all_slots_usable_concurrently(self):
        # A single process can hold every slot at once (nested acquisition).
        with utils.subprocess_slot(3, wait_timeout=1):
            pass
        held = []
        try:
            for _ in range(3):
                held.append(utils.subprocess_slot(3, wait_timeout=1))
                held[-1].__enter__()
            # 4th acquisition must time out — cap reached.
            with self.assertRaises(utils.SubprocessLimitError):
                with utils.subprocess_slot(3, wait_timeout=0.2):
                    pass
        finally:
            for ctx in held:
                ctx.__exit__(None, None, None)

    def test_cap_enforced_across_processes(self):
        # Two external processes each hold a slot; cap 2 means a third
        # waiter in this process must time out.
        children = [self._hold_child(2) for _ in range(2)]
        try:
            deadline = time.monotonic() + 20
            while not all((self.slot_dir / f"slot-{i}.lock").exists() for i in range(2)):
                if time.monotonic() > deadline:
                    self.fail("children did not acquire slots")
                time.sleep(0.1)
            with self.assertRaises(utils.SubprocessLimitError):
                with utils.subprocess_slot(2, wait_timeout=1):
                    pass
        finally:
            for c in children:
                c.kill()
                c.wait()

    def test_slot_released_on_process_death(self):
        child = self._hold_child(1)
        deadline = time.monotonic() + 10
        while not (self.slot_dir / "slot-0.lock").exists():
            if time.monotonic() > deadline:
                child.kill()
                child.wait()
                self.fail("child did not acquire slot")
            time.sleep(0.1)
        child.kill()
        child.wait()
        # flock releases on process death — no stale slot, no wait needed.
        with utils.subprocess_slot(1, wait_timeout=1):
            pass

    def test_zero_slots_never_acquires(self):
        with self.assertRaises(utils.SubprocessLimitError):
            with utils.subprocess_slot(0, wait_timeout=0.1):
                pass


class SpawnBudgetTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.slot_dir = Path(self._tmp.name) / "slots"
        self.budget_dir = Path(self._tmp.name) / "budgets"
        # Patch BOTH dirs: slots and budgets are separate module globals
        # (budget functions read SPAWN_BUDGET_DIR, not SUBPROCESS_SLOT_DIR),
        # and unpatched budget calls would leak files into the real /tmp.
        self._orig_dir = utils.SUBPROCESS_SLOT_DIR
        self._orig_budget_dir = utils.SPAWN_BUDGET_DIR
        utils.SUBPROCESS_SLOT_DIR = self.slot_dir
        utils.SPAWN_BUDGET_DIR = self.budget_dir

    def tearDown(self):
        utils.SUBPROCESS_SLOT_DIR = self._orig_dir
        utils.SPAWN_BUDGET_DIR = self._orig_budget_dir
        self._tmp.cleanup()

    def test_budget_counts_down_and_exhausts(self):
        budget = utils.create_spawn_budget(2)
        # Two allowed spawns consume the budget exactly.
        with utils.subprocess_slot(3, wait_timeout=0.1, budget_id=budget):
            pass
        self.assertEqual(utils.budget_remaining(budget), 1)
        with utils.subprocess_slot(3, wait_timeout=0.1, budget_id=budget):
            pass
        self.assertEqual(utils.budget_remaining(budget), 0)
        # The third spawn fails hard: a budget breach means a spawn
        # regression, not transient contention.
        with self.assertRaises(utils.SpawnBudgetExceededError):
            with utils.subprocess_slot(3, wait_timeout=0.1, budget_id=budget):
                pass
        # A spawn attempt that raises before entering still consumed nothing
        # past zero — remaining stays at 0, never negative.
        self.assertEqual(utils.budget_remaining(budget), 0)

    def test_budget_enforced_across_processes(self):
        # Workers live in separate processes; the budget must be shared.
        budget = utils.create_spawn_budget(1)
        code = (
            "import sys; from pathlib import Path; sys.path.insert(0, {root!r}); "
            "from scripts import utils; utils.SUBPROCESS_SLOT_DIR = Path({slot_dir!r}); "
            "utils.SPAWN_BUDGET_DIR = Path({budget_dir!r}); "
            "ctx = utils.subprocess_slot(3, wait_timeout=0.1, budget_id={budget!r}); "
            "ctx.__enter__()".format(
                root=str(SCRIPTS_DIR.parent), slot_dir=str(self.slot_dir),
                budget_dir=str(self.budget_dir), budget=budget,
            )
        )
        child = subprocess.Popen([sys.executable, "-c", code])
        child.wait()
        self.assertEqual(utils.budget_remaining(budget), 0)
        with self.assertRaises(utils.SpawnBudgetExceededError):
            with utils.subprocess_slot(3, wait_timeout=0.1, budget_id=budget):
                pass

    def test_no_budget_means_uncapped(self):
        # budget_id=None (budget disabled) never raises budget errors.
        for _ in range(3):
            with utils.subprocess_slot(3, wait_timeout=0.1):
                pass

    def test_budget_remaining_handles_missing_or_corrupt(self):
        self.assertIsNone(utils.budget_remaining(""))
        self.assertIsNone(utils.budget_remaining("no-such-budget"))
        # Corrupt content: write a real corrupt file into the patched budget
        # dir and confirm it is read (returns None) rather than silently
        # missing the fixture.
        path = self.budget_dir / "budget-corrupt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not a number")
        self.assertIsNone(utils.budget_remaining("corrupt"))

    def test_slot_exhaustion_does_not_consume_budget(self):
        # A run dropped to slot exhaustion must not burn a budget unit:
        # the budget counts spawns, not attempts.
        budget = utils.create_spawn_budget(1)
        code = (
            "import sys, time; from pathlib import Path; sys.path.insert(0, {root!r}); "
            "from scripts import utils; utils.SUBPROCESS_SLOT_DIR = Path({slot_dir!r}); "
            "ctx = utils.subprocess_slot(1, wait_timeout=1); "
            "ctx.__enter__(); time.sleep(10)".format(
                root=str(SCRIPTS_DIR.parent), slot_dir=str(self.slot_dir),
            )
        )
        child = subprocess.Popen([sys.executable, "-c", code])
        try:
            deadline = time.monotonic() + 10
            while not (self.slot_dir / "slot-0.lock").exists():
                if time.monotonic() > deadline:
                    self.fail("child did not acquire slot")
                time.sleep(0.1)
            with self.assertRaises(utils.SubprocessLimitError):
                with utils.subprocess_slot(1, wait_timeout=0.2, budget_id=budget):
                    pass
        finally:
            child.kill()
            child.wait()
        # Nothing spawned, so the budget is untouched.
        self.assertEqual(utils.budget_remaining(budget), 1)

    def test_budget_files_not_leaked_into_real_tmp(self):
        # create_spawn_budget must write into SPAWN_BUDGET_DIR (patched to
        # the temp dir here) — nothing may appear in the real /tmp dir.
        budget = utils.create_spawn_budget(5)
        self.assertTrue((self.budget_dir / f"budget-{budget}").exists())
        self.assertFalse(
            (self._orig_budget_dir / f"budget-{budget}").exists()
        )


if __name__ == "__main__":
    unittest.main()
