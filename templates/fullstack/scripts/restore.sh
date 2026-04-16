#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
BACKUP_PATH="${2:-}"
TARGET="${3:-all}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }
test -n "$BACKUP_PATH" || { echo "Usage: ./scripts/restore.sh <env> <backup-file-or-dir> [all|app|n8n]" >&2; exit 1; }
test -e "$BACKUP_PATH" || { echo "Missing backup path: $BACKUP_PATH" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

restore_file() {
  local dump_file="$1"
  local db_user="$2"
  local db_name="$3"
  test -f "$dump_file" || { echo "Missing dump file: $dump_file" >&2; exit 1; }
  cat "$dump_file" | docker compose --env-file "$ENV_FILE" exec -T db \
    psql -v ON_ERROR_STOP=1 -U "$db_user" -d "$db_name"
}

if [[ -d "$BACKUP_PATH" ]]; then
  APP_DUMP="$BACKUP_PATH/app_db.sql"
  N8N_DUMP="$BACKUP_PATH/n8n_db.sql"
else
  APP_DUMP="$BACKUP_PATH"
  N8N_DUMP="$BACKUP_PATH"
fi

case "$TARGET" in
  all)
    if [[ ! -d "$BACKUP_PATH" ]]; then
      echo "Target 'all' requiere un directorio de backup con app_db.sql y n8n_db.sql" >&2
      exit 1
    fi
    restore_file "$APP_DUMP" "$APP_DB_USER" "$APP_DB_NAME"
    restore_file "$N8N_DUMP" "$N8N_DB_USER" "$N8N_DB_NAME"
    ;;
  app)
    restore_file "$APP_DUMP" "$APP_DB_USER" "$APP_DB_NAME"
    ;;
  n8n)
    restore_file "$N8N_DUMP" "$N8N_DB_USER" "$N8N_DB_NAME"
    ;;
  *)
    echo "Invalid target '$TARGET'. Use all, app or n8n." >&2
    exit 1
    ;;
esac

echo "Restore completed from: $BACKUP_PATH (target: $TARGET)"
