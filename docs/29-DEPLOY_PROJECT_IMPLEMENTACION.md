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
- hace preflight de puertos host antes del `up`
- en modo normal ejecuta `docker compose up -d`
- por default agrega `--build`
- usa `docker-compose.yml` para `prod`
- usa `docker-compose.yml` + `compose.override.yml` para `dev`
- verifica servicios running
- verifica respuesta HTTP de `root`, `/health` y `/n8n/`
- tolera warm-up inicial del stack con reintentos dentro del `--timeout`

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
- puertos host detectados como ocupados antes de invocar Docker

## Regla de fallo temprano

Si algun puerto publicado del env ya esta ocupado en el host, `deploy-project` debe fallar antes de `docker compose up` con un mensaje accionable que indique la variable afectada, por ejemplo `N8N_PORT=15678`.

## Regla de warm-up

Si el stack responde `connection refused` durante los primeros segundos posteriores al `up`, `deploy-project` no debe fallar de inmediato. Debe reintentar los checks HTTP hasta agotar el `--timeout`.

## Limitacion de este entorno

En este workspace no hay Docker disponible en PATH. Por eso la validacion ejecutada de esta fase se hizo en modo `--validate-only`.

Tambien se confirmo que el comando falla de forma controlada con un mensaje claro cuando se ejecuta sin Docker disponible.

## Resultado

La siguiente fase ya puede implementar `backup-project` y `audit-project` sobre proyectos generados y desplegables.
