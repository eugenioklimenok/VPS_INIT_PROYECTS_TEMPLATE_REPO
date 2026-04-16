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

ensure_user_ssh_access() {
  local user="$1"
  local public_key="$2"
  local home_dir ssh_dir auth_keys

  [[ -n "$public_key" ]] || abort "Missing SSH public key for $user"

  home_dir="$(resolve_user_home "$user")" || abort "Cannot resolve home directory for $user"
  ssh_dir="${home_dir}/.ssh"
  auth_keys="${ssh_dir}/authorized_keys"

  mkdir -p "$ssh_dir" || abort "Failed to create $ssh_dir"
  touch "$auth_keys" || abort "Failed to create $auth_keys"

  if grep -Fxq "$public_key" "$auth_keys"; then
    log_ok "SSH public key already installed for $user"
  else
    printf '%s\n' "$public_key" >> "$auth_keys" || abort "Failed to append SSH public key"
    log_ok "SSH public key installed for $user"
  fi

  chown -R "$user:$user" "$ssh_dir" || abort "Failed to set ownership for $ssh_dir"
  chmod 700 "$ssh_dir" || abort "Failed to set permissions on $ssh_dir"
  chmod 600 "$auth_keys" || abort "Failed to set permissions on $auth_keys"
  log_ok "SSH access prepared for $user ($auth_keys)"
}
