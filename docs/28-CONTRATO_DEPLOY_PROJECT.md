# Contrato funcional de deploy-project

## Nombre

`deploy-project`

## Tipo

Deploy del proyecto.

## Proposito

Validar un proyecto generado por el framework, leer el env correspondiente, levantar o actualizar el stack Docker y ejecutar checks minimos de salud.

## Responsabilidad exacta

Debe:

- validar la estructura del proyecto
- validar el env seleccionado
- comprobar que no queden placeholders sin resolver
- ejecutar `docker compose up -d`
- hacer checks minimos de contenedores y rutas HTTP
- dejar un resumen final claro

## Lo que si hace

- valida archivos y directorios criticos
- valida variables requeridas del env
- despliega el stack del proyecto
- verifica servicios running
- verifica `root`, `/health` y `/n8n/`

## Lo que no hace

- no crea el proyecto
- no modifica el template del framework
- no instala Docker en el host
- no configura el VPS
- no genera backups
- no audita backups historicos

## Inputs obligatorios

- ruta del proyecto o directorio actual

## Inputs opcionales

- `--env dev|prod`
- `--validate-only`
- `--no-build`
- `--skip-health-checks`
- `--timeout`

## Validaciones obligatorias

- existencia de `docker-compose.yml`, `compose.override.yml`, `Makefile`
- existencia de `api/`, `caddy/`, `env/`, `scripts/`, `postgres/`, `n8n/`, `backups`
- existencia de `env/.env.<env>`
- variables requeridas presentes
- puertos validos y sin duplicacion
- placeholders del template completamente resueltos

## Output humano

Debe incluir:

- ruta del proyecto
- env utilizado
- resultado de validacion o deploy
- proximo estado operativo esperado

## Exit codes oficiales

- `0`: validacion o deploy correctos
- `2`: fallo funcional de validacion, docker o salud del stack
- `3`: error de uso o input invalido

## Criterio de exito

`deploy-project` queda bien definido si cualquier tecnico puede saber exactamente que valida, que ejecuta y hasta donde llega el deploy.
