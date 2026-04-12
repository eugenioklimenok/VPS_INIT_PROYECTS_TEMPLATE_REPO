# Alcance y principios

## Alcance del framework

El framework cubre:

- preparacion base de VPS Ubuntu Server LTS
- configuracion del usuario operativo estandar
- estructura base de directorios del host
- instalacion de paquetes base
- configuracion SSH y firewall
- instalacion de Docker y Compose
- generacion de un proyecto full stack desde template
- despliegue del proyecto
- auditoria del host y del proyecto
- backup base de datos y archivos criticos

## Fuera de alcance inicial

Queda fuera de la primera iteracion:

- CI/CD formal
- clustering
- balanceo multi host
- observabilidad enterprise
- orquestacion multi servidor
- alta disponibilidad avanzada
- secretos centralizados externos

## Principios rectores

### 1. Una sola fuente operativa

Los cambios estructurales deben vivir en el framework y no en ajustes manuales dispersos sobre el servidor.

### 2. Auditoria antes y despues

No se automatiza a ciegas. Debe existir verificacion antes de cambiar y verificacion despues de cambiar.

### 3. Host minimo, servicios en Docker

El host debe quedarse con lo justo:

- Docker
- utilidades base
- SSH
- UFW
- scripts operativos

Los servicios de aplicacion deben vivir preferentemente en contenedores.

### 4. Portabilidad

El flujo debe ser repetible en nuevos VPS sin reescritura manual del proceso.

### 5. Orden desde el inicio

Nombres, rutas, variables, estructura y backups deben quedar definidos desde la primera version.

### 6. Separacion de responsabilidades

Cada comando debe tener una responsabilidad clara. No se deben mezclar bootstrap del host, scaffolding de proyecto y deploy del stack en un solo script.

### 7. Evolucion por fases

Primero se consolida el VPS base. Luego el template de proyecto. Despues deploy, backup y auditoria del proyecto.
