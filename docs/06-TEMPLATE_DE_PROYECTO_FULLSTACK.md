# Template de proyecto full stack

## Objetivo

Todo proyecto nuevo debe nacer con una estructura uniforme para reducir decisiones repetidas y evitar desorden operativo.

## Ruta objetivo

```text
/home/alex/apps/NOMBRE_PROYECTO
```

## Estructura minima esperada

```text
/home/alex/apps/NOMBRE_PROYECTO/
|-- api/
|   |-- app/
|   |-- requirements.txt
|   `-- Dockerfile
|-- caddy/
|   `-- Caddyfile
|-- postgres/
|   `-- data/
|-- n8n/
|   `-- data/
|-- backups/
|-- env/
|   |-- .env.example
|   |-- .env.dev
|   `-- .env.prod
|-- scripts/
|   |-- up.sh
|   |-- down.sh
|   |-- logs.sh
|   |-- backup.sh
|   `-- restore.sh
|-- docker-compose.yml
|-- compose.override.yml
|-- Makefile
`-- README.md
```

## Stack base

- API en FastAPI
- PostgreSQL en contenedor
- n8n en contenedor
- Caddy como proxy

## Naming estandar

### Proyecto

- nombre simple
- minusculas
- sin espacios
- sin caracteres raros

### Contenedores

- `proyecto_api`
- `proyecto_db`
- `proyecto_n8n`
- `proyecto_caddy`

### Red

- `proyecto_net`

## Variables base

- `PROJECT_NAME`
- `API_PORT`
- `POSTGRES_PORT`
- `N8N_PORT`
- `CADDY_HTTP_PORT`
- `CADDY_HTTPS_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DOMAIN_NAME`

## Politica de envs

- versionar solo `.env.example`
- no versionar `.env.dev`
- no versionar `.env.prod`
- separar defaults de secretos reales

## Politica de volumenes

Persistencia minima esperada:

- datos de PostgreSQL
- datos de n8n
- backups del proyecto

## Politica de backups

- cada proyecto debe contemplar backup diario desde el inicio
- los nombres de backup deben incluir timestamp
- la restauracion basica debe estar contemplada en scripts o runbook

## Scripts operativos del proyecto

Cada proyecto debe incluir scripts simples para:

- subir stack
- bajar stack
- ver logs
- generar backup
- restaurar backup basico

## Resultado esperado

`new-project` debe poder generar esta estructura sin decisiones manuales de ultimo momento.
