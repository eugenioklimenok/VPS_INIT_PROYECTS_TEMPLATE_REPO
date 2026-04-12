#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_RESULTS_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_RESULTS_SH_LOADED="1"

RESULTS=()
RESULT_OKS=0
RESULT_INFOS=0
RESULT_WARNS=0
RESULT_FAILS=0
EXIT_CODE=0

init_results() {
  RESULTS=()
  RESULT_OKS=0
  RESULT_INFOS=0
  RESULT_WARNS=0
  RESULT_FAILS=0
  EXIT_CODE=0
}

add_result() {
  local status="$1"
  local category="$2"
  local message="$3"

  RESULTS+=("${status}|${category}|${message}")

  case "$status" in
    OK)
      RESULT_OKS=$((RESULT_OKS + 1))
      ;;
    INFO)
      RESULT_INFOS=$((RESULT_INFOS + 1))
      ;;
    WARN)
      RESULT_WARNS=$((RESULT_WARNS + 1))
      ;;
    FAIL)
      RESULT_FAILS=$((RESULT_FAILS + 1))
      ;;
    *)
      printf '[FAIL] Unsupported result status: %s\n' "$status" >&2
      exit 3
      ;;
  esac
}

record_ok() {
  add_result "OK" "$1" "$2"
}

record_info() {
  add_result "INFO" "$1" "$2"
}

record_warn() {
  add_result "WARN" "$1" "$2"
}

record_fail() {
  add_result "FAIL" "$1" "$2"
}

set_exit_code_from_results() {
  if [[ "$RESULT_FAILS" -gt 0 ]]; then
    EXIT_CODE=2
  elif [[ "$RESULT_WARNS" -gt 0 ]]; then
    EXIT_CODE=1
  else
    EXIT_CODE=0
  fi
}

print_results_human() {
  local line status category message

  for line in "${RESULTS[@]}"; do
    IFS='|' read -r status category message <<< "$line"
    printf '[%s] %-10s %s\n' "$status" "$category" "$message"
  done
}

print_results_summary() {
  printf 'Summary:\n'
  printf '  OK:    %s\n' "$RESULT_OKS"
  printf '  INFO:  %s\n' "$RESULT_INFOS"
  printf '  WARN:  %s\n' "$RESULT_WARNS"
  printf '  FAIL:  %s\n' "$RESULT_FAILS"
  printf '  Exit code: %s\n' "$EXIT_CODE"
}
