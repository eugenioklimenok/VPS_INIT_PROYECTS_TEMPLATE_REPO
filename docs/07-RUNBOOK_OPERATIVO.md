# Runbook operativo

## Flujo para VPS nuevo

1. acceder al VPS con el usuario inicial del proveedor
2. instalar `git` si hace falta
3. clonar el framework interno
4. ejecutar auditoria inicial del host
5. ejecutar bootstrap del VPS
6. ejecutar auditoria posterior
7. aplicar endurecimiento cuando ya exista acceso por key validado
8. ejecutar nueva auditoria

## Flujo para proyecto nuevo

1. ejecutar `new-project`
2. definir nombre del proyecto
3. revisar estructura generada
4. completar archivos `.env`
5. ejecutar `deploy-project`
6. verificar salud minima del stack
7. ejecutar `audit-project`
8. dejar backup base funcionando

## Flujo de operacion diaria

1. revisar logs cuando haya incidentes
2. auditar host y proyecto de forma periodica
3. ejecutar o verificar backup diario
4. revisar capacidad de disco, RAM y volumenes

## Flujo de recuperacion basica

1. identificar el proyecto afectado
2. inspeccionar contenedores y logs
3. verificar backups disponibles
4. restaurar base de datos o archivos criticos
5. volver a auditar el proyecto

## Regla operativa

No hacer cambios estructurales manuales en el VPS sin dejar luego reflejada la logica en el framework.

## Orden recomendado de trabajo

### Antes de automatizar

- definir contrato
- definir inputs
- definir outputs
- definir criterios de error

### Antes de desplegar

- auditar host
- validar envs
- validar template
- validar puertos y rutas

### Antes de endurecer SSH

- confirmar acceso por key
- confirmar usuario sudo operativo
- confirmar conectividad estable
