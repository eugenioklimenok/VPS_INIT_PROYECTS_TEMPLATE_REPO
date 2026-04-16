# TDD Técnico Completo - VPS_INIT_PROYECTS_TEMPLATE_REPO (v1.1)

## 1. Objetivo

Definir el diseño técnico operativo del framework para:

1. preparar un VPS Ubuntu
2. generar un proyecto fullstack estándar
3. desplegar, auditar y respaldar el proyecto de forma repetible

Este documento reemplaza el baseline anterior y fija como regla obligatoria:

- **n8n usa PostgreSQL siempre**
- **SQLite no es opción válida para n8n**

## 2. Arquitectura general

El framework se organiza en dos bloques.

### 2.1 Bloque host

- `audit-vps`: auditoría read-only del host
- `init-vps`: bootstrap inicial del host
- `harden-vps`: hardening adicional de seguridad

### 2.2 Bloque proyecto

- `new-project`: genera scaffold fullstack
- `deploy-project`: valida y despliega stack
- `audit-project`: audita estructura + runtime + backups
- `backup-project`: genera dumps y artefactos de respaldo

## 3. Stack del proyecto generado

- API: FastAPI
- Proxy/edge: Caddy
- Workflows: n8n
- DB: PostgreSQL (único servicio por proyecto)
- Orquestación: Docker Compose

## 4. Modelo de persistencia (v1.1)

Cada proyecto tiene un único servicio PostgreSQL (`db`) y dos bases lógicas:

- DB de app:
  - `APP_DB_NAME`
  - `APP_DB_USER`
  - `APP_DB_PASSWORD`
- DB de n8n:
  - `N8N_DB_NAME`
  - `N8N_DB_USER`
  - `N8N_DB_PASSWORD`

Además, se define un usuario admin de bootstrap:

- `POSTGRES_ADMIN_USER`
- `POSTGRES_ADMIN_PASSWORD`

El bootstrap inicial de DB/roles se hace en primer arranque con:

- `postgres/init/01-bootstrap-multi-db.sql`

## 5. Variables de entorno estándar

Variables obligatorias en `env/.env.dev` y `env/.env.prod`:

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
- `SECRET_KEY`

## 6. Política `.env`

- Se versiona:
  - `env/.env.example`
- No se versiona:
  - `env/.env.dev`
  - `env/.env.prod`
- Objetivo:
  - evitar secretos reales en Git
  - mantener template reutilizable

Inicialización recomendada por proyecto:

```bash
cp env/.env.example env/.env.dev
cp env/.env.example env/.env.prod
```

Luego ajustar credenciales y dominio reales.

## 7. Contrato técnico de comandos

## 7.1 `new-project`

Genera proyecto completo desde `templates/fullstack`.

Responsabilidades:

- validar nombre de proyecto y puertos
- resolver placeholders
- generar envs (`.env.example`, `.env.dev`, `.env.prod`)
- definir DB app + DB n8n
- dejar scripts operativos listos

Salida:

- árbol de proyecto en `<base-path>/<project_name>`

## 7.2 `deploy-project`

Fases:

1. validar layout y env
2. validar Docker/Compose
3. preflight de puertos host
4. `docker compose up -d` (con `--build` por defecto)
5. checks de salud HTTP

Reglas de puertos:

- bloquea puertos ocupados por procesos externos
- permite redeploy cuando puertos ya están ocupados por el mismo proyecto

## 7.3 `audit-project`

Chequea:

- archivos/directorios requeridos
- variables env obligatorias
- placeholders sin resolver
- estado de contenedores
- checks HTTP (`root`, `health`, `n8n`)
- existencia/frescura de backups

## 7.4 `backup-project`

Genera artefactos en `<project>/backups` (o `--output-dir`):

- dump app DB: `*_app_pg_<timestamp>.sql.gz`
- dump n8n DB: `*_n8n_pg_<timestamp>.sql.gz`
- config archive: `*_config_<timestamp>.tar.gz`
- manifest: `*_manifest_<timestamp>.json`

El manifest incluye:

- proyecto
- entorno
- timestamp UTC
- metadata de DB app y DB n8n
- lista de archivos creados

## 8. Estructura esperada del proyecto generado

```text
<project>/
|-- api/
|   |-- app/main.py
|   |-- requirements.txt
|   `-- Dockerfile
|-- backups/
|-- caddy/
|   `-- Caddyfile
|-- env/
|   |-- .env.example
|   |-- .env.dev
|   `-- .env.prod
|-- n8n/
|-- postgres/
|   |-- .gitkeep
|   `-- init/
|       `-- 01-bootstrap-multi-db.sql
|-- scripts/
|   |-- up.sh
|   |-- down.sh
|   |-- logs.sh
|   |-- backup.sh
|   `-- restore.sh
|-- docker-compose.yml
|-- compose.override.yml
`-- Makefile
```

## 9. Flujo Git recomendado

Separación obligatoria:

1. Repo framework/template (este repo)
2. Repo de cada proyecto generado (nuevo remoto independiente)

No mezclar commits del proyecto real en el repo del framework.

Flujo para nacimiento de repo de proyecto:

```bash
cd /home/alex/apps/<project>
rm -rf .git
git init
git add -A
git commit -m "Initial scaffold from framework"
git branch -M main
git remote add origin <repo_proyecto>
git push -u origin main
```

## 10. Seguridad y hardening

Bloque host aporta baseline:

- UFW activo con puertos requeridos
- SSH endurecido en `init-vps`
- hardening adicional en `harden-vps`

Bloque proyecto:

- secretos fuera de Git (`.env.dev/.env.prod`)
- servicios containerizados
- validaciones antes de deploy

## 11. Criterios de aceptación v1.1

Se considera correcto cuando:

1. `new-project` genera envs y placeholders sin inconsistencias
2. `deploy-project --validate-only` pasa
3. `deploy-project` levanta stack y checks mínimos
4. `audit-project` refleja estado real sin contradicciones
5. `backup-project` genera dumps de app DB y n8n DB
6. no existe configuración de n8n con SQLite

## 12. Regla innegociable

En este framework:

- **n8n no usa SQLite**
- **n8n usa PostgreSQL siempre**
