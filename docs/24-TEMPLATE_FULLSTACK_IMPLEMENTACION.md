# Template fullstack - Implementacion

## Estado

Fase 7 implementada a nivel de template y contrato.

## Template materializado

`templates/fullstack` ya contiene:

- stack Docker base
- API FastAPI minima
- Caddyfile base
- envs base
- scripts operativos
- Makefile
- `.gitignore`
- persistencia prevista para PostgreSQL, n8n y backups

## Convencion de placeholders

El template usa placeholders `__NOMBRE__` para que `new-project` pueda renderizar el proyecto sin ambiguedad.

## Decisiones cerradas

- stack base: FastAPI + PostgreSQL + n8n + Caddy
- red del proyecto: `__PROJECT_NAME___net`
- contenedores: `__PROJECT_NAME___api`, `__PROJECT_NAME___db`, `__PROJECT_NAME___n8n`, `__PROJECT_NAME___caddy`
- envs versionados en template: `.env.example`, `.env.dev`, `.env.prod`
- scripts operativos incluidos desde el inicio
- backup PostgreSQL contemplado desde el template

## Resultado

La forma del proyecto ya quedo cerrada. La siguiente fase puede implementar `new-project` sin volver a decidir como debe lucir el proyecto generado.
