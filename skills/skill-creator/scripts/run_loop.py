#!/usr/bin/env python3
"""Run the eval + improve loop until all pass or max iterations reached.

Combines run_eval.py and improve_description.py in a loop, tracking history
and returning the best description found. Supports train/test split to prevent
overfitting.
"""

import argparse
import fcntl
import hashlib
import json
import os
import random
import signal
import socket
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

from scripts.generate_report import generate_html
from scripts.improve_description import improve_description
from scripts.run_eval import find_project_root, run_eval
from scripts.utils import _secure_dir, create_spawn_budget, DEFAULT_EVAL_MODEL, parse_skill_md

# Per-skill lock so concurrent loops tuning the same skill fail fast instead
# of duplicating API spend. Local /tmp only — no cross-machine protection.
LOCK_DIR = Path(tempfile.gettempdir()) / "aiconfig-run-loop"

# fd and content of the per-skill lock held by this process. acquire_lock
# sets them; release_lock (or process exit) closes the fd, releasing the flock.
_held_lock_fd: int | None = None
_held_lock_info: dict | None = None


class LoopLockError(Exception):
    """Another live run_loop instance holds the lock for this skill."""


def acquire_lock(skill_path: Path, lock_dir: Path = LOCK_DIR) -> Path:
    """Take the per-skill lock, or raise LoopLockError if a live holder exists.

    flock(LOCK_EX|LOCK_NB) on the lock file is the race-safe arbiter: two
    processes starting simultaneously cannot both win it, and the kernel
    releases it when the holder dies, so a killed loop leaves no stale lock.
    The file's JSON content (pid, started, results_dir) is advisory —
    written best-effort for the refusal message and post-hoc forensics.
    """
    lock_dir.mkdir(parents=True, exist_ok=True)
    _secure_dir(lock_dir)
    lock_path = lock_dir / (hashlib.sha256(str(skill_path.resolve()).encode()).hexdigest()[:16] + ".lock")
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        # flock held means a live holder (the kernel releases it on death,
        # so there is no stale-lock case). The JSON content is advisory.
        os.close(fd)
        try:
            holder = json.loads(lock_path.read_text())
        except (json.JSONDecodeError, OSError):
            holder = None
        pid_desc = str(holder.get("pid")) if holder else "unknown"
        started = (holder.get("started") or "unknown") if holder else "unknown"
        results = (holder.get("results_dir") or "unknown") if holder else "unknown"
        raise LoopLockError(
            f"run_loop is already tuning {skill_path} "
            f"(PID {pid_desc or 'unknown'}, started {started}, "
            f"results in {results}). "
            f"Re-run with --force to override."
        )
    info = {
        "pid": os.getpid(),
        "skill_path": str(skill_path.resolve()),
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results_dir": None,  # filled in by main() once the results dir exists
    }
    _write_lock_info(fd, info)
    global _held_lock_fd, _held_lock_info
    # Keep fd open until release — closing it releases the flock.
    _held_lock_fd = fd
    _held_lock_info = info
    return lock_path


def _write_lock_info(fd: int, info: dict) -> None:
    """Rewrite the advisory JSON through the flocked fd (same inode, no
    tmp+replace — replacing the file would swap the inode out from under
    the held flock and re-introduce the orphaned-inode over-admission race)."""
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, json.dumps(info).encode())


def update_held_lock_results_dir(results_dir: Path | None) -> None:
    """Record the results dir in the held lock so duplicates can point at it.

    Operates on the module-global held lock (acquire_lock's single slot);
    there is no path parameter because the lock is process state, not a
    path-scoped resource.
    """
    if _held_lock_fd is None or _held_lock_info is None:
        return
    _held_lock_info["results_dir"] = str(results_dir) if results_dir else None
    try:
        _write_lock_info(_held_lock_fd, _held_lock_info)
    except OSError:
        pass  # best-effort annotation; lock is already held via flock


def release_lock() -> None:
    """Release the held per-skill lock (close the fd, dropping the flock).

    Never unlinks the lock file: unlinking lets a racing acquirer flock the
    orphaned inode while another creates a fresh file at the same path (same
    over-admission race the subprocess-slot limiter avoids by never
    unlinking its slot files). No path parameter — same reason as
    update_held_lock_results_dir.
    """
    global _held_lock_fd, _held_lock_info
    if _held_lock_fd is not None:
        try:
            os.close(_held_lock_fd)
        except OSError:
            pass
        _held_lock_fd = None
        _held_lock_info = None


def write_run_metadata(results_dir: Path, args: argparse.Namespace) -> None:
    """Persist run identity (PID, host, git head, flags) for post-hoc forensics."""
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        head = None
    metadata = {
        "pid": os.getpid(),
        "hostname": socket.gethostname(),
        "git_head": head,
        "args": {k: v for k, v in vars(args).items()},
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (results_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2))


def split_eval_set(eval_set: list[dict], holdout: float, seed: int = 42) -> tuple[list[dict], list[dict]]:
    """Split eval set into train and test sets, stratified by should_trigger."""
    random.seed(seed)

    # Separate by should_trigger
    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]

    # Shuffle each group
    random.shuffle(trigger)
    random.shuffle(no_trigger)

    # Calculate split points
    n_trigger_test = max(1, int(len(trigger) * holdout))
    n_no_trigger_test = max(1, int(len(no_trigger) * holdout))

    # Split
    test_set = trigger[:n_trigger_test] + no_trigger[:n_no_trigger_test]
    train_set = trigger[n_trigger_test:] + no_trigger[n_no_trigger_test:]

    return train_set, test_set


def run_loop(
    eval_set: list[dict],
    skill_path: Path,
    description_override: str | None,
    num_workers: int,
    timeout: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    holdout: float,
    model: str,
    verbose: bool,
    live_report_path: Path | None = None,
    log_dir: Path | None = None,
) -> dict:
    """Run the eval + improvement loop."""
    project_root = find_project_root()
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description

    # Split into train/test if holdout > 0
    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
        if verbose:
            print(f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})", file=sys.stderr)
    else:
        train_set = eval_set
        test_set = []

    history = []
    exit_reason = "unknown"

    # Loop-wide spawn budget: the expected total across all iterations.
    # Each iteration evaluates len(all_queries) x runs_per_query, and every
    # iteration except a last passing one runs improve_description (up to 2
    # spawns each: improvement + optional over-limit rewrite). Budgeting the
    # worst case means a normal run never notices it, but a retry/respawn
    # regression trips SpawnBudgetExceededError instead of silently
    # duplicating API spend.
    expected_eval_spawns = len(train_set + test_set) * runs_per_query * max_iterations
    expected_improve_spawns = 2 * max(0, max_iterations - 1)
    spawn_budget_id = create_spawn_budget(expected_eval_spawns + expected_improve_spawns)

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}", file=sys.stderr)
            print(f"Description: {current_description}", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)

        # Evaluate train + test together in one batch for parallelism
        all_queries = train_set + test_set
        t0 = time.time()
        all_results = run_eval(
            eval_set=all_queries,
            skill_name=name,
            description=current_description,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            model=model,
            spawn_budget_id=spawn_budget_id,
        )
        eval_elapsed = time.time() - t0

        # Split results back into train/test by matching queries
        train_queries_set = {q["query"] for q in train_set}
        train_result_list = [r for r in all_results["results"] if r["query"] in train_queries_set]
        test_result_list = [r for r in all_results["results"] if r["query"] not in train_queries_set]

        train_passed = sum(1 for r in train_result_list if r["pass"])
        train_total = len(train_result_list)
        train_summary = {"passed": train_passed, "failed": train_total - train_passed, "total": train_total}
        train_results = {"results": train_result_list, "summary": train_summary}

        if test_set:
            test_passed = sum(1 for r in test_result_list if r["pass"])
            test_total = len(test_result_list)
            test_summary = {"passed": test_passed, "failed": test_total - test_passed, "total": test_total}
            test_results = {"results": test_result_list, "summary": test_summary}
        else:
            test_results = None
            test_summary = None

        history.append({
            "iteration": iteration,
            "description": current_description,
            "train_passed": train_summary["passed"],
            "train_failed": train_summary["failed"],
            "train_total": train_summary["total"],
            "train_results": train_results["results"],
            "test_passed": test_summary["passed"] if test_summary else None,
            "test_failed": test_summary["failed"] if test_summary else None,
            "test_total": test_summary["total"] if test_summary else None,
            "test_results": test_results["results"] if test_results else None,
            # Queries dropped to slot exhaustion this iteration — carried
            # into results.json/history so a shrunken total is explainable.
            "dropped": all_results["summary"].get("dropped", []),
            # For backward compat with report generator
            "passed": train_summary["passed"],
            "failed": train_summary["failed"],
            "total": train_summary["total"],
            "results": train_results["results"],
        })

        # Write live report if path provided
        if live_report_path:
            partial_output = {
                "original_description": original_description,
                "best_description": current_description,
                "best_score": "in progress",
                "iterations_run": len(history),
                "holdout": holdout,
                "train_size": len(train_set),
                "test_size": len(test_set),
                "history": history,
            }
            live_report_path.write_text(generate_html(partial_output, auto_refresh=True, skill_name=name))

        if verbose:
            def print_eval_stats(label, results, elapsed):
                pos = [r for r in results if r["should_trigger"]]
                neg = [r for r in results if not r["should_trigger"]]
                tp = sum(r["triggers"] for r in pos)
                pos_runs = sum(r["runs"] for r in pos)
                fn = pos_runs - tp
                fp = sum(r["triggers"] for r in neg)
                neg_runs = sum(r["runs"] for r in neg)
                tn = neg_runs - fp
                total = tp + tn + fp + fn
                precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
                accuracy = (tp + tn) / total if total > 0 else 0.0
                print(f"{label}: {tp+tn}/{total} correct, precision={precision:.0%} recall={recall:.0%} accuracy={accuracy:.0%} ({elapsed:.1f}s)", file=sys.stderr)
                for r in results:
                    status = "PASS" if r["pass"] else "FAIL"
                    rate_str = f"{r['triggers']}/{r['runs']}"
                    print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:60]}", file=sys.stderr)

            print_eval_stats("Train", train_results["results"], eval_elapsed)
            if test_summary:
                print_eval_stats("Test ", test_results["results"], 0)

        if train_summary["failed"] == 0:
            exit_reason = f"all_passed (iteration {iteration})"
            if verbose:
                print(f"\nAll train queries passed on iteration {iteration}!", file=sys.stderr)
            break

        if iteration == max_iterations:
            exit_reason = f"max_iterations ({max_iterations})"
            if verbose:
                print(f"\nMax iterations reached ({max_iterations}).", file=sys.stderr)
            break

        # Improve the description based on train results
        if verbose:
            print(f"\nImproving description...", file=sys.stderr)

        t0 = time.time()
        # Strip test scores from history so improvement model can't see them
        blinded_history = [
            {k: v for k, v in h.items() if not k.startswith("test_")}
            for h in history
        ]
        new_description = improve_description(
            skill_name=name,
            skill_content=content,
            current_description=current_description,
            eval_results=train_results,
            history=blinded_history,
            model=model,
            log_dir=log_dir,
            iteration=iteration,
            budget_id=spawn_budget_id,
        )
        improve_elapsed = time.time() - t0

        if verbose:
            print(f"Proposed ({improve_elapsed:.1f}s): {new_description}", file=sys.stderr)

        current_description = new_description

    # Find the best iteration by TEST score (or train if no test set)
    if test_set:
        best = max(history, key=lambda h: h["test_passed"] or 0)
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best = max(history, key=lambda h: h["train_passed"])
        best_score = f"{best['train_passed']}/{best['train_total']}"

    if verbose:
        print(f"\nExit reason: {exit_reason}", file=sys.stderr)
        print(f"Best score: {best_score} (iteration {best['iteration']})", file=sys.stderr)

    return {
        "exit_reason": exit_reason,
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": f"{best['test_passed']}/{best['test_total']}" if test_set else None,
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "history": history,
    }


def main():
    parser = argparse.ArgumentParser(description="Run eval + improve loop")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--holdout", type=float, default=0.4, help="Fraction of eval set to hold out for testing (0 to disable)")
    parser.add_argument("--model", default=DEFAULT_EVAL_MODEL, help="Model for eval queries and description improvement (default: %(default)s — cheap evals; description is tuned against whatever model the eval runs)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    parser.add_argument("--report", default="auto", help="Generate HTML report at this path (default: 'auto' for temp file, 'none' to disable)")
    parser.add_argument("--results-dir", default=None, help="Save all outputs (results.json, report.html, log.txt) to a timestamped subdirectory here")
    parser.add_argument("--force", action="store_true", help="Start even if another run_loop holds this skill's lock")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    if not args.force:
        try:
            lock_path = acquire_lock(skill_path)
        except LoopLockError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(2)
        # Release on SIGTERM so a killed loop doesn't leave a stale lock, and
        # on normal/abnormal exit. --force skips the lock entirely.
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(2))
        try:
            _run_locked(args, eval_set, skill_path, lock_path)
        finally:
            release_lock()
    else:
        _run_locked(args, eval_set, skill_path, None)


def _run_locked(
    args: argparse.Namespace,
    eval_set: list[dict],
    skill_path: Path,
    lock_path: Path | None,
) -> None:
    name, _, _ = parse_skill_md(skill_path)

    # Set up live report path
    if args.report != "none":
        if args.report == "auto":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            live_report_path = Path(tempfile.gettempdir()) / f"skill_description_report_{skill_path.name}_{timestamp}.html"
        else:
            live_report_path = Path(args.report)
        # Open the report immediately so the user can watch
        live_report_path.write_text("<html><body><h1>Starting optimization loop...</h1><meta http-equiv='refresh' content='5'></body></html>")
        webbrowser.open(str(live_report_path))
    else:
        live_report_path = None

    # Determine output directory (create before run_loop so logs can be written)
    if args.results_dir:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path(args.results_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)
    else:
        results_dir = None

    log_dir = results_dir / "logs" if results_dir else None

    if results_dir:
        write_run_metadata(results_dir, args)
    if lock_path:
        update_held_lock_results_dir(results_dir)

    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        holdout=args.holdout,
        model=args.model,
        verbose=args.verbose,
        live_report_path=live_report_path,
        log_dir=log_dir,
    )

    # Save JSON output
    json_output = json.dumps(output, indent=2)
    print(json_output)
    if results_dir:
        (results_dir / "results.json").write_text(json_output)

    # Write final HTML report (without auto-refresh)
    if live_report_path:
        live_report_path.write_text(generate_html(output, auto_refresh=False, skill_name=name))
        print(f"\nReport: {live_report_path}", file=sys.stderr)

    if results_dir and live_report_path:
        (results_dir / "report.html").write_text(generate_html(output, auto_refresh=False, skill_name=name))

    if results_dir:
        print(f"Results saved to: {results_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
