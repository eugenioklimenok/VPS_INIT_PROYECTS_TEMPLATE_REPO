# Plan de implementacion

## Objetivo del plan

Implementar el framework en un orden sano, con dependencias claras y sin mezclar demasiadas responsabilidades al mismo tiempo.

## Fase 1: base del repo

Entregables:

- estructura del repo
- configuracion base
- convenciones de nombres
- documentacion aprobada

Trabajo:

1. crear estructura oficial del repo
2. definir `bin/`, `lib/`, `templates/`, `config/`, `docs/`, `tests/`, `reports/`
3. congelar la documentacion como baseline

## Fase 2: host bootstrap

Entregables:

- `audit-vps`
- `init-vps`
- `harden-vps`

Trabajo:

1. implementar librerias Bash comunes
2. implementar checks de auditoria del host
3. implementar bootstrap base del VPS
4. implementar endurecimiento posterior
5. definir reportes y exit codes

## Fase 3: template de proyecto

Entregables:

- `templates/fullstack/`
- `new-project`

Trabajo:

1. definir template exacto del stack
2. preparar archivos base del proyecto
3. implementar generador del proyecto en Python
4. validar naming, rutas y variables

## Fase 4: deploy del proyecto

Entregables:

- `deploy-project`

Trabajo:

1. validar proyecto generado
2. leer envs requeridos
3. construir y levantar stack
4. ejecutar checks minimos de salud

## Fase 5: backup y auditoria del proyecto

Entregables:

- `backup-project`
- `audit-project`

Trabajo:

1. definir formato y destino de backups
2. implementar dump de PostgreSQL
3. implementar auditoria de stack y backups
4. documentar recuperacion basica

## Orden real recomendado

1. cerrar documentacion
2. implementar Fase 2
3. probar en VPS real
4. implementar Fase 3
5. implementar Fase 4
6. implementar Fase 5
7. agregar pruebas y endurecimiento adicional

## Regla de control

No pasar a la fase siguiente sin:

- contrato funcional definido
- criterios de aceptacion claros
- alcance acordado
