from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class TemplateRuntimeConsistencyTest(unittest.TestCase):
    def test_n8n_secure_cookie_is_wired_in_env_and_compose(self) -> None:
        env_dev = (REPO_ROOT / "templates" / "fullstack" / "env" / "env.dev.template").read_text(encoding="utf-8")
        env_example = (REPO_ROOT / "templates" / "fullstack" / "env" / "env.example.template").read_text(encoding="utf-8")
        compose = (REPO_ROOT / "templates" / "fullstack" / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("N8N_SECURE_COOKIE=false", env_dev)
        self.assertIn("N8N_SECURE_COOKIE=false", env_example)
        self.assertIn('N8N_SECURE_COOKIE: "${N8N_SECURE_COOKIE}"', compose)

    def test_dev_caddy_is_http_only(self) -> None:
        caddyfile = (REPO_ROOT / "templates" / "fullstack" / "caddy" / "Caddyfile").read_text(encoding="utf-8")
        self.assertRegex(caddyfile, r"^http://\{\$DOMAIN_NAME:localhost\}\s*\{")

    def test_restore_script_supports_clean_mode(self) -> None:
        restore_script = (REPO_ROOT / "templates" / "fullstack" / "scripts" / "restore.sh").read_text(encoding="utf-8")
        self.assertIn("[--clean]", restore_script)
        self.assertIn("DROP DATABASE IF EXISTS", restore_script)
        self.assertIn("CREATE DATABASE", restore_script)
        self.assertIn("ON_ERROR_STOP=1", restore_script)

    def test_dev_template_uses_domain_placeholder(self) -> None:
        env_dev = (REPO_ROOT / "templates" / "fullstack" / "env" / "env.dev.template").read_text(encoding="utf-8")
        self.assertIn("DOMAIN_NAME=__DOMAIN_NAME__", env_dev)
        self.assertIn("N8N_BASE_URL=http://__DOMAIN_NAME__:__CADDY_HTTP_PORT__/n8n/", env_dev)
        self.assertIsNone(re.search(r"DOMAIN_NAME=localhost", env_dev))


if __name__ == "__main__":
    unittest.main()
