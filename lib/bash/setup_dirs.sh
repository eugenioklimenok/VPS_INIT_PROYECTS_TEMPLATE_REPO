#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_DIRS_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_DIRS_SH_LOADED="1"

ensure_standard_dirs() {
  local user="$1"
  local dirs=(
    "/home/$user/apps"
    "/home/$user/repos"
    "/home/$user/backups"
    "/home/$user/scripts"
  )
  local dir

  log_step "Ensuring standard directory structure"

  for dir in "${dirs[@]}"; do
    mkdir -p "$dir" || abort "Failed to create directory: $dir"
    chown "$user:$user" "$dir" || abort "Failed to set ownership on $dir"
    chmod 755 "$dir" || abort "Failed to set permissions on $dir"
    log_ok "Directory ready: $dir"
  done
}
