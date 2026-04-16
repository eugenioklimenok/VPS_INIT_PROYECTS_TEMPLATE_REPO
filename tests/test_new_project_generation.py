from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = REPO_ROOT / "bin"


class NewProjectGenerationCompletenessTest(unittest.TestCase):
    def test_generated_project_has_new_db_model_without_placeholders(self) -> None:
        workspace = REPO_ROOT / "reports" / "test_new_project_generation"
        project = workspace / "check-app"
        if workspace.exists():
            self.rmtree_force(workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(
                [
                    sys.executable,
                    str(BIN_DIR / "new-project"),
                    "check-app",
                    "--base-path",
                    str(workspace),
                    "--domain",
                    "localhost",
                ],
                cwd=str(REPO_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )

            env_dev = (project / "env" / ".env.dev").read_text(encoding="utf-8")
            sql_bootstrap = (project / "postgres" / "init" / "01-bootstrap-multi-db.sql").read_text(encoding="utf-8")

            required_env_keys = (
                "POSTGRES_ADMIN_USER=",
                "POSTGRES_ADMIN_PASSWORD=",
                "APP_DB_NAME=",
                "APP_DB_USER=",
                "APP_DB_PASSWORD=",
                "N8N_DB_NAME=",
                "N8N_DB_USER=",
                "N8N_DB_PASSWORD=",
            )
            for key in required_env_keys:
                self.assertIn(key, env_dev)

            self.assertNotIn("POSTGRES_DB=", env_dev)
            self.assertNotIn("POSTGRES_USER=", env_dev)
            self.assertNotIn("POSTGRES_PASSWORD=", env_dev)

            self.assertIn("CREATE DATABASE", sql_bootstrap)
            self.assertIsNone(re.search(r"__[A-Z0-9_]+__", sql_bootstrap))
            self.assertIsNone(re.search(r"__[A-Z0-9_]+__", env_dev))
        finally:
            if workspace.exists():
                self.rmtree_force(workspace)

    def rmtree_force(self, path: Path) -> None:
        def onexc(function, target, excinfo):
            os.chmod(target, 0o700)
            function(target)

        shutil.rmtree(path, onexc=onexc)


if __name__ == "__main__":
    unittest.main()
