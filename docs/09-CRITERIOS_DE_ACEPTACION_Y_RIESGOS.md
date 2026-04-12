# Criterios de aceptacion y riesgos

## Criterios de aceptacion generales

El framework se considera bien encaminado si:

- la documentacion define un flujo coherente de punta a punta
- cada comando tiene responsabilidad clara
- el host queda auditable
- el proyecto generado queda estructurado y desplegable
- los backups son previsibles
- el stack completo es repetible

## Criterios de aceptacion por comando

### `audit-vps`

- no modifica el servidor
- detecta desvio del estandar del host
- devuelve salida legible y severidades utiles

### `init-vps`

- deja un Ubuntu nuevo en estado base operativo
- es razonablemente idempotente
- falla de forma segura ante errores criticos

### `harden-vps`

- reduce superficie de acceso sin romper operacion
- permite pasar a acceso por key solamente

### `new-project`

- genera estructura uniforme
- valida inputs
- crea archivos base coherentes

### `deploy-project`

- levanta stack valido
- informa fallos de configuracion
- ejecuta validaciones minimas de salud

### `backup-project`

- genera artefactos con timestamp
- deja ruta de salida previsible
- contempla restauracion basica

### `audit-project`

- detecta problemas de contenedores
- detecta faltantes de backups o volumenes
- ayuda a diagnosticar estado general

## Riesgos a evitar

### 1. Mezclar framework y proyecto

Riesgo:

- que cada proyecto termine cargando logica que deberia vivir en el framework

### 2. Automatizar sin contrato

Riesgo:

- scripts que hacen cosas correctas en apariencia pero con criterios distintos entre si

### 3. Meter demasiado en el host

Riesgo:

- perder portabilidad y volver fragil el entorno

### 4. No fijar naming desde el inicio

Riesgo:

- stacks desordenados, rutas distintas y scripts menos mantenibles

### 5. Manejar secretos de forma incorrecta

Riesgo:

- exponer `.env` reales o meter credenciales en Git

### 6. Saltar pruebas en VPS real

Riesgo:

- tener una documentacion buena pero una implementacion no validada en condiciones reales

## Decision operativa

La siguiente etapa no debe ser escribir todo de golpe. La siguiente etapa debe ser implementar el bloque de host primero, validarlo en entorno real y luego avanzar con el template de proyecto.
