from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "lib" / "python"))

from vps_init_framework.deploy_project import DeployConfig, preflight_host_ports
from vps_init_framework.project_ops import ProjectOpsError


def make_config() -> DeployConfig:
    return DeployConfig(
        project_path=Path("/tmp/proj"),
        env_name="dev",
        env_file=Path("/tmp/proj/env/.env.dev"),
        validate_only=False,
        no_build=False,
        skip_health_checks=False,
        timeout=30,
        env_values={
            "API_PORT": "18000",
            "POSTGRES_PORT": "15432",
            "N8N_PORT": "15678",
            "CADDY_HTTP_PORT": "18080",
            "CADDY_HTTPS_PORT": "18443",
        },
    )


class DeployProjectPreflightPortsTest(unittest.TestCase):
    def test_preflight_passes_when_ports_are_free(self) -> None:
        config = make_config()
        with patch(
            "vps_init_framework.deploy_project.get_project_running_published_ports",
            return_value=set(),
        ), patch(
            "vps_init_framework.deploy_project.is_tcp_port_in_use",
            return_value=False,
        ):
            preflight_host_ports(config)

    def test_preflight_passes_when_ports_are_owned_by_same_project(self) -> None:
        config = make_config()
        own_ports = {18000, 15432, 15678, 18080, 18443}
        with patch(
            "vps_init_framework.deploy_project.get_project_running_published_ports",
            return_value=own_ports,
        ), patch(
            "vps_init_framework.deploy_project.is_tcp_port_in_use",
            return_value=True,
        ):
            preflight_host_ports(config)

    def test_preflight_fails_when_foreign_process_uses_ports(self) -> None:
        config = make_config()
        with patch(
            "vps_init_framework.deploy_project.get_project_running_published_ports",
            return_value=set(),
        ), patch(
            "vps_init_framework.deploy_project.is_tcp_port_in_use",
            return_value=True,
        ):
            with self.assertRaises(ProjectOpsError):
                preflight_host_ports(config)


if __name__ == "__main__":
    unittest.main()
