# Contrato funcional de harden-vps

## Nombre

`harden-vps`

## Tipo

Endurecimiento del host.

## Proposito

Llevar un host ya inicializado desde el modo operativo inicial a un modo de seguridad mas estricto, con foco principal en SSH y controles basicos del servidor.

## Responsabilidad exacta

Debe:

- aplicar endurecimiento posterior al bootstrap
- reducir superficie de acceso del host
- reforzar configuracion SSH sin romper la operacion
- dejar registro claro de lo aplicado

## Lo que si hace

- ajusta configuracion de SSH a modo endurecido
- valida sintaxis antes de recargar
- puede revisar permisos y condiciones minimas de acceso por key
- deja reporte o resumen final

## Lo que no hace

- no reemplaza `init-vps`
- no crea usuario operativo desde cero
- no instala Docker ni paquetes base del bootstrap
- no genera proyectos
- no despliega stacks
- no hace backup del proyecto

## Requisitos de ejecucion

- root o sudo
- host ya pasado por `init-vps` o equivalente
- acceso por key ya validado antes de deshabilitar password auth

## Flags oficiales

### `--user <user>`

Usuario operativo principal a validar para hardening.

Default:

- `alex`

### `--non-interactive`

Ejecuta sin confirmacion manual.

### `--report <file>`

Guarda reporte resumido de endurecimiento.

### `--help`

Muestra ayuda y termina sin aplicar cambios.

## Inputs

- usuario operativo objetivo
- configuracion SSH actual
- presencia de llaves validas para el usuario operativo
- estado general del host luego del bootstrap

## Acciones obligatorias

### SSH

- mantener `PermitRootLogin no`
- asegurar `PubkeyAuthentication yes`
- deshabilitar `PasswordAuthentication`
- validar sintaxis con `sshd -t`
- recargar servicio solo si la configuracion es valida

### Validaciones de seguridad minima

- comprobar que el usuario objetivo exista
- comprobar que exista acceso por key o al menos `authorized_keys` utilizable antes de dejar key-only
- comprobar que el host siga accesible bajo la politica definida

## Output humano

Debe incluir:

- configuracion endurecida aplicada
- validaciones previas realizadas
- resultado del endurecimiento
- recomendacion de reauditar el host

## Reporte opcional

Debe incluir como minimo:

- timestamp
- usuario objetivo
- estado final de password auth
- estado final de root login
- observaciones relevantes

## Exit codes oficiales

- `0`: endurecimiento aplicado correctamente
- `2`: fallo funcional critico o riesgo de lockout detectado
- `3`: error de uso, prerequisito ausente o ejecucion invalida

## Condicion de seguridad obligatoria

`harden-vps` no debe dejar el host en modo key-only si no hay evidencia razonable de acceso por key para el usuario objetivo.

## Criterio de exito

El comando queda bien definido si endurece el host de forma predecible y con proteccion explicita contra lockout operativo.
