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
  - `N8N_SECURE_COOKIE` (`false` en dev/lab HTTP, `true` en prod HTTPS)

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

### 3) Auditar host inicial (read-only)

```bash
./bin/audit-vps --expected-user alex --output /tmp/audit-before.txt || true
cat /tmp/audit-before.txt
```

Tambien soportado:

```bash
python3 ./bin/audit-vps --expected-user alex --output /tmp/audit-before.txt || true
```

### 4) Inicializar host

```bash
python3 ./bin/init-vps --user alex --timezone America/Argentina/Buenos_Aires --with-password-auth --public-key "ssh-ed25519 AAAA... alex@laptop"
```

Contrato de acceso SSH en `init-vps`:
- instala `~alex/.ssh/authorized_keys` con ownership/permisos correctos
- falla si no recibe clave publica (salvo `--allow-without-public-key` explicito)
- no desactiva password auth ni root login en esta fase

### 5) Validar acceso SSH de alex

```bash
ssh -i <ruta-clave-privada> alex@<ip-vps>
```

### 6) Harden host (paso final SSH)

```bash
python3 ./bin/harden-vps --user alex
python3 ./bin/audit-vps --expected-user alex --output /tmp/audit-after.txt
cat /tmp/audit-after.txt
```

`harden-vps` valida hardening efectivo con `sshd -T` (no solo cambios en archivos) y falla si `PasswordAuthentication`, `PubkeyAuthentication`, `PermitRootLogin` o `KbdInteractiveAuthentication` no quedan en el baseline esperado.

### 7) Cambiar a usuario operativo

```bash
su - alex
mkdir -p /home/alex/repos
cd /home/alex/repos
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
```

### 8) Generar proyecto

```bash
python3 ./bin/new-project soporte-app --base-path /home/alex/apps --domain 192.168.1.38
```

Regla de dominio en dev:
- `new-project --domain` ahora se respeta en `.env.dev`, `.env.example` y `.env.prod`.
- El acceso dev/lab queda coherente con ese valor.

### 9) Revisar envs generados

```bash
cd /home/alex/apps/soporte-app
ls -la env
sed -n '1,220p' env/.env.dev
sed -n '1,220p' env/.env.prod
```

### 10) Validar deploy sin levantar contenedores

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/deploy-project /home/alex/apps/soporte-app --env dev --validate-only
```

### 11) Deploy real

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/deploy-project /home/alex/apps/soporte-app --env dev --timeout 90
```

Acceso dev/lab esperado (HTTP puro):
- `http://<ip-o-domain>:<CADDY_HTTP_PORT>/`
- `http://<ip-o-domain>:<CADDY_HTTP_PORT>/n8n/`

Notas:
- En dev, Caddy no fuerza redirect HTTPS.
- n8n usa `N8N_SECURE_COOKIE=false`.
- En prod/HTTPS, usar `N8N_SECURE_COOKIE=true`.

### 12) Auditar proyecto y validar runtime

```bash
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/audit-project /home/alex/apps/soporte-app --env dev
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml ps
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml logs --tail=120
```

### 13) Ejecutar backup y verificar artefactos

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
# restore completo recomendado (limpia y recrea DBs antes de restaurar)
./scripts/restore.sh dev backups/20260415_0130 all --clean

# restore solo app
./scripts/restore.sh dev backups/20260415_0130 app --clean

# restore solo n8n
./scripts/restore.sh dev backups/20260415_0130 n8n --clean
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
