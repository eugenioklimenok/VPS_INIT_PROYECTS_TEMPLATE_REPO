from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BIN_DIR = REPO_ROOT / "bin"


class FrameworkSmokeTest(unittest.TestCase):
    def test_project_flow_validate_only(self) -> None:
        base_path = REPO_ROOT / "reports" / "smoke_test_workspace"
        project_path = base_path / "smoke-app"
        if base_path.exists():
            self.rmtree_force(base_path)
        base_path.mkdir(parents=True, exist_ok=True)
        try:
            self.run_cmd(
                [
                    str(BIN_DIR / "new-project"),
                    "smoke-app",
                    "--base-path",
                    str(base_path),
                    "--domain",
                    "smoke.local",
                    "--api-port",
                    "38000",
                    "--postgres-port",
                    "35432",
                    "--n8n-port",
                    "35678",
                    "--caddy-http-port",
                    "38080",
                    "--caddy-https-port",
                    "38443",
                ]
            )

            self.assertTrue((project_path / "docker-compose.yml").is_file())

            self.run_cmd([str(BIN_DIR / "deploy-project"), str(project_path), "--env", "dev", "--validate-only"])
            self.run_cmd([str(BIN_DIR / "backup-project"), str(project_path), "--env", "dev", "--validate-only"])

            audit_report = self.run_cmd(
                [
                    str(BIN_DIR / "audit-project"),
                    str(project_path),
                    "--env",
                    "dev",
                    "--validate-only",
                    "--json",
                ]
            )
            report = json.loads(audit_report.stdout)
            self.assertEqual(report["summary"]["errors"], 0)
            self.assertGreaterEqual(report["summary"]["warnings"], 1)
        finally:
            if base_path.exists():
                self.rmtree_force(base_path)

    def rmtree_force(self, path: Path) -> None:
        def onexc(function, target, excinfo):
            os.chmod(target, 0o700)
            function(target)

        shutil.rmtree(path, onexc=onexc)

    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
