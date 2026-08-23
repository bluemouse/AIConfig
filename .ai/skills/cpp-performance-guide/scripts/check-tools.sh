#!/usr/bin/env bash
set -u

have() { command -v "$1" >/dev/null 2>&1; }
show_tool() {
  if have "$1"; then
    printf 'yes  %s  %s\n' "$1" "$(command -v "$1")"
  else
    printf 'no   %s\n' "$1"
  fi
}

echo "== C++ performance tool check =="
for t in perf taskset numactl lscpu cpupower turbostat hyperfine heaptrack valgrind callgrind_annotate kcachegrind google-pprof tracy-profiler llvm-profdata llvm-objdump objdump clang clang++ gcc g++ cmake ninja; do
  show_tool "$t"
done

echo
if [ -r /proc/sys/kernel/perf_event_paranoid ]; then
  printf 'perf_event_paranoid: %s\n' "$(cat /proc/sys/kernel/perf_event_paranoid)"
else
  echo "perf_event_paranoid: unavailable"
fi

if [ -r /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
  printf 'cpu0 governor: %s\n' "$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
else
  echo "cpu0 governor: unavailable"
fi

echo
if have lscpu; then
  lscpu | sed -n '1,25p'
elif [ -r /proc/cpuinfo ]; then
  grep -m1 'model name' /proc/cpuinfo || true
  grep -m1 'cpu cores' /proc/cpuinfo || true
else
  echo "cpu info: unavailable"
fi
