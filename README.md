# VPS_INIT_PROYECTS_TEMPLATE_REPO

Framework operativo para Ubuntu VPS con dos bloques:

- Host: `audit-vps`, `init-vps`, `harden-vps`
- Proyecto: `new-project`, `deploy-project`, `audit-project`, `backup-project`

Baseline oficial v1.1:

- Stack: FastAPI + PostgreSQL + n8n + Caddy (Docker Compose)
- n8n usa PostgreSQL obligatoriamente (no SQLite)
- Un motor PostgreSQL por proyecto con 2 DB lógicas:
  - `APP_DB_*`
  - `N8N_DB_*`

## Prerrequisitos

- Ubuntu 24.04 LTS (recomendado)
- Python 3.12+
- Docker Engine + Docker Compose plugin
- Git

## Flujo rápido (framework)

```bash
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
python3 -m unittest tests/smoke/test_framework_smoke.py
```

## Flujo host (VPS limpio)

```bash
sudo ./bin/audit-vps --expected-user alex --output /tmp/audit-before.txt || true
sudo ./bin/init-vps --user alex --timezone America/Argentina/Buenos_Aires --with-password-auth
sudo passwd alex
sudo ./bin/harden-vps --user alex
sudo ./bin/audit-vps --expected-user alex --output /tmp/audit-after.txt
```

## Flujo proyecto

```bash
python3 ./bin/new-project soporte-app --base-path /home/alex/apps --domain localhost
python3 ./bin/deploy-project /home/alex/apps/soporte-app --env dev --validate-only
python3 ./bin/deploy-project /home/alex/apps/soporte-app --env dev --timeout 90
python3 ./bin/audit-project /home/alex/apps/soporte-app --env dev
python3 ./bin/backup-project /home/alex/apps/soporte-app --env dev
```

## Política `.env`

- Se versiona: `env/.env.example`
- No se versiona: `env/.env.dev`, `env/.env.prod` (secretos reales)
- Inicialización recomendada:
  1. `cp env/.env.example env/.env.dev`
  2. `cp env/.env.example env/.env.prod`
  3. ajustar credenciales y dominio
- Variables DB explícitas:
  - Admin Postgres: `POSTGRES_ADMIN_USER`, `POSTGRES_ADMIN_PASSWORD`
  - DB App: `APP_DB_NAME`, `APP_DB_USER`, `APP_DB_PASSWORD`
  - DB n8n: `N8N_DB_NAME`, `N8N_DB_USER`, `N8N_DB_PASSWORD`

## Flujo Git recomendado (sin mezcla)

1. Repo framework (este repo): evoluciona comandos, template y docs.
2. Proyecto generado: repo Git propio e independiente.

Nacimiento de repo nuevo para proyecto generado (`/home/alex/apps/soporte-app`):

```bash
cd /home/alex/apps/soporte-app
rm -rf .git
git init
git add -A
git commit -m "Initial scaffold from VPS_INIT_PROYECTS_TEMPLATE_REPO"
git branch -M main
git remote add origin <URL_REPO_PROYECTO>
git push -u origin main
```

## Backup del proyecto

`backup-project` crea:

- dump comprimido DB app: `*_app_pg_<timestamp>.sql.gz`
- dump comprimido DB n8n: `*_n8n_pg_<timestamp>.sql.gz`
- tar.gz de configuración (`env`, compose, caddy, makefile)
- manifest JSON con metadata de artefactos y DBs

## Documentación principal

- TDD técnico actual: `docs/38-TDD_TECNICO_COMPLETO.md`
- Quickstart: `docs/37-QUICKSTART.md`
- Manual usuario final: `docs/35-GUIA_USUARIO_FINAL_VPS_INIT.md`
