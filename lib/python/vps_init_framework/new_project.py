from __future__ import annotations

import argparse
import secrets
import shutil
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
import re


PROJECT_NAME_RE = re.compile(r"^[a-z0-9-]+$")
DB_IDENTIFIER_RE = re.compile(r"^[a-z_][a-z0-9_]*$")
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
    ".sql",
    ".gitignore",
}
TEMPLATE_FILE_RENAMES = {
    "gitignore.template": ".gitignore",
    "env/env.example.template": "env/.env.example",
    "env/env.dev.template": "env/.env.dev",
    "env/env.prod.template": "env/.env.prod",
}


@dataclass
class NewProjectConfig:
    project_name: str
    domain_name: str
    api_port: int
    postgres_port: int
    n8n_port: int
    caddy_http_port: int
    caddy_https_port: int
    postgres_admin_user: str
    postgres_admin_password: str
    app_db_name: str
    app_db_user: str
    app_db_password: str
    n8n_db_name: str
    n8n_db_user: str
    n8n_db_password: str
    n8n_basic_auth_user: str
    n8n_basic_auth_password: str
    secret_key: str
    base_path: Path
    output_path: Path
    repo_root: Path


class UsageError(Exception):
    pass


class GenerationError(Exception):
    pass


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        repo_root = Path(__file__).resolve().parents[3]
        defaults = load_defaults(repo_root / "config" / "defaults.env")
        config = build_config(args, repo_root, defaults)
        generate_project(config)
    except UsageError as exc:
        print(f"Usage error: {exc}", file=sys.stderr)
        return 3
    except GenerationError as exc:
        print(f"Generation error: {exc}", file=sys.stderr)
        return 2

    print_summary(config)
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="new-project",
        description="Genera un proyecto full stack desde templates/fullstack.",
    )
    parser.add_argument("project_name", help="Nombre del proyecto en minusculas y kebab-case.")
    parser.add_argument(
        "--base-path",
        dest="base_path",
        help="Ruta base donde se creara el proyecto. Default: valor de defaults.env.",
    )
    parser.add_argument("--domain", default="localhost", help="Dominio base del proyecto.")
    parser.add_argument("--api-port", type=int, default=18000, help="Puerto host para la API en desarrollo.")
    parser.add_argument("--postgres-port", type=int, default=15432, help="Puerto host para PostgreSQL.")
    parser.add_argument("--n8n-port", type=int, default=15678, help="Puerto host para n8n.")
    parser.add_argument("--caddy-http-port", type=int, default=18080, help="Puerto HTTP para Caddy.")
    parser.add_argument("--caddy-https-port", type=int, default=18443, help="Puerto HTTPS para Caddy.")
    parser.add_argument("--db-admin-user", help="Usuario admin PostgreSQL del stack.")
    parser.add_argument("--db-admin-password", help="Password admin PostgreSQL del stack.")
    parser.add_argument("--app-db-name", help="Nombre de la base de datos de la app.")
    parser.add_argument("--app-db-user", help="Usuario de la base de datos de la app.")
    parser.add_argument("--app-db-password", help="Password del usuario de la base de datos de la app.")
    parser.add_argument("--n8n-db-name", help="Nombre de la base de datos de n8n.")
    parser.add_argument("--n8n-db-user", help="Usuario de la base de datos de n8n.")
    parser.add_argument("--n8n-db-password", help="Password del usuario de la base de datos de n8n.")
    parser.add_argument("--postgres-db", help="Alias legacy de --app-db-name.")
    parser.add_argument("--postgres-user", help="Alias legacy de --app-db-user.")
    parser.add_argument("--postgres-password", help="Alias legacy de --app-db-password.")
    parser.add_argument("--n8n-user", default="admin", help="Usuario inicial para Basic Auth de n8n.")
    parser.add_argument("--n8n-password", help="Password inicial para Basic Auth de n8n.")
    parser.add_argument("--secret-key", help="Secret key inicial para la API.")
    return parser.parse_args(argv)


def load_defaults(path: Path) -> dict[str, str]:
    defaults: dict[str, str] = {}
    if not path.exists():
        return defaults

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        defaults[key.strip()] = value.strip().strip('"')
    return defaults


def build_config(args: argparse.Namespace, repo_root: Path, defaults: dict[str, str]) -> NewProjectConfig:
    validate_project_name(args.project_name)
    validate_domain(args.domain)

    ports = {
        "api_port": args.api_port,
        "postgres_port": args.postgres_port,
        "n8n_port": args.n8n_port,
        "caddy_http_port": args.caddy_http_port,
        "caddy_https_port": args.caddy_https_port,
    }
    validate_ports(ports)

    base_path_raw = args.base_path or defaults.get("DEFAULT_APPS_DIR", "/home/alex/apps")
    base_path = Path(base_path_raw).expanduser()
    if not base_path.is_absolute():
        base_path = (Path.cwd() / base_path).resolve()
    else:
        base_path = base_path.resolve()

    output_path = base_path / args.project_name
    if output_path.exists():
        raise GenerationError(f"la ruta destino ya existe: {output_path}")

    db_safe = args.project_name.replace("-", "_")
    app_db_name = args.app_db_name or args.postgres_db or db_safe
    app_db_user = args.app_db_user or args.postgres_user or f"{db_safe}_app"
    app_db_password = args.app_db_password or args.postgres_password or generate_secret(24)
    n8n_db_name = args.n8n_db_name or f"{db_safe}_n8n"
    n8n_db_user = args.n8n_db_user or f"{db_safe}_n8n"
    n8n_db_password = args.n8n_db_password or generate_secret(24)
    postgres_admin_user = args.db_admin_user or f"{db_safe}_admin"
    postgres_admin_password = args.db_admin_password or generate_secret(24)

    validate_db_identifier(app_db_name, "app_db_name")
    validate_db_identifier(app_db_user, "app_db_user")
    validate_db_identifier(n8n_db_name, "n8n_db_name")
    validate_db_identifier(n8n_db_user, "n8n_db_user")
    validate_db_identifier(postgres_admin_user, "db_admin_user")
    if app_db_name == n8n_db_name:
        raise UsageError("app_db_name y n8n_db_name deben ser distintos")

    return NewProjectConfig(
        project_name=args.project_name,
        domain_name=args.domain,
        api_port=args.api_port,
        postgres_port=args.postgres_port,
        n8n_port=args.n8n_port,
        caddy_http_port=args.caddy_http_port,
        caddy_https_port=args.caddy_https_port,
        postgres_admin_user=postgres_admin_user,
        postgres_admin_password=postgres_admin_password,
        app_db_name=app_db_name,
        app_db_user=app_db_user,
        app_db_password=app_db_password,
        n8n_db_name=n8n_db_name,
        n8n_db_user=n8n_db_user,
        n8n_db_password=n8n_db_password,
        n8n_basic_auth_user=args.n8n_user,
        n8n_basic_auth_password=args.n8n_password or generate_secret(18),
        secret_key=args.secret_key or generate_secret(32),
        base_path=base_path,
        output_path=output_path,
        repo_root=repo_root,
    )


def validate_project_name(project_name: str) -> None:
    if not project_name:
        raise UsageError("project_name no puede ser vacio")
    if not PROJECT_NAME_RE.fullmatch(project_name):
        raise UsageError("project_name debe usar solo a-z, 0-9 y '-'")
    if project_name.startswith("-") or project_name.endswith("-"):
        raise UsageError("project_name no puede comenzar o terminar con '-'")


def validate_domain(domain_name: str) -> None:
    if not domain_name or any(char.isspace() for char in domain_name):
        raise UsageError("domain no puede ser vacio ni contener espacios")


def validate_db_identifier(value: str, field_name: str) -> None:
    if not DB_IDENTIFIER_RE.fullmatch(value):
        raise UsageError(f"{field_name} debe usar solo a-z, 0-9 y '_' y comenzar con letra o '_'")


def validate_ports(ports: dict[str, int]) -> None:
    values = list(ports.values())
    for name, value in ports.items():
        if value < 1 or value > 65535:
            raise UsageError(f"{name} debe estar entre 1 y 65535")
    if len(set(values)) != len(values):
        raise UsageError("los puertos no deben repetirse entre API, PostgreSQL, n8n y Caddy")


def generate_secret(length: int) -> str:
    return secrets.token_urlsafe(length)[:length]


def generate_project(config: NewProjectConfig) -> None:
    template_path = config.repo_root / "templates" / "fullstack"
    if not template_path.exists():
        raise GenerationError(f"template no encontrado: {template_path}")

    try:
        config.base_path.mkdir(parents=True, exist_ok=True)
        shutil.copytree(template_path, config.output_path)
        materialize_template_filenames(config.output_path)
        render_tree(config.output_path, build_placeholder_map(config))
        make_scripts_executable(config.output_path / "scripts")
    except Exception as exc:  # pragma: no cover - defensive path
        if config.output_path.exists():
            shutil.rmtree(config.output_path, ignore_errors=True)
        raise GenerationError(str(exc)) from exc


def build_placeholder_map(config: NewProjectConfig) -> dict[str, str]:
    return {
        "__PROJECT_NAME__": config.project_name,
        "__DOMAIN_NAME__": config.domain_name,
        "__API_PORT__": str(config.api_port),
        "__POSTGRES_PORT__": str(config.postgres_port),
        "__N8N_PORT__": str(config.n8n_port),
        "__CADDY_HTTP_PORT__": str(config.caddy_http_port),
        "__CADDY_HTTPS_PORT__": str(config.caddy_https_port),
        "__POSTGRES_ADMIN_USER__": config.postgres_admin_user,
        "__POSTGRES_ADMIN_PASSWORD__": config.postgres_admin_password,
        "__APP_DB_NAME__": config.app_db_name,
        "__APP_DB_USER__": config.app_db_user,
        "__APP_DB_PASSWORD__": config.app_db_password,
        "__N8N_DB_NAME__": config.n8n_db_name,
        "__N8N_DB_USER__": config.n8n_db_user,
        "__N8N_DB_PASSWORD__": config.n8n_db_password,
        "__N8N_BASIC_AUTH_USER__": config.n8n_basic_auth_user,
        "__N8N_BASIC_AUTH_PASSWORD__": config.n8n_basic_auth_password,
        "__SECRET_KEY__": config.secret_key,
    }


def materialize_template_filenames(project_path: Path) -> None:
    for source_relative, target_relative in TEMPLATE_FILE_RENAMES.items():
        source_path = project_path / source_relative
        target_path = project_path / target_relative
        if not source_path.exists():
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(target_path)


def render_tree(project_path: Path, placeholders: dict[str, str]) -> None:
    rename_paths(project_path, placeholders)
    for path in sorted(project_path.rglob("*")):
        if not path.is_file():
            continue
        render_file(path, placeholders)


def rename_paths(project_path: Path, placeholders: dict[str, str]) -> None:
    paths = sorted(project_path.rglob("*"), key=lambda current: len(str(current)), reverse=True)
    for path in paths:
        new_name = path.name
        for placeholder, value in placeholders.items():
            new_name = new_name.replace(placeholder, value)
        if new_name != path.name:
            path.rename(path.with_name(new_name))


def render_file(path: Path, placeholders: dict[str, str]) -> None:
    if path.suffix not in TEXT_FILE_SUFFIXES and path.name not in {".gitignore", ".env.example", ".env.dev", ".env.prod"}:
        return

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return

    rendered = content
    for placeholder, value in placeholders.items():
        rendered = rendered.replace(placeholder, value)

    if rendered != content:
        path.write_text(rendered, encoding="utf-8", newline="\n")


def make_scripts_executable(scripts_path: Path) -> None:
    if not scripts_path.exists():
        return
    for script in scripts_path.glob("*.sh"):
        current_mode = script.stat().st_mode
        script.chmod(current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def print_summary(config: NewProjectConfig) -> None:
    print("Proyecto generado correctamente")
    print(f"Nombre: {config.project_name}")
    print(f"Ruta: {config.output_path}")
    print("Placeholders resueltos:")
    print(f"- DOMAIN_NAME={config.domain_name}")
    print(f"- API_PORT={config.api_port}")
    print(f"- POSTGRES_PORT={config.postgres_port}")
    print(f"- N8N_PORT={config.n8n_port}")
    print(f"- CADDY_HTTP_PORT={config.caddy_http_port}")
    print(f"- CADDY_HTTPS_PORT={config.caddy_https_port}")
    print(f"- POSTGRES_ADMIN_USER={config.postgres_admin_user}")
    print(f"- APP_DB_NAME={config.app_db_name}")
    print(f"- APP_DB_USER={config.app_db_user}")
    print(f"- N8N_DB_NAME={config.n8n_db_name}")
    print(f"- N8N_DB_USER={config.n8n_db_user}")
    print(f"- N8N_BASIC_AUTH_USER={config.n8n_basic_auth_user}")
    print("Proximos pasos:")
    print("1. Revisar env/.env.dev y env/.env.prod")
    print("2. Ajustar dominio y credenciales reales")
    print("3. Levantar el stack con make up o scripts/up.sh")
