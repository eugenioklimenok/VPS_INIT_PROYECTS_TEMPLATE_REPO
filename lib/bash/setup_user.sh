#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_USER_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_USER_SH_LOADED="1"

ensure_user() {
  local user="$1"
  local home_dir shell_name

  log_step "Ensuring operating user: $user"

  if id "$user" >/dev/null 2>&1; then
    log_ok "User $user already exists"
  else
    adduser --disabled-password --gecos "" "$user" || abort "Failed to create user $user"
    log_ok "User $user created"
  fi

  home_dir="$(getent passwd "$user" | cut -d: -f6)"
  shell_name="$(getent passwd "$user" | cut -d: -f7)"

  if [[ "$home_dir" == "/home/$user" ]]; then
    log_ok "Home directory is correct: $home_dir"
  else
    log_warn "User $user has unexpected home: ${home_dir:-unknown}"
  fi

  if [[ "$shell_name" != "/bin/bash" ]]; then
    usermod -s /bin/bash "$user" || abort "Failed to set shell /bin/bash for $user"
    log_ok "Shell set to /bin/bash for $user"
  else
    log_ok "Shell already /bin/bash for $user"
  fi

  if id -nG "$user" 2>/dev/null | grep -qw sudo; then
    log_ok "User $user already belongs to sudo group"
  else
    usermod -aG sudo "$user" || abort "Failed to add $user to sudo group"
    log_ok "User $user added to sudo group"
  fi
}
