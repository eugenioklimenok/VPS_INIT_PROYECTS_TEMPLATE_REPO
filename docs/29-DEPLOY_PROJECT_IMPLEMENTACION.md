# deploy-project - Implementacion

## Estado

Fase 9 implementada.

## Forma de ejecucion

`deploy-project [project_path] [flags]`

Flags principales:

- `--env`
- `--validate-only`
- `--no-build`
- `--skip-health-checks`
- `--timeout`

## Logica implementada

`deploy-project`:

- valida estructura del proyecto generado
- carga y valida `env/.env.dev` o `env/.env.prod`
- verifica que no queden placeholders `__PLACEHOLDER__`
- en modo normal ejecuta `docker compose up -d`
- por default agrega `--build`
- usa `docker-compose.yml` para `prod`
- usa `docker-compose.yml` + `compose.override.yml` para `dev`
- verifica servicios running
- verifica respuesta HTTP de `root`, `/health` y `/n8n/`

## Reglas operativas

- `project_path` default: directorio actual
- `--validate-only`: no requiere Docker, solo valida estructura y envs
- `--no-build`: evita reconstruccion de imagenes
- `--skip-health-checks`: salta checks posteriores al `up`

## Validacion cerrada

- estructura requerida del proyecto
- env requerido presente
- variables obligatorias cargadas
- puertos validos y no repetidos
- template completamente renderizado

## Limitacion de este entorno

En este workspace no hay Docker disponible en PATH. Por eso la validacion ejecutada de esta fase se hizo en modo `--validate-only`.

Tambien se confirmo que el comando falla de forma controlada con un mensaje claro cuando se ejecuta sin Docker disponible.

## Resultado

La siguiente fase ya puede implementar `backup-project` y `audit-project` sobre proyectos generados y desplegables.
