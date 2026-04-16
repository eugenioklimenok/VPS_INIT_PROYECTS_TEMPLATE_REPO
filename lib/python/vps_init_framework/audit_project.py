from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from vps_init_framework.project_ops import (
    HTTP_OK_STATUSES,
    ProjectOpsError,
    ensure_docker_available,
    ensure_http_status,
    ensure_validation_ok,
    get_expected_services,
    get_running_services,
    validate_project_layout,
)


@dataclass
class AuditConfig:
    project_path: Path
    env_name: str
    env_file: Path
    validate_only: bool
    skip_runtime_checks: bool
    timeout: int
    json_output: bool
    output_path: Path | None
    backup_max_age_hours: int


class UsageError(Exception):
    pass


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = build_config(args)
        report = build_report(config)
    except UsageError as exc:
        print(f"Usage error: {exc}", file=sys.stderr)
        return 3
    except ProjectOpsError as exc:
        print(f"Audit error: {exc}", file=sys.stderr)
        return 2

    emit_report(config, report)
    if report["summary"]["errors"] > 0:
        return 2
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="audit-project", description="Audita el estado estructural y operativo de un proyecto.")
    parser.add_argument("project_path", nargs="?", default=".", help="Ruta del proyecto. Default: directorio actual.")
    parser.add_argument("--env", dest="env_name", default="dev", choices=("dev", "prod"), help="Entorno a auditar.")
    parser.add_argument("--validate-only", action="store_true", help="Audita solo estructura, envs y backups.")
    parser.add_argument("--skip-runtime-checks", action="store_true", help="Omite Docker y checks HTTP.")
    parser.add_argument("--timeout", type=int, default=15, help="Timeout HTTP en segundos.")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Emite salida JSON.")
    parser.add_argument("--output", dest="output_path", help="Guarda la salida de auditoria en un archivo.")
    parser.add_argument("--backup-max-age-hours", type=int, default=48, help="Maximo de horas aceptables para el ultimo backup.")
    return parser.parse_args(argv)


def build_config(args: argparse.Namespace) -> AuditConfig:
    project_path = Path(args.project_path).expanduser().resolve()
    env_file = project_path / "env" / f".env.{args.env_name}"
    output_path = Path(args.output_path).expanduser().resolve() if args.output_path else None
    return AuditConfig(
        project_path=project_path,
        env_name=args.env_name,
        env_file=env_file,
        validate_only=args.validate_only,
        skip_runtime_checks=args.skip_runtime_checks,
        timeout=args.timeout,
        json_output=args.json_output,
        output_path=output_path,
        backup_max_age_hours=args.backup_max_age_hours,
    )


def build_report(config: AuditConfig) -> dict[str, object]:
    validation = validate_project_layout(config.project_path, config.env_file)
    findings: list[dict[str, str]] = []

    add_validation_findings(findings, validation)
    backup_info = inspect_backups(config)

    runtime_skipped = config.validate_only or config.skip_runtime_checks
    if runtime_skipped:
        findings.append({"severity": "info", "check": "runtime", "message": "runtime checks omitidos"})
    else:
        ensure_validation_ok(validation)
        ensure_docker_available()
        add_runtime_findings(findings, config, validation.env_values)

    summary = summarize_findings(findings)
    return {
        "project_path": str(config.project_path),
        "env": config.env_name,
        "env_file": str(config.env_file),
        "backup_info": backup_info,
        "findings": findings,
        "summary": summary,
    }


def add_validation_findings(findings: list[dict[str, str]], validation) -> None:
    if validation.missing_files:
        findings.append({"severity": "error", "check": "files", "message": ", ".join(validation.missing_files)})
    else:
        findings.append({"severity": "ok", "check": "files", "message": "archivos requeridos presentes"})

    if validation.missing_dirs:
        findings.append({"severity": "error", "check": "dirs", "message": ", ".join(validation.missing_dirs)})
    else:
        findings.append({"severity": "ok", "check": "dirs", "message": "directorios requeridos presentes"})

    if validation.missing_env:
        findings.append({"severity": "error", "check": "env", "message": ", ".join(validation.missing_env)})
    else:
        findings.append({"severity": "ok", "check": "env", "message": "variables requeridas presentes"})

    if validation.unresolved_placeholders:
        findings.append({"severity": "error", "check": "placeholders", "message": validation.unresolved_placeholders[0]})
    else:
        findings.append({"severity": "ok", "check": "placeholders", "message": "template completamente renderizado"})


def inspect_backups(config: AuditConfig) -> dict[str, object]:
    backups_dir = config.project_path / "backups"
    backup_files = sorted(path for path in backups_dir.glob("*") if path.is_file() and path.name != ".gitkeep")
    if not backup_files:
        return {"count": 0, "latest": None, "fresh": False}

    latest = max(backup_files, key=lambda current: current.stat().st_mtime)
    age_seconds = datetime.now(timezone.utc).timestamp() - latest.stat().st_mtime
    age_hours = age_seconds / 3600
    return {
        "count": len(backup_files),
        "latest": latest.name,
        "fresh": age_hours <= config.backup_max_age_hours,
        "age_hours": round(age_hours, 2),
    }


def add_runtime_findings(findings: list[dict[str, str]], config: AuditConfig, env_values: dict[str, str]) -> None:
    expected = get_expected_services(config.project_path, config.env_file, config.env_name)
    running = get_running_services(config.project_path, config.env_file, config.env_name)
    missing = [service for service in expected if service not in running]
    if missing:
        findings.append({"severity": "error", "check": "containers", "message": ", ".join(missing)})
    else:
        findings.append({"severity": "ok", "check": "containers", "message": "todos los servicios estan running"})

    caddy_port = int(env_values["CADDY_HTTP_PORT"])
    api_port = int(env_values["API_PORT"])
    checks = [
        ("root", f"http://127.0.0.1:{caddy_port}/", HTTP_OK_STATUSES),
        ("health", f"http://127.0.0.1:{api_port}/health", {200, 307, 308}),
        ("n8n", f"http://127.0.0.1:{caddy_port}/n8n/", HTTP_OK_STATUSES),
    ]
    for label, url, accepted in checks:
        try:
            status = ensure_http_status(url, config.timeout, accepted, label)
            findings.append({"severity": "ok", "check": label, "message": f"status {status}"})
        except ProjectOpsError as exc:
            findings.append({"severity": "error", "check": label, "message": str(exc)})


def summarize_findings(findings: list[dict[str, str]]) -> dict[str, int]:
    summary = {"errors": 0, "warnings": 0, "oks": 0, "infos": 0}
    for item in findings:
        severity = item["severity"]
        if severity == "error":
            summary["errors"] += 1
        elif severity == "warning":
            summary["warnings"] += 1
        elif severity == "ok":
            summary["oks"] += 1
        else:
            summary["infos"] += 1
    return summary


def emit_report(config: AuditConfig, report: dict[str, object]) -> None:
    backup_info = report["backup_info"]
    if backup_info["count"] == 0:
        report["findings"].append({"severity": "warning", "check": "backups", "message": "no hay backups generados"})
    elif backup_info["fresh"]:
        report["findings"].append({"severity": "ok", "check": "backups", "message": f"ultimo backup: {backup_info['latest']}"})
    else:
        report["findings"].append(
            {
                "severity": "warning",
                "check": "backups",
                "message": f"backup antiguo: {backup_info['latest']} ({backup_info['age_hours']}h)",
            }
        )
    report["summary"] = summarize_findings(report["findings"])

    if config.json_output:
        output = json.dumps(report, indent=2) + "\n"
    else:
        lines = [
            "Auditoria de proyecto",
            f"Proyecto: {report['project_path']}",
            f"Env: {report['env']}",
        ]
        for finding in report["findings"]:
            lines.append(f"[{finding['severity'].upper()}] {finding['check']}: {finding['message']}")
        lines.append(
            "Resumen: "
            + f"errors={report['summary']['errors']} "
            + f"warnings={report['summary']['warnings']} "
            + f"oks={report['summary']['oks']} "
            + f"infos={report['summary']['infos']}"
        )
        output = "\n".join(lines) + "\n"

    if config.output_path:
        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        config.output_path.write_text(output, encoding="utf-8")

    sys.stdout.write(output)
