from __future__ import annotations

import shutil
import subprocess
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
import re


PLACEHOLDER_RE = re.compile(r"__[A-Z0-9_]+__")
TEXT_FILE_SUFFIXES = {
    "",
    ".env",
    ".example",
    ".md",
    ".txt",
    ".py",
    ".yml",
    ".yaml",
    ".sh",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".gitignore",
}
REQUIRED_FILES = (
    "docker-compose.yml",
    "compose.override.yml",
    "Makefile",
    "api/Dockerfile",
    "api/requirements.txt",
    "api/app/main.py",
    "caddy/Caddyfile",
    "env/.env.example",
    "env/.env.dev",
    "env/.env.prod",
    "scripts/up.sh",
    "scripts/down.sh",
    "scripts/logs.sh",
    "scripts/backup.sh",
    "scripts/restore.sh",
)
REQUIRED_DIRS = (
    "api/app",
    "backups",
    "caddy",
    "env",
    "n8n",
    "postgres",
    "scripts",
)
REQUIRED_ENV_KEYS = (
    "PROJECT_NAME",
    "APP_ENV",
    "DOMAIN_NAME",
    "API_PORT",
    "POSTGRES_PORT",
    "N8N_PORT",
    "CADDY_HTTP_PORT",
    "CADDY_HTTPS_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "N8N_PROTOCOL",
    "N8N_BASE_URL",
    "N8N_BASIC_AUTH_USER",
    "N8N_BASIC_AUTH_PASSWORD",
    "SECRET_KEY",
)
PUBLISHED_PORT_KEYS = (
    "API_PORT",
    "POSTGRES_PORT",
    "N8N_PORT",
    "CADDY_HTTP_PORT",
    "CADDY_HTTPS_PORT",
)
HTTP_OK_STATUSES = {200, 301, 302, 401, 403}


@dataclass
class ProjectValidation:
    project_path: Path
    env_file: Path
    env_values: dict[str, str]
    missing_files: list[str]
    missing_dirs: list[str]
    missing_env: list[str]
    unresolved_placeholders: list[str]


class ProjectOpsError(Exception):
    pass


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        raise ProjectOpsError(f"env file no encontrado: {path}")

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def validate_ports(env_values: dict[str, str]) -> None:
    ports: list[int] = []
    for key in PUBLISHED_PORT_KEYS:
        try:
            value = int(env_values[key])
        except ValueError as exc:
            raise ProjectOpsError(f"{key} debe ser numerico") from exc
        if value < 1 or value > 65535:
            raise ProjectOpsError(f"{key} debe estar entre 1 y 65535")
        ports.append(value)
    if len(set(ports)) != len(ports):
        raise ProjectOpsError("los puertos publicados no deben repetirse")


def get_published_ports(env_values: dict[str, str]) -> dict[str, int]:
    ports: dict[str, int] = {}
    for key in PUBLISHED_PORT_KEYS:
        ports[key] = int(env_values[key])
    return ports


def is_tcp_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def find_port_conflicts(message: str, env_values: dict[str, str]) -> list[str]:
    matches = sorted({int(match) for match in re.findall(r"(?::|port )(\d{2,5})(?=\D|$)", message)})
    if not matches:
        return []
    by_port = {port: key for key, port in get_published_ports(env_values).items()}
    conflicts: list[str] = []
    for port in matches:
        key = by_port.get(port)
        if key:
            conflicts.append(f"{key}={port}")
        else:
            conflicts.append(str(port))
    return conflicts


def find_unresolved_placeholders(project_path: Path) -> list[str]:
    unresolved: list[str] = []
    for path in sorted(project_path.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix not in TEXT_FILE_SUFFIXES and path.name not in {".gitignore", ".env.example", ".env.dev", ".env.prod"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        match = PLACEHOLDER_RE.search(content)
        if match:
            unresolved.append(f"{path.relative_to(project_path)} -> {match.group(0)}")
    return unresolved


def validate_project_layout(project_path: Path, env_file: Path) -> ProjectValidation:
    if not project_path.exists():
        raise ProjectOpsError(f"ruta de proyecto no encontrada: {project_path}")
    if not project_path.is_dir():
        raise ProjectOpsError(f"project_path no es un directorio: {project_path}")

    env_values = load_env_file(env_file)
    missing_files = [item for item in REQUIRED_FILES if not (project_path / item).is_file()]
    missing_dirs = [item for item in REQUIRED_DIRS if not (project_path / item).is_dir()]
    missing_env = [key for key in REQUIRED_ENV_KEYS if not env_values.get(key)]
    validate_ports(env_values)
    unresolved = find_unresolved_placeholders(project_path)
    return ProjectValidation(
        project_path=project_path,
        env_file=env_file,
        env_values=env_values,
        missing_files=missing_files,
        missing_dirs=missing_dirs,
        missing_env=missing_env,
        unresolved_placeholders=unresolved,
    )


def ensure_validation_ok(validation: ProjectValidation) -> None:
    if validation.missing_files:
        raise ProjectOpsError(f"faltan archivos requeridos: {', '.join(validation.missing_files)}")
    if validation.missing_dirs:
        raise ProjectOpsError(f"faltan directorios requeridos: {', '.join(validation.missing_dirs)}")
    if validation.missing_env:
        raise ProjectOpsError(
            f"faltan variables requeridas en {validation.env_file.name}: {', '.join(validation.missing_env)}"
        )
    if validation.unresolved_placeholders:
        raise ProjectOpsError(f"quedan placeholders sin resolver: {validation.unresolved_placeholders[0]}")


def ensure_docker_available() -> None:
    docker_bin = shutil.which("docker")
    if not docker_bin:
        raise ProjectOpsError("docker no esta disponible en PATH")
    run_command(["docker", "compose", "version"], cwd=Path.cwd(), error_prefix="docker compose no disponible")


def compose_base_command(project_path: Path, env_file: Path, env_name: str) -> list[str]:
    command = [
        "docker",
        "compose",
        "--env-file",
        str(env_file),
        "-f",
        "docker-compose.yml",
    ]
    if env_name == "dev":
        command.extend(["-f", "compose.override.yml"])
    return command


def run_command(command: list[str], cwd: Path, error_prefix: str, text: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        command,
        cwd=str(cwd),
        check=False,
        capture_output=True,
        text=text,
    )
    if result.returncode != 0:
        stderr = result.stderr if text else result.stderr.decode("utf-8", errors="replace")
        stdout = result.stdout if text else result.stdout.decode("utf-8", errors="replace")
        message = stderr.strip() or stdout.strip() or "sin detalle"
        raise ProjectOpsError(f"{error_prefix}: {message}")
    return result


def get_expected_services(project_path: Path, env_file: Path, env_name: str) -> list[str]:
    result = run_command(
        compose_base_command(project_path, env_file, env_name) + ["config", "--services"],
        cwd=project_path,
        error_prefix="no se pudieron resolver servicios del compose",
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def get_running_services(project_path: Path, env_file: Path, env_name: str) -> list[str]:
    result = run_command(
        compose_base_command(project_path, env_file, env_name) + ["ps", "--services", "--status", "running"],
        cwd=project_path,
        error_prefix="no se pudo leer estado de servicios",
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def ensure_http_status(url: str, timeout: int, accepted_statuses: set[int], label: str) -> int:
    deadline = time.monotonic() + max(timeout, 1)
    last_status: int | None = None
    last_reason: str | None = None

    while time.monotonic() < deadline:
        remaining = max(deadline - time.monotonic(), 0.2)
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=min(remaining, 2.0)) as response:
                status = response.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            last_status = status
        except urllib.error.URLError as exc:
            last_reason = str(exc.reason)
            time.sleep(0.5)
            continue
        else:
            last_status = status

        if status in accepted_statuses:
            return status
        time.sleep(0.5)

    if last_reason:
        raise ProjectOpsError(f"fallo check HTTP de {label}: {last_reason}")
    if last_status is not None:
        raise ProjectOpsError(f"status invalido en {label}: {last_status}")
    raise ProjectOpsError(f"fallo check HTTP de {label}: sin respuesta")
