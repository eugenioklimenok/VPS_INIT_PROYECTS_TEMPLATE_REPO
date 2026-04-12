#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_USER_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_USER_SH_LOADED="1"

check_user() {
  local user="$1"
  local category="USER"

  if ! id "$user" >/dev/null 2>&1; then
    record_fail "$category" "User $user does not exist"
    return
  fi

  local passwd_entry home_dir shell_name groups
  passwd_entry="$(getent passwd "$user" 2>/dev/null || true)"

  if [[ -z "$passwd_entry" ]]; then
    record_fail "$category" "Could not resolve passwd entry for $user"
    return
  fi

  home_dir="$(printf '%s' "$passwd_entry" | cut -d: -f6)"
  shell_name="$(printf '%s' "$passwd_entry" | cut -d: -f7)"
  groups="$(id -nG "$user" 2>/dev/null || true)"

  if [[ "$home_dir" == "/home/$user" ]]; then
    record_ok "$category" "Home directory correct: $home_dir"
  else
    record_warn "$category" "Unexpected home directory: ${home_dir:-unknown}"
  fi

  case "$shell_name" in
    /bin/bash)
      record_ok "$category" "Shell is bash"
      ;;
    /usr/sbin/nologin|/bin/false|"")
      record_fail "$category" "Shell invalid or blocked: ${shell_name:-empty}"
      ;;
    *)
      record_warn "$category" "Unexpected shell: $shell_name"
      ;;
  esac

  if printf '%s' "$groups" | grep -qw "sudo"; then
    record_ok "$category" "User belongs to sudo group"
  else
    record_fail "$category" "User does not belong to sudo group"
  fi
}
