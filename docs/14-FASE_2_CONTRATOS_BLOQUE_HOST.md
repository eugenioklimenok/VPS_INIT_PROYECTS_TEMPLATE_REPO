# Fase 2 - Contratos del bloque host

## Estado

Fase 2 cerrada.

## Objetivo cumplido

Quedo cerrado el contrato funcional del bloque host con definicion precisa de:

- alcance
- flags
- entradas
- salidas
- exit codes
- limites operativos

para:

- `audit-vps`
- `init-vps`
- `harden-vps`

## Entregables de esta fase

- `docs/10-CONTRATOS_BLOQUE_HOST.md`
- `docs/11-CONTRATO_AUDIT_VPS.md`
- `docs/12-CONTRATO_INIT_VPS.md`
- `docs/13-CONTRATO_HARDEN_VPS.md`

## Criterio de aprobacion cumplido

La fase se considera cerrada porque ya no hay ambiguedad sobre:

1. que hace cada comando
2. que no hace cada comando
3. con que opciones se ejecuta
4. que necesita como input
5. que entrega como output
6. con que codigos termina

## Lo que todavia no entra

Fase 2 no implementa:

- scripts reales en `bin/`
- librerias Bash reales
- chequeos reales del host
- cambios reales sobre el servidor

## Resultado operativo de esta fase

La siguiente fase ya puede implementar la base tecnica del bloque host sin necesidad de seguir redefiniendo contratos.
