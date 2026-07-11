#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run-perf-record.sh <binary-or-command> [args...]

Environment:
  PERF_FREQ       Sampling frequency (default: 999)
  PERF_CALLGRAPH  Call graph mode: fp, dwarf, or lbr (default: fp)
  PERF_DATA       Output perf data file (default: perf.data)
  CPUSET          Optional CPU list for taskset
  NUMA_NODE       Optional NUMA node for numactl
  FLAMEGRAPH_DIR  Optional directory containing stackcollapse-perf.pl and flamegraph.pl
  FLAMEGRAPH_OUT  Output SVG path when FLAMEGRAPH_DIR is set (default: flame.svg)
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

freq="${PERF_FREQ:-999}"
callgraph="${PERF_CALLGRAPH:-fp}"
data="${PERF_DATA:-perf.data}"
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
perf record -F "$freq" --call-graph "$callgraph" -o "$data" -- "${cmd[@]}"
set +x

echo "perf data written to $data"
echo "Open with: perf report -i $data"

run_flamegraph_script() {
  local script="$1"
  if [ -x "$script" ]; then
    "$script"
  elif [ -f "$script" ]; then
    perl "$script"
  else
    return 1
  fi
}

if [ -n "${FLAMEGRAPH_DIR:-}" ]; then
  stackcollapse="$FLAMEGRAPH_DIR/stackcollapse-perf.pl"
  flamegraph="$FLAMEGRAPH_DIR/flamegraph.pl"
  out="${FLAMEGRAPH_OUT:-flame.svg}"
  if { [ -f "$stackcollapse" ] || [ -x "$stackcollapse" ]; } && { [ -f "$flamegraph" ] || [ -x "$flamegraph" ]; }; then
    perf script -i "$data" | run_flamegraph_script "$stackcollapse" | run_flamegraph_script "$flamegraph" > "$out"
    echo "flamegraph written to $out"
  else
    echo "warning: FLAMEGRAPH_DIR set but stackcollapse-perf.pl or flamegraph.pl not found" >&2
  fi
fi
