# __PROJECT_NAME__

Proyecto full stack generado desde el template oficial del framework.

## Stack

- FastAPI
- PostgreSQL
- n8n
- Caddy

## Estructura

```text
__PROJECT_NAME__/
|-- api/
|-- backups/
|-- caddy/
|-- env/
|-- n8n/
|-- postgres/
|-- scripts/
|-- compose.override.yml
|-- docker-compose.yml
`-- Makefile
```

## Variables del proyecto

Este proyecto se genera a partir de placeholders del framework.

Placeholders principales:

- `__PROJECT_NAME__`
- `__DOMAIN_NAME__`
- `__API_PORT__`
- `__POSTGRES_PORT__`
- `__N8N_PORT__`
- `__CADDY_HTTP_PORT__`
- `__CADDY_HTTPS_PORT__`
- `__POSTGRES_DB__`
- `__POSTGRES_USER__`
- `__POSTGRES_PASSWORD__`
- `__N8N_BASIC_AUTH_USER__`
- `__N8N_BASIC_AUTH_PASSWORD__`
- `__SECRET_KEY__`

## Primer uso

1. Revisar `env/.env.dev` y `env/.env.prod`
2. Ajustar `__DOMAIN_NAME__` y credenciales reales
3. Levantar el stack con `make up`
4. Validar servicios con `make ps` y `make logs`

## Scripts operativos

- `scripts/up.sh`
- `scripts/down.sh`
- `scripts/logs.sh`
- `scripts/backup.sh`
- `scripts/restore.sh`

## Notas

- `env/.env.example` se versiona
- `env/.env.dev` y `env/.env.prod` no deben versionarse en proyectos reales
- n8n usa PostgreSQL del stack (no SQLite)
- la persistencia de PostgreSQL y n8n usa volumenes Docker nombrados (`postgres_data`, `n8n_data`)
- la carpeta `backups` es persistente a nivel proyecto
