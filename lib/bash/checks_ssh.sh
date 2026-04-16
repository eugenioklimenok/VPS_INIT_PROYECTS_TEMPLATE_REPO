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

  local sshd_t_error
  if ! sshd_t_error="$(run_sshd_syntax_check)"; then
    if [[ -n "$sshd_t_error" ]] && [[ "${VERBOSE_MODE:-no}" == "yes" ]]; then
      record_info "$category" "sshd -t detail: $sshd_t_error"
    fi

    if [[ "${EUID:-$(id -u)}" -ne 0 ]] && [[ -n "$sshd_t_error" ]] && printf '%s' "$sshd_t_error" | grep -Eqi 'permission denied|host key|privilege separation'; then
      record_warn "$category" "SSH syntax check could not be completed without root privileges"
      return
    fi

    record_fail "$category" "SSH configuration syntax invalid"
    return
  fi
  record_ok "$category" "SSH configuration syntax valid"

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

run_sshd_syntax_check() {
  local output=""
  local rc=0

  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    output="$(sshd -t 2>&1)"
    rc=$?
  elif command_exists sudo; then
    output="$(sudo -n sshd -t 2>&1)"
    rc=$?
    if [[ $rc -ne 0 ]] && printf '%s' "$output" | grep -Eqi 'password is required|a terminal is required'; then
      output="$(sshd -t 2>&1)"
      rc=$?
    fi
  else
    output="$(sshd -t 2>&1)"
    rc=$?
  fi

  if [[ $rc -ne 0 ]]; then
    printf '%s' "$output"
    return "$rc"
  fi

  return 0
}
