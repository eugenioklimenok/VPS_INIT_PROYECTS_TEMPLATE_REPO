# Infra comun Bash

Base tecnica compartida para los comandos del bloque host.

## Archivos

- `common.sh`: helpers generales, carga de defaults, manejo de errores, utilidades de sistema y rutas
- `log.sh`: salida humana consistente, niveles de log y soporte opcional de color
- `results.sh`: almacenamiento y resumen de resultados para comandos con hallazgos o severidades

## Objetivo

Evitar duplicacion entre:

- `audit-vps`
- `init-vps`
- `harden-vps`

## Regla

Los comandos del host deben apoyarse primero en esta capa comun antes de agregar helpers especificos por comando.
