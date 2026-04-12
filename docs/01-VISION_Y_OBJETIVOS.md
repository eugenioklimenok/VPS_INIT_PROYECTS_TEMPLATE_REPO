# Vision y objetivos

## Vision

Construir un framework interno que convierta tareas operativas repetitivas en flujos estandarizados, auditables y faciles de repetir.

El framework debe cubrir dos dominios conectados:

1. el host
2. el proyecto

La idea central es evitar improvisacion en:

- preparacion de VPS
- estructura de proyectos
- despliegues
- backups
- verificaciones operativas

## Problema que resuelve

Sin una base comun, cada VPS y cada proyecto tienden a nacer con diferencias pequenas pero costosas:

- usuarios o permisos inconsistentes
- carpetas creadas a mano
- configuraciones SSH distintas
- reglas de firewall incompletas
- stacks Docker con nombres variables
- backups sin criterio uniforme
- documentacion operativa dispersa

Este framework busca eliminar esa deriva operativa.

## Objetivos principales

1. Estandarizar el bootstrap de un VPS Ubuntu nuevo.
2. Estandarizar la estructura de un proyecto full stack.
3. Estandarizar el despliegue sobre Docker.
4. Estandarizar auditoria y backups.
5. Reducir tareas manuales no repetibles.
6. Mantener una base portable y facil de evolucionar.

## Objetivos tecnicos

- usar Bash para todo lo cercano al sistema operativo
- usar Python para scaffolding, validacion y render de templates
- separar framework interno de codigo de proyectos
- priorizar defaults seguros y predecibles
- permitir ejecucion idempotente cuando aplique

## Resultado esperado

El resultado final debe permitir pasar de un VPS vacio y un nombre de proyecto a un entorno full stack funcional, repetible y entendible, con un flujo claro desde el dia 1.
