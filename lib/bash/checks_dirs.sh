#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_DIRS_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_DIRS_SH_LOADED="1"

check_one_dir() {
  local user="$1"
  local dir="$2"
  local category="DIRS"
  local owner

  if [[ ! -d "$dir" ]]; then
    record_fail "$category" "Missing directory: $dir"
    return
  fi

  record_ok "$category" "Directory exists: $dir"

  owner="$(stat -c '%U:%G' "$dir" 2>/dev/null || true)"
  if [[ "$owner" == "$user:$user" ]]; then
    record_ok "$category" "Ownership correct for $dir ($owner)"
  else
    record_warn "$category" "Unexpected ownership for $dir (${owner:-unknown})"
  fi
}

check_dirs() {
  local user="$1"
  check_one_dir "$user" "/home/$user/apps"
  check_one_dir "$user" "/home/$user/repos"
  check_one_dir "$user" "/home/$user/backups"
  check_one_dir "$user" "/home/$user/scripts"
}
