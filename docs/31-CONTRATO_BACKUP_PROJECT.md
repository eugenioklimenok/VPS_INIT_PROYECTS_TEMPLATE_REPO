# Contrato funcional de backup-project

## Nombre

`backup-project`

## Tipo

Backup del proyecto.

## Proposito

Generar un backup basico y previsible del proyecto, empezando por PostgreSQL y archivos criticos de configuracion.

## Responsabilidad exacta

Debe:

- validar la estructura del proyecto
- validar el env seleccionado
- generar dump PostgreSQL con timestamp
- generar backup de archivos criticos del proyecto
- dejar un manifiesto simple de los artefactos creados
- dejar un resumen final claro

## Lo que si hace

- valida estructura, envs y placeholders
- crea backup en el directorio de salida
- guarda naming estandar con timestamp
- incluye restauracion basica a partir de los artefactos

## Lo que no hace

- no despliega el proyecto
- no reconfigura Docker
- no modifica el template
- no restaura automaticamente el proyecto

## Inputs opcionales

- `--env dev|prod`
- `--output-dir`
- `--validate-only`
- `--skip-db-dump`
- `--skip-config-archive`

## Regla operativa

Si se usa `--skip-db-dump`, el comando puede generar solo backup de configuracion sin requerir Docker.

## Exit codes oficiales

- `0`: validacion o backup correctos
- `2`: fallo funcional de validacion, Docker o backup
- `3`: error de uso o input invalido
