# Estandar VPS

## Sistema operativo

- Ubuntu Server LTS

## Usuario operativo

- usuario esperado: `alex`
- shell esperada: `/bin/bash`
- grupo administrativo: `sudo`

## Estructura base del host

Rutas estandar:

- `/home/alex/apps`
- `/home/alex/repos`
- `/home/alex/backups`
- `/home/alex/scripts`

## Politica SSH

### Fase inicial

- root login por SSH deshabilitado
- password auth permitido
- pubkey auth habilitado

### Fase endurecida

- root login deshabilitado
- password auth deshabilitado
- acceso solo por key

## Firewall

Minimo esperado con UFW:

- `22/tcp`
- `80/tcp`
- `443/tcp`

## Runtime de contenedores

Base esperada:

- Docker Engine
- Docker Compose plugin

## Proxy estandar del stack

- Caddy como proxy reverso del proyecto
- ejecutado dentro del stack Docker del proyecto, no como servicio principal del host

## Paquetes base

Lista inicial recomendada:

- `curl`
- `wget`
- `git`
- `ca-certificates`
- `gnupg`
- `lsb-release`
- `unzip`
- `tar`
- `gzip`
- `rsync`
- `nano`

## Reglas del host

- no instalar servicios de aplicacion directamente en el host salvo excepcion justificada
- mantener nombres y rutas previsibles
- priorizar cambios via framework
- permitir auditoria facil del estado real

## Configuracion deseada del host

El host debe quedar listo para:

1. clonar repos
2. correr Docker
3. desplegar proyectos generados por el framework
4. respaldar datos de forma controlada
