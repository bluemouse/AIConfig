#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run-google-benchmark.sh <bench-binary> [extra benchmark args...]

Environment:
  BENCH_REPS    Repetitions (default: 10)
  BENCH_WARMUP  Minimum warmup time seconds (default: 0.5)
  BENCH_FILTER  Optional benchmark filter
  BENCH_OUT     Output JSON path (default: benchmark-YYYYmmdd-HHMMSS.json)
  CPUSET        Optional CPU list for taskset
EOF
}

if [ "$#" -lt 1 ]; then
  usage
  exit 2
fi

bench="$1"
shift
if [ ! -x "$bench" ]; then
  echo "error: benchmark binary is not executable: $bench" >&2
  exit 126
fi

reps="${BENCH_REPS:-10}"
warmup="${BENCH_WARMUP:-0.5}"
out="${BENCH_OUT:-benchmark-$(date +%Y%m%d-%H%M%S).json}"
cmd=("$bench" --benchmark_format=json --benchmark_repetitions="$reps" --benchmark_min_warmup_time="$warmup" --benchmark_out="$out" --benchmark_out_format=json)

if [ -n "${BENCH_FILTER:-}" ]; then
  cmd+=(--benchmark_filter="$BENCH_FILTER")
fi
cmd+=("$@")

if [ -n "${CPUSET:-}" ]; then
  if command -v taskset >/dev/null 2>&1; then
    cmd=(taskset -c "$CPUSET" "${cmd[@]}")
  else
    echo "warning: CPUSET requested but taskset not found" >&2
  fi
fi

set -x
"${cmd[@]}"
set +x

echo "benchmark json written to $out"
