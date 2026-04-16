from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AuditVpsEntrypointTest(unittest.TestCase):
    def test_audit_vps_entrypoint_is_valid_python(self) -> None:
        py_compile.compile(str(REPO_ROOT / "bin" / "audit-vps"), doraise=True)

    def test_audit_vps_help_runs_with_python3(self) -> None:
        if shutil.which("bash") is None:
            self.skipTest("bash no disponible en PATH para ejecutar wrapper audit-vps")
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "bin" / "audit-vps"), "--help"],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Usage: audit-vps", result.stdout)


if __name__ == "__main__":
    unittest.main()
