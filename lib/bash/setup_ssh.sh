#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_SSH_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_SSH_SH_LOADED="1"

ensure_sshd_setting() {
  local key="$1"
  local value="$2"
  local file="$3"

  if grep -Eq "^[#[:space:]]*${key}[[:space:]]+" "$file"; then
    sed -i -E "s|^[#[:space:]]*${key}[[:space:]]+.*|${key} ${value}|g" "$file" \
      || abort "Failed updating SSH setting $key"
  else
    printf '%s %s\n' "$key" "$value" >> "$file" || abort "Failed appending SSH setting $key"
  fi
}

configure_ssh() {
  local password_auth="$1"
  local cfg="/etc/ssh/sshd_config"
  local backup_file

  log_step "Configuring SSH baseline"

  [[ -f "$cfg" ]] || abort "SSH config file not found: $cfg"

  backup_file="${cfg}.bak.$(timestamp_compact)"
  cp "$cfg" "$backup_file" || abort "Failed to backup SSH config"
  log_ok "SSH config backup created: $backup_file"

  ensure_sshd_setting "PermitRootLogin" "no" "$cfg"
  ensure_sshd_setting "PubkeyAuthentication" "yes" "$cfg"
  ensure_sshd_setting "PasswordAuthentication" "$password_auth" "$cfg"

  sshd -t || abort "Invalid sshd_config after changes"

  systemctl reload ssh || systemctl restart ssh || abort "Failed to reload/restart SSH service"

  log_ok "SSH configured: root login disabled, pubkey enabled, password auth=$password_auth"
}
