# new-project - Implementacion

## Estado

Fase 8 implementada.

## Forma de ejecucion

`new-project <project_name> [flags]`

Flags principales:

- `--base-path`
- `--domain`
- `--api-port`
- `--postgres-port`
- `--n8n-port`
- `--caddy-http-port`
- `--caddy-https-port`
- `--postgres-db`
- `--postgres-user`
- `--postgres-password`
- `--n8n-user`
- `--n8n-password`
- `--secret-key`

## Logica implementada

`new-project`:

- carga defaults desde `config/defaults.env`
- valida el nombre del proyecto
- valida dominio y puertos
- resuelve la ruta de salida
- copia `templates/fullstack`
- materializa archivos fuente del template a sus nombres finales
- renderiza placeholders del template
- marca scripts `.sh` como ejecutables
- emite un resumen final con proximos pasos

## Defaults operativos

- base path por default: `DEFAULT_APPS_DIR`
- dominio por default: `localhost`
- puertos por default: `8000`, `5432`, `5678`, `80`, `443`
- `POSTGRES_DB` y `POSTGRES_USER`: nombre del proyecto con `-` reemplazado por `_`
- passwords y `SECRET_KEY`: generados si no se informan

## Validaciones cerradas

- nombre en kebab-case estricto
- ruta destino no existente
- dominio sin espacios
- puertos entre `1` y `65535`
- sin puertos duplicados entre servicios publicados

## Resultado

La siguiente fase ya puede apoyarse en proyectos generados automaticamente desde el template oficial.

## Regla de materializacion

`new-project` convierte archivos fuente del framework:

- `gitignore.template` -> `.gitignore`
- `env/env.example.template` -> `env/.env.example`
- `env/env.dev.template` -> `env/.env.dev`
- `env/env.prod.template` -> `env/.env.prod`

## Validacion realizada

Se valido en este workspace:

- compilacion Python del modulo
- generacion real de un proyecto temporal
- verificacion de estructura creada
- verificacion de placeholders completamente resueltos
