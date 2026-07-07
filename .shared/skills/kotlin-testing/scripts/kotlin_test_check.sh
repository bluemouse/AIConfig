#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"
for arg in "$@"; do
  case "$arg" in
    --dry-run) MODE="dry-run" ;;
    --quick) MODE="quick" ;;
    --full) MODE="full" ;;
    -h|--help)
      cat <<'HELP'
Usage: kotlin_test_check.sh [--dry-run|--quick|--full]

Discovers likely Kotlin/JVM test and quality tasks in a Gradle project.
--dry-run  print commands only
--quick    run the primary test task when available
--full     run test/check plus configured coverage/lint/static-analysis tasks
HELP
      exit 0
      ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [[ -x ./gradlew ]]; then
  GRADLE=(./gradlew)
elif command -v gradle >/dev/null 2>&1; then
  GRADLE=(gradle)
else
  echo "No Gradle wrapper or gradle command found." >&2
  echo "For standalone files, compile manually with kotlinc or create a Gradle project." >&2
  exit 1
fi

run_or_print() {
  printf '+ '
  printf '%q ' "${GRADLE[@]}" "$@"
  printf '\n'
  if [[ "$MODE" != "dry-run" ]]; then
    "${GRADLE[@]}" "$@"
  fi
}

TASKS=""
if TASK_OUTPUT=$("${GRADLE[@]}" tasks --all -q 2>/dev/null); then
  TASKS="$TASK_OUTPUT"
else
  echo "Could not list Gradle tasks; falling back to common task names." >&2
fi

has_task() {
  local task="$1"
  if [[ -z "$TASKS" ]]; then
    [[ "$task" == "test" || "$task" == "check" ]]
  else
    grep -Eq "(^|[[:space:]:])${task}($|[[:space:]-])" <<<"$TASKS"
  fi
}

COMMON_FULL_TASKS=(test check koverVerify koverHtmlReport ktlintCheck detekt)

if [[ "$MODE" == "dry-run" ]]; then
  echo "Mode: dry-run"
elif [[ "$MODE" == "quick" ]]; then
  echo "Mode: quick"
else
  echo "Mode: full"
fi

if [[ "$MODE" == "quick" ]]; then
  if has_task test; then
    run_or_print test
  else
    echo "No test task discovered." >&2
    exit 1
  fi
  exit 0
fi

if [[ "$MODE" == "dry-run" ]]; then
  for task in "${COMMON_FULL_TASKS[@]}"; do
    if has_task "$task"; then
      run_or_print "$task"
    fi
  done
  exit 0
fi

ran_any=false
for task in "${COMMON_FULL_TASKS[@]}"; do
  if has_task "$task"; then
    run_or_print "$task"
    ran_any=true
  fi
done

if [[ "$ran_any" == false ]]; then
  echo "No common Kotlin test/check tasks discovered." >&2
  exit 1
fi
