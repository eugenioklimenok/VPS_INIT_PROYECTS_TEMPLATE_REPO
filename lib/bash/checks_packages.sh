#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_PACKAGES_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_PACKAGES_SH_LOADED="1"

check_packages() {
  local category="PACKAGES"
  local missing=()
  local critical_missing=0
  local pkg

  for pkg in $DEFAULT_REQUIRED_PACKAGES; do
    if ! package_installed "$pkg"; then
      missing+=("$pkg")
      case "$pkg" in
        curl|git)
          critical_missing=$((critical_missing + 1))
          ;;
      esac
    fi
  done

  if [[ "${#missing[@]}" -eq 0 ]]; then
    record_ok "$category" "All required base packages installed"
    return
  fi

  if [[ "$critical_missing" -gt 0 ]]; then
    record_fail "$category" "Missing critical packages: $(join_by ' ' "${missing[@]}")"
  else
    record_warn "$category" "Missing packages: $(join_by ' ' "${missing[@]}")"
  fi
}
