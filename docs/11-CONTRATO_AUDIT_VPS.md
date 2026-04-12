# Contrato funcional de audit-vps

## Nombre

`audit-vps`

## Tipo

Auditoria read-only del host.

## Proposito

Inspeccionar el VPS y detectar desvio del estandar del host sin modificar configuracion, usuarios, paquetes ni servicios.

## Responsabilidad exacta

Debe validar:

- sistema operativo
- usuario operativo esperado
- estado de SSH
- estado de UFW
- presencia y estado de Docker
- estructura base de directorios
- paquetes base
- estado basico del sistema

## Lo que si hace

- lee configuracion y estado del host
- clasifica hallazgos por severidad
- imprime resumen legible
- puede emitir salida estructurada
- puede escribir reporte a archivo si se solicita

## Lo que no hace

- no crea usuarios
- no modifica `sshd_config`
- no habilita ni deshabilita UFW
- no instala paquetes
- no instala Docker
- no crea directorios
- no reinicia servicios
- no despliega proyectos

## Contexto de ejecucion

- puede ejecutarse sin root en la mayoria de los casos
- algunos checks pueden degradarse si el entorno no permite leer cierta informacion
- no requiere modo interactivo

## Flags oficiales

### `--expected-user <user>`

Define el usuario operativo esperado.

Default:

- `alex`

### `--strict`

Hace mas severos algunos hallazgos.

Uso esperado:

- convertir ciertos `WARN` en `FAIL`, especialmente en seguridad

### `--verbose`

Habilita detalle adicional en la salida humana.

### `--json`

Emite salida estructurada en JSON.

### `--output <file>`

Guarda la salida en archivo en vez de solo stdout.

### `--help`

Muestra ayuda y termina sin ejecutar checks.

## Inputs

- estado real del sistema operativo
- configuracion SSH
- configuracion y estado de UFW
- estado de Docker
- usuario esperado
- estructura de carpetas del host

## Checks oficiales

### Sistema operativo

- existencia de `/etc/os-release`
- `ID=ubuntu`
- version detectada
- estado LTS

### Usuario

- existencia del usuario esperado
- home esperado
- shell esperada
- pertenencia a `sudo`

### SSH

- presencia de `sshd`
- servicio SSH activo
- config legible y valida
- `PermitRootLogin no`
- `PasswordAuthentication` segun severidad
- `PubkeyAuthentication yes`

### UFW

- `ufw` instalado
- UFW activo
- `22/tcp`
- `80/tcp`
- `443/tcp`

### Docker

- comando `docker` disponible
- daemon operativo
- plugin Compose disponible
- usuario en grupo `docker`

### Directorios

- `/home/<user>/apps`
- `/home/<user>/repos`
- `/home/<user>/backups`
- `/home/<user>/scripts`

### Paquetes base

- lista base definida por el framework

### Estado del sistema

- espacio en disco
- RAM
- swap
- timezone
- hostname
- IP principal

## Output humano

Debe incluir:

- encabezado del comando
- host evaluado
- timestamp
- usuario esperado
- modo estricto o normal
- lista de hallazgos
- resumen final por severidad
- exit code resultante

## Output JSON

Debe incluir al menos:

- host
- timestamp
- expected_user
- strict_mode
- summary
- results

## Severidades oficiales

- `OK`
- `INFO`
- `WARN`
- `FAIL`

## Politica de severidad

- `FAIL` cuando el host incumple algo critico del estandar
- `WARN` cuando hay desvio no bloqueante o endurecimiento pendiente
- `INFO` para informacion operativa
- `OK` para conformidad explicita

## Exit codes oficiales

- `0`: sin warnings ni fails
- `1`: hay warnings pero no fails
- `2`: hay uno o mas fails
- `3`: error de ejecucion o uso invalido del comando

## Criterio de exito

El comando queda bien definido si puede ejecutarse sobre cualquier VPS objetivo y producir un diagnostico consistente sin tocar el host.
