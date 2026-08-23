#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run-perf-stat.sh <binary-or-command> [args...]

Environment:
  PERF_REPEAT   Number of repetitions (default: 5)
  PERF_EVENTS   Comma-separated events (default: cycles,instructions,branches,branch-misses,cache-references,cache-misses,context-switches,cpu-migrations,page-faults)
  CPUSET        Optional CPU list for taskset, e.g. 2 or 2-5
  NUMA_NODE     Optional NUMA node for numactl --cpunodebind/--membind
EOF
}

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

if ! command -v perf >/dev/null 2>&1; then
  echo "error: perf not found" >&2
  exit 127
fi

repeat="${PERF_REPEAT:-5}"
events="${PERF_EVENTS:-cycles,instructions,branches,branch-misses,cache-references,cache-misses,context-switches,cpu-migrations,page-faults}"
cmd=("$@")

if [ -n "${CPUSET:-}" ]; then
  if command -v taskset >/dev/null 2>&1; then
    cmd=(taskset -c "$CPUSET" "${cmd[@]}")
  else
    echo "warning: CPUSET requested but taskset not found" >&2
  fi
fi

if [ -n "${NUMA_NODE:-}" ]; then
  if command -v numactl >/dev/null 2>&1; then
    cmd=(numactl --cpunodebind="$NUMA_NODE" --membind="$NUMA_NODE" "${cmd[@]}")
  else
    echo "warning: NUMA_NODE requested but numactl not found" >&2
  fi
fi

set -x
perf stat -r "$repeat" -e "$events" -- "${cmd[@]}"
