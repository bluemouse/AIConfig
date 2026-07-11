#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/collect-compiler-remarks.sh <clang|gcc> <out-dir> -- <compile-command...>

Examples:
  scripts/collect-compiler-remarks.sh clang remarks -- clang++ -O3 -std=c++20 -c kernel.cpp -o kernel.o
  scripts/collect-compiler-remarks.sh gcc remarks -- g++ -O3 -std=c++20 -c kernel.cpp -o kernel.o

This wrapper is for one compiler command, not a whole build system command.
EOF
}

if [ "$#" -lt 4 ]; then
  usage
  exit 2
fi

compiler="$1"
out_dir="$2"
shift 2
if [ "$1" != "--" ]; then
  usage
  exit 2
fi
shift

mkdir -p "$out_dir"

case "$compiler" in
  clang)
    flags=(-Rpass=.* -Rpass-missed=.* -Rpass-analysis=.* -fsave-optimization-record)
    ;;
  gcc)
    flags=(-fopt-info-vec-optimized -fopt-info-vec-missed -fopt-info-inline-optimized)
    ;;
  *)
    echo "error: first argument must be clang or gcc" >&2
    exit 2
    ;;
esac

log="$out_dir/remarks.log"
echo "command: $* ${flags[*]}" > "$log"
"$@" "${flags[@]}" >> "$log" 2>&1

echo "remarks log written to $log"
find "$out_dir" -maxdepth 1 -type f | sort
