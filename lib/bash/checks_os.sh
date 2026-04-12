#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_OS_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_OS_SH_LOADED="1"

check_os() {
  local category="OS"

  if [[ ! -f /etc/os-release ]]; then
    record_fail "$category" "Missing /etc/os-release"
    return
  fi

  # shellcheck disable=SC1091
  source /etc/os-release

  if [[ "${ID:-}" != "ubuntu" ]]; then
    record_fail "$category" "Unsupported distro: ${ID:-unknown}"
    return
  fi

  if [[ -n "${VERSION_ID:-}" ]]; then
    record_ok "$category" "Ubuntu detected: ${PRETTY_NAME:-Ubuntu ${VERSION_ID}}"
  else
    record_warn "$category" "Ubuntu detected but VERSION_ID is missing"
  fi

  if printf '%s' "${VERSION:-}" | grep -qi "LTS"; then
    record_ok "$category" "Ubuntu LTS release detected"
  else
    record_warn "$category" "Ubuntu detected but not an LTS release"
  fi
}
