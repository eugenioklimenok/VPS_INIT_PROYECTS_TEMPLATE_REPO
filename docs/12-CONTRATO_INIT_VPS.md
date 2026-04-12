# Contrato funcional de init-vps

## Nombre

`init-vps`

## Tipo

Bootstrap del host.

## Proposito

Convertir un VPS Ubuntu nuevo o semi preparado en un host base operativo segun el estandar del framework.

## Responsabilidad exacta

Debe:

- validar que el entorno sea compatible
- asegurar el usuario operativo estandar
- crear estructura base de directorios
- instalar paquetes base
- configurar SSH inicial
- configurar UFW
- instalar Docker y Compose plugin
- dejar un resumen final claro

## Lo que si hace

- modifica configuracion del host
- crea o ajusta usuario operativo
- instala paquetes del sistema
- toca configuracion SSH
- habilita y configura firewall
- instala Docker oficial

## Lo que no hace

- no genera proyectos
- no despliega stacks de aplicacion
- no instala Caddy como stack del proyecto
- no instala FastAPI, PostgreSQL o n8n como proyecto
- no configura backups del proyecto
- no endurece el host al modo final si eso implica key-only sin validacion previa

## Requisitos de ejecucion

- root o sudo
- Ubuntu Server LTS compatible
- conectividad suficiente para instalar paquetes cuando haga falta

## Flags oficiales

### `--user <user>`

Usuario operativo a asegurar.

Default:

- `alex`

### `--timezone <tz>`

Timezone a aplicar al host.

Ejemplo:

- `America/Argentina/Buenos_Aires`

### `--with-password-auth`

Mantiene SSH con password habilitado en la fase inicial.

### `--disable-password-auth`

Deshabilita password auth en esta misma etapa.

Uso esperado:

- solo si ya existe acceso por key validado

### `--skip-docker`

Omite instalacion de Docker.

Uso esperado:

- debugging
- entornos especiales

### `--non-interactive`

Ejecuta sin confirmacion manual.

### `--report <file>`

Escribe un reporte resumido de la ejecucion.

### `--help`

Muestra ayuda y termina sin aplicar cambios.

## Inputs

- sistema operativo del host
- usuario objetivo
- timezone opcional
- politica inicial de password auth
- estado actual de paquetes y servicios

## Prechecks obligatorios

- verificar root o sudo
- verificar Ubuntu compatible
- verificar presencia de gestor de paquetes

## Acciones obligatorias

### Usuario

- crear usuario si no existe
- asegurar shell valida
- asegurar pertenencia a `sudo`

### Directorios

- crear `/home/<user>/apps`
- crear `/home/<user>/repos`
- crear `/home/<user>/backups`
- crear `/home/<user>/scripts`
- asegurar ownership correcto

### Paquetes base

- actualizar indices
- instalar paquetes base requeridos

### Timezone

- aplicar timezone si fue solicitada

### SSH

- hacer backup de configuracion antes de tocarla
- asegurar `PermitRootLogin no`
- asegurar `PubkeyAuthentication yes`
- configurar `PasswordAuthentication` segun flags
- validar sintaxis antes de recargar servicio

### UFW

- asegurar presencia de `22/tcp`
- asegurar presencia de `80/tcp`
- asegurar presencia de `443/tcp`
- habilitar UFW

### Docker

- instalar prerequisitos
- configurar repo oficial
- instalar Docker Engine
- instalar Docker Compose plugin
- asegurar servicio activo
- agregar usuario al grupo `docker`

## Output humano

Debe incluir:

- pasos ejecutados
- acciones aplicadas
- hallazgos relevantes
- resumen final
- pasos recomendados posteriores

## Reporte opcional

Debe incluir como minimo:

- timestamp
- usuario objetivo
- timezone aplicada o no aplicada
- politica de password auth
- si Docker fue instalado o salteado

## Exit codes oficiales

- `0`: ejecucion correcta
- `2`: fallo funcional critico durante bootstrap
- `3`: error de uso, entorno no soportado o ejecucion invalida

## Postcondiciones esperadas

Si termina con `0`, el host deberia quedar listo para:

1. auditarse con `audit-vps`
2. operar con usuario estandar
3. correr Docker
4. alojar proyectos generados despues

## Criterio de exito

El comando queda bien definido si cualquier tecnico puede saber exactamente que va a tocar del host antes de ejecutarlo.
