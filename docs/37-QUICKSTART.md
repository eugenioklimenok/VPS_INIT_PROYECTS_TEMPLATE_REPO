# Quickstart

## Para que sirve

Este quickstart permite probar el framework rapido sobre una VM Ubuntu limpia o restaurada desde snapshot.

Usa el flujo recomendado:

1. preparar host
2. auditar host
3. inicializar host
4. endurecer host
5. generar proyecto
6. desplegar
7. auditar
8. respaldar

## Requisitos minimos

- Ubuntu 24.04 LTS o similar
- usuario con `sudo`
- internet funcionando
- snapshot limpio recomendado

## Paso 1: instalar prerequisitos

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl wget python3 python3-pip python3-venv make ca-certificates gnupg lsb-release unzip tar gzip rsync nano
```

## Paso 2: clonar repo

```bash
mkdir -p ~/work
cd ~/work
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd ~/work/VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
export FRAMEWORK_DIR="$PWD"
export REPORT_DIR="$HOME/vps-framework-reports"
mkdir -p "$REPORT_DIR"
```

## Paso 3: validar framework

```bash
python3 -m unittest tests/smoke/test_framework_smoke.py
python3 -m unittest tests.test_project_ops
```

Resultado esperado:

- ambos tests en `OK`

## Paso 4: auditar host

```bash
sudo ./bin/audit-vps --expected-user alex --output "$REPORT_DIR/01-audit-before.txt"
cat "$REPORT_DIR/01-audit-before.txt"
```

## Paso 5: inicializar host

```bash
sudo ./bin/init-vps \
  --user alex \
  --timezone America/Argentina/Buenos_Aires \
  --with-password-auth \
  --report "$REPORT_DIR/02-init-vps.txt"
```

Verificar:

```bash
cat "$REPORT_DIR/02-init-vps.txt"
docker --version
docker compose version
sudo ufw status
```

## Paso 6: reauditar host

```bash
sudo ./bin/audit-vps --expected-user alex --strict --output "$REPORT_DIR/03-audit-after-init.txt"
cat "$REPORT_DIR/03-audit-after-init.txt"
```

## Paso 7: preparar clave SSH

En Windows host:

```powershell
ssh-keygen -t ed25519
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

En Ubuntu:

```bash
sudo mkdir -p /home/alex/.ssh
sudo nano /home/alex/.ssh/authorized_keys
sudo chown -R alex:alex /home/alex/.ssh
sudo chmod 700 /home/alex/.ssh
sudo chmod 600 /home/alex/.ssh/authorized_keys
```

## Paso 8: endurecer host

```bash
sudo ./bin/harden-vps \
  --user alex \
  --report "$REPORT_DIR/04-harden-vps.txt"

sudo ./bin/audit-vps --expected-user alex --strict --output "$REPORT_DIR/05-audit-after-harden.txt"
cat "$REPORT_DIR/05-audit-after-harden.txt"
```

## Paso 9: generar proyecto de prueba

```bash
python3 ./bin/new-project smoke-app \
  --base-path "$PWD/reports/manual_debug" \
  --domain 127.0.0.1
```

Verificar env:

```bash
cat "$PWD/reports/manual_debug/smoke-app/env/.env.dev"
```

Puertos default esperados:

- `API_PORT=18000`
- `POSTGRES_PORT=15432`
- `N8N_PORT=15678`
- `CADDY_HTTP_PORT=18080`
- `CADDY_HTTPS_PORT=18443`

## Paso 10: validar y desplegar

```bash
python3 ./bin/deploy-project "$PWD/reports/manual_debug/smoke-app" --env dev --validate-only
python3 ./bin/deploy-project "$PWD/reports/manual_debug/smoke-app" --env dev
```

## Paso 11: validar stack

```bash
cd "$PWD/reports/manual_debug/smoke-app"
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml ps
curl http://127.0.0.1:18080/
curl http://127.0.0.1:18080/health
curl -I http://127.0.0.1:18080/n8n/
```

## Paso 12: auditar y respaldar

```bash
python3 "$FRAMEWORK_DIR/bin/audit-project" "$FRAMEWORK_DIR/reports/manual_debug/smoke-app" --env dev
python3 "$FRAMEWORK_DIR/bin/backup-project" "$FRAMEWORK_DIR/reports/manual_debug/smoke-app" --env dev
python3 "$FRAMEWORK_DIR/bin/audit-project" "$FRAMEWORK_DIR/reports/manual_debug/smoke-app" --env dev
ls -lah "$FRAMEWORK_DIR/reports/manual_debug/smoke-app/backups"
```

## Si algo falla

Logs del stack:

```bash
cd "$FRAMEWORK_DIR/reports/manual_debug/smoke-app"
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml logs -f --tail=200
```

Puertos ocupados:

```bash
sudo ss -ltnp | grep -E ':(18000|15432|15678|18080|18443)\b' || true
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

## Resultado final esperado

La prueba se considera correcta si:

1. host queda alineado despues de `init-vps` y `harden-vps`
2. `new-project` genera `smoke-app` sin tocar archivos a mano
3. `deploy-project` completa el deploy
4. `audit-project` muestra estado usable
5. `backup-project` genera artefactos en `backups/`

## Documentacion complementaria

- `docs/35-GUIA_USUARIO_FINAL_VPS_INIT.md`
- `docs/36-MANUAL_USO_PASO_A_PASO.md`
