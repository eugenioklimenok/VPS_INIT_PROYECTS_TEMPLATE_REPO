# TDD Tecnico Completo - VPS_INIT_PROYECTS_TEMPLATE_REPO (v1.1)

## 1. Objetivo

Estandarizar un flujo reproducible para:

1. preparar VPS Ubuntu
2. generar proyecto fullstack base
3. desplegar, auditar y respaldar en forma operativa

Regla obligatoria:

- n8n usa PostgreSQL siempre
- SQLite queda fuera del runtime activo

## 2. Arquitectura

### Bloque host

- `audit-vps`
- `init-vps`
- `harden-vps`

Nota de ejecucion:
- `audit-vps` funciona tanto como ejecutable (`./bin/audit-vps`) como invocado por Python (`python3 ./bin/audit-vps`).

### Bloque proyecto

- `new-project`
- `deploy-project`
- `audit-project`
- `backup-project`

## 3. Stack del proyecto generado

- FastAPI
- PostgreSQL
- n8n
- Caddy
- Docker Compose

## 4. Modelo de base de datos

Un servicio PostgreSQL (`db`) por proyecto con separacion logica:

- DB app: `APP_DB_NAME`, `APP_DB_USER`, `APP_DB_PASSWORD`
- DB n8n: `N8N_DB_NAME`, `N8N_DB_USER`, `N8N_DB_PASSWORD`
- usuario admin de bootstrap: `POSTGRES_ADMIN_USER`, `POSTGRES_ADMIN_PASSWORD`

Creacion inicial automatica:

- `postgres/init/01-bootstrap-multi-db.sql` en `docker-entrypoint-initdb.d`
- crea usuarios de app y n8n
- crea bases app y n8n
- asigna ownership y grants

## 5. Variables env obligatorias

- `PROJECT_NAME`
- `APP_ENV`
- `TIMEZONE`
- `DOMAIN_NAME`
- `API_PORT`
- `POSTGRES_PORT`
- `N8N_PORT`
- `CADDY_HTTP_PORT`
- `CADDY_HTTPS_PORT`
- `POSTGRES_ADMIN_USER`
- `POSTGRES_ADMIN_PASSWORD`
- `APP_DB_NAME`
- `APP_DB_USER`
- `APP_DB_PASSWORD`
- `N8N_DB_NAME`
- `N8N_DB_USER`
- `N8N_DB_PASSWORD`
- `N8N_PROTOCOL`
- `N8N_BASE_URL`
- `N8N_BASIC_AUTH_USER`
- `N8N_BASIC_AUTH_PASSWORD`
- `N8N_SECURE_COOKIE`
- `SECRET_KEY`

Politica:

- se versiona: `env/.env.example`
- no se versiona: `env/.env.dev`, `env/.env.prod`
- regla de dominio dev: `new-project --domain` se materializa tambien en `.env.dev`
- regla cookie n8n:
  - dev/lab HTTP: `N8N_SECURE_COOKIE=false`
  - prod/HTTPS: `N8N_SECURE_COOKIE=true`

## 6. Contrato de comandos (resumen)

### `new-project`

- valida nombre/puertos
- materializa template
- resuelve placeholders
- genera `.env.example`, `.env.dev`, `.env.prod`
- genera bootstrap SQL con valores renderizados

### `deploy-project`

Pre-deploy:

- estructura y env requeridos
- placeholders resueltos
- puertos validos y sin conflicto externo
- disponibilidad Docker/Compose

Deploy:

- `docker compose up -d` (`--build` por defecto)

Post-deploy:

- servicios esperados running
- `db` responde ready (`pg_isready`)
- APP_DB y N8N_DB existen en PostgreSQL
- checks HTTP de root, health API y `/n8n/`
- en dev/lab: root y `/n8n/` por HTTP sin redirect HTTPS forzado desde Caddy

### `audit-project`

- valida estructura/env/placeholders
- valida estado runtime (si no se omite):
  - contenedores running
  - db ready
  - existencia de APP_DB y N8N_DB
  - checks HTTP
- valida existencia/frescura de backups

### `backup-project`

Genera por corrida:

- `backups/YYYYMMDD_HHMM/app_db.sql`
- `backups/YYYYMMDD_HHMM/n8n_db.sql`
- `backups/YYYYMMDD_HHMM/config.tar.gz`
- `backups/YYYYMMDD_HHMM/metadata.json`

## 7. Restore

`scripts/restore.sh` soporta:

- restore total desde carpeta de corrida (`all`)
- restore individual de `app` o `n8n`
- modo limpio recomendado (`--clean`) para recovery reproducible:
  - termina conexiones activas
  - drop/recreate DB target con owner correcto
  - restaura dump con `ON_ERROR_STOP=1`

Uso:

```bash
./scripts/restore.sh <env> <backup-file-or-dir> [all|app|n8n] [--clean]
```

## 8. Estructura esperada del proyecto

```text
<project>/
|-- api/
|-- backups/
|-- caddy/
|-- env/
|-- n8n/
|-- postgres/
|   `-- init/01-bootstrap-multi-db.sql
|-- scripts/
|-- docker-compose.yml
|-- compose.override.yml
`-- Makefile
```

## 9. Flujo operativo recomendado

Referencia ejecutable:

- `README.md` (runbook de primer deploy)

## 10. Criterios de aceptacion v1.1

1. n8n corre sobre PostgreSQL
2. APP y N8N tienen DB separadas
3. deploy valida runtime real (incluyendo DB existence)
4. backup cubre ambas DB
5. restore es consistente con el formato de backup
