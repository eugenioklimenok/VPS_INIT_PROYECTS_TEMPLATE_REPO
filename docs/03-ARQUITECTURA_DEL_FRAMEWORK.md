# Arquitectura del framework

## Modelo por capas

La solucion se divide en tres capas operativas.

## Capa 1: VPS bootstrap

Responsabilidad:

- preparar el host
- validar sistema operativo
- asegurar usuario operativo
- instalar componentes base
- configurar seguridad inicial

Comandos principales:

- `audit-vps`
- `init-vps`
- `harden-vps`

## Capa 2: Project scaffolding

Responsabilidad:

- generar una estructura de proyecto uniforme
- crear archivos base
- renderizar templates y variables
- preparar scripts operativos del proyecto

Comando principal:

- `new-project`

## Capa 3: Deploy y operacion

Responsabilidad:

- levantar servicios
- validar salud minima
- ejecutar backups
- auditar estado del stack

Comandos principales:

- `deploy-project`
- `backup-project`
- `audit-project`

## Estructura objetivo del framework

```text
VPS_INIT_PROYECTS_TEMPLATE_REPO/
|-- bin/
|   |-- init-vps
|   |-- harden-vps
|   |-- audit-vps
|   |-- new-project
|   |-- deploy-project
|   |-- backup-project
|   `-- audit-project
|-- lib/
|   |-- bash/
|   `-- python/
|-- templates/
|   `-- fullstack/
|-- config/
|-- docs/
|-- reports/
`-- tests/
```

## Stack tecnologico recomendado

### Bash

Para:

- bootstrap del host
- SSH
- UFW
- Docker
- paquetes
- backups simples
- chequeos operativos del sistema

### Python

Para:

- scaffolding del proyecto
- validacion de inputs
- render de templates
- logica mas rica de composicion de archivos
- futuras verificaciones con estructura de datos mas expresiva

## Regla de separacion

El framework interno debe vivir separado del codigo de los proyectos. Un proyecto generado no debe contener la logica completa del framework; solo debe contener su stack, su configuracion y sus scripts de operacion locales.
