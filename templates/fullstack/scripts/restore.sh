#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
BACKUP_PATH="${2:-}"
TARGET="${3:-all}"
MODE_FLAG="${4:-}"
ENV_FILE="env/.env.${ENVIRONMENT}"
IS_CLEAN_MODE="no"

if [[ "$MODE_FLAG" == "--clean" ]]; then
  IS_CLEAN_MODE="yes"
elif [[ -n "$MODE_FLAG" ]]; then
  echo "Invalid mode '$MODE_FLAG'. Supported: --clean" >&2
  exit 1
fi

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }
test -n "$BACKUP_PATH" || { echo "Usage: ./scripts/restore.sh <env> <backup-file-or-dir> [all|app|n8n] [--clean]" >&2; exit 1; }
test -e "$BACKUP_PATH" || { echo "Missing backup path: $BACKUP_PATH" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

compose_db_exec() {
  docker compose --env-file "$ENV_FILE" exec -T db "$@"
}

check_required_env() {
  local keys=(
    "POSTGRES_ADMIN_USER"
    "APP_DB_NAME"
    "APP_DB_USER"
    "N8N_DB_NAME"
    "N8N_DB_USER"
  )
  local key
  for key in "${keys[@]}"; do
    if [[ -z "${!key:-}" ]]; then
      echo "Missing required env key: $key" >&2
      exit 1
    fi
  done
}

validate_target() {
  case "$TARGET" in
    all|app|n8n) ;;
    *)
      echo "Invalid target '$TARGET'. Use all, app or n8n." >&2
      exit 1
      ;;
  esac
}

terminate_connections() {
  local db_name="$1"
  echo "[STEP] Terminating active connections for DB '$db_name'"
  compose_db_exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_ADMIN_USER" -d postgres \
    -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${db_name}' AND pid <> pg_backend_pid();"
}

drop_and_recreate_database() {
  local db_name="$1"
  local db_owner="$2"
  echo "[STEP] Recreating DB '$db_name' with owner '$db_owner'"
  compose_db_exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_ADMIN_USER" -d postgres \
    -c "DROP DATABASE IF EXISTS \"${db_name}\";"
  compose_db_exec psql -v ON_ERROR_STOP=1 -U "$POSTGRES_ADMIN_USER" -d postgres \
    -c "CREATE DATABASE \"${db_name}\" OWNER \"${db_owner}\";"
}

restore_file() {
  local dump_file="$1"
  local db_owner="$2"
  local db_name="$3"
  test -f "$dump_file" || { echo "Missing dump file: $dump_file" >&2; exit 1; }
  if [[ "$IS_CLEAN_MODE" == "yes" ]]; then
    terminate_connections "$db_name"
    drop_and_recreate_database "$db_name" "$db_owner"
  fi
  echo "[STEP] Restoring dump '$dump_file' into DB '$db_name'"
  cat "$dump_file" | compose_db_exec psql -v ON_ERROR_STOP=1 -U "$db_owner" -d "$db_name"
}

if [[ -d "$BACKUP_PATH" ]]; then
  APP_DUMP="$BACKUP_PATH/app_db.sql"
  N8N_DUMP="$BACKUP_PATH/n8n_db.sql"
else
  APP_DUMP="$BACKUP_PATH"
  N8N_DUMP="$BACKUP_PATH"
fi

check_required_env
validate_target

if [[ "$TARGET" == "all" && ! -d "$BACKUP_PATH" ]]; then
  echo "Target 'all' requiere un directorio de backup con app_db.sql y n8n_db.sql" >&2
  exit 1
fi

echo "[STEP] Restore mode: ${IS_CLEAN_MODE}"
echo "[STEP] Backup source: ${BACKUP_PATH}"
echo "[STEP] Target: ${TARGET}"

if [[ "$TARGET" == "all" || "$TARGET" == "app" ]]; then
  restore_file "$APP_DUMP" "$APP_DB_USER" "$APP_DB_NAME"
fi
if [[ "$TARGET" == "all" || "$TARGET" == "n8n" ]]; then
  restore_file "$N8N_DUMP" "$N8N_DB_USER" "$N8N_DB_NAME"
fi

echo "Restore completed from: $BACKUP_PATH (target: $TARGET, clean: $IS_CLEAN_MODE)"
