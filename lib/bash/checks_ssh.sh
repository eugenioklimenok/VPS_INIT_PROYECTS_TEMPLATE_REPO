#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_CHECKS_SSH_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_CHECKS_SSH_SH_LOADED="1"

check_ssh() {
  local category="SSH"
  local cfg="/etc/ssh/sshd_config"

  if ! command_exists sshd; then
    record_fail "$category" "sshd command not found"
    return
  fi

  if command_exists systemctl; then
    if systemctl is-active ssh >/dev/null 2>&1; then
      record_ok "$category" "SSH service active"
    else
      record_fail "$category" "SSH service inactive"
    fi
  else
    record_warn "$category" "systemctl not available; could not verify SSH service state"
  fi

  if [[ ! -f "$cfg" ]]; then
    record_fail "$category" "Missing $cfg"
    return
  fi

  if ! sshd -t >/dev/null 2>&1; then
    record_fail "$category" "SSH configuration syntax invalid"
    return
  fi

  local sshd_t root_login pass_auth pubkey_auth
  sshd_t="$(sshd -T 2>/dev/null || true)"

  root_login="$(printf '%s\n' "$sshd_t" | awk '/^permitrootlogin / {print $2}')"
  pass_auth="$(printf '%s\n' "$sshd_t" | awk '/^passwordauthentication / {print $2}')"
  pubkey_auth="$(printf '%s\n' "$sshd_t" | awk '/^pubkeyauthentication / {print $2}')"

  if [[ "$root_login" == "no" ]]; then
    record_ok "$category" "Root login disabled"
  else
    record_fail "$category" "Root login enabled or unresolved (${root_login:-unknown})"
  fi

  if [[ "$pass_auth" == "no" ]]; then
    record_ok "$category" "Password authentication disabled"
  else
    if is_yes "${STRICT_MODE:-no}"; then
      record_fail "$category" "Password authentication enabled in strict mode"
    else
      record_warn "$category" "Password authentication enabled"
    fi
  fi

  if [[ "$pubkey_auth" == "yes" ]]; then
    record_ok "$category" "Pubkey authentication enabled"
  else
    record_fail "$category" "Pubkey authentication disabled or unresolved (${pubkey_auth:-unknown})"
  fi
}
