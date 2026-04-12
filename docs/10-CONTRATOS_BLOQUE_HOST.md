# Contratos del bloque host

## Estado

Fase 2 cerrada a nivel funcional.

## Objetivo

Definir de forma precisa y sin ambiguedad el contrato funcional de:

- `audit-vps`
- `init-vps`
- `harden-vps`

## Regla de lectura

Este documento funciona como vista general del bloque host. Los detalles operativos de cada comando viven en sus contratos individuales.

## Orden operativo oficial

1. `audit-vps`
2. `init-vps`
3. `audit-vps`
4. `harden-vps`
5. `audit-vps`

## Responsabilidad de cada comando

### `audit-vps`

- audita el host sin modificarlo
- detecta desvio del estandar
- informa severidades y estado general

### `init-vps`

- deja un Ubuntu nuevo en estado base operativo
- crea o valida el usuario estandar
- aplica configuracion inicial del host

### `harden-vps`

- aplica endurecimiento posterior
- reduce superficie de acceso
- lleva el host desde modo inicial a modo mas estricto

## Limites del bloque host

El bloque host no debe:

- crear proyectos
- desplegar stacks de aplicacion
- instalar FastAPI, PostgreSQL, n8n o Caddy como stack de proyecto
- renderizar templates del proyecto
- hacer backup del proyecto
- auditar contenedores del proyecto

## Entradas comunes del bloque host

- VPS Ubuntu Server LTS
- acceso con privilegios suficientes
- usuario objetivo esperado: `alex`, salvo override explicito

## Salidas comunes del bloque host

- salida humana legible
- codigos de salida predecibles
- reportes opcionales cuando el comando lo soporte

## Criterio general de aprobacion

La fase queda aprobada si cualquier lector tecnico puede responder sin dudas:

1. que hace cada comando
2. que no hace cada comando
3. con que flags se ejecuta
4. que inputs necesita
5. que output emite
6. con que exit codes termina
