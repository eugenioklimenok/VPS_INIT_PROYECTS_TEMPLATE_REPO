#!/usr/bin/env bash
set -euo pipefail

ENVIRONMENT="${1:-dev}"
ENV_FILE="env/.env.${ENVIRONMENT}"

test -f "$ENV_FILE" || { echo "Missing env file: $ENV_FILE" >&2; exit 1; }

set -a
source "$ENV_FILE"
set +a

TIMESTAMP="$(date -u '+%Y%m%d_%H%M')"
RUN_DIR="backups/${TIMESTAMP}"
APP_BACKUP_FILE="${RUN_DIR}/app_db.sql"
N8N_BACKUP_FILE="${RUN_DIR}/n8n_db.sql"
CONFIG_BACKUP_FILE="${RUN_DIR}/config.tar.gz"
METADATA_FILE="${RUN_DIR}/metadata.json"

mkdir -p "$RUN_DIR"

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "$APP_DB_USER" -d "$APP_DB_NAME" > "$APP_BACKUP_FILE"

docker compose --env-file "$ENV_FILE" exec -T db \
  pg_dump -U "$N8N_DB_USER" -d "$N8N_DB_NAME" > "$N8N_BACKUP_FILE"

tar -czf "$CONFIG_BACKUP_FILE" \
  docker-compose.yml \
  compose.override.yml \
  Makefile \
  caddy/Caddyfile \
  env/.env.example \
  "$ENV_FILE"

cat > "$METADATA_FILE" <<EOF
{
  "project_name": "${PROJECT_NAME}",
  "created_at_utc": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "databases": {
    "app": {"name": "${APP_DB_NAME}", "user": "${APP_DB_USER}"},
    "n8n": {"name": "${N8N_DB_NAME}", "user": "${N8N_DB_USER}"}
  },
  "files": [
    "app_db.sql",
    "n8n_db.sql",
    "config.tar.gz",
    "metadata.json"
  ]
}
EOF

echo "Backup created: $APP_BACKUP_FILE"
echo "Backup created: $N8N_BACKUP_FILE"
echo "Backup created: $CONFIG_BACKUP_FILE"
echo "Backup created: $METADATA_FILE"
