from __future__ import annotations

import argparse
import gzip
import json
import sys
import tarfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from vps_init_framework.project_ops import (
    ProjectOpsError,
    compose_base_command,
    ensure_docker_available,
    ensure_validation_ok,
    run_command,
    validate_project_layout,
)


@dataclass
class BackupConfig:
    project_path: Path
    env_name: str
    env_file: Path
    output_dir: Path
    validate_only: bool
    skip_db_dump: bool
    skip_config_archive: bool


class UsageError(Exception):
    pass


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = build_config(args)
        validation = validate_project_layout(config.project_path, config.env_file)
        ensure_validation_ok(validation)
        output_dir = prepare_output_dir(config)
        if config.validate_only:
            print_validation_summary(config, output_dir)
            return 0
        if not config.skip_db_dump:
            ensure_docker_available()
        created_files = create_backup(config, validation.env_values, output_dir)
    except UsageError as exc:
        print(f"Usage error: {exc}", file=sys.stderr)
        return 3
    except ProjectOpsError as exc:
        print(f"Backup error: {exc}", file=sys.stderr)
        return 2

    print_backup_summary(config, created_files)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="backup-project", description="Genera backups basicos del proyecto.")
    parser.add_argument("project_path", nargs="?", default=".", help="Ruta del proyecto. Default: directorio actual.")
    parser.add_argument("--env", dest="env_name", default="dev", choices=("dev", "prod"), help="Entorno a respaldar.")
    parser.add_argument("--output-dir", help="Directorio de salida para backups. Default: <project>/backups.")
    parser.add_argument("--validate-only", action="store_true", help="Valida estructura y plan de backup sin ejecutar Docker.")
    parser.add_argument("--skip-db-dump", action="store_true", help="No generar dump PostgreSQL.")
    parser.add_argument("--skip-config-archive", action="store_true", help="No generar tar.gz de envs, compose y caddy.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> BackupConfig:
    project_path = Path(args.project_path).expanduser().resolve()
    env_file = project_path / "env" / f".env.{args.env_name}"
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else project_path / "backups"
    return BackupConfig(
        project_path=project_path,
        env_name=args.env_name,
        env_file=env_file,
        output_dir=output_dir,
        validate_only=args.validate_only,
        skip_db_dump=args.skip_db_dump,
        skip_config_archive=args.skip_config_archive,
    )


def prepare_output_dir(config: BackupConfig) -> Path:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    return config.output_dir


def create_backup(config: BackupConfig, env_values: dict[str, str], output_dir: Path) -> list[Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    project_name = env_values["PROJECT_NAME"]
    created_files: list[Path] = []

    if not config.skip_db_dump:
        dumps = (
            ("app", env_values["APP_DB_USER"], env_values["APP_DB_NAME"]),
            ("n8n", env_values["N8N_DB_USER"], env_values["N8N_DB_NAME"]),
        )
        for label, db_user, db_name in dumps:
            db_backup = output_dir / f"{project_name}_{label}_pg_{timestamp}.sql.gz"
            result = run_command(
                compose_base_command(config.project_path, config.env_file, config.env_name)
                + ["exec", "-T", "db", "pg_dump", "-U", db_user, "-d", db_name],
                cwd=config.project_path,
                error_prefix=f"fallo dump PostgreSQL ({label})",
                text=False,
            )
            with gzip.open(db_backup, "wb") as handle:
                handle.write(result.stdout)
            created_files.append(db_backup)

    if not config.skip_config_archive:
        config_backup = output_dir / f"{project_name}_config_{timestamp}.tar.gz"
        with tarfile.open(config_backup, "w:gz") as archive:
            for relative in (
                "docker-compose.yml",
                "compose.override.yml",
                "Makefile",
                "caddy/Caddyfile",
                "env/.env.example",
                f"env/.env.{config.env_name}",
            ):
                archive.add(config.project_path / relative, arcname=relative)
        created_files.append(config_backup)

    manifest = output_dir / f"{project_name}_manifest_{timestamp}.json"
    manifest.write_text(
        json.dumps(
            {
                "project_name": project_name,
                "env": config.env_name,
                "created_at_utc": timestamp,
                "databases": {
                    "app": {"name": env_values["APP_DB_NAME"], "user": env_values["APP_DB_USER"]},
                    "n8n": {"name": env_values["N8N_DB_NAME"], "user": env_values["N8N_DB_USER"]},
                },
                "files": [str(path.name) for path in created_files],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    created_files.append(manifest)
    return created_files


def print_validation_summary(config: BackupConfig, output_dir: Path) -> None:
    print("Validacion de backup correcta")
    print(f"Proyecto: {config.project_path}")
    print(f"Env: {config.env_name}")
    print(f"Output dir: {output_dir}")
    print("Resultado: estructura y plan de backup correctos")


def print_backup_summary(config: BackupConfig, created_files: list[Path]) -> None:
    print("Backup completado correctamente")
    print(f"Proyecto: {config.project_path}")
    print(f"Env: {config.env_name}")
    print("Artefactos creados:")
    for path in created_files:
        print(f"- {path}")
