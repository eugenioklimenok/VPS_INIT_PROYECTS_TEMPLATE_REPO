#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_UFW_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_UFW_SH_LOADED="1"

ensure_ufw_rule() {
  local rule="$1"

  if ufw status 2>/dev/null | grep -Eq "(^|[[:space:]])${rule}([[:space:]]|$)"; then
    log_ok "UFW rule already present: $rule"
  else
    ufw allow "$rule" || abort "Failed to allow UFW rule: $rule"
    log_ok "UFW rule added: $rule"
  fi
}

configure_ufw() {
  log_step "Configuring UFW"

  command_exists ufw || abort "ufw command not found"

  ensure_ufw_rule "22/tcp"
  ensure_ufw_rule "80/tcp"
  ensure_ufw_rule "443/tcp"

  ufw --force enable || abort "Failed to enable UFW"

  log_ok "UFW enabled"
}
