# Suite de comandos

## Vision general

La suite de comandos del framework se divide en comandos de host y comandos de proyecto.

## Comandos del host

### `audit-vps`

Tipo:

- auditoria

Responsabilidad:

- inspeccionar el VPS sin modificarlo
- validar sistema operativo, usuario, SSH, UFW, Docker, paquetes, directorios y estado basico del sistema

Garantias:

- no crea usuarios
- no instala paquetes
- no modifica configuracion
- no reinicia servicios

### `init-vps`

Tipo:

- bootstrap

Responsabilidad:

- dejar un VPS Ubuntu en estado base operativo
- crear o validar usuario operativo
- crear directorios estandar
- instalar paquetes base
- configurar SSH base
- habilitar UFW
- instalar Docker

### `harden-vps`

Tipo:

- seguridad

Responsabilidad:

- aplicar endurecimiento posterior al bootstrap inicial
- dejar acceso por key solamente cuando corresponda
- revisar permisos y configuracion SSH

## Comandos del proyecto

### `new-project`

Tipo:

- scaffold

Responsabilidad:

- crear un proyecto full stack desde template
- validar nombre del proyecto
- generar archivos, rutas, scripts y envs base

### `deploy-project`

Tipo:

- deploy

Responsabilidad:

- levantar o actualizar el stack Docker del proyecto
- validar archivos criticos
- ejecutar verificaciones minimas de salud

### `backup-project`

Tipo:

- backup

Responsabilidad:

- respaldar PostgreSQL
- respaldar configuraciones importantes
- guardar backups con timestamp y naming estandar

### `audit-project`

Tipo:

- auditoria

Responsabilidad:

- validar estado de contenedores
- validar puertos, conectividad y volumenes
- comprobar backups recientes y salud basica del stack

## Secuencia recomendada

### Host nuevo

1. `audit-vps`
2. `init-vps`
3. `audit-vps`
4. `harden-vps`
5. `audit-vps`

### Proyecto nuevo

1. `new-project`
2. completar `.env`
3. `deploy-project`
4. `audit-project`
5. `backup-project`

## Regla de diseno

Cada comando debe tener:

- input claro
- output claro
- errores comprensibles
- responsabilidad unica o bien delimitada
