"""Shared utilities for skill-creator scripts."""

import fcntl
import os
import tempfile
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

# Machine-wide cap on concurrent `claude -p` subprocesses spawned by ALL
# skill-creator eval processes combined. Prevents the 2026-11-20 failure
# mode where ~140 independently launched loops each ran N workers.
SUBPROCESS_SLOT_DIR = Path(tempfile.gettempdir()) / "aiconfig-eval-slots"
DEFAULT_MAX_SUBPROCESSES = 10

# Default model for eval/improve `claude -p` subprocesses. Haiku keeps the
# per-run cost of trigger evals (queries x runs_per_query spawns) low; pass
# --model to measure trigger behavior on a different model. Keep in mind the
# description is tuned against whatever model the eval runs.
DEFAULT_EVAL_MODEL = "claude-haiku-5-5"


class SubprocessLimitError(RuntimeError):
    """No subprocess slot became free within the wait window."""


class SpawnBudgetExceededError(RuntimeError):
    """The eval spawned more subprocesses than its caller budgeted.

    Raised by subprocess_slot when the spawn budget is exhausted. This is a
    correctness tripwire, not backpressure: the expected spawn count is
    computed upfront (queries x runs + improvement calls), so hitting it
    means a retry/respawn regression is duplicating work. Fail hard and let
    the operator look at the run rather than silently continuing.
    """


# Per-eval spawn budgets, keyed by budget id. Workers live in a
# ProcessPoolExecutor, so the budget must be shared across processes:
# each budget is a file holding the remaining count under flock.
SPAWN_BUDGET_DIR = Path(tempfile.gettempdir()) / "aiconfig-eval-slots"


def _secure_dir(path: Path) -> None:
    """Restrict a lock/budget dir to this user (best-effort).

    The dirs live in shared /tmp with predictable names; 0700 keeps other
    local users from pre-holding flocks (DoS) or tampering with advisory
    content. If the dir pre-exists owned by another user, chmod fails and
    flock remains the only protection — the caller proceeds regardless.
    """
    try:
        os.chmod(path, 0o700)
    except OSError:
        pass


def _sweep_stale_budgets(budget_dir: Path, max_age_s: float = 86400.0) -> None:
    """Unlink budget files older than `max_age_s` (default: 1 day).

    Budget files are read post-hoc but never deleted by their run, so
    without a sweeper the dir grows unboundedly across runs. Any budget
    file older than a day belongs to a finished run.
    """
    now = time.time()
    for p in budget_dir.glob("budget-*"):
        try:
            if now - p.stat().st_mtime > max_age_s:
                p.unlink()
        except OSError:
            pass


def create_spawn_budget(total: int) -> str:
    """Create a fresh spawn budget of `total` subprocesses and return its id.

    Callers compute the expected count upfront (e.g. queries x runs_per_query
    plus improvement calls) and pass it here. The budget is advisory-free:
    every subprocess_slot call with this budget decrements it once, and the
    (total - remaining) difference after the run tells you what actually
    happened.
    """
    budget_id = uuid.uuid4().hex[:12]
    path = SPAWN_BUDGET_DIR / f"budget-{budget_id}"
    SPAWN_BUDGET_DIR.mkdir(parents=True, exist_ok=True)
    _secure_dir(SPAWN_BUDGET_DIR)
    _sweep_stale_budgets(SPAWN_BUDGET_DIR)
    with open(path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(str(total))
        f.flush()
    return budget_id


def budget_remaining(budget_id: str) -> int | None:
    """Return the remaining spawn budget, or None if unknown/unreadable."""
    if not budget_id:
        return None
    path = SPAWN_BUDGET_DIR / f"budget-{budget_id}"
    try:
        with open(path) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return None


def _consume_spawn_budget(budget_id: str | None) -> None:
    """Atomically decrement the budget or raise SpawnBudgetExceededError.

    A missing budget file (e.g. swept while a >1-day run was still going)
    trips the same hard fail as an exhausted budget: both mean the budget
    can no longer vouch for the spawn count, and a FileNotFoundError here
    would otherwise be swallowed by run_eval's generic handler and recorded
    as a trigger failure.
    """
    if not budget_id:
        return
    path = SPAWN_BUDGET_DIR / f"budget-{budget_id}"
    try:
        f = open(path, "r+")
    except FileNotFoundError:
        raise SpawnBudgetExceededError(
            f"Spawn budget file for {budget_id} is gone — it can no longer "
            f"vouch for the spawn count. Treat as a budget breach and "
            f"investigate before re-running."
        )
    with f:
        fcntl.flock(f, fcntl.LOCK_EX)
        raw = f.read().strip()
        try:
            remaining = int(raw)
        except ValueError:
            remaining = 0
        if remaining <= 0:
            raise SpawnBudgetExceededError(
                f"Spawn budget {budget_id} exhausted — the eval is spawning "
                f"more subprocesses than its expected count. This indicates "
                f"a retry/respawn regression, not transient contention; "
                f"investigate before re-running."
            )
        f.seek(0)
        f.write(str(remaining - 1))
        f.truncate()


@contextmanager
def subprocess_slot(
    max_slots: int = DEFAULT_MAX_SUBPROCESSES,
    wait_timeout: float = 60.0,
    budget_id: str | None = None,
):
    """Hold one of `max_slots` machine-wide slots around a subprocess spawn.

    Each slot is a lockfile held with flock for the duration of the context;
    the kernel releases it automatically when the holding process dies, so a
    killed loop cannot leak slots. All eval processes on the machine contend
    for the same slot files, making the cap global rather than per-process.

    Slot files are never unlinked: unlinking after release would let a waiter
    flock the orphaned inode while a fresh acquirer creates a new file at the
    same path, admitting two holders against one slot. flock on the persistent
    path is the sole arbiter, so the cap stays exact.

    When `budget_id` is set (create_spawn_budget), the cumulative spawn count
    is decremented only after a slot is acquired — a run dropped to slot
    exhaustion consumes nothing. Exceeding the budget raises
    SpawnBudgetExceededError (after releasing the slot) so a runaway spawner
    fails hard instead of duplicating API spend.
    """
    SUBPROCESS_SLOT_DIR.mkdir(parents=True, exist_ok=True)
    _secure_dir(SUBPROCESS_SLOT_DIR)
    slot_fd: int | None = None
    deadline = time.monotonic() + wait_timeout
    while time.monotonic() < deadline:
        for i in range(max_slots):
            path = SUBPROCESS_SLOT_DIR / f"slot-{i}.lock"
            fd = os.open(path, os.O_CREAT | os.O_RDWR)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                os.close(fd)
                continue
            slot_fd = fd
            break
        if slot_fd is not None:
            break
        time.sleep(0.5)
    if slot_fd is None:
        raise SubprocessLimitError(
            f"No free subprocess slot after {wait_timeout}s "
            f"(cap {max_slots}, held by other eval processes)"
        )
    # Consume the budget only now that a spawn will actually happen; release
    # the slot before raising so the budget tripwire never pins a slot.
    try:
        _consume_spawn_budget(budget_id)  # raises SpawnBudgetExceededError
    except SpawnBudgetExceededError:
        fcntl.flock(slot_fd, fcntl.LOCK_UN)
        os.close(slot_fd)
        raise
    try:
        yield
    finally:
        fcntl.flock(slot_fd, fcntl.LOCK_UN)
        os.close(slot_fd)


def parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            # Handle YAML multiline indicators (>, |, >-, |-)
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content
