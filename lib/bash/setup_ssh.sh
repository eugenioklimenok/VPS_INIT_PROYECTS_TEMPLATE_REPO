#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_SETUP_SSH_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_SETUP_SSH_SH_LOADED="1"

SSHD_CONFIG_FILE="${SSHD_CONFIG_FILE:-/etc/ssh/sshd_config}"
SSHD_CONFIG_DIR="${SSHD_CONFIG_DIR:-/etc/ssh/sshd_config.d}"
SSHD_FRAMEWORK_DROPIN="${SSHD_FRAMEWORK_DROPIN:-$SSHD_CONFIG_DIR/99-vps-init-framework.conf}"

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

collect_sshd_conf_files() {
  local cfg_dir="$1"

  [[ -d "$cfg_dir" ]] || return 0
  find "$cfg_dir" -maxdepth 1 -type f -name '*.conf' -print 2>/dev/null | sort
}

ensure_framework_sshd_dropin() {
  local password_auth="$1"

  mkdir -p "$SSHD_CONFIG_DIR" || abort "Failed to create SSH include directory: $SSHD_CONFIG_DIR"

  cat > "$SSHD_FRAMEWORK_DROPIN" <<EOF
# Managed by VPS_INIT_PROYECTS_TEMPLATE_REPO
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication $password_auth
KbdInteractiveAuthentication no
EOF

  log_ok "SSH include baseline enforced in $SSHD_FRAMEWORK_DROPIN"
}

normalize_include_conflicts() {
  local password_auth="$1"
  local file

  while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    [[ "$file" == "$SSHD_FRAMEWORK_DROPIN" ]] && continue

    if grep -Eq '^[#[:space:]]*(PermitRootLogin|PubkeyAuthentication|PasswordAuthentication|KbdInteractiveAuthentication)[[:space:]]+' "$file"; then
      ensure_sshd_setting "PermitRootLogin" "no" "$file"
      ensure_sshd_setting "PubkeyAuthentication" "yes" "$file"
      ensure_sshd_setting "PasswordAuthentication" "$password_auth" "$file"
      ensure_sshd_setting "KbdInteractiveAuthentication" "no" "$file"
      log_info "Normalized SSH overrides in $file"
    fi
  done < <(collect_sshd_conf_files "$SSHD_CONFIG_DIR")
}

sshd_effective_value() {
  local output="$1"
  local key="$2"

  printf '%s\n' "$output" | awk -v pattern="^${key} " '$0 ~ pattern {print $2; exit}'
}

validate_effective_sshd_state() {
  local expected_password_auth="$1"
  local expected_pubkey_auth="$2"
  local expected_root_login="$3"
  local expected_kbd_auth="$4"
  local sshd_t_output mismatch=0
  local actual_password actual_pubkey actual_root actual_kbd

  sshd_t_output="$(sshd -T 2>&1)" || abort "Failed to read effective sshd config: $sshd_t_output"

  actual_password="$(sshd_effective_value "$sshd_t_output" "passwordauthentication")"
  actual_pubkey="$(sshd_effective_value "$sshd_t_output" "pubkeyauthentication")"
  actual_root="$(sshd_effective_value "$sshd_t_output" "permitrootlogin")"
  actual_kbd="$(sshd_effective_value "$sshd_t_output" "kbdinteractiveauthentication")"

  if [[ "$actual_password" != "$expected_password_auth" ]]; then
    log_fail "Effective passwordauthentication mismatch: expected=$expected_password_auth actual=${actual_password:-unset}"
    mismatch=1
  fi

  if [[ "$actual_pubkey" != "$expected_pubkey_auth" ]]; then
    log_fail "Effective pubkeyauthentication mismatch: expected=$expected_pubkey_auth actual=${actual_pubkey:-unset}"
    mismatch=1
  fi

  if [[ "$actual_root" != "$expected_root_login" ]]; then
    log_fail "Effective permitrootlogin mismatch: expected=$expected_root_login actual=${actual_root:-unset}"
    mismatch=1
  fi

  if [[ "$actual_kbd" != "$expected_kbd_auth" ]]; then
    log_fail "Effective kbdinteractiveauthentication mismatch: expected=$expected_kbd_auth actual=${actual_kbd:-unset}"
    mismatch=1
  fi

  if [[ "$mismatch" -ne 0 ]]; then
    abort "Effective SSH baseline does not match expected values"
  fi

  log_ok "Effective SSH config validated (sshd -T)"
}

configure_ssh() {
  local password_auth="$1"
  local cfg="$SSHD_CONFIG_FILE"
  local backup_file

  log_step "Configuring SSH baseline"

  [[ -f "$cfg" ]] || abort "SSH config file not found: $cfg"

  backup_file="${cfg}.bak.$(timestamp_compact)"
  cp "$cfg" "$backup_file" || abort "Failed to backup SSH config"
  log_ok "SSH config backup created: $backup_file"

  ensure_sshd_setting "PermitRootLogin" "no" "$cfg"
  ensure_sshd_setting "PubkeyAuthentication" "yes" "$cfg"
  ensure_sshd_setting "PasswordAuthentication" "$password_auth" "$cfg"
  ensure_sshd_setting "KbdInteractiveAuthentication" "no" "$cfg"

  ensure_framework_sshd_dropin "$password_auth"
  normalize_include_conflicts "$password_auth"

  sshd -t || abort "Invalid sshd_config after changes"
  validate_effective_sshd_state "$password_auth" "yes" "no" "no"

  systemctl reload ssh || systemctl restart ssh || abort "Failed to reload/restart SSH service"
  validate_effective_sshd_state "$password_auth" "yes" "no" "no"

  log_ok "SSH configured: root login disabled, pubkey enabled, password auth=$password_auth, kbd-interactive disabled"
}
