#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_UFW_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_UFW_SH_LOADED="1"

ufw_has_rule() {
  local port="$1"
  ufw status 2>/dev/null | grep -Eq "(^|[[:space:]])${port}(/tcp)?[[:space:]]"
}

check_ufw() {
  local category="UFW"
  local ufw_status

  if ! command_exists ufw; then
    record_fail "$category" "ufw command not found"
    return
  fi

  ufw_status="$(ufw status 2>/dev/null | head -n1 || true)"

  if printf '%s' "$ufw_status" | grep -qi "Status: active"; then
    record_ok "$category" "UFW active"
  else
    if is_yes "${STRICT_MODE:-no}"; then
      record_fail "$category" "UFW inactive in strict mode"
    else
      record_warn "$category" "UFW inactive"
    fi
  fi

  if ufw_has_rule 22; then
    record_ok "$category" "Port 22 allowed"
  else
    record_fail "$category" "Port 22 not allowed"
  fi

  if ufw_has_rule 80; then
    record_ok "$category" "Port 80 allowed"
  else
    record_warn "$category" "Port 80 not allowed"
  fi

  if ufw_has_rule 443; then
    record_ok "$category" "Port 443 allowed"
  else
    record_warn "$category" "Port 443 not allowed"
  fi
}
