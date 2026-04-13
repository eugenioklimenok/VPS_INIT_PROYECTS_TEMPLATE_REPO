# VPS_INIT_PROYECTS_TEMPLATE_REPO

Base documental nueva para un framework interno orientado a:

- bootstrap de VPS Ubuntu
- creacion de proyectos full stack desde template
- despliegue, auditoria y backup bajo una misma logica operativa

Este directorio nace como una base nueva e independiente. La carpeta original del workspace queda solo como referencia historica y no forma parte de esta nueva linea documental.

## Objetivo

Definir una base oficial, ordenada y autocontenida para construir un framework que permita:

1. estandarizar VPS nuevos
2. crear proyectos full stack repetibles
3. desplegar y operar stacks con minima friccion
4. auditar el estado del host y del proyecto
5. mantener backups previsibles y restaurables

## Estado actual de esta carpeta

Fase 1 queda cerrada con:

- documentacion base aprobada
- estructura real del repo creada
- placeholders minimos en las zonas aun vacias

Fase 2 queda cerrada con:

- contrato funcional del bloque host definido
- alcance, flags, entradas, salidas y exit codes documentados
- limites de `audit-vps`, `init-vps` y `harden-vps` aclarados sin ambiguedad

Fase 3 queda cerrada con:

- infraestructura Bash comun creada
- defaults del framework centralizados
- base tecnica compartida lista para el bloque host

Fase 4 queda cerrada con:

- `audit-vps` implementado
- checks modulares del host creados
- auditoria read-only lista para detectar desvio del estandar

Fase 5 queda cerrada con:

- `init-vps` implementado
- modulos de bootstrap del host creados
- flujo del bloque host listo para completar endurecimiento

Fase 6 queda cerrada con:

- `harden-vps` implementado
- endurecimiento SSH key-only separado del bootstrap
- bloque host completo a nivel de implementacion

Fase 7 queda cerrada con:

- template `fullstack` materializado
- stack base del proyecto definido con archivos reales
- contrato de `new-project` cerrado

Fase 8 queda cerrada con:

- `new-project` implementado en Python
- generacion automatica del proyecto desde `templates/fullstack`
- validaciones de naming, rutas y placeholders cerradas

Fase 9 queda cerrada con:

- `deploy-project` implementado en Python
- validacion de proyecto, envs y placeholders cerrada
- deploy del stack y checks minimos de salud definidos

Fase 10 queda cerrada con:

- `backup-project` implementado en Python
- `audit-project` implementado en Python
- smoke tests del flujo principal agregados
- framework completo a nivel de implementacion local

Documentacion de usuario final agregada:

- guia conceptual completa del framework
- manual detallado de uso sobre Linux y VPS de laboratorio
- quickstart operativo resumido

La siguiente etapa sera validacion de punta a punta en VPS real con Docker.

## Mapa documental

- `docs/00-FASE_1_BASE_DEL_REPO.md`
- `docs/01-VISION_Y_OBJETIVOS.md`
- `docs/02-ALCANCE_Y_PRINCIPIOS.md`
- `docs/03-ARQUITECTURA_DEL_FRAMEWORK.md`
- `docs/04-ESTANDAR_VPS.md`
- `docs/05-SUITE_DE_COMANDOS.md`
- `docs/06-TEMPLATE_DE_PROYECTO_FULLSTACK.md`
- `docs/07-RUNBOOK_OPERATIVO.md`
- `docs/08-PLAN_DE_IMPLEMENTACION.md`
- `docs/09-CRITERIOS_DE_ACEPTACION_Y_RIESGOS.md`
- `docs/10-CONTRATOS_BLOQUE_HOST.md`
- `docs/11-CONTRATO_AUDIT_VPS.md`
- `docs/12-CONTRATO_INIT_VPS.md`
- `docs/13-CONTRATO_HARDEN_VPS.md`
- `docs/14-FASE_2_CONTRATOS_BLOQUE_HOST.md`
- `docs/15-INFRA_COMUN_BASH.md`
- `docs/16-FASE_3_INFRA_COMUN_BASH.md`
- `docs/17-AUDIT_VPS_IMPLEMENTACION.md`
- `docs/18-FASE_4_AUDITORIA_HOST.md`
- `docs/19-INIT_VPS_IMPLEMENTACION.md`
- `docs/20-FASE_5_BOOTSTRAP_HOST.md`
- `docs/21-HARDEN_VPS_IMPLEMENTACION.md`
- `docs/22-FASE_6_HARDENING_HOST.md`
- `docs/23-CONTRATO_NEW_PROJECT.md`
- `docs/24-TEMPLATE_FULLSTACK_IMPLEMENTACION.md`
- `docs/25-FASE_7_TEMPLATE_PROYECTO.md`
- `docs/26-NEW_PROJECT_IMPLEMENTACION.md`
- `docs/27-FASE_8_SCAFFOLDING_PROYECTO.md`
- `docs/28-CONTRATO_DEPLOY_PROJECT.md`
- `docs/29-DEPLOY_PROJECT_IMPLEMENTACION.md`
- `docs/30-FASE_9_DEPLOY_PROYECTO.md`
- `docs/31-CONTRATO_BACKUP_PROJECT.md`
- `docs/32-CONTRATO_AUDIT_PROJECT.md`
- `docs/33-OPERACION_PROYECTO_IMPLEMENTACION.md`
- `docs/34-FASE_10_OPERACION_PROYECTO.md`
- `docs/35-GUIA_USUARIO_FINAL_VPS_INIT.md`
- `docs/36-MANUAL_USO_PASO_A_PASO.md`
- `docs/37-QUICKSTART.md`

## Resultado esperado

Cuando esta linea de trabajo este implementada, deberia ser posible:

1. tomar un VPS Ubuntu nuevo
2. dejarlo en un estado operativo estandar
3. generar un proyecto full stack consistente
4. desplegarlo sobre Docker con configuracion previsible
5. auditar y respaldar el entorno de forma repetible

## Regla de trabajo

No avanzar con codigo, scripts ni cambios estructurales fuera de esta carpeta nueva sin aprobacion explicita.

## Estructura creada en Fase 1

```text
VPS_INIT_PROYECTS_TEMPLATE_REPO/
|-- README.md
|-- bin/
|-- config/
|-- docs/
|-- lib/
|   |-- bash/
|   `-- python/
|-- reports/
|-- templates/
|   `-- fullstack/
|       |-- api/
|       |   `-- app/
|       |-- caddy/
|       |-- env/
|       |-- n8n/
|       |   `-- data/
|       |-- postgres/
|       |   `-- data/
|       `-- scripts/
`-- tests/
    |-- fixtures/
    `-- smoke/
```
