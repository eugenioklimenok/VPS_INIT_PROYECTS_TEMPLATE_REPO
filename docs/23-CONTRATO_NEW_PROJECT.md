# Contrato funcional de new-project

## Nombre

`new-project`

## Tipo

Scaffold del proyecto.

## Proposito

Generar un proyecto full stack nuevo a partir del template oficial `templates/fullstack`, resolviendo placeholders, creando archivos base y dejando el proyecto listo para completar envs y desplegar.

## Responsabilidad exacta

Debe:

- validar el nombre del proyecto
- resolver ruta destino del proyecto
- copiar el template oficial
- reemplazar placeholders del template
- crear archivos base del proyecto
- dejar un resumen final claro

## Lo que si hace

- crea una carpeta nueva de proyecto
- renderiza variables del template
- genera archivos listos para edicion
- deja scripts operativos y stack Docker base

## Lo que no hace

- no despliega el stack
- no ejecuta `docker compose up`
- no instala dependencias del host
- no modifica configuracion del VPS
- no crea backups reales
- no valida salud operativa del proyecto ya levantado

## Inputs obligatorios

- nombre del proyecto

## Inputs opcionales

- dominio
- puertos
- credenciales iniciales seguras
- ruta base alternativa

## Defaults de puertos del scaffold

Para evitar choques con servicios ya existentes en hosts de prueba o VPS no limpios, `new-project` debe generar por default:

- `API_PORT=18000`
- `POSTGRES_PORT=15432`
- `N8N_PORT=15678`
- `CADDY_HTTP_PORT=18080`
- `CADDY_HTTPS_PORT=18443`

## Validaciones obligatorias

### Nombre del proyecto

Debe ser:

- minusculas
- sin espacios
- con `a-z`, `0-9` y `-`
- no vacio
- no conflictivo con un proyecto ya existente en la ruta destino

### Ruta destino

Default:

- `/home/alex/apps/<project_name>`

## Placeholders oficiales del template

- `__PROJECT_NAME__`
- `__DOMAIN_NAME__`
- `__API_PORT__`
- `__POSTGRES_PORT__`
- `__N8N_PORT__`
- `__CADDY_HTTP_PORT__`
- `__CADDY_HTTPS_PORT__`
- `__POSTGRES_ADMIN_USER__`
- `__POSTGRES_ADMIN_PASSWORD__`
- `__APP_DB_NAME__`
- `__APP_DB_USER__`
- `__APP_DB_PASSWORD__`
- `__N8N_DB_NAME__`
- `__N8N_DB_USER__`
- `__N8N_DB_PASSWORD__`
- `__N8N_BASIC_AUTH_USER__`
- `__N8N_BASIC_AUTH_PASSWORD__`
- `__SECRET_KEY__`

## Archivos que debe generar

- `.gitignore`
- `README.md`
- `docker-compose.yml`
- `compose.override.yml`
- `Makefile`
- `api/app/main.py`
- `api/requirements.txt`
- `api/Dockerfile`
- `caddy/Caddyfile`
- `env/.env.example`
- `env/.env.dev`
- `env/.env.prod`
- `scripts/up.sh`
- `scripts/down.sh`
- `scripts/logs.sh`
- `scripts/backup.sh`
- `scripts/restore.sh`

## Output humano

Debe incluir:

- nombre del proyecto generado
- ruta de salida
- placeholders resueltos
- proximos pasos recomendados

## Exit codes oficiales

- `0`: generacion correcta
- `2`: fallo funcional al crear o renderizar
- `3`: error de uso o input invalido

## Criterio de exito

`new-project` queda bien definido si cualquier tecnico puede saber que recibe, que genera y que no hace antes de ejecutarlo.
