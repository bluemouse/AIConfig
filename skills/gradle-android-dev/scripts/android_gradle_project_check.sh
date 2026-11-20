#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: android_gradle_project_check.sh [--dry-run|--quick|--full|--perf|--device] [project-dir]

Modes:
  --dry-run  Print detected Android Gradle project info and commands without running Gradle.
  --quick    Run lightweight configuration/discovery checks.
  --full     Run assembleDebug, testDebugUnitTest, and lintDebug when available by task name.
  --perf     Run local profiling-oriented checks without publishing build scans.
  --device   Run connectedDebugAndroidTest after discovery; requires a device/emulator.

Default mode is --dry-run. Default project-dir is the current directory.
EOF
}

mode="--dry-run"
project_dir="."

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run|--quick|--full|--perf|--device)
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
  gradle_cmd="sh ./gradlew"
elif command -v gradle >/dev/null 2>&1; then
  gradle_cmd="gradle"
else
  echo "No Gradle wrapper or gradle executable found." >&2
  exit 2
fi

echo "Project root: $root"
echo "Gradle command: $gradle_cmd"

echo
echo "Android-related build files:"
find . -maxdepth 4 \( -name 'settings.gradle' -o -name 'settings.gradle.kts' -o -name 'build.gradle' -o -name 'build.gradle.kts' -o -name 'gradle.properties' -o -name 'libs.versions.toml' -o -name 'AndroidManifest.xml' \) | sort | sed -n '1,200p'

echo
echo "Android plugin declarations:"
find . -maxdepth 4 \( -name 'build.gradle' -o -name 'build.gradle.kts' \) -print0 \
  | xargs -0 grep -nE 'com\.android\.(application|library|test)|org\.jetbrains\.kotlin\.android|kotlin\("android"\)' 2>/dev/null \
  | sed -n '1,160p' || true

echo
echo "Android DSL hints:"
find . -maxdepth 4 \( -name 'build.gradle' -o -name 'build.gradle.kts' \) -print0 \
  | xargs -0 grep -nE 'namespace|compileSdk|minSdk|targetSdk|buildTypes|productFlavors|flavorDimensions|androidComponents|lint|signingConfigs|minifyEnabled|isMinifyEnabled' 2>/dev/null \
  | sed -n '1,220p' || true

detect_static_variant() {
  local file flavor
  while IFS= read -r file; do
    [ -n "$file" ] || continue
    flavor="$(
      awk '
        BEGIN { in_pf = 0; depth = 0; in_comment = 0 }
        function emit_flavor(name) {
          print toupper(substr(name, 1, 1)) substr(name, 2)
          exit 0
        }
        function check_segment(seg, brace,    tok) {
          if (match(seg, /(create|register)[[:space:]]*\([[:space:]]*["'\''][A-Za-z][A-Za-z0-9_]*["'\'']/)) {
            tok = substr(seg, RSTART, RLENGTH)
            sub(/["'\'']$/, "", tok)
            sub(/^.*["'\'']/, "", tok)
            emit_flavor(tok)
          }
          if (match(seg, /(^|[^A-Za-z0-9_])val[[:space:]]+[A-Za-z][A-Za-z0-9_]*[[:space:]]+by[[:space:]]+(creating|registering)/)) {
            tok = substr(seg, RSTART, RLENGTH)
            sub(/^.*val[[:space:]]+/, "", tok)
            sub(/[[:space:]]+by[[:space:]]+.*$/, "", tok)
            emit_flavor(tok)
          }
          if (brace == "{" && match(seg, /(^|[^A-Za-z0-9_.])[A-Za-z][A-Za-z0-9_]*[[:space:]]*$/)) {
            tok = substr(seg, RSTART, RLENGTH)
            sub(/^[^A-Za-z]+/, "", tok)
            sub(/[[:space:]]+$/, "", tok)
            if (tok != "all" && tok != "configureEach" && tok != "create" && tok != "register" && tok != "creating" && tok != "registering") {
              emit_flavor(tok)
            }
          }
        }
        {
          line = $0
          out = ""
          while (length(line) > 0) {
            if (in_comment) {
              idx = index(line, "*/")
              if (idx == 0) { line = ""; break }
              line = substr(line, idx + 2)
              in_comment = 0
            } else {
              c_idx = index(line, "/*")
              l_idx = index(line, "//")
              if (l_idx > 0 && (c_idx == 0 || l_idx < c_idx)) {
                out = out substr(line, 1, l_idx - 1)
                line = ""
                break
              } else if (c_idx > 0) {
                out = out substr(line, 1, c_idx - 1)
                line = substr(line, c_idx + 2)
                in_comment = 1
              } else {
                out = out line
                line = ""
              }
            }
          }
          s = out
          while (length(s) > 0) {
            if (!in_pf) {
              if (match(s, /(^|[^A-Za-z0-9_])productFlavors[[:space:]]*[{]/)) {
                in_pf = 1
                depth = 1
                s = substr(s, RSTART + RLENGTH)
              } else {
                break
              }
            } else {
              if (match(s, /[{}]/)) {
                bpos = RSTART
                seg = substr(s, 1, bpos - 1)
                brace = substr(s, bpos, 1)
                if (depth == 1) {
                  check_segment(seg, brace)
                }
                if (brace == "{") depth++
                else depth--
                if (depth <= 0) {
                  in_pf = 0
                  depth = 0
                }
                s = substr(s, bpos + 1)
              } else {
                if (depth == 1) {
                  check_segment(s, "")
                }
                break
              }
            }
          }
        }
      ' "$file"
    )"
    if [ -n "$flavor" ]; then
      printf '%sDebug\n' "$flavor"
      return 0
    fi
  done < <(find . -maxdepth 4 \( -name 'build.gradle' -o -name 'build.gradle.kts' \) | sort)
  printf 'Debug\n'
}

static_variant="$(detect_static_variant)"
variant_suffix="$static_variant"

if [ "$mode" = "--full" ] || [ "$mode" = "--perf" ] || [ "$mode" = "--device" ]; then
  task_output="$(sh -c "$gradle_cmd tasks --all" 2>/dev/null || true)"
  if [ -n "$task_output" ]; then
    if printf '%s\n' "$task_output" | grep -Eq '^[[:space:]]*([A-Za-z0-9_.-]*:)*(testDebugUnitTest|lintDebug)([[:space:]]|$)'; then
      variant_suffix="Debug"
    else
      discovered_flavor="$(
        {
          printf '%s\n' "$task_output" \
            | sed -nE 's/^[[:space:]]*([A-Za-z0-9_.-]*:)*test([A-Z][A-Za-z0-9]*)DebugUnitTest([[:space:]].*|$)/\2/p' \
            | head -n 1
        } || true
      )"
      if [ -z "$discovered_flavor" ]; then
        discovered_flavor="$(
          {
            printf '%s\n' "$task_output" \
              | sed -nE 's/^[[:space:]]*([A-Za-z0-9_.-]*:)*assemble([A-Z][A-Za-z0-9]*)Debug([[:space:]].*|$)/\2/p' \
              | grep -Ev '(AndroidTest|UnitTest)$' \
              | head -n 1
          } || true
        )"
      fi
      if [ -z "$discovered_flavor" ]; then
        discovered_flavor="$(
          {
            printf '%s\n' "$task_output" \
              | sed -nE 's/^[[:space:]]*([A-Za-z0-9_.-]*:)*lint([A-Z][A-Za-z0-9]*)Debug([[:space:]].*|$)/\2/p' \
              | grep -Ev '^(Fix|Analyze|Report|Vital|Model)' \
              | head -n 1
          } || true
        )"
      fi
      if [ -n "$discovered_flavor" ]; then
        variant_suffix="${discovered_flavor}Debug"
      fi
    fi
  fi
fi

assemble_task="assemble${variant_suffix}"
unit_test_task="test${variant_suffix}UnitTest"
lint_task="lint${variant_suffix}"
connected_test_task="connected${variant_suffix}AndroidTest"

preflight_commands=(
  "$gradle_cmd --version"
  "$gradle_cmd help --stacktrace"
)
quick_commands=(
  "${preflight_commands[@]}"
  "$gradle_cmd tasks --all"
)
full_commands=(
  "$gradle_cmd $assemble_task --stacktrace"
  "$gradle_cmd $unit_test_task --stacktrace"
  "$gradle_cmd $lint_task --stacktrace"
)
perf_commands=(
  "$gradle_cmd help --profile"
  "$gradle_cmd $assemble_task --profile"
)
device_commands=(
  "$gradle_cmd $connected_test_task --stacktrace"
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
    print_commands "${quick_commands[@]}" "${full_commands[@]}" "${perf_commands[@]}" "${device_commands[@]}"
    ;;
  --quick)
    run_commands "${quick_commands[@]}"
    ;;
  --full)
    run_commands "${preflight_commands[@]}" "${full_commands[@]}"
    ;;
  --perf)
    run_commands "${perf_commands[@]}"
    ;;
  --device)
    run_commands "${preflight_commands[@]}" "${device_commands[@]}"
    ;;
esac
