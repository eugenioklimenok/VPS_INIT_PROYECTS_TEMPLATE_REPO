# demo-portcheck

Proyecto full stack generado desde el template oficial del framework.

## Stack

- FastAPI
- PostgreSQL
- n8n
- Caddy

## Estructura

```text
demo-portcheck/
|-- api/
|-- backups/
|-- caddy/
|-- env/
|-- n8n/
|   `-- data/
|-- postgres/
|   `-- data/
|-- scripts/
|-- compose.override.yml
|-- docker-compose.yml
`-- Makefile
```

## Variables del proyecto

Este proyecto se genera a partir de placeholders del framework.

Placeholders principales:

- `demo-portcheck`
- `localhost`
- `18000`
- `15432`
- `15678`
- `18080`
- `18443`
- `demo_portcheck`
- `demo_portcheck`
- `4bAGXT1Dbi5vLwbf_NXxjGNW`
- `admin`
- `-zd9HFOMFAxPqKQ0cQ`
- `liB7H-UAWpz_la8uQLp3pIZxN9AhVk4J`

## Primer uso

1. Revisar `env/.env.dev` y `env/.env.prod`
2. Ajustar `localhost` y credenciales reales
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
- los directorios `postgres/data`, `n8n/data` y `backups` son persistentes
