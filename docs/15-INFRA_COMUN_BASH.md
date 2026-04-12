# Infra comun Bash

## Estado

Fase 3 cerrada a nivel de base tecnica compartida.

## Objetivo

Definir y materializar la infraestructura comun que van a reutilizar los comandos del bloque host.

## Componentes creados

### `lib/bash/common.sh`

Responsabilidad:

- helpers generales
- manejo de errores
- carga de defaults
- utilidades de sistema
- timestamps y hostname
- helpers de archivos y valores booleanos

### `lib/bash/log.sh`

Responsabilidad:

- salida humana uniforme
- niveles `STEP`, `INFO`, `OK`, `WARN`, `FAIL`, `DEBUG`
- soporte opcional de color
- control de verbosidad

### `lib/bash/results.sh`

Responsabilidad:

- almacenamiento comun de resultados
- severidades reutilizables
- resumen de hallazgos
- calculo de exit code basado en resultados

### `config/defaults.env`

Responsabilidad:

- defaults del framework
- usuario esperado
- rutas base
- timezone por defecto
- politica inicial de SSH
- puertos requeridos
- paquetes base

## Diseno aplicado

La infraestructura comun se construyo para que:

- `audit-vps` reutilice `common.sh`, `log.sh` y `results.sh`
- `init-vps` reutilice `common.sh` y `log.sh`
- `harden-vps` reutilice `common.sh` y `log.sh`

## Duplicacion evitada

Se evita duplicar:

- manejo de errores
- carga de defaults
- funciones de root y comandos del sistema
- hostname y timezone
- logging de consola
- almacenamiento de resultados

## Limite de esta fase

Fase 3 no implementa aun comandos finales del bloque host. Deja la base lista para hacerlo en la siguiente fase.
