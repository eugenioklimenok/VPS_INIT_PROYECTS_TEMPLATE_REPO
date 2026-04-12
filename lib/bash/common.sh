#!/usr/bin/env bash

if [[ -n "${VPS_FRAMEWORK_COMMON_SH_LOADED:-}" ]]; then
  return 0
fi
readonly VPS_FRAMEWORK_COMMON_SH_LOADED="1"

framework_repo_root() {
  local source_path
  source_path="${BASH_SOURCE[0]}"
  cd "$(dirname "$source_path")/../.." >/dev/null 2>&1 && pwd
}

FRAMEWORK_ROOT="$(framework_repo_root)"

current_timestamp() {
  date '+%Y-%m-%d %H:%M:%S'
}

timestamp_compact() {
  date '+%Y%m%d_%H%M%S'
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

package_installed() {
  dpkg -s "$1" >/dev/null 2>&1
}

abort() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 2
}

die() {
  printf '[FAIL] %s\n' "$*" >&2
  exit 3
}

require_root() {
  [[ "${EUID:-$(id -u)}" -eq 0 ]] || abort "This command must run as root or via sudo"
}

ensure_parent_dir() {
  local target="$1"
  local parent
  parent="$(dirname "$target")"
  [[ -d "$parent" ]] || mkdir -p "$parent" || abort "Failed to create parent directory: $parent"
}

write_text_file() {
  local target="$1"
  shift
  ensure_parent_dir "$target"
  printf '%s\n' "$@" > "$target" || abort "Failed to write file: $target"
}

safe_hostname() {
  if command_exists hostnamectl; then
    hostnamectl --static 2>/dev/null && return 0
  fi

  hostname 2>/dev/null || echo "unknown"
}

safe_timezone() {
  if command_exists timedatectl; then
    local tz
    tz="$(timedatectl show --property=Timezone --value 2>/dev/null || true)"
    if [[ -n "$tz" ]]; then
      printf '%s\n' "$tz"
      return 0
    fi
  fi

  if [[ -f /etc/timezone ]]; then
    cat /etc/timezone
    return 0
  fi

  echo "unknown"
}

normalize_yes_no() {
  case "${1:-}" in
    yes|y|true|1|on)
      printf 'yes\n'
      ;;
    no|n|false|0|off)
      printf 'no\n'
      ;;
    *)
      return 1
      ;;
  esac
}

is_yes() {
  [[ "${1:-}" == "yes" ]]
}

join_by() {
  local delimiter="$1"
  shift
  local first="yes"
  local value

  for value in "$@"; do
    if [[ "$first" == "yes" ]]; then
      printf '%s' "$value"
      first="no"
    else
      printf '%s%s' "$delimiter" "$value"
    fi
  done
}

config_get_or_default() {
  local value="$1"
  local default_value="$2"

  if [[ -n "$value" ]]; then
    printf '%s\n' "$value"
  else
    printf '%s\n' "$default_value"
  fi
}

resolve_user_home() {
  local user="$1"
  local passwd_entry

  passwd_entry="$(getent passwd "$user" 2>/dev/null || true)"
  [[ -n "$passwd_entry" ]] || return 1

  printf '%s\n' "$passwd_entry" | cut -d: -f6
}

authorized_keys_path_for_user() {
  local user="$1"
  local home_dir

  home_dir="$(resolve_user_home "$user")" || return 1
  printf '%s/.ssh/authorized_keys\n' "$home_dir"
}

require_nonempty_authorized_keys() {
  local user="$1"
  local auth_keys

  auth_keys="$(authorized_keys_path_for_user "$user")" || abort "Cannot resolve home directory for $user"

  if [[ ! -s "$auth_keys" ]]; then
    abort "Refusing to continue without a non-empty authorized_keys for $user"
  fi

  printf '%s\n' "$auth_keys"
}

load_defaults() {
  local cfg="${1:-$FRAMEWORK_ROOT/config/defaults.env}"

  if [[ -f "$cfg" ]]; then
    # shellcheck disable=SC1090
    source "$cfg"
  fi

  DEFAULT_USER="${DEFAULT_USER:-alex}"
  DEFAULT_HOME_BASE="${DEFAULT_HOME_BASE:-/home}"
  DEFAULT_APPS_DIR="${DEFAULT_APPS_DIR:-$DEFAULT_HOME_BASE/$DEFAULT_USER/apps}"
  DEFAULT_REPOS_DIR="${DEFAULT_REPOS_DIR:-$DEFAULT_HOME_BASE/$DEFAULT_USER/repos}"
  DEFAULT_BACKUPS_DIR="${DEFAULT_BACKUPS_DIR:-$DEFAULT_HOME_BASE/$DEFAULT_USER/backups}"
  DEFAULT_SCRIPTS_DIR="${DEFAULT_SCRIPTS_DIR:-$DEFAULT_HOME_BASE/$DEFAULT_USER/scripts}"
  DEFAULT_TIMEZONE="${DEFAULT_TIMEZONE:-UTC}"
  DEFAULT_ALLOW_PASSWORD_AUTH="${DEFAULT_ALLOW_PASSWORD_AUTH:-yes}"
  DEFAULT_PERMIT_ROOT_LOGIN="${DEFAULT_PERMIT_ROOT_LOGIN:-no}"
  DEFAULT_PUBKEY_AUTH="${DEFAULT_PUBKEY_AUTH:-yes}"
  DEFAULT_REQUIRED_PORTS="${DEFAULT_REQUIRED_PORTS:-22 80 443}"
  DEFAULT_REQUIRED_PACKAGES="${DEFAULT_REQUIRED_PACKAGES:-curl wget git ca-certificates gnupg lsb-release unzip tar gzip rsync nano}"
  DEFAULT_REPORTS_DIR="${DEFAULT_REPORTS_DIR:-$FRAMEWORK_ROOT/reports}"
}
