# VPS_INIT_PROYECTS_TEMPLATE_REPO

Framework operativo para Ubuntu VPS:

- Host: `audit-vps`, `init-vps`, `harden-vps`
- Proyecto: `new-project`, `deploy-project`, `audit-project`, `backup-project`

Baseline v1.1:

- FastAPI + PostgreSQL + n8n + Caddy (Docker Compose)
- n8n usa PostgreSQL solamente (sin SQLite)
- un PostgreSQL por proyecto con DB separadas:
  - `APP_DB_*`
  - `N8N_DB_*`

## Prerrequisitos

- Ubuntu 24.04 LTS recomendado
- Python 3.12+
- Docker Engine + Docker Compose plugin
- Git

## Politica `.env`

- Se versiona: `env/.env.example`
- No se versiona: `env/.env.dev`, `env/.env.prod`
- Variables DB obligatorias:
  - `POSTGRES_ADMIN_USER`, `POSTGRES_ADMIN_PASSWORD`
  - `APP_DB_NAME`, `APP_DB_USER`, `APP_DB_PASSWORD`
  - `N8N_DB_NAME`, `N8N_DB_USER`, `N8N_DB_PASSWORD`

## Runbook operativo real (primer deploy)

### 1) Preparar VPS (root o sudo)

```bash
sudo -i
apt update -y
apt install -y git
```

### 2) Clonar framework

```bash
mkdir -p /opt/work
cd /opt/work
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
```

### 3) Auditar host inicial

```bash
./bin/audit-vps --expected-user alex --output /tmp/audit-before.txt || true
cat /tmp/audit-before.txt
```

### 4) Inicializar host

```bash
./bin/init-vps --user alex --timezone America/Argentina/Buenos_Aires --with-password-auth
passwd alex
```

### 5) Harden host

```bash
./bin/harden-vps --user alex
./bin/audit-vps --expected-user alex --output /tmp/audit-after.txt
cat /tmp/audit-after.txt
```

### 6) Cambiar a usuario operativo

```bash
su - alex
mkdir -p /home/alex/repos
cd /home/alex/repos
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
```

### 7) Generar proyecto

```bash
python3 ./bin/new-project soporte-app --base-path /home/alex/apps --domain localhost
```

### 8) Revisar envs generados

```bash
cd /home/alex/apps/soporte-app
ls -la env
sed -n '1,220p' env/.env.dev
sed -n '1,220p' env/.env.prod
```

### 9) Validar deploy sin levantar contenedores

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/deploy-project /home/alex/apps/soporte-app --env dev --validate-only
```

### 10) Deploy real

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/deploy-project /home/alex/apps/soporte-app --env dev --timeout 90
```

### 11) Auditar proyecto y validar runtime

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/audit-project /home/alex/apps/soporte-app --env dev
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml ps
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml logs --tail=120
```

### 12) Ejecutar backup y verificar artefactos

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/backup-project /home/alex/apps/soporte-app --env dev
find /home/alex/apps/soporte-app/backups -maxdepth 2 -type f | sort
```

Esperado por corrida:

- `backups/YYYYMMDD_HHMM/app_db.sql`
- `backups/YYYYMMDD_HHMM/n8n_db.sql`
- `backups/YYYYMMDD_HHMM/config.tar.gz`
- `backups/YYYYMMDD_HHMM/metadata.json`

## Restore operativo

Desde proyecto generado:

```bash
# restore completo (app + n8n) desde carpeta de corrida
./scripts/restore.sh dev backups/20260415_0130 all

# restore solo app
./scripts/restore.sh dev backups/20260415_0130/app_db.sql app

# restore solo n8n
./scripts/restore.sh dev backups/20260415_0130/n8n_db.sql n8n
```

## Flujo Git recomendado (sin mezclar framework y proyecto)

1. El framework se versiona en este repo.
2. Cada proyecto generado vive en otro repo Git remoto.

Inicializar Git del proyecto generado:

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

## Documentacion baseline

- `docs/38-TDD_TECNICO_COMPLETO.md`
