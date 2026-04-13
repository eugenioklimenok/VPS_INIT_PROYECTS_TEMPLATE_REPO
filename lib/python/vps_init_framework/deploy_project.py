from __future__ import annotations

import argparse
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from vps_init_framework.project_ops import (
    HTTP_OK_STATUSES,
    ProjectOpsError,
    compose_base_command,
    ensure_docker_available,
    ensure_http_status,
    ensure_validation_ok,
    find_port_conflicts,
    get_expected_services,
    get_running_services,
    get_published_ports,
    is_tcp_port_in_use,
    run_command,
    validate_project_layout,
)


@dataclass
class DeployConfig:
    project_path: Path
    env_name: str
    env_file: Path
    validate_only: bool
    no_build: bool
    skip_health_checks: bool
    timeout: int
    env_values: dict[str, str]


class UsageError(Exception):
    pass


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = build_config(args)
        print("[STEP] Validando estructura y env del proyecto")
        validate_project(config)
        if config.validate_only:
            print_validation_summary(config)
            return 0
        print("[STEP] Verificando Docker y Compose")
        ensure_docker_available()
        print("[STEP] Ejecutando deploy real (docker compose up)")
        run_compose_up(config)
        if not config.skip_health_checks:
            print("[STEP] Ejecutando checks de salud del stack")
            run_health_checks(config)
    except UsageError as exc:
        print(f"Usage error: {exc}", file=sys.stderr)
        return 3
    except ProjectOpsError as exc:
        print(f"Deploy error: {exc}", file=sys.stderr)
        return 2

    print_deploy_summary(config)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="deploy-project",
        description="Valida y despliega un proyecto generado por el framework.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Ruta del proyecto a desplegar. Default: directorio actual.")
    parser.add_argument("--env", dest="env_name", default="dev", choices=("dev", "prod"), help="Entorno a desplegar: dev o prod.")
    parser.add_argument("--validate-only", action="store_true", help="Valida estructura y envs sin ejecutar docker compose.")
    parser.add_argument("--no-build", action="store_true", help="Ejecuta docker compose up -d sin --build.")
    parser.add_argument("--skip-health-checks", action="store_true", help="Omite checks HTTP y de contenedores tras el deploy.")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout en segundos para checks HTTP. Default: 30.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> DeployConfig:
    project_path = Path(args.project_path).expanduser().resolve()
    env_file = project_path / "env" / f".env.{args.env_name}"
    validation = validate_project_layout(project_path, env_file)
    return DeployConfig(
        project_path=project_path,
        env_name=args.env_name,
        env_file=env_file,
        validate_only=args.validate_only,
        no_build=args.no_build,
        skip_health_checks=args.skip_health_checks,
        timeout=args.timeout,
        env_values=validation.env_values,
    )


def validate_project(config: DeployConfig) -> None:
    try:
        validation = validate_project_layout(config.project_path, config.env_file)
    except ProjectOpsError as exc:
        raise UsageError(str(exc)) from exc
    ensure_validation_ok(validation)


def run_compose_up(config: DeployConfig) -> None:
    preflight_host_ports(config)
    command = compose_base_command(config.project_path, config.env_file, config.env_name) + ["up", "-d"]
    if not config.no_build:
        command.append("--build")
    try:
        run_command_streaming(command, cwd=config.project_path, error_prefix="fallo docker compose up")
    except ProjectOpsError as exc:
        conflicts = find_port_conflicts(str(exc), config.env_values)
        if conflicts:
            joined = ", ".join(conflicts)
            raise ProjectOpsError(
                f"puertos ocupados en el host: {joined}. Ajusta env/.env.{config.env_name} o libera esos puertos antes del deploy"
            ) from exc
        raise


def preflight_host_ports(config: DeployConfig) -> None:
    conflicts: list[str] = []
    for key, port in get_published_ports(config.env_values).items():
        if is_tcp_port_in_use(port):
            conflicts.append(f"{key}={port}")
    if conflicts:
        joined = ", ".join(conflicts)
        raise ProjectOpsError(
            f"puertos ocupados en el host antes del deploy: {joined}. Ajusta env/.env.{config.env_name} o libera esos puertos"
        )


def run_health_checks(config: DeployConfig) -> None:
    expected_services = get_expected_services(config.project_path, config.env_file, config.env_name)
    running_services = get_running_services(config.project_path, config.env_file, config.env_name)
    missing = [service for service in expected_services if service not in running_services]
    if missing:
        raise ProjectOpsError(f"servicios no running despues del deploy: {', '.join(missing)}")

    caddy_http_port = int(config.env_values["CADDY_HTTP_PORT"])
    caddy_root = f"http://127.0.0.1:{caddy_http_port}/"
    caddy_health = f"http://127.0.0.1:{caddy_http_port}/health"
    n8n_url = f"http://127.0.0.1:{caddy_http_port}/n8n/"

    ensure_http_status(caddy_root, config.timeout, {200}, "root del stack")
    ensure_http_status(caddy_health, config.timeout, {200}, "health de la API")
    ensure_http_status(n8n_url, config.timeout, HTTP_OK_STATUSES, "ruta /n8n/")


def run_command_streaming(command: list[str], cwd: Path, error_prefix: str) -> None:
    printable = " ".join(command)
    print(f"[INFO] Ejecutando: {printable}")
    process = subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    try:
        assert process.stdout is not None
        for line in process.stdout:
            print(line.rstrip())
        return_code = process.wait()
    except KeyboardInterrupt as exc:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.terminate()
        raise ProjectOpsError(
            "deploy interrumpido por usuario. Puede quedar estado parcial. "
            "Recupera con: docker compose --env-file env/.env.dev -f docker-compose.yml -f compose.override.yml down -v --remove-orphans"
        ) from exc

    if return_code != 0:
        raise ProjectOpsError(f"{error_prefix}: codigo de salida {return_code}")


def print_validation_summary(config: DeployConfig) -> None:
    print("Validacion de proyecto correcta")
    print(f"Proyecto: {config.project_path}")
    print(f"Env: {config.env_name}")
    print(f"Env file: {config.env_file}")
    print("Resultado: estructura, envs y placeholders correctos")


def print_deploy_summary(config: DeployConfig) -> None:
    print("Deploy completado correctamente")
    print(f"Proyecto: {config.project_path}")
    print(f"Env: {config.env_name}")
    print(f"Env file: {config.env_file}")
    print("Checks minimos: OK")
