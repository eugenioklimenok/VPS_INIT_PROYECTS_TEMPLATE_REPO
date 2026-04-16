# VPS_INIT_PROYECTS_TEMPLATE_REPO

Framework para estandarizar todo el ciclo inicial de un proyecto en VPS Ubuntu:

- preparar host (`audit-vps`, `init-vps`, `harden-vps`)
- crear proyecto base fullstack (`new-project`)
- desplegar, auditar y respaldar (`deploy-project`, `audit-project`, `backup-project`)

Este repo es una plantilla operativa. Los proyectos generados (`/home/alex/apps/<proyecto>`) viven separados y pueden tener su propio Git independiente.

## Que resuelve

Problemas que ataca este framework:

- VPS nuevos configurados "a mano" de forma inconsistente
- tiempo perdido recreando estructura base de proyectos
- deploys no repetibles
- falta de auditoria y backup estandar

Resultado esperado:

1. host Ubuntu con baseline consistente
2. proyecto generado con estructura y envs correctos
3. deploy reproducible sobre Docker Compose
4. auditoria automatica de host/proyecto
5. backups versionados con timestamp

## Comandos del framework

Bloque host:

- `./bin/audit-vps`
- `./bin/init-vps`
- `./bin/harden-vps`

Bloque proyecto:

- `python3 ./bin/new-project <nombre>`
- `python3 ./bin/deploy-project <ruta_proyecto> --env dev|prod`
- `python3 ./bin/audit-project <ruta_proyecto> --env dev|prod`
- `python3 ./bin/backup-project <ruta_proyecto> --env dev|prod`

## Inicio rapido (flujo recomendado)

### 1) En VPS limpio, clonar template

```bash
sudo -i
apt update -y
apt install -y git
mkdir -p /opt/work && cd /opt/work
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
```

### 2) Auditar host inicial y bootstrap

```bash
./bin/audit-vps --expected-user alex --output /tmp/audit-before.txt || true
./bin/init-vps --user alex --timezone America/Argentina/Buenos_Aires --with-password-auth
passwd alex
su - alex
```

### 3) Trabajar como `alex`

```bash
mkdir -p /home/alex/repos && cd /home/alex/repos
git clone https://github.com/eugenioklimenok/VPS_INIT_PROYECTS_TEMPLATE_REPO.git
cd VPS_INIT_PROYECTS_TEMPLATE_REPO
chmod +x bin/*
```

### 4) Crear proyecto y validar

```bash
python3 ./bin/new-project soporte-app --base-path /home/alex/apps --domain localhost
python3 ./bin/deploy-project /home/alex/apps/soporte-app --env dev --validate-only
```

### 5) Deploy real, auditoria y backup

```bash
python3 ./bin/deploy-project /home/alex/apps/soporte-app --env dev --timeout 90
python3 ./bin/audit-project /home/alex/apps/soporte-app --env dev
python3 ./bin/backup-project /home/alex/apps/soporte-app --env dev
```

## Notas operativas importantes

### 1) `localhost` vs `127.0.0.1` en dev

Para pruebas locales con Caddy/TLS, usar `--domain localhost` evita problemas de certificado al consultar HTTPS.

Si usas `127.0.0.1`, podes ver redireccion `308` en HTTP y errores TLS al pegarle por IP al puerto HTTPS.

### 2) Redeploy idempotente

`deploy-project` ya permite redeploy cuando los puertos publicados estan ocupados por el mismo stack del proyecto.
Si los ocupa otro proceso, bloquea con mensaje claro.

### 3) Si interrumpis un deploy

Si cortaste a mitad de proceso, limpia estado parcial y redeploy:

```bash
cd /home/alex/apps/soporte-app
docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml down -v --remove-orphans
python3 /home/alex/repos/VPS_INIT_PROYECTS_TEMPLATE_REPO/bin/deploy-project /home/alex/apps/soporte-app --env dev --timeout 90
```

## Separacion entre template y proyecto generado

Modelo recomendado:

- template del framework: `VPS_INIT_PROYECTS_TEMPLATE_REPO` (este repo)
- proyecto real: `/home/alex/apps/soporte-app` (otro repo Git, remoto propio)

No mezclar commits del proyecto real dentro del repo template.

## Estructura del repo

```text
VPS_INIT_PROYECTS_TEMPLATE_REPO/
|-- README.md
|-- bin/
|-- config/
|-- docs/
|-- lib/
|   |-- bash/
|   `-- python/
|-- reports/
|-- templates/
|   `-- fullstack/
|       |-- api/
|       |   `-- app/
|       |-- caddy/
|       |-- env/
|       |-- n8n/
|       |-- postgres/
|       `-- scripts/
`-- tests/
    |-- fixtures/
    `-- smoke/
```

## Documentacion completa

Guia extendida y manuales:

- `docs/38-TDD_TECNICO_COMPLETO.md`
- `docs/35-GUIA_USUARIO_FINAL_VPS_INIT.md`
- `docs/36-MANUAL_USO_PASO_A_PASO.md`
- `docs/37-QUICKSTART.md`

Documentacion funcional por fases/contratos:

- `docs/10-CONTRATOS_BLOQUE_HOST.md`
- `docs/23-CONTRATO_NEW_PROJECT.md`
- `docs/28-CONTRATO_DEPLOY_PROJECT.md`
- `docs/31-CONTRATO_BACKUP_PROJECT.md`
- `docs/32-CONTRATO_AUDIT_PROJECT.md`
