#!/usr/bin/env python3
"""Compare benchmark JSON metrics and fail on regressions.

Supports Google Benchmark JSON (benchmarks array with name and metrics) and simple
JSON objects shaped as {"benchmarks": [{"name": ..., "real_time": ...}]}.
Lower metric values are treated as better by default.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple


def load_benchmarks(path: Path, metric: str) -> Dict[str, float]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"failed to read {path}: {exc}") from exc

    if isinstance(data, dict) and isinstance(data.get("benchmarks"), list):
        rows = data["benchmarks"]
    elif isinstance(data, list):
        rows = data
    else:
        raise SystemExit(f"{path} must contain a benchmarks array or be an array of rows")

    result: Dict[str, float] = {}
    rows_seen = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        rows_seen += 1
        name = row.get("name") or row.get("run_name") or row.get("benchmark")
        value = row.get(metric)
        if name is None or value is None:
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(numeric):
            continue
        name_str = str(name)
        if name_str in result:
            print(
                f"warning: duplicate benchmark name '{name_str}' in {path}; using last value",
                file=sys.stderr,
            )
        # Google Benchmark may include aggregate rows. Keep explicit rows as-is so
        # callers can compare either aggregate-only output or raw repetitions.
        result[name_str] = numeric

    if rows_seen and not result:
        raise SystemExit(f"no values for metric '{metric}' in {path}")

    return result


def compare(
    baseline: Dict[str, float],
    current: Dict[str, float],
    threshold_pct: float,
    higher_is_better: bool,
) -> Tuple[int, Iterable[str]]:
    lines = []
    failures = 0
    names = sorted(set(baseline) & set(current))
    missing_current = sorted(set(baseline) - set(current))
    new_current = sorted(set(current) - set(baseline))

    if not names:
        return 2, ["no overlapping benchmark names found"]

    for name in names:
        old = baseline[name]
        new = current[name]
        if old == 0:
            delta_pct = 0.0 if new == 0 else math.inf
        else:
            delta_pct = ((new - old) / abs(old)) * 100.0
        improvement_pct = delta_pct if higher_is_better else -delta_pct
        regressed = improvement_pct < -threshold_pct
        status = "REGRESSION" if regressed else "ok"
        if regressed:
            failures += 1
        lines.append(
            f"{status:10s} {name}: baseline={old:.6g} current={new:.6g} "
            f"delta={delta_pct:+.2f}%"
        )

    if missing_current:
        failures += len(missing_current)
        lines.append("missing benchmarks in current: " + ", ".join(missing_current))
    if new_current:
        lines.append("new benchmarks in current: " + ", ".join(new_current))

    return (1 if failures else 0), lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_pos", nargs="?", type=Path, help="baseline JSON (positional shorthand)")
    parser.add_argument("current_pos", nargs="?", type=Path, help="current JSON (positional shorthand)")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--current", type=Path)
    parser.add_argument("--metric", default="real_time")
    parser.add_argument("--regression-threshold", type=float, default=5.0)
    parser.add_argument("--higher-is-better", action="store_true")
    args = parser.parse_args()

    baseline_path = args.baseline or args.baseline_pos
    current_path = args.current or args.current_pos
    if baseline_path is None or current_path is None:
        parser.error("provide baseline and current JSON paths, either positionally or with --baseline/--current")

    baseline = load_benchmarks(baseline_path, args.metric)
    current = load_benchmarks(current_path, args.metric)
    code, lines = compare(baseline, current, args.regression_threshold, args.higher_is_better)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
