#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'HELP'
Usage: kotlin_project_check.sh [--dry-run] [--quick|--full] [project-dir]

Runs or prints likely verification commands for a plain Kotlin project.

Modes:
  --quick    Run a compact compile/test/check pass. Default.
  --full     Include clean/check plus configured lint/static-analysis tasks.
  --dry-run  Print commands without executing them.
  --help     Show this help.

Behavior:
  - Uses ./gradlew when present, otherwise gradle if available.
  - Inspects Gradle tasks when possible.
  - Falls back to kotlinc for simple standalone .kt files when no Gradle build exists.
HELP
}

DRY_RUN=0
MODE=quick
PROJECT_DIR=.

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --quick)
      MODE=quick
      shift
      ;;
    --full)
      MODE=full
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --*)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      PROJECT_DIR="$1"
      shift
      ;;
  esac
done

cd "$PROJECT_DIR"

run_cmd() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf 'DRY-RUN: %s\n' "$*"
  else
    printf 'RUN: %s\n' "$*"
    "$@"
  fi
}

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

GRADLE_CMD=""
if [ -x ./gradlew ]; then
  GRADLE_CMD=./gradlew
elif has_cmd gradle; then
  GRADLE_CMD=gradle
fi

if [ -n "$GRADLE_CMD" ] && { [ -f build.gradle.kts ] || [ -f build.gradle ] || [ -f settings.gradle.kts ] || [ -f settings.gradle ]; }; then
  TASK_OUTPUT=""
  if [ "$DRY_RUN" -eq 0 ]; then
    TASK_OUTPUT="$($GRADLE_CMD -q tasks --all 2>/dev/null || true)"
  fi

  task_exists() {
    local task="$1"
    if [ "$DRY_RUN" -eq 1 ]; then
      return 0
    fi
    printf '%s\n' "$TASK_OUTPUT" | grep -Eq "(^|[[:space:]])${task}($|[[:space:]-])"
  }

  COMMANDS=()
  if [ "$MODE" = full ]; then
    if task_exists clean; then COMMANDS+=(clean); fi
    if task_exists check; then COMMANDS+=(check); fi
    if task_exists ktlintCheck; then COMMANDS+=(ktlintCheck); fi
    if task_exists detekt; then COMMANDS+=(detekt); fi
    if [ "${#COMMANDS[@]}" -eq 0 ]; then COMMANDS+=(test); fi
  else
    if task_exists compileKotlin; then COMMANDS+=(compileKotlin); fi
    if task_exists test; then COMMANDS+=(test); fi
    if task_exists check && [ "${#COMMANDS[@]}" -eq 0 ]; then COMMANDS+=(check); fi
    if [ "${#COMMANDS[@]}" -eq 0 ]; then COMMANDS+=(test); fi
  fi

  run_cmd "$GRADLE_CMD" "${COMMANDS[@]}"
  exit 0
fi

mapfile -t KOTLIN_FILES < <(find . -type f -name '*.kt' \
  ! -path './build/*' \
  ! -path './.gradle/*' \
  ! -path './out/*' | sort)

if [ "${#KOTLIN_FILES[@]}" -eq 0 ]; then
  echo "No Gradle build or Kotlin files found in $(pwd)" >&2
  exit 1
fi

if ! has_cmd kotlinc; then
  echo "Found Kotlin files but neither Gradle nor kotlinc is available." >&2
  printf 'Files:\n' >&2
  printf '  %s\n' "${KOTLIN_FILES[@]}" >&2
  exit 1
fi

OUTPUT_JAR="${TMPDIR:-/tmp}/kotlin-project-check.jar"
run_cmd kotlinc "${KOTLIN_FILES[@]}" -d "$OUTPUT_JAR"
