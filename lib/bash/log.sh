#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_LOG_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_LOG_SH_LOADED="1"

LOG_VERBOSE="${LOG_VERBOSE:-no}"
LOG_USE_COLOR="${LOG_USE_COLOR:-auto}"

_log_supports_color() {
  [[ -t 1 ]] || return 1
  [[ -z "${NO_COLOR:-}" ]] || return 1
  command -v tput >/dev/null 2>&1 || return 1
  [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]
}

_log_color_for_level() {
  case "$1" in
    STEP) printf '\033[1;36m' ;;
    INFO) printf '\033[0;34m' ;;
    OK)   printf '\033[0;32m' ;;
    WARN) printf '\033[0;33m' ;;
    FAIL) printf '\033[0;31m' ;;
    DEBUG) printf '\033[0;35m' ;;
    *)    printf '' ;;
  esac
}

_log_reset_color() {
  printf '\033[0m'
}

_log_emit() {
  local level="$1"
  shift
  local message="$*"

  if [[ "$level" == "DEBUG" && "$LOG_VERBOSE" != "yes" ]]; then
    return 0
  fi

  if [[ "$LOG_USE_COLOR" == "yes" ]] || { [[ "$LOG_USE_COLOR" == "auto" ]] && _log_supports_color; }; then
    printf '%s[%s]%s %s\n' "$(_log_color_for_level "$level")" "$level" "$(_log_reset_color)" "$message"
  else
    printf '[%s] %s\n' "$level" "$message"
  fi
}

log_step() {
  printf '\n'
  _log_emit "STEP" "$*"
}

log_info() {
  _log_emit "INFO" "$*"
}

log_ok() {
  _log_emit "OK" "$*"
}

log_warn() {
  _log_emit "WARN" "$*"
}

log_fail() {
  _log_emit "FAIL" "$*"
}

log_debug() {
  _log_emit "DEBUG" "$*"
}
