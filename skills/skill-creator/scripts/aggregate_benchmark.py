#!/usr/bin/env python3
"""
Aggregate individual run results into benchmark summary statistics.

Reads grading.json files from run directories and produces:
- run_summary with mean, stddev, min, max for each metric
- delta between with_skill and without_skill configurations
- named pairwise comparisons over matched task/repeat pairs
- truthful metric availability (missing tokens are null, never chars)

Usage:
    python aggregate_benchmark.py <benchmark_dir>

Example:
    python aggregate_benchmark.py benchmarks/2026-01-15T10-30-00/

The script supports two directory layouts:

    Workspace layout (from skill-creator iterations):
    <benchmark_dir>/
    └── eval-N/
        ├── with_skill/
        │   ├── run-1/grading.json
        │   └── run-2/grading.json
        └── without_skill/
            ├── run-1/grading.json
            └── run-2/grading.json

    Legacy layout (with runs/ subdirectory):
    <benchmark_dir>/
    └── runs/
        └── eval-N/
            ├── with_skill/
            │   └── run-1/grading.json
            └── without_skill/
                └── run-1/grading.json
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def calculate_stats(values: list[float]) -> dict:
    """Calculate mean, stddev, min, max for a list of values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4)
    }


def load_run_results(benchmark_dir: Path) -> dict:
    """
    Load all run results from a benchmark directory.

    Returns dict keyed by config name (e.g. "with_skill"/"without_skill",
    or "new_skill"/"old_skill"), each containing a list of run results.
    """
    # Support both layouts: eval dirs directly under benchmark_dir, or under runs/
    runs_dir = benchmark_dir / "runs"
    if runs_dir.exists():
        search_dir = runs_dir
    elif list(benchmark_dir.glob("eval-*")):
        search_dir = benchmark_dir
    else:
        print(f"No eval directories found in {benchmark_dir} or {benchmark_dir / 'runs'}")
        return {}

    results: dict[str, list] = {}

    for eval_idx, eval_dir in enumerate(sorted(search_dir.glob("eval-*"))):
        metadata_path = eval_dir / "eval_metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path) as mf:
                    eval_id = json.load(mf).get("eval_id", eval_idx)
            except (json.JSONDecodeError, OSError):
                eval_id = eval_idx
        else:
            try:
                eval_id = int(eval_dir.name.split("-")[1])
            except ValueError:
                eval_id = eval_idx

        # Discover config directories dynamically rather than hardcoding names
        for config_dir in sorted(eval_dir.iterdir()):
            if not config_dir.is_dir():
                continue
            # Skip non-config directories (inputs, outputs, etc.)
            if not list(config_dir.glob("run-*")):
                continue
            config = config_dir.name
            if config not in results:
                results[config] = []

            for run_dir in sorted(config_dir.glob("run-*")):
                run_number = int(run_dir.name.split("-")[1])

                # run_status.json is the infrastructure-error signal:
                # errored/timeout runs are excluded from deltas (failed_runs)
                status_file = run_dir / "run_status.json"
                status = "completed"
                if status_file.exists():
                    try:
                        with open(status_file) as sf:
                            status = json.load(sf).get("status", "completed")
                    except (json.JSONDecodeError, OSError):
                        pass
                if status in ("errored", "timeout"):
                    results[config].append({
                        "eval_id": eval_id,
                        "run_number": run_number,
                        "failed_infra": True,
                        "status": status,
                    })
                    continue

                grading_file = run_dir / "grading.json"

                if not grading_file.exists():
                    print(f"Warning: grading.json not found in {run_dir}")
                    continue

                try:
                    with open(grading_file) as f:
                        grading = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON in {grading_file}: {e}")
                    continue

                # Extract metrics
                result = {
                    "eval_id": eval_id,
                    "run_number": run_number,
                    "pass_rate": grading.get("summary", {}).get("pass_rate", 0.0),
                    "passed": grading.get("summary", {}).get("passed", 0),
                    "failed": grading.get("summary", {}).get("failed", 0),
                    "total": grading.get("summary", {}).get("total", 0),
                }

                # Extract timing — grading.json first, then sibling timing.json
                timing = grading.get("timing", {})
                result["time_seconds"] = timing.get("total_duration_seconds")
                timing_file = run_dir / "timing.json"
                timing_data = {}
                if timing_file.exists():
                    try:
                        with open(timing_file) as tf:
                            timing_data = json.load(tf)
                    except json.JSONDecodeError:
                        pass
                if result["time_seconds"] is None:
                    result["time_seconds"] = timing_data.get("total_duration_seconds")
                # unmeasured stays None — never a zero substitute

                # Tokens are never substituted by output_chars: a missing
                # token count is null (unavailable), not a character count
                # or zero. Sources: timing.json (any layout), then
                # execution_metrics.total_tokens.
                tokens = timing_data.get("total_tokens")
                if tokens is None:
                    tokens = timing.get("total_tokens")
                metrics = grading.get("execution_metrics", {})
                if tokens is None:
                    tokens = metrics.get("total_tokens")
                result["tokens"] = tokens
                result["output_chars"] = metrics.get("output_chars")
                result["tool_calls"] = metrics.get("total_tool_calls", 0)
                result["errors"] = metrics.get("errors_encountered", 0)

                # Extract expectations — viewer requires fields: text, passed, evidence
                raw_expectations = grading.get("expectations", [])
                for exp in raw_expectations:
                    if "text" not in exp or "passed" not in exp:
                        print(f"Warning: expectation in {grading_file} missing required fields (text, passed, evidence): {exp}")
                result["expectations"] = raw_expectations

                # Extract notes from user_notes_summary
                notes_summary = grading.get("user_notes_summary", {})
                notes = []
                notes.extend(notes_summary.get("uncertainties", []))
                notes.extend(notes_summary.get("needs_review", []))
                notes.extend(notes_summary.get("workarounds", []))
                result["notes"] = notes

                results[config].append(result)

    return results


def aggregate_results(results: dict) -> tuple:
    """
    Aggregate run results into summary statistics.

    Returns (run_summary, comparisons, metric_availability, run_counts).
    - run_summary: per-configuration stats; a metric with zero measured
      samples has no stats object (never a null mean, never zero-filled).
    - comparisons: named pairwise comparisons over matched task/repeat
      pairs, with unmatched/duplicate/failed diagnostics.
    - metric_availability: measured/total counts per arm and metric.
    - run_counts: graded run count per arm.
    """
    run_summary = {}
    metric_availability = {}
    run_counts = {}

    for config in sorted(results.keys()):
        runs = results.get(config, [])
        graded = [r for r in runs if not r.get("failed_infra") and "pass_rate" in r]
        run_counts[config] = len(graded)
        if not graded:
            # no stats object at all — never a zero-filled placeholder;
            # run_counts/metric_availability disclose the zero state
            run_summary[config] = {}
            metric_availability[config] = {
                "tokens": {"measured": 0, "total": 0},
                "time_seconds": {"measured": 0, "total": 0},
            }
            continue

        pass_rates = [r["pass_rate"] for r in graded]
        config_stats = {"pass_rate": calculate_stats(pass_rates)}

        times = [r["time_seconds"] for r in graded
                 if r.get("time_seconds") is not None]
        tokens = [r["tokens"] for r in graded if r.get("tokens") is not None]

        if times:
            config_stats["time_seconds"] = calculate_stats(times)
        if tokens:
            config_stats["tokens"] = calculate_stats(tokens)

        run_summary[config] = config_stats
        metric_availability[config] = {
            "tokens": {"measured": len(tokens), "total": len(graded)},
            "time_seconds": {"measured": len(times), "total": len(graded)},
        }

    comparisons = {}
    configs = sorted(results.keys())
    if len(configs) >= 2:
        for i, a in enumerate(configs):
            for b in configs[i + 1:]:
                comparisons[f"{a}_vs_{b}"] = pairwise_comparison(a, b, results)

    return run_summary, comparisons, metric_availability, run_counts


def pairwise_comparison(config_a: str, config_b: str, results: dict) -> dict:
    """Compare two arms over matched (eval_id, run_number) pairs only."""
    def graded_index(config):
        idx = {}
        for r in results.get(config, []):
            if r.get("failed_infra") or "pass_rate" not in r:
                continue
            key = (r["eval_id"], r["run_number"])
            idx.setdefault(key, []).append(r)
        return idx

    idx_a = graded_index(config_a)
    idx_b = graded_index(config_b)
    # eval_id may be int or string depending on metadata; compare as strings
    all_keys = sorted(set(idx_a) | set(idx_b),
                       key=lambda k: (str(k[0]), k[1]))

    matched = 0
    unmatched = []
    duplicates = []
    failed_runs = []
    delta_pass = []
    delta_time = []
    delta_tokens = []

    for key in all_keys:
        ra = idx_a.get(key)
        rb = idx_b.get(key)
        for config, runs in ((config_a, ra), (config_b, rb)):
            if runs and len(runs) > 1:
                duplicates.append({"eval_id": key[0], "run_number": key[1],
                                    "configuration": config,
                                    "count": len(runs)})
        if ra is None or rb is None:
            unmatched.append({"eval_id": key[0], "run_number": key[1],
                              "missing_from": config_b if ra is not None else config_a})
            continue
        # duplicates are excluded from paired deltas
        if len(ra) > 1 or len(rb) > 1:
            continue
        a, b = ra[0], rb[0]
        matched += 1
        delta_pass.append(a["pass_rate"] - b["pass_rate"])
        if a.get("time_seconds") is not None and b.get("time_seconds") is not None:
            delta_time.append(a["time_seconds"] - b["time_seconds"])
        if a.get("tokens") is not None and b.get("tokens") is not None:
            delta_tokens.append(a["tokens"] - b["tokens"])

    # infrastructure-failed runs
    for config in (config_a, config_b):
        for r in results.get(config, []):
            if r.get("failed_infra"):
                failed_runs.append({"eval_id": r["eval_id"],
                                    "run_number": r["run_number"],
                                    "configuration": config,
                                    "status": r.get("status")})

    def fmt(values, fmt_str):
        if not values:
            return None
        return fmt_str.format(sum(values) / len(values))

    comparison = {
        "primary": config_a,
        "baseline": config_b,
        "matched_pairs": matched,
        "unmatched": unmatched,
        "duplicates": duplicates,
        "failed_runs": failed_runs,
        "delta_pass_rate": fmt(delta_pass, "{:+.2f}"),
        "delta_time_seconds": fmt(delta_time, "{:+.1f}"),
        "delta_tokens": fmt(delta_tokens, "{:+.0f}"),
    }
    return {k: v for k, v in comparison.items() if v is not None}


def calculate_delta(run_summary: dict, primary: str, baseline: str) -> dict:
    """Legacy delta: primary minus baseline. A metric either selected arm
    lacks is omitted entirely (consumers render it as unavailable)."""
    delta = {}
    p = run_summary.get(primary, {})
    b = run_summary.get(baseline, {})
    if "pass_rate" in p and "pass_rate" in b:
        delta["pass_rate"] = f"{p['pass_rate']['mean'] - b['pass_rate']['mean']:+.2f}"
    if "time_seconds" in p and "time_seconds" in b:
        delta["time_seconds"] = f"{p['time_seconds']['mean'] - b['time_seconds']['mean']:+.1f}"
    if "tokens" in p and "tokens" in b:
        delta["tokens"] = f"{p['tokens']['mean'] - b['tokens']['mean']:+.0f}"
    return delta


def generate_benchmark(benchmark_dir: Path, skill_name: str = "",
                        skill_path: str = "",
                        primary: str = None, baseline: str = None,
                        executor_model: str = None) -> dict:
    """
    Generate complete benchmark.json from run results.

    With primary/baseline selected, run_summary is ordered primary first,
    then baseline, then remaining arms, and the legacy delta equals
    primary minus baseline. Without a selection and with more than two
    arms, raises ValueError naming the arms.
    """
    results = load_run_results(benchmark_dir)
    run_summary, comparisons, metric_availability, run_counts = aggregate_results(results)

    configs = [k for k in run_summary if k != "delta"]
    if primary is not None or baseline is not None:
        for arm in (primary, baseline):
            if arm is not None and arm not in run_summary:
                raise ValueError(f"Selected arm not found: {arm} (found: {', '.join(sorted(run_summary))})")
    elif len(configs) > 2:
        raise ValueError(
            f"Multiple arms discovered ({', '.join(sorted(configs))}) with no "
            "--primary/--baseline selection; ambiguity is not allowed")

    for config in configs:
        if run_counts.get(config, 0) == 0:
            raise ValueError(f"Arm '{config}' has zero graded runs; iteration is incomplete")

    # Order arms: primary first, then baseline, then the rest (sorted)
    if primary is not None:
        ordered = [primary]
        if baseline is not None:
            ordered.append(baseline)
        ordered += [c for c in sorted(configs) if c not in ordered]
        run_summary = {c: run_summary[c] for c in ordered}
    elif baseline is not None:
        ordered = [baseline] + [c for c in sorted(configs) if c != baseline]
        run_summary = {c: run_summary[c] for c in ordered}

    if len(configs) >= 2:
        if primary is not None:
            p, b = primary, baseline
        else:
            # No explicit roles: infer them by conventional config names so the
            # delta keeps the documented "primary minus baseline" sign.
            # Candidate/new arms win primary; baseline/without arms are baseline.
            primary_names = ("with_skill", "new_skill", "candidate", "improved")
            baseline_names = ("without_skill", "old_skill", "baseline", "original")
            p = next((c for c in configs if c in primary_names), None)
            b = next((c for c in configs if c in baseline_names), None)
            if p is None or b is None:
                # Unrecognized names: fall back to sorted order (first minus
                # second) — callers comparing versions must pass --primary/--baseline.
                p, b = configs[0], configs[1]
        run_summary["delta"] = calculate_delta(run_summary, p, b)

    # Build runs array for benchmark.json (graded runs only; infra-failed
    # runs appear in comparisons.failed_runs instead)
    runs = []
    for config in results:
        for result in results[config]:
            if result.get("failed_infra"):
                continue
            runs.append({
                "eval_id": result["eval_id"],
                "configuration": config,
                "run_number": result["run_number"],
                "result": {
                    "pass_rate": result["pass_rate"],
                    "passed": result["passed"],
                    "failed": result["failed"],
                    "total": result["total"],
                    "time_seconds": result["time_seconds"],
                    "tokens": result.get("tokens"),
                    "output_chars": result.get("output_chars"),
                    "tool_calls": result.get("tool_calls", 0),
                    "errors": result.get("errors", 0)
                },
                "expectations": result["expectations"],
                "notes": result["notes"]
            })

    # Determine eval IDs from results
    eval_ids = sorted(set(
        r["eval_id"]
        for config in results.values()
        for r in config
    ))

    benchmark = {
        "metadata": {
            "skill_name": skill_name or "<skill-name>",
            "skill_path": skill_path or "<path/to/skill>",
            "executor_model": executor_model or "unavailable",
            "analyzer_model": "<model-name>",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evals_run": eval_ids,
            "runs_per_configuration": min(run_counts.values()) if run_counts else 0
        },
        "runs": runs,
        "run_summary": run_summary,
        "comparisons": comparisons,
        "metric_availability": metric_availability,
        "run_counts": run_counts,
        "notes": []  # To be filled by analyzer
    }

    return benchmark


def generate_markdown(benchmark: dict) -> str:
    """Generate human-readable benchmark.md from benchmark data."""
    metadata = benchmark["metadata"]
    run_summary = benchmark["run_summary"]

    # Determine config names (excluding "delta")
    configs = [k for k in run_summary if k != "delta"]
    config_a = configs[0] if len(configs) >= 1 else "config_a"
    config_b = configs[1] if len(configs) >= 2 else "config_b"
    label_a = config_a.replace("_", " ").title()
    label_b = config_b.replace("_", " ").title()

    lines = [
        f"# Skill Benchmark: {metadata['skill_name']}",
        "",
        f"**Model**: {metadata['executor_model']}",
        f"**Date**: {metadata['timestamp']}",
        f"**Evals**: {', '.join(map(str, metadata['evals_run']))} ({metadata['runs_per_configuration']} runs each per configuration)",
        "",
        "## Summary",
        "",
        f"| Metric | {label_a} | {label_b} | Delta |",
        "|--------|------------|---------------|-------|",
    ]

    a_summary = run_summary.get(config_a, {})
    b_summary = run_summary.get(config_b, {})
    delta = run_summary.get("delta", {})

    # A missing stats object is unavailable: render "—", never "0 ± 0".
    def stat_cell(stats: dict, suffix: str, pct: bool) -> str:
        if not stats or "mean" not in stats:
            return "—"
        if pct:
            return f"{stats['mean']*100:.0f}% ± {stats['stddev']*100:.0f}%"
        return f"{stats['mean']:.1f}{suffix} ± {stats['stddev']:.1f}{suffix}"

    lines.append(f"| Pass Rate | {stat_cell(a_summary.get('pass_rate'), '', True)} | {stat_cell(b_summary.get('pass_rate'), '', True)} | {delta.get('pass_rate', '—')} |")
    lines.append(f"| Time | {stat_cell(a_summary.get('time_seconds'), 's', False)} | {stat_cell(b_summary.get('time_seconds'), 's', False)} | {delta.get('time_seconds', '—')} |")
    lines.append(f"| Tokens | {stat_cell(a_summary.get('tokens'), '', False)} | {stat_cell(b_summary.get('tokens'), '', False)} | {delta.get('tokens', '—')} |")

    # Notes section
    if benchmark.get("notes"):
        lines.extend([
            "",
            "## Notes",
            ""
        ])
        for note in benchmark["notes"]:
            lines.append(f"- {note}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate benchmark run results into summary statistics"
    )
    parser.add_argument(
        "benchmark_dir",
        type=Path,
        help="Path to the benchmark directory"
    )
    parser.add_argument(
        "--skill-name",
        default="",
        help="Name of the skill being benchmarked"
    )
    parser.add_argument(
        "--skill-path",
        default="",
        help="Path to the skill being benchmarked"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output path for benchmark.json (default: <benchmark_dir>/benchmark.json)"
    )
    parser.add_argument(
        "--primary",
        default=None,
        help="Primary arm for delta and run_summary ordering (e.g. candidate)"
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Baseline arm for delta and run_summary ordering (e.g. current)"
    )
    parser.add_argument(
        "--executor-model",
        default=None,
        help="Executor model id recorded in metadata (default: unavailable)"
    )

    args = parser.parse_args()

    if (args.primary is None) != (args.baseline is None):
        print("Error: --primary and --baseline must be given together")
        sys.exit(1)

    if not args.benchmark_dir.exists():
        print(f"Directory not found: {args.benchmark_dir}")
        sys.exit(1)

    # Generate benchmark
    try:
        benchmark = generate_benchmark(
            args.benchmark_dir, args.skill_name, args.skill_path,
            primary=args.primary, baseline=args.baseline,
            executor_model=args.executor_model,
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine output paths
    output_json = args.output or (args.benchmark_dir / "benchmark.json")
    output_md = output_json.with_suffix(".md")

    # Write benchmark.json
    with open(output_json, "w") as f:
        json.dump(benchmark, f, indent=2)
    print(f"Generated: {output_json}")

    # Write benchmark.md
    markdown = generate_markdown(benchmark)
    with open(output_md, "w") as f:
        f.write(markdown)
    print(f"Generated: {output_md}")

    # Print summary
    run_summary = benchmark["run_summary"]
    configs = [k for k in run_summary if k != "delta"]
    delta = run_summary.get("delta", {})

    print(f"\nSummary:")
    for config in configs:
        pr_stats = run_summary[config].get("pass_rate", {})
        label = config.replace("_", " ").title()
        if "mean" in pr_stats:
            print(f"  {label}: {pr_stats['mean']*100:.1f}% pass rate")
        else:
            print(f"  {label}: — pass rate (no graded runs)")
    print(f"  Delta:         {delta.get('pass_rate', '—')}")


if __name__ == "__main__":
    main()
