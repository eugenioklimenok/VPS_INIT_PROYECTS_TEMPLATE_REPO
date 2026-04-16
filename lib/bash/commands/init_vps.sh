#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# shellcheck source=../../common.sh
source "$REPO_ROOT/lib/bash/common.sh"
# shellcheck source=../../log.sh
source "$REPO_ROOT/lib/bash/log.sh"
# shellcheck source=../../setup_user.sh
source "$REPO_ROOT/lib/bash/setup_user.sh"
# shellcheck source=../../setup_dirs.sh
source "$REPO_ROOT/lib/bash/setup_dirs.sh"
# shellcheck source=../../setup_packages.sh
source "$REPO_ROOT/lib/bash/setup_packages.sh"
# shellcheck source=../../setup_ssh.sh
source "$REPO_ROOT/lib/bash/setup_ssh.sh"
# shellcheck source=../../setup_ufw.sh
source "$REPO_ROOT/lib/bash/setup_ufw.sh"
# shellcheck source=../../setup_docker.sh
source "$REPO_ROOT/lib/bash/setup_docker.sh"

TARGET_USER=""
TARGET_TIMEZONE=""
PASSWORD_AUTH_MODE=""
SKIP_DOCKER="no"
NON_INTERACTIVE="no"
REPORT_FILE=""
SSH_PUBLIC_KEY=""
SSH_PUBLIC_KEY_FILE=""
ALLOW_WITHOUT_PUBLIC_KEY="no"
PASSWORD_AUTH_FLAGS_SET=0
PUBLIC_KEY_FLAGS_SET=0

usage() {
  cat <<'EOF'
Usage: init-vps [options]

Options:
  --user <user>                 Operating user to ensure (default: from config or alex)
  --timezone <tz>               Timezone to set, e.g. America/Argentina/Buenos_Aires
  --public-key <ssh-pubkey>     Public SSH key to install for remote access
  --public-key-file <file>      File containing the public SSH key to install
  --allow-without-public-key    Explicitly allow init without installing a public key
  --with-password-auth          Keep SSH password authentication enabled
  --disable-password-auth       Disable SSH password authentication
  --skip-docker                 Skip Docker installation
  --non-interactive             Do not prompt for confirmation
  --report <file>               Save execution report to file
  --help                        Show this help
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --user)
        shift
        TARGET_USER="${1:-}"
        [[ -n "$TARGET_USER" ]] || die "Missing value for --user"
        ;;
      --timezone)
        shift
        TARGET_TIMEZONE="${1:-}"
        [[ -n "$TARGET_TIMEZONE" ]] || die "Missing value for --timezone"
        ;;
      --public-key)
        shift
        SSH_PUBLIC_KEY="${1:-}"
        [[ -n "$SSH_PUBLIC_KEY" ]] || die "Missing value for --public-key"
        PUBLIC_KEY_FLAGS_SET=$((PUBLIC_KEY_FLAGS_SET + 1))
        ;;
      --public-key-file)
        shift
        SSH_PUBLIC_KEY_FILE="${1:-}"
        [[ -n "$SSH_PUBLIC_KEY_FILE" ]] || die "Missing value for --public-key-file"
        PUBLIC_KEY_FLAGS_SET=$((PUBLIC_KEY_FLAGS_SET + 1))
        ;;
      --allow-without-public-key)
        ALLOW_WITHOUT_PUBLIC_KEY="yes"
        ;;
      --with-password-auth)
        PASSWORD_AUTH_MODE="yes"
        PASSWORD_AUTH_FLAGS_SET=$((PASSWORD_AUTH_FLAGS_SET + 1))
        ;;
      --disable-password-auth)
        PASSWORD_AUTH_MODE="no"
        PASSWORD_AUTH_FLAGS_SET=$((PASSWORD_AUTH_FLAGS_SET + 1))
        ;;
      --skip-docker)
        SKIP_DOCKER="yes"
        ;;
      --non-interactive)
        NON_INTERACTIVE="yes"
        ;;
      --report)
        shift
        REPORT_FILE="${1:-}"
        [[ -n "$REPORT_FILE" ]] || die "Missing value for --report"
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        die "Unknown argument: $1"
        ;;
    esac
    shift
  done
}

read_public_key_file() {
  local key_file="$1"
  local key_line

  [[ -f "$key_file" ]] || die "Public key file not found: $key_file"
  key_line="$(grep -m1 -E '^[[:space:]]*[^[:space:]#]+' "$key_file" || true)"
  key_line="${key_line#"${key_line%%[![:space:]]*}"}"
  [[ -n "$key_line" ]] || die "Public key file is empty: $key_file"
  printf '%s\n' "$key_line"
}

validate_public_key_format() {
  local key="$1"
  case "$key" in
    ssh-*' '*|ecdsa-*' '*)
      return 0
      ;;
    *)
      die "Invalid SSH public key format. Use --public-key '<type> <key> [comment]'"
      ;;
  esac
}

normalize_options() {
  TARGET_USER="$(config_get_or_default "$TARGET_USER" "$DEFAULT_USER")"

  if [[ "$PASSWORD_AUTH_FLAGS_SET" -gt 1 ]]; then
    die "Use only one of --with-password-auth or --disable-password-auth"
  fi

  if [[ -n "$PASSWORD_AUTH_MODE" ]]; then
    PASSWORD_AUTH_MODE="$(normalize_yes_no "$PASSWORD_AUTH_MODE")" || die "Invalid password auth mode"
  else
    PASSWORD_AUTH_MODE="$(normalize_yes_no "$DEFAULT_ALLOW_PASSWORD_AUTH")" || die "Invalid DEFAULT_ALLOW_PASSWORD_AUTH"
  fi

  if [[ "$PUBLIC_KEY_FLAGS_SET" -gt 1 ]]; then
    die "Use only one of --public-key or --public-key-file"
  fi

  if [[ -z "$SSH_PUBLIC_KEY" && -n "$SSH_PUBLIC_KEY_FILE" ]]; then
    SSH_PUBLIC_KEY="$(read_public_key_file "$SSH_PUBLIC_KEY_FILE")"
  fi

  if [[ -z "$SSH_PUBLIC_KEY" && -n "${DEFAULT_ADMIN_PUBLIC_KEY_FILE:-}" ]]; then
    SSH_PUBLIC_KEY="$(read_public_key_file "$DEFAULT_ADMIN_PUBLIC_KEY_FILE")"
  fi

  if [[ -z "$SSH_PUBLIC_KEY" && -n "${DEFAULT_ADMIN_PUBLIC_KEY:-}" ]]; then
    SSH_PUBLIC_KEY="$DEFAULT_ADMIN_PUBLIC_KEY"
  fi

  if [[ -n "$SSH_PUBLIC_KEY" ]]; then
    validate_public_key_format "$SSH_PUBLIC_KEY"
  elif ! is_yes "$ALLOW_WITHOUT_PUBLIC_KEY"; then
    die "Missing SSH public key. Provide --public-key/--public-key-file or pass --allow-without-public-key explicitly."
  fi
}

precheck_os() {
  log_step "Validating operating system"

  [[ -f /etc/os-release ]] || abort "Missing /etc/os-release"

  # shellcheck disable=SC1091
  source /etc/os-release

  [[ "${ID:-}" == "ubuntu" ]] || abort "Unsupported distro: ${ID:-unknown}"
  log_ok "Ubuntu detected: ${PRETTY_NAME:-unknown}"
}

precheck_environment() {
  log_step "Validating execution environment"

  require_root
  command_exists apt-get || abort "apt-get not available"
  log_ok "apt-get available"
}

validate_key_only_prereq() {
  local auth_keys

  if [[ "$PASSWORD_AUTH_MODE" != "no" ]]; then
    return 0
  fi

  auth_keys="$(require_nonempty_authorized_keys "$TARGET_USER")"

  log_ok "Key-only prerequisite satisfied for $TARGET_USER ($auth_keys)"
}

confirm_plan() {
  if is_yes "$NON_INTERACTIVE"; then
    return 0
  fi

  printf '\n'
  printf 'This will initialize the VPS with the following baseline:\n'
  printf '  User:             %s\n' "$TARGET_USER"
  printf '  Timezone:         %s\n' "${TARGET_TIMEZONE:-<unchanged>}"
  printf '  Password auth:    %s\n' "$PASSWORD_AUTH_MODE"
  printf '  Docker install:   %s\n' "$(if is_yes "$SKIP_DOCKER"; then printf 'no'; else printf 'yes'; fi)"
  printf '  Public key:       %s\n' "$(if [[ -n "$SSH_PUBLIC_KEY" ]]; then printf 'configured'; else printf 'not configured (explicit override)'; fi)"
  printf '  Root login SSH:   no\n'
  printf '  UFW ports:        22, 80, 443\n'
  printf '\n'

  read -r -p "Continue? [y/N]: " answer
  case "$answer" in
    y|Y|yes|YES)
      ;;
    *)
      printf 'Aborted.\n'
      exit 0
      ;;
  esac
}

maybe_set_timezone() {
  if [[ -z "$TARGET_TIMEZONE" ]]; then
    log_info "Timezone unchanged"
    return 0
  fi

  log_step "Configuring timezone"
  timedatectl set-timezone "$TARGET_TIMEZONE" || abort "Failed to set timezone to $TARGET_TIMEZONE"
  log_ok "Timezone set to $TARGET_TIMEZONE"
}

write_report_if_requested() {
  [[ -n "$REPORT_FILE" ]] || return 0

  write_text_file "$REPORT_FILE" \
    "init-vps report" \
    "timestamp=$(current_timestamp)" \
    "target_user=$TARGET_USER" \
    "timezone=${TARGET_TIMEZONE:-unchanged}" \
    "password_auth=$PASSWORD_AUTH_MODE" \
    "docker_installed=$(if is_yes "$SKIP_DOCKER"; then printf 'no'; else printf 'yes'; fi)" \
    "ssh_public_key_installed=$(if [[ -n "$SSH_PUBLIC_KEY" ]]; then printf 'yes'; else printf 'no'; fi)"

  log_ok "Report written to $REPORT_FILE"
}

print_summary() {
  cat <<EOF

=== init-vps summary ===
User:              $TARGET_USER
Timezone:          ${TARGET_TIMEZONE:-unchanged}
Password auth:     $PASSWORD_AUTH_MODE
Docker installed:  $(if is_yes "$SKIP_DOCKER"; then printf 'no'; else printf 'yes'; fi)
Public key ready:  $(if [[ -n "$SSH_PUBLIC_KEY" ]]; then printf 'yes'; else printf 'no (explicit override)'; fi)
Report file:       ${REPORT_FILE:-stdout only}

Next recommended steps:
  1. Validate SSH login as $TARGET_USER using key auth
  2. Run: ./bin/audit-vps
  3. Run: ./bin/harden-vps only after key-login validation
EOF
}

main() {
  load_defaults "$REPO_ROOT/config/defaults.env"
  parse_args "$@"
  normalize_options

  log_debug "Framework root: $REPO_ROOT"
  log_debug "Target user: $TARGET_USER"

  precheck_os
  precheck_environment
  confirm_plan

  ensure_user "$TARGET_USER"
  if [[ -n "$SSH_PUBLIC_KEY" ]]; then
    ensure_user_ssh_access "$TARGET_USER" "$SSH_PUBLIC_KEY"
  else
    log_warn "Init executed without installing SSH public key (--allow-without-public-key)"
  fi
  validate_key_only_prereq
  ensure_standard_dirs "$TARGET_USER"
  install_base_packages
  maybe_set_timezone
  configure_ssh "$PASSWORD_AUTH_MODE"
  configure_ufw

  if is_yes "$SKIP_DOCKER"; then
    log_info "Skipping Docker installation by request"
  else
    install_docker_stack "$TARGET_USER"
  fi

  write_report_if_requested
  print_summary
}

main "$@"
