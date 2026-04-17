from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class HardenEffectiveSshTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bash_path = shutil.which("bash")
        if self.bash_path is None:
            self.skipTest("bash no disponible en PATH para pruebas de harden SSH")

    def test_configure_ssh_normalizes_include_conflicts_and_validates_effective_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="host-harden-ssh-") as tmpdir:
            tmp = Path(tmpdir)
            etc_ssh = tmp / "etc-ssh"
            cfg = etc_ssh / "sshd_config"
            conf_d = etc_ssh / "sshd_config.d"
            fakebin = tmp / "fakebin"

            conf_d.mkdir(parents=True, exist_ok=True)
            fakebin.mkdir(parents=True, exist_ok=True)

            cfg.write_text(
                "Include /etc/ssh/sshd_config.d/*.conf\n"
                "PasswordAuthentication yes\n"
                "PubkeyAuthentication yes\n"
                "PermitRootLogin no\n",
                encoding="utf-8",
            )
            (conf_d / "50-cloud-init.conf").write_text(
                "PasswordAuthentication yes\n"
                "KbdInteractiveAuthentication yes\n",
                encoding="utf-8",
            )

            self._write_fake_runtime(fakebin)

            bash_program = f"""
set -euo pipefail
source "{(REPO_ROOT / "lib" / "bash" / "common.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "log.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "setup_ssh.sh").as_posix()}"
configure_ssh no
"""
            env = dict(os.environ)
            env["PATH"] = f"{fakebin}{os.pathsep}{env.get('PATH', '')}"
            env["SSHD_CONFIG_FILE"] = str(cfg)
            env["SSHD_CONFIG_DIR"] = str(conf_d)
            env["SSHD_FRAMEWORK_DROPIN"] = str(conf_d / "99-vps-init-framework.conf")
            env["FAKE_SSHD_CONFIG_FILE"] = str(cfg)
            env["FAKE_SSHD_CONFIG_DIR"] = str(conf_d)

            result = subprocess.run(
                [self.bash_path, "-c", bash_program],
                cwd=str(REPO_ROOT),
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, msg=f"stdout={result.stdout}\nstderr={result.stderr}")
            self.assertIn("Effective SSH config validated (sshd -T)", result.stdout)

            include_contents = (conf_d / "50-cloud-init.conf").read_text(encoding="utf-8")
            self.assertIn("PasswordAuthentication no", include_contents)
            self.assertIn("KbdInteractiveAuthentication no", include_contents)

            managed_dropin = (conf_d / "99-vps-init-framework.conf").read_text(encoding="utf-8")
            self.assertIn("PasswordAuthentication no", managed_dropin)
            self.assertIn("PubkeyAuthentication yes", managed_dropin)
            self.assertIn("PermitRootLogin no", managed_dropin)
            self.assertIn("KbdInteractiveAuthentication no", managed_dropin)

    def test_harden_fails_when_effective_state_keeps_password_auth_enabled(self) -> None:
        with tempfile.TemporaryDirectory(prefix="host-harden-ssh-fail-") as tmpdir:
            tmp = Path(tmpdir)
            etc_ssh = tmp / "etc-ssh"
            cfg = etc_ssh / "sshd_config"
            conf_d = etc_ssh / "sshd_config.d"
            fakebin = tmp / "fakebin"

            conf_d.mkdir(parents=True, exist_ok=True)
            fakebin.mkdir(parents=True, exist_ok=True)

            cfg.write_text("Include /etc/ssh/sshd_config.d/*.conf\n", encoding="utf-8")
            self._write_fake_runtime(fakebin)

            bash_program = f"""
set -euo pipefail
source "{(REPO_ROOT / "lib" / "bash" / "common.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "log.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "setup_ssh.sh").as_posix()}"
source "{(REPO_ROOT / "lib" / "bash" / "harden_ssh.sh").as_posix()}"
ensure_ssh_permissions() {{ :; }}
harden_ssh_access alex
"""
            env = dict(os.environ)
            env["PATH"] = f"{fakebin}{os.pathsep}{env.get('PATH', '')}"
            env["SSHD_CONFIG_FILE"] = str(cfg)
            env["SSHD_CONFIG_DIR"] = str(conf_d)
            env["SSHD_FRAMEWORK_DROPIN"] = str(conf_d / "99-vps-init-framework.conf")
            env["FAKE_SSHD_CONFIG_FILE"] = str(cfg)
            env["FAKE_SSHD_CONFIG_DIR"] = str(conf_d)
            env["FAKE_SSHD_FORCE_PASSWORD"] = "yes"

            result = subprocess.run(
                [self.bash_path, "-c", bash_program],
                cwd=str(REPO_ROOT),
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Effective passwordauthentication mismatch", result.stdout)
            self.assertNotIn("SSH hardened for key-only access", result.stdout)

    def _write_fake_runtime(self, fakebin: Path) -> None:
        sshd_script = """#!/usr/bin/env bash
set -euo pipefail
cfg="${FAKE_SSHD_CONFIG_FILE:?}"
dir="${FAKE_SSHD_CONFIG_DIR:?}"

emit_effective() {
  local password="yes"
  local pubkey="yes"
  local root="prohibit-password"
  local kbd="yes"
  local f line key val

  for f in "$cfg" $(find "$dir" -maxdepth 1 -type f -name '*.conf' | sort); do
    [[ -f "$f" ]] || continue
    while IFS= read -r line; do
      line="${line%%#*}"
      line="$(echo "$line" | xargs || true)"
      [[ -n "$line" ]] || continue
      key="$(echo "$line" | awk '{print tolower($1)}')"
      val="$(echo "$line" | awk '{print tolower($2)}')"
      case "$key" in
        passwordauthentication) password="$val" ;;
        pubkeyauthentication) pubkey="$val" ;;
        permitrootlogin) root="$val" ;;
        kbdinteractiveauthentication) kbd="$val" ;;
      esac
    done < "$f"
  done

  if [[ "${FAKE_SSHD_FORCE_PASSWORD:-no}" == "yes" ]]; then
    password="yes"
  fi

  cat <<EOF
passwordauthentication $password
pubkeyauthentication $pubkey
permitrootlogin $root
kbdinteractiveauthentication $kbd
EOF
}

case "${1:-}" in
  -t)
    exit 0
    ;;
  -T)
    emit_effective
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
"""
        systemctl_script = """#!/usr/bin/env bash
if [[ "$1" == "reload" && "$2" == "ssh" ]]; then
  exit 0
fi
if [[ "$1" == "restart" && "$2" == "ssh" ]]; then
  exit 0
fi
exit 0
"""

        for name, body in {"sshd": sshd_script, "systemctl": systemctl_script}.items():
            path = fakebin / name
            path.write_text(body, encoding="utf-8")
            path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
