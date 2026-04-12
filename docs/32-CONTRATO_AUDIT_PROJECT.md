# Contrato funcional de audit-project

## Nombre

`audit-project`

## Tipo

Auditoria del proyecto.

## Proposito

Auditar el estado estructural y operativo del proyecto, incluyendo envs, placeholders, backups y, cuando corresponda, servicios y checks HTTP.

## Responsabilidad exacta

Debe:

- validar estructura del proyecto
- validar envs del entorno elegido
- detectar placeholders sin resolver
- inspeccionar backups existentes
- revisar servicios running cuando Docker este disponible
- emitir salida legible o JSON

## Lo que si hace

- devuelve findings con severidad
- informa errores estructurales
- informa warnings por backups faltantes o viejos
- puede generar reporte JSON

## Lo que no hace

- no modifica el proyecto
- no genera backups
- no despliega el stack
- no corrige configuracion

## Inputs opcionales

- `--env dev|prod`
- `--validate-only`
- `--skip-runtime-checks`
- `--timeout`
- `--json`
- `--output`
- `--backup-max-age-hours`

## Exit codes oficiales

- `0`: auditoria sin errores
- `2`: auditoria con errores funcionales
- `3`: error de uso o input invalido
