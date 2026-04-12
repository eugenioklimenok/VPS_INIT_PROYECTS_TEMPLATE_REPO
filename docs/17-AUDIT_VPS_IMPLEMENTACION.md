# audit-vps - Implementacion

## Estado

Fase 4 implementada.

## Componentes creados

- `bin/audit-vps`
- `lib/bash/checks_os.sh`
- `lib/bash/checks_user.sh`
- `lib/bash/checks_ssh.sh`
- `lib/bash/checks_ufw.sh`
- `lib/bash/checks_docker.sh`
- `lib/bash/checks_dirs.sh`
- `lib/bash/checks_packages.sh`
- `lib/bash/checks_system.sh`

## Estructura aplicada

La implementacion se separa en:

- un entrypoint
- modulos de checks por dominio
- una base comun reutilizada desde Fase 3

## Cobertura funcional

`audit-vps` ya cubre:

- SO
- usuario
- SSH
- UFW
- Docker
- directorios
- paquetes
- sistema

## Garantia funcional

La implementacion esta pensada como auditoria read-only del host.

No contiene logica para:

- instalar paquetes
- crear usuarios
- modificar firewall
- modificar configuracion SSH
- escribir cambios en el sistema

## Outputs soportados

- salida humana
- salida JSON
- escritura opcional a archivo con `--output`

## Limitacion de validacion en este entorno

La validacion automatica con `bash -n` no pudo ejecutarse aqui porque el entorno actual de Windows no tiene `bash` disponible en PATH.
