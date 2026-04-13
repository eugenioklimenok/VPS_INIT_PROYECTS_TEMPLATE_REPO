# Manual de uso paso a paso

## Objetivo de este manual

Este manual describe como usar el framework desde cero en una VM Linux Ubuntu o en un VPS Ubuntu, en el orden correcto y con el resultado esperado en cada etapa.

El manual esta escrito para que cualquier tecnico pueda:

1. clonar el repo
2. preparar el host
3. generar un proyecto
4. desplegarlo
5. auditarlo
6. respaldarlo

## Suposiciones

El manual asume:

- Ubuntu 24.04 LTS o similar
- acceso sudo disponible
- salida a internet
- Git disponible o instalable
- entorno limpio o restaurado desde snapshot

## Regla de oro

No mezclar el orden de los pasos.

Secuencia correcta:

1. prerequisitos
2. clonacion
3. smoke tests
4. `audit-vps`
5. `init-vps`
6. `audit-vps`
7. clave SSH
8. `harden-vps`
9. `audit-vps`
10. `new-project`
11. `deploy-project`
12. `audit-project`
13. `backup-project`
14. `audit-project`

## Parte A - Preparacion inicial

## Paso 1: confirmar conectividad

```bash
ping -c 3 github.com
```

Resultado esperado:

- respuestas correctas

Si falla:

- revisar red de la VM
- revisar modo NAT o Bridged

## Paso 2: actualizar sistema e instalar prerequisitos

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl wget python3 python3-pip python3-venv make ca-certificates gnupg lsb-release unzip tar gzip rsync nano
```

Resultado esperado:

- paquetes instalados sin errores graves

## Paso 3: clonar el repo

```bash
mkdir -p ~/work
cd ~/work
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd ~/work/VPS_INIT_PROYECTS_TEMPLATE_REPO
```

Resultado esperado:

- repo clonado correctamente

## Paso 4: preparar variables de trabajo

```bash
chmod +x bin/*
export FRAMEWORK_DIR="$PWD"
export REPORT_DIR="$HOME/vps-framework-reports"
mkdir -p "$REPORT_DIR"
```

## Parte B - Validacion del framework

## Paso 5: correr smoke tests

```bash
python3 -m unittest tests/smoke/test_framework_smoke.py
python3 -m unittest tests.test_project_ops
```

Resultado esperado:

- ambos tests en `OK`

Si falla:

- no continuar con el resto
- revisar salida del test exacto

## Paso 6: probar ayuda de comandos

```bash
./bin/audit-vps --help
./bin/init-vps --help
./bin/harden-vps --help
python3 ./bin/new-project --help
python3 ./bin/deploy-project --help
python3 ./bin/backup-project --help
python3 ./bin/audit-project --help
```

Resultado esperado:

- todos los comandos responden con ayuda

## Parte C - Bloque host

## Paso 7: auditoria inicial del host

```bash
sudo ./bin/audit-vps --expected-user alex --output "$REPORT_DIR/01-audit-before.txt"
cat "$REPORT_DIR/01-audit-before.txt"
```

Resultado esperado:

- informe del host
- pueden aparecer warnings o fails si el host esta sin preparar

Interpretacion:

- `OK`: ese punto ya esta alineado
- `WARN`: hay una desviacion menor o tolerable
- `FAIL`: hay una desviacion fuerte que impide considerar el host alineado

## Paso 8: bootstrap del host

Primera ejecucion recomendada:

```bash
sudo ./bin/init-vps \
  --user alex \
  --timezone America/Argentina/Buenos_Aires \
  --with-password-auth \
  --report "$REPORT_DIR/02-init-vps.txt"
```

Que hace:

- asegura usuario `alex`
- asegura rutas estandar
- instala paquetes base
- configura SSH base
- configura UFW
- instala Docker y Compose

## Paso 9: revisar resultado del bootstrap

```bash
cat "$REPORT_DIR/02-init-vps.txt"
id alex
ls -la /home/alex
ls -la /home/alex/apps
ls -la /home/alex/repos
ls -la /home/alex/backups
ls -la /home/alex/scripts
docker --version
docker compose version
sudo ufw status
systemctl status ssh --no-pager
```

Resultado esperado:

- usuario `alex` existente
- rutas creadas
- Docker y Compose disponibles
- UFW activo

## Paso 10: reauditar el host

```bash
sudo ./bin/audit-vps --expected-user alex --strict --output "$REPORT_DIR/03-audit-after-init.txt"
cat "$REPORT_DIR/03-audit-after-init.txt"
```

Resultado esperado:

- clara mejora respecto a la auditoria inicial

## Paso 11: preparar acceso SSH por clave

No avanzar con hardening sin esto.

En Windows host:

```powershell
ssh-keygen -t ed25519
type $env:USERPROFILE\.ssh\id_ed25519.pub
```

Copiar clave publica.

En la VM:

```bash
sudo mkdir -p /home/alex/.ssh
sudo nano /home/alex/.ssh/authorized_keys
sudo chown -R alex:alex /home/alex/.ssh
sudo chmod 700 /home/alex/.ssh
sudo chmod 600 /home/alex/.ssh/authorized_keys
```

Obtener IP:

```bash
ip a
```

Probar desde el host:

```powershell
ssh alex@IP_DE_LA_VM
```

Resultado esperado:

- acceso por clave al usuario `alex`

## Paso 12: hardening

```bash
sudo ./bin/harden-vps \
  --user alex \
  --report "$REPORT_DIR/04-harden-vps.txt"
```

Revisar reporte:

```bash
cat "$REPORT_DIR/04-harden-vps.txt"
```

## Paso 13: auditoria posterior al hardening

```bash
sudo ./bin/audit-vps --expected-user alex --strict --output "$REPORT_DIR/05-audit-after-harden.txt"
cat "$REPORT_DIR/05-audit-after-harden.txt"
```

Resultado esperado:

- root login deshabilitado
- pubkey auth habilitado
- si password auth sigue habilitado, puede verse como warning segun configuracion

## Parte D - Bloque proyecto

## Paso 14: generar proyecto

```bash
python3 ./bin/new-project smoke-app \
  --base-path "$PWD/reports/manual_debug" \
  --domain 127.0.0.1
```

Resultado esperado:

- proyecto generado correctamente
- ruta creada bajo `reports/manual_debug/smoke-app`

## Paso 15: revisar env generado

```bash
cat "$PWD/reports/manual_debug/smoke-app/env/.env.dev"
```

Resultado esperado:

- puertos default altos:
  - `API_PORT=18000`
  - `POSTGRES_PORT=15432`
  - `N8N_PORT=15678`
  - `CADDY_HTTP_PORT=18080`
  - `CADDY_HTTPS_PORT=18443`

## Paso 16: validacion estructural previa

```bash
python3 ./bin/deploy-project "$PWD/reports/manual_debug/smoke-app" --env dev --validate-only
```

Resultado esperado:

- validacion correcta

Si falla:

- revisar archivos faltantes
- revisar env
- revisar placeholders

## Paso 17: deploy real

```bash
python3 ./bin/deploy-project "$PWD/reports/manual_debug/smoke-app" --env dev
```

Que hace:

- valida estructura
- valida puertos
- valida que no haya placeholders
- detecta puertos ocupados antes del `up`
- ejecuta `docker compose up -d --build`
- espera warm-up basico
- revisa root, `/health` y `/n8n/`

Resultado esperado:

- `Deploy completado correctamente`

## Paso 18: validaciones manuales del stack

```bash
cd "$PWD/reports/manual_debug/smoke-app"
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml ps
curl http://127.0.0.1:18080/
curl http://127.0.0.1:18080/health
curl -I http://127.0.0.1:18080/n8n/
```

Resultado esperado:

- contenedores `running`
- endpoints respondiendo

Si falla:

```bash
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml logs -f --tail=200
```

## Paso 19: auditar proyecto

```bash
python3 ./bin/audit-project "$PWD/reports/manual_debug/smoke-app" --env dev
```

Resultado esperado:

- estructura correcta
- contenedores visibles
- endpoints operativos

Guardar JSON opcional:

```bash
python3 ./bin/audit-project "$PWD/reports/manual_debug/smoke-app" \
  --env dev \
  --json \
  --output "$REPORT_DIR/06-audit-project.json"
```

## Paso 20: generar backup

```bash
python3 ./bin/backup-project "$PWD/reports/manual_debug/smoke-app" --env dev
```

Resultado esperado:

- backup generado

Verificar:

```bash
ls -lah "$PWD/reports/manual_debug/smoke-app/backups"
```

## Paso 21: auditar otra vez

```bash
python3 ./bin/audit-project "$PWD/reports/manual_debug/smoke-app" --env dev
```

Resultado esperado:

- backups detectados

## Errores frecuentes y como leerlos

## Error: `env file no encontrado`

Causa probable:

- proyecto viejo generado antes de una correccion
- proyecto incompleto o parcialmente borrado

Accion:

- borrar el proyecto de prueba y regenerarlo

## Error: `puertos ocupados en el host antes del deploy`

Causa probable:

- servicio previo en el host
- contenedor viejo corriendo
- VM contaminada por prueba anterior

Accion:

- identificar puertos:

```bash
sudo ss -ltnp | grep -E ':(18000|15432|15678|18080|18443)\b' || true
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

- limpiar contenedores o procesos anteriores

## Error: `fallo check HTTP ... connection refused`

Causa probable:

- stack aun arrancando
- servicio caido
- Caddy o API no llegaron a estado listo

Accion:

- revisar logs:

```bash
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml logs -f --tail=200
```

## Error: `permission denied` al borrar proyecto

Causa probable:

- archivos bind-mounted creados por Docker con permisos de root

Accion:

```bash
sudo rm -rf "$PWD/reports/manual_debug/smoke-app"
```

## Error: Docker legacy o Compose faltante

Accion:

- volver al bloque host
- reauditar
- confirmar `docker compose version`

## Checklist final

La prueba se considera correcta si:

1. smoke tests del framework pasan
2. `audit-vps` inicial corre
3. `init-vps` deja host alineado
4. `harden-vps` no rompe acceso SSH
5. `new-project` genera un proyecto completo
6. `deploy-project --validate-only` pasa
7. `deploy-project` real completa
8. `audit-project` informa estado usable
9. `backup-project` genera artefactos
10. `audit-project` posterior ve backups

## Recomendacion de operacion real

Una vez validado en laboratorio:

- usar un VPS limpio real
- repetir la misma secuencia
- mover proyectos reales a `/home/alex/apps`
- usar snapshots o backups del proveedor antes de cambios grandes
