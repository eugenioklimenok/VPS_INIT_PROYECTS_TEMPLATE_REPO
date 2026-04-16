# __PROJECT_NAME__

Proyecto fullstack generado por `VPS_INIT_PROYECTS_TEMPLATE_REPO`.

## Stack

- FastAPI
- PostgreSQL
- n8n
- Caddy

## DB model

- admin bootstrap: `POSTGRES_ADMIN_USER`, `POSTGRES_ADMIN_PASSWORD`
- app DB: `APP_DB_NAME`, `APP_DB_USER`, `APP_DB_PASSWORD`
- n8n DB: `N8N_DB_NAME`, `N8N_DB_USER`, `N8N_DB_PASSWORD`

n8n usa PostgreSQL del stack (`DB_TYPE=postgresdb`), no SQLite.

## Primer uso

```bash
cp env/.env.example env/.env.dev
cp env/.env.example env/.env.prod
make up
make ps
```

## Backup

`scripts/backup.sh <env>` crea:

- `backups/YYYYMMDD_HHMM/app_db.sql`
- `backups/YYYYMMDD_HHMM/n8n_db.sql`
- `backups/YYYYMMDD_HHMM/metadata.json`

## Restore

```bash
# restore completo
./scripts/restore.sh dev backups/20260415_0130 all

# restore solo app
./scripts/restore.sh dev backups/20260415_0130/app_db.sql app

# restore solo n8n
./scripts/restore.sh dev backups/20260415_0130/n8n_db.sql n8n
```
