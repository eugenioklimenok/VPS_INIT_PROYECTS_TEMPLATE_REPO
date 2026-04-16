# TDD Tecnico Completo - VPS_INIT_PROYECTS_TEMPLATE_REPO

## 1. Objetivo del documento

Este documento consolida el diseno tecnico implementado del framework `VPS_INIT_PROYECTS_TEMPLATE_REPO`.

Su objetivo es dejar documentado, en un unico lugar:

- que componentes existen
- que comandos fueron implementados
- que stack tecnico genera el template
- como se configura
- que puertos usa por default
- que valida cada comando
- como operar y administrar un VPS y los proyectos generados desde este framework

Este TDD describe el estado real implementado al cierre de `v1.0.0`.

## 2. Alcance del framework

El framework cubre dos bloques funcionales claramente separados.

### 2.1 Bloque host

Responsable de preparar y auditar un VPS Ubuntu:

- `audit-vps`
- `init-vps`
- `harden-vps`

### 2.2 Bloque proyecto

Responsable de generar, desplegar, auditar y respaldar proyectos creados desde template:

- `new-project`
- `deploy-project`
- `audit-project`
- `backup-project`

## 3. Arquitectura general

La arquitectura operativa se divide en tres capas:

1. baseline del host Ubuntu
2. scaffolding del proyecto
3. despliegue y operacion del stack

La idea central es separar claramente:

- infraestructura base del VPS
- template generador
- proyecto real generado

El repo actual es el framework/template. Los proyectos generados viven aparte, normalmente en:

- `/home/alex/apps/<nombre_proyecto>`

## 4. Stack tecnico implementado

El template `fullstack` actualmente genera un stack basado en:

- FastAPI
- PostgreSQL 16 Alpine
- n8n `1.83.2`
- Caddy `2.8-alpine`
- Docker Compose

## 5. Baseline del host esperado

El framework asume un host Ubuntu LTS con un usuario operativo estandar.

### 5.1 Usuario y rutas base por default

Defaults cargados desde `config/defaults.env`:

- `DEFAULT_USER=alex`
- `DEFAULT_HOME_BASE=/home`
- `DEFAULT_APPS_DIR=/home/alex/apps`
- `DEFAULT_REPOS_DIR=/home/alex/repos`
- `DEFAULT_BACKUPS_DIR=/home/alex/backups`
- `DEFAULT_SCRIPTS_DIR=/home/alex/scripts`
- `DEFAULT_TIMEZONE=UTC`

### 5.2 Politica base del host

Defaults funcionales:

- password auth permitido inicialmente: `yes`
- root login SSH: `no`
- pubkey auth: `yes`
- puertos requeridos: `22 80 443`

### 5.3 Paquetes base requeridos

Definidos en `config/defaults.env`:

- `curl`
- `wget`
- `git`
- `ca-certificates`
- `gnupg`
- `lsb-release`
- `unzip`
- `tar`
- `gzip`
- `rsync`
- `nano`

Adicionalmente, durante bootstrap se prepara Docker Engine + Docker Compose plugin.

## 6. Comandos del bloque host

### 6.1 `audit-vps`

Auditoria read-only del host.

Cobertura implementada:

- sistema operativo
- usuario esperado
- SSH
- UFW
- Docker
- directorios base
- paquetes base
- estado general del sistema

Importante:

- no instala nada
- no crea usuarios
- no modifica configuracion

Salidas:

- humana
- JSON
- archivo opcional con `--output`

### 6.2 `init-vps`

Bootstrap idempotente del host.

Cobertura:

- prechecks
- creacion/validacion de usuario operativo
- creacion de directorios base
- instalacion de paquetes base
- timezone opcional
- baseline SSH
- baseline UFW
- instalacion Docker y Compose

Flags principales:

- `--user`
- `--timezone`
- `--with-password-auth`
- `--disable-password-auth`
- `--skip-docker`
- `--non-interactive`
- `--report`

Proteccion relevante:

- si se pide `--disable-password-auth`, exige `authorized_keys` no vacia antes de pasar a key-only

### 6.3 `harden-vps`

Endurecimiento posterior del host, especialmente SSH.

Cobertura:

- validacion del usuario objetivo
- validacion de `authorized_keys`
- permisos de `.ssh`
- modo key-only

Objetivo:

- separar bootstrap inicial de hardening estricto

## 7. Infra comun Bash del bloque host

La capa host reutiliza componentes comunes:

- `lib/bash/common.sh`
- `lib/bash/log.sh`
- `lib/bash/results.sh`

Responsabilidades:

- carga de defaults
- helpers de sistema
- control de errores
- logging uniforme
- almacenamiento y resumen de resultados

Esto reduce duplicacion entre `audit-vps`, `init-vps` y `harden-vps`.

## 8. Comando `new-project`

`new-project` genera un proyecto fullstack desde `templates/fullstack`.

Implementado en Python:

- `lib/python/vps_init_framework/new_project.py`

### 8.1 Validaciones

- `project_name` obligatorio
- formato `kebab-case`
- dominio no vacio ni con espacios
- puertos entre `1` y `65535`
- puertos no repetidos entre si
- ruta destino no debe existir

### 8.2 Defaults funcionales

Si no se pasan flags, usa:

- dominio: `localhost`
- `API_PORT=18000`
- `POSTGRES_PORT=15432`
- `N8N_PORT=15678`
- `CADDY_HTTP_PORT=18080`
- `CADDY_HTTPS_PORT=18443`
- usuario Basic Auth de n8n: `admin`
- base path: `DEFAULT_APPS_DIR`

### 8.3 Credenciales generadas automaticamente

Si no se pasan manualmente:

- `POSTGRES_PASSWORD`
- `N8N_BASIC_AUTH_PASSWORD`
- `SECRET_KEY`

se generan automaticamente con `secrets.token_urlsafe(...)`.

### 8.4 Placeholders resueltos

El template reemplaza:

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

## 9. Estructura del proyecto generado

La estructura generada actualmente es:

```text
<project>/
|-- api/
|   |-- app/
|   |   |-- __init__.py
|   |   `-- main.py
|   |-- Dockerfile
|   `-- requirements.txt
|-- backups/
|-- caddy/
|   `-- Caddyfile
|-- env/
|   |-- .env.example
|   |-- .env.dev
|   `-- .env.prod
|-- n8n/
|-- postgres/
|-- scripts/
|   |-- up.sh
|   |-- down.sh
|   |-- logs.sh
|   |-- backup.sh
|   `-- restore.sh
|-- .gitignore
|-- compose.override.yml
|-- docker-compose.yml
|-- Makefile
`-- README.md
```

## 10. Configuracion del proyecto generado

### 10.1 Variables principales de entorno

`env/.env.dev` y `env/.env.prod` contienen:

- `PROJECT_NAME`
- `APP_ENV`
- `TIMEZONE`
- `DOMAIN_NAME`
- `API_PORT`
- `POSTGRES_PORT`
- `N8N_PORT`
- `CADDY_HTTP_PORT`
- `CADDY_HTTPS_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `N8N_PROTOCOL`
- `N8N_BASE_URL`
- `N8N_BASIC_AUTH_USER`
- `N8N_BASIC_AUTH_PASSWORD`
- `SECRET_KEY`

### 10.2 Modo dev por default

En `env.dev.template`:

- `APP_ENV=development`
- `TIMEZONE=UTC`
- `N8N_PROTOCOL=http`
- `N8N_BASE_URL=http://localhost:<CADDY_HTTP_PORT>/n8n/`

## 11. Puertos por default

Puertos publicados por default:

- API host: `18000`
- PostgreSQL host: `15432`
- n8n host: `15678`
- Caddy HTTP host: `18080`
- Caddy HTTPS host: `18443`

Puertos internos del stack:

- API contenedor: `8000`
- PostgreSQL contenedor: `5432`
- n8n contenedor: `5678`
- Caddy contenedor: `80/443`

## 12. Diseno Docker Compose

### 12.1 Servicio `api`

- se construye desde `./api`
- expone internamente `8000`
- en dev publica `API_PORT:8000` mediante `compose.override.yml`
- recibe variables de DB, `SECRET_KEY` y `N8N_BASE_URL`
- depende de `db`

### 12.2 Servicio `db`

- imagen: `postgres:16-alpine`
- publica `POSTGRES_PORT:5432`
- usa volumen nombrado `postgres_data`
- reinicio: `unless-stopped`

### 12.3 Servicio `n8n`

- imagen: `n8nio/n8n:1.83.2`
- publica `N8N_PORT:5678`
- usa volumen nombrado `n8n_data`
- path interno configurado en `/n8n/`
- Basic Auth activo
- persistencia basada en SQLite interno de n8n

### 12.4 Servicio `caddy`

- imagen: `caddy:2.8-alpine`
- publica:
  - `CADDY_HTTP_PORT:80`
  - `CADDY_HTTPS_PORT:443`
- enruta:
  - `/n8n/*` hacia `n8n:5678`
  - resto hacia `api:8000`
- usa volumenes nombrados:
  - `caddy_data`
  - `caddy_config`

## 13. Red, persistencia y aislamiento

### 13.1 Red

Cada proyecto crea su propia red Docker:

- `__PROJECT_NAME___net`

### 13.2 Persistencia

Persistencia implementada con volumenes nombrados:

- `postgres_data`
- `n8n_data`
- `caddy_data`
- `caddy_config`

Esto evita errores tipicos de bind mounts con directorios locales no vacios.

### 13.3 Separacion entre proyectos

Cada proyecto:

- vive en su propia carpeta
- usa su propia red Docker
- usa sus propios volumenes Docker
- debe usar puertos publicados distintos o una estrategia de routing compatible

## 14. `compose.override.yml` en desarrollo

El override de dev hace dos cosas:

- monta `./api/app` dentro del contenedor
- ejecuta Uvicorn con `--reload`
- publica la API hacia el host en `API_PORT`

En consecuencia:

- `docker-compose.yml` representa base comun
- `compose.override.yml` completa comportamiento de desarrollo

## 15. Diseno de routing HTTP/TLS

`Caddyfile` actual:

- comprime respuestas con `gzip`
- publica virtual host `${DOMAIN_NAME:localhost}`
- reverse proxy de `/n8n/*` a `n8n:5678`
- reverse proxy del resto a `api:8000`

### 15.1 Consideracion importante sobre `localhost` y `127.0.0.1`

En dev, el valor recomendado para `DOMAIN_NAME` es `localhost`.

Motivo:

- con `127.0.0.1` puede haber redirect HTTP `308` hacia HTTPS con comportamiento TLS no ideal para pruebas locales
- con `localhost` el flujo TLS local via Caddy es mas consistente

## 16. `deploy-project`

Implementado en:

- `lib/python/vps_init_framework/deploy_project.py`

### 16.1 Responsabilidades

- validar estructura del proyecto
- validar env seleccionado
- validar que no queden placeholders
- verificar disponibilidad de Docker y Compose
- preflight de puertos host
- ejecutar `docker compose up -d --build`
- verificar servicios running
- ejecutar checks HTTP minimos

### 16.2 Modos

- `--validate-only`
- `--no-build`
- `--skip-health-checks`
- `--timeout`

### 16.3 Idempotencia del redeploy

`deploy-project` ya tolera redeploy cuando los puertos detectados como ocupados pertenecen al mismo stack del proyecto.

Bloquea solo si:

- los puertos los usa otro proceso
- o los usa otro stack distinto

### 16.4 Checks de salud implementados

Checks actuales:

- `root` por Caddy HTTP, aceptando redirects/estados validos
- `health` directo contra API en `API_PORT`, esperando `200`
- `n8n` por Caddy HTTP, aceptando estados de redirect o auth

### 16.5 Tolerancia a warm-up

Los checks HTTP reintentan dentro del timeout definido.

Tambien toleran errores transitorios como:

- `connection refused`
- `connection reset`
- `socket timeout`
- `remote disconnected`

### 16.6 Interrupcion segura

Si el usuario interrumpe con `Ctrl+C`, el comando informa posible estado parcial y el comando de recuperacion recomendado.

## 17. `audit-project`

Implementado en:

- `lib/python/vps_init_framework/audit_project.py`

### 17.1 Responsabilidades

- auditar estructura del proyecto
- validar variables requeridas
- detectar placeholders no resueltos
- verificar contenedores running
- verificar estado HTTP funcional
- revisar existencia y frescura de backups

### 17.2 Modos

- `--validate-only`
- `--skip-runtime-checks`
- `--timeout`
- `--json`
- `--output`
- `--backup-max-age-hours`

### 17.3 Hallazgos emitidos

Severidades:

- `ok`
- `warning`
- `error`
- `info`

Resumen:

- `errors`
- `warnings`
- `oks`
- `infos`

## 18. `backup-project`

Implementado en:

- `lib/python/vps_init_framework/backup_project.py`

### 18.1 Responsabilidades

- validar proyecto y env
- generar dump PostgreSQL comprimido
- generar archivo tar.gz de configuracion
- generar manifest JSON del backup

### 18.2 Artefactos generados

Con timestamp UTC:

- `<project>_pg_<timestamp>.sql.gz`
- `<project>_config_<timestamp>.tar.gz`
- `<project>_manifest_<timestamp>.json`

### 18.3 Modos

- `--validate-only`
- `--skip-db-dump`
- `--skip-config-archive`
- `--output-dir`

## 19. Operacion cotidiana esperada

### 19.1 Primera vez en VPS limpio

Secuencia esperada:

1. `audit-vps`
2. `init-vps`
3. `harden-vps` si se quiere key-only
4. trabajar luego como usuario operativo

### 19.2 Cada proyecto nuevo

Secuencia esperada:

1. `new-project`
2. revisar envs
3. `deploy-project`
4. `audit-project`
5. `backup-project`

Importante:

- `init-vps` no se corre por cada proyecto
- el bloque host se ejecuta una vez por VPS, no una vez por app

## 20. Administracion de multiples proyectos en un mismo VPS

El modelo soporta multiples proyectos en el mismo host, siempre que:

- cada proyecto tenga su propia carpeta
- cada proyecto tenga su propio repo Git
- cada proyecto use puertos compatibles

Ejemplo:

- `/home/alex/apps/app01`
- `/home/alex/apps/app02`

Cada uno con su propio:

- `docker-compose.yml`
- red Docker
- volumenes
- backups
- auditoria

## 21. Separacion entre repo template y proyecto real

Separacion recomendada:

- repo framework: `VPS_INIT_PROYECTS_TEMPLATE_REPO`
- repo proyecto generado: por ejemplo `SOPORTE_APP`

No se deben mezclar:

- commits del framework
- codigo de negocio del proyecto generado

El template es la base de arranque. El proyecto generado pasa luego a evolucionar por su propio ciclo Git.

## 22. Reglas tecnicas relevantes ya resueltas durante validacion

Durante la validacion real se corrigieron y cerraron estas reglas:

- persistencia de PostgreSQL y n8n con volumenes nombrados
- tolerancia a errores transitorios en health checks
- no seguir redirects HTTP cuando el codigo en si es el estado esperado
- chequeo de health de API directo por `API_PORT`
- preflight de puertos que tolera puertos del mismo stack en redeploy
- README principal alineado al estado real del framework

## 23. Limitaciones conocidas

El framework actual:

- esta orientado a Ubuntu
- asume Docker Compose como capa de orquestacion local
- no administra aun multiples templates de proyecto
- no crea automaticamente el repo Git remoto del proyecto generado
- no implementa restore completo automatizado del dump PostgreSQL a nivel CLI dedicado

## 24. Estado de validacion

Estado validado:

- suite de tests locales del framework
- smoke tests
- generacion de proyecto
- deploy real en VPS de laboratorio
- auditoria del proyecto desplegado
- backup real con artefactos generados

## 25. Conclusion tecnica

El proyecto actual implementa un framework funcional para:

- estandarizar un VPS Ubuntu nuevo
- generar un proyecto fullstack opinionado
- desplegarlo de forma repetible
- auditar su estado tecnico
- respaldar configuracion y base de datos

La implementacion cerrada en `v1.0.0` es apta como baseline operativo y como base para evolucion futura del framework.
