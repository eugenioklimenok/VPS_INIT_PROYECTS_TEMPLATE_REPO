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

## Acceso dev/lab (HTTP)

- El template dev usa Caddy en HTTP puro (sin redirect forzado a HTTPS).
- URLs esperadas en laboratorio:
  - `http://<ip-o-dominio>:<CADDY_HTTP_PORT>/`
  - `http://<ip-o-dominio>:<CADDY_HTTP_PORT>/n8n/`
- En `env/.env.dev`:
  - `N8N_PROTOCOL=http`
  - `N8N_SECURE_COOKIE=false`

Para producción HTTPS, configurar dominio real, certificados y `N8N_SECURE_COOKIE=true` (ya viene así en `.env.prod`).

## Backup

`scripts/backup.sh <env>` crea:

- `backups/YYYYMMDD_HHMM/app_db.sql`
- `backups/YYYYMMDD_HHMM/n8n_db.sql`
- `backups/YYYYMMDD_HHMM/metadata.json`

## Restore

```bash
# restore completo
./scripts/restore.sh dev backups/20260415_0130 all --clean

# restore solo app
./scripts/restore.sh dev backups/20260415_0130 app --clean

# restore solo n8n
./scripts/restore.sh dev backups/20260415_0130 n8n --clean
```
