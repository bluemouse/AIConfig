#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: gradle_project_check.sh [--dry-run|--quick|--full|--perf] [project-dir]

Modes:
  --dry-run  Print detected project info and commands without running Gradle.
  --quick    Run lightweight configuration and discovery checks.
  --full     Run check with stacktrace after lightweight checks.
  --perf     Run local profiling-oriented checks without publishing build scans.

Default mode is --dry-run. Default project-dir is the current directory.
EOF
}

mode="--dry-run"
project_dir="."

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run|--quick|--full|--perf)
      mode="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      project_dir="$1"
      shift
      ;;
  esac
done

cd "$project_dir"

find_root() {
  local dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/gradlew" ] || [ -f "$dir/settings.gradle.kts" ] || [ -f "$dir/settings.gradle" ]; then
      printf '%s\n' "$dir"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  printf '%s\n' "$PWD"
}

root="$(find_root)"
cd "$root"

if [ -x "./gradlew" ]; then
  gradle_cmd="./gradlew"
elif [ -f "./gradlew" ]; then
  chmod +x ./gradlew 2>/dev/null || true
  gradle_cmd="./gradlew"
elif command -v gradle >/dev/null 2>&1; then
  gradle_cmd="gradle"
else
  echo "No Gradle wrapper or gradle executable found." >&2
  exit 2
fi

echo "Project root: $root"
echo "Gradle command: $gradle_cmd"

echo
echo "Build files:"
find . -maxdepth 3 \( -name 'settings.gradle' -o -name 'settings.gradle.kts' -o -name 'build.gradle' -o -name 'build.gradle.kts' -o -name 'gradle.properties' -o -name 'libs.versions.toml' \) | sort

echo
echo "Likely plugin declarations:"
find . -maxdepth 3 \( -name 'build.gradle' -o -name 'build.gradle.kts' -o -name 'settings.gradle' -o -name 'settings.gradle.kts' \) -print0 \
  | xargs -0 grep -nE '^[[:space:]]*(id\(|id |alias\(|kotlin\(|`java|java-library|application)' 2>/dev/null \
  | sed -n '1,120p' || true

quick_commands=(
  "$gradle_cmd --version"
  "$gradle_cmd help --stacktrace"
  "$gradle_cmd tasks --all"
)
full_commands=(
  "$gradle_cmd check --stacktrace"
)
perf_commands=(
  "$gradle_cmd help --profile"
  "$gradle_cmd help --configuration-cache --configuration-cache-problems=warn"
)

print_commands() {
  echo
  echo "Commands:"
  for cmd in "$@"; do
    echo "  $cmd"
  done
}

run_commands() {
  for cmd in "$@"; do
    echo
    echo "+ $cmd"
    sh -c "$cmd"
  done
}

case "$mode" in
  --dry-run)
    print_commands "${quick_commands[@]}" "${full_commands[@]}" "${perf_commands[@]}"
    ;;
  --quick)
    run_commands "${quick_commands[@]}"
    ;;
  --full)
    run_commands "${quick_commands[@]}" "${full_commands[@]}"
    ;;
  --perf)
    run_commands "${perf_commands[@]}"
    ;;
esac
