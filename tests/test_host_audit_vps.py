from __future__ import annotations

import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AuditVpsEntrypointTest(unittest.TestCase):
    def test_audit_vps_entrypoint_is_valid_python(self) -> None:
        py_compile.compile(str(REPO_ROOT / "bin" / "audit-vps"), doraise=True)

    def test_init_vps_entrypoint_is_valid_python(self) -> None:
        py_compile.compile(str(REPO_ROOT / "bin" / "init-vps"), doraise=True)

    def test_harden_vps_entrypoint_is_valid_python(self) -> None:
        py_compile.compile(str(REPO_ROOT / "bin" / "harden-vps"), doraise=True)

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

    def test_init_vps_help_runs_with_python3(self) -> None:
        if shutil.which("bash") is None:
            self.skipTest("bash no disponible en PATH para ejecutar wrapper init-vps")
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "bin" / "init-vps"), "--help"],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Usage: init-vps", result.stdout)
        self.assertIn("--public-key", result.stdout)

    def test_harden_vps_help_runs_with_python3(self) -> None:
        if shutil.which("bash") is None:
            self.skipTest("bash no disponible en PATH para ejecutar wrapper harden-vps")
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "bin" / "harden-vps"), "--help"],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Usage: harden-vps", result.stdout)

    def test_init_vps_requires_public_key_or_explicit_override(self) -> None:
        if shutil.which("bash") is None:
            self.skipTest("bash no disponible en PATH para ejecutar wrapper init-vps")
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "bin" / "init-vps"), "--non-interactive"],
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing SSH public key", result.stderr)

    def test_init_vps_allow_without_public_key_is_explicit(self) -> None:
        if shutil.which("bash") is None:
            self.skipTest("bash no disponible en PATH para ejecutar wrapper init-vps")
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "bin" / "init-vps"),
                "--non-interactive",
                "--allow-without-public-key",
            ],
            cwd=str(REPO_ROOT),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Missing SSH public key", result.stderr)

    def test_ssh_syntax_check_does_not_false_fail_when_sshd_t_is_valid(self) -> None:
        bash_path = shutil.which("bash")
        if bash_path is None:
            self.skipTest("bash no disponible en PATH para pruebas de checks_ssh")

        with tempfile.TemporaryDirectory(prefix="host-ssh-check-") as tmpdir:
            fakebin = Path(tmpdir) / "fakebin"
            fakebin.mkdir(parents=True, exist_ok=True)

            sshd_script = """#!/usr/bin/env bash
if [[ "$1" == "-t" ]]; then
  exit 0
fi
if [[ "$1" == "-T" ]]; then
  cat <<'EOF'
permitrootlogin no
passwordauthentication yes
pubkeyauthentication yes
EOF
  exit 0
fi
exit 0
"""
            systemctl_script = """#!/usr/bin/env bash
if [[ "$1" == "is-active" && "$2" == "ssh" ]]; then
  exit 0
fi
exit 0
"""
            sudo_script = """#!/usr/bin/env bash
if [[ "$1" == "-n" ]]; then
  shift
fi
"$@"
"""

            for name, body in {"sshd": sshd_script, "systemctl": systemctl_script, "sudo": sudo_script}.items():
                path = fakebin / name
                path.write_text(body, encoding="utf-8")
                path.chmod(0o755)

            bash_program = f"""
set -euo pipefail
source "{(REPO_ROOT / "lib" / "bash" / "common.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "results.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "checks_ssh.sh").as_posix()}"
STRICT_MODE="no"
VERBOSE_MODE="no"
init_results
check_ssh
printf '%s\\n' "${{RESULTS[@]}}"
"""
            env = dict(**os.environ)
            env["PATH"] = f"{fakebin}{os.pathsep}{env.get('PATH', '')}"

            result = subprocess.run(
                [bash_path, "-c", bash_program],
                cwd=str(REPO_ROOT),
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertIn("OK|SSH|SSH configuration syntax valid", result.stdout)
            self.assertNotIn("FAIL|SSH|SSH configuration syntax invalid", result.stdout)


if __name__ == "__main__":
    unittest.main()
