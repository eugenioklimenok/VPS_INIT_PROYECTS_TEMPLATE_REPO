# Guia de usuario final - VPS_INIT_PROYECTS_TEMPLATE_REPO

## Que es este framework

`VPS_INIT_PROYECTS_TEMPLATE_REPO` es un framework interno para estandarizar tres momentos de trabajo que normalmente se resuelven de forma manual y dispersa:

1. preparar un VPS Ubuntu nuevo
2. generar un proyecto full stack base
3. desplegar, auditar y respaldar ese proyecto bajo una logica repetible

La finalidad del framework es reducir variaciones entre servidores, acelerar la creacion de proyectos y dejar trazabilidad operativa clara.

## Que problema resuelve

Sin este framework, cada VPS y cada proyecto tienden a quedar distintos:

- usuarios y rutas cambian segun quien lo prepare
- SSH y firewall quedan configurados de forma desigual
- Docker y Compose no siempre quedan instalados igual
- los proyectos nacen con estructuras distintas
- los backups se resuelven tarde y sin criterio unico
- las auditorias terminan siendo chequeos manuales

Este framework busca resolver eso con contratos claros, comandos concretos y un template unico de referencia.

## Cual es la idea central

El framework separa el trabajo en dos dominios:

### Dominio host

Se ocupa del servidor Ubuntu.

Incluye:

- auditoria inicial del VPS
- bootstrap del host
- hardening posterior

Comandos:

- `audit-vps`
- `init-vps`
- `harden-vps`

### Dominio proyecto

Se ocupa del proyecto desplegable.

Incluye:

- scaffolding desde template
- deploy del stack
- backup
- auditoria del proyecto

Comandos:

- `new-project`
- `deploy-project`
- `backup-project`
- `audit-project`

## Como esta armado

## Estructura general

```text
VPS_INIT_PROYECTS_TEMPLATE_REPO/
|-- bin/
|-- config/
|-- docs/
|-- lib/
|   |-- bash/
|   `-- python/
|-- reports/
|-- templates/
|   `-- fullstack/
`-- tests/
```

## Rol de cada carpeta

- `bin/`
  Entry points del framework. Desde aca se ejecutan los comandos principales.

- `config/`
  Defaults globales del framework, por ejemplo usuario objetivo, rutas estandar y parametros base.

- `lib/bash/`
  Infra comun para el bloque host. Aca vive la logica compartida de auditoria, bootstrap y hardening.

- `lib/python/`
  Infra comun para el bloque proyecto. Aca viven el scaffolding, el deploy, el backup y la auditoria del stack.

- `templates/fullstack/`
  Template oficial del proyecto que `new-project` copia y renderiza.

- `reports/`
  Carpeta de salida para reportes y pruebas locales. No debe usarse como lugar permanente de proyectos productivos.

- `tests/`
  Pruebas de humo y pruebas tecnicas del framework.

## Logica de implementacion

La logica del framework no mezcla todo junto. El orden correcto es:

1. auditar el host
2. inicializar el host
3. endurecer el host
4. generar el proyecto
5. validar el proyecto
6. desplegar el proyecto
7. auditar el proyecto
8. generar backup
9. auditar nuevamente

Ese orden es importante porque evita usar comandos de proyecto sobre un host incompleto.

## Stack objetivo del template

El template `fullstack` hoy esta pensado para un stack estandar:

- FastAPI
- PostgreSQL
- n8n
- Caddy
- Docker Compose

La estructura generada incluye:

- API base en `api/`
- proxy Caddy en `caddy/`
- envs del proyecto en `env/`
- scripts operativos en `scripts/`
- persistencia para PostgreSQL y n8n
- carpeta `backups/`

## Filosofia de uso

Este framework esta pensado para:

- ejecutarse muchas veces
- reducir intervencion manual
- detectar problemas temprano
- fallar con mensajes utiles
- trabajar sobre contratos predecibles

No esta pensado para:

- reemplazar completamente el criterio tecnico
- ocultar problemas del host
- resolver automaticamente todos los conflictos posibles de un servidor ya contaminado

## Reglas operativas importantes

### Regla 1: preferir host limpio

La mejor validacion del framework se logra sobre una VM o VPS limpio. En hosts ya usados pueden aparecer:

- puertos ocupados
- Docker legacy
- contenedores residuales
- reglas de firewall previas
- permisos alterados por pruebas anteriores

### Regla 2: snapshots siempre

Para pruebas de laboratorio conviene usar snapshots antes y despues de hitos importantes:

- antes de `init-vps`
- antes de `harden-vps`
- antes del primer deploy real

### Regla 3: no endurecer SSH sin clave validada

`harden-vps` no debe correrse si todavia no se comprobo acceso por clave SSH al usuario operativo.

### Regla 4: no usar `reports/` como entorno productivo

`reports/` es util para pruebas del framework. Un proyecto real productivo debe vivir bajo la ruta estandar del host, por ejemplo:

- `/home/alex/apps/<project_name>`

## Que resultados deberia obtener un usuario

Si el framework se usa correctamente, el usuario final deberia poder:

1. tomar una VM Ubuntu o un VPS limpio
2. dejar el host en un estado estandar
3. generar un proyecto consistente sin tocar archivos del template a mano
4. desplegar el stack con un comando
5. auditar el host y el proyecto
6. generar backups basicos repetibles

## Comandos principales y su funcion

### `audit-vps`

Audita el host en modo read-only.

Sirve para detectar:

- estado del sistema operativo
- estado del usuario esperado
- estado de SSH
- estado de UFW
- disponibilidad de Docker y Compose
- existencia de rutas estandar

### `init-vps`

Prepara el host Ubuntu base.

Debe dejar:

- usuario operativo
- rutas estandar
- paquetes base
- SSH base
- UFW habilitado
- Docker y Compose listos

### `harden-vps`

Aplica endurecimiento posterior, sobre todo sobre SSH.

### `new-project`

Genera un proyecto nuevo desde el template oficial.

### `deploy-project`

Valida el proyecto, valida puertos, levanta el stack y corre checks minimos de salud.

### `backup-project`

Genera backup basico del proyecto y del stack.

### `audit-project`

Audita estructura, contenedores, endpoints y estado general del proyecto desplegado.

## Consideraciones de prueba real

En las validaciones realizadas durante el desarrollo aparecieron tres clases de problemas reales:

1. archivos de template que no debian depender de dotfiles ignorados
2. puertos por default demasiado comunes para entornos no limpios
3. checks HTTP demasiado tempranos inmediatamente despues del deploy

Esos puntos quedaron ajustados en el framework actual.

## A quien va dirigido

Este framework esta pensado para:

- administrador tecnico que prepara VPS Ubuntu
- desarrollador que necesita generar un proyecto base rapido
- operador que necesita deploy, audit y backup repetibles

## Recomendacion final de uso

Usar siempre este framework con la siguiente disciplina:

1. clonar repo
2. correr smoke tests
3. correr bloque host
4. validar acceso SSH
5. correr bloque proyecto
6. hacer auditoria y backup

Esa secuencia evita la mayor parte de los errores de orden y deja una validacion mas limpia del sistema.
