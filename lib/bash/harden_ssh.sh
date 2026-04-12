#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_HARDEN_SSH_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_HARDEN_SSH_SH_LOADED="1"

ensure_ssh_permissions() {
  local user="$1"
  local home_dir ssh_dir auth_keys

  home_dir="$(resolve_user_home "$user")" || abort "Cannot resolve home directory for $user"
  ssh_dir="${home_dir}/.ssh"
  auth_keys="$(require_nonempty_authorized_keys "$user")"

  [[ -d "$ssh_dir" ]] || abort "Missing SSH directory for $user: $ssh_dir"

  chown "$user:$user" "$ssh_dir" || abort "Failed to set ownership on $ssh_dir"
  chmod 700 "$ssh_dir" || abort "Failed to set permissions on $ssh_dir"
  log_ok "SSH directory permissions hardened: $ssh_dir"

  chown "$user:$user" "$auth_keys" || abort "Failed to set ownership on $auth_keys"
  chmod 600 "$auth_keys" || abort "Failed to set permissions on $auth_keys"
  log_ok "authorized_keys permissions hardened: $auth_keys"
}

harden_ssh_access() {
  local user="$1"

  log_step "Hardening SSH access"
  ensure_ssh_permissions "$user"
  configure_ssh "no"
  log_ok "SSH hardened for key-only access"
}
