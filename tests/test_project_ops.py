from __future__ import annotations

import socket
import threading
import time
import unittest
import urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch
from subprocess import CompletedProcess

from lib.python.vps_init_framework.project_ops import (
    ProjectOpsError,
    ensure_databases_exist,
    ensure_http_status,
    ensure_postgres_ready,
)


class OkHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


class ProjectOpsHttpRetryTest(unittest.TestCase):
    def test_ensure_http_status_retries_until_service_is_ready(self) -> None:
        port = reserve_free_port()
        server = HTTPServer(("127.0.0.1", port), OkHandler)
        thread = threading.Thread(target=start_server_late, args=(server, 1.0), daemon=True)
        thread.start()
        try:
            status = ensure_http_status(f"http://127.0.0.1:{port}/", timeout=5, accepted_statuses={200}, label="root")
            self.assertEqual(status, 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_ensure_http_status_handles_connection_reset_then_recovers(self) -> None:
        class FakeResponse:
            status = 200

            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, exc_type, exc, tb) -> bool:  # noqa: ANN001
                return False

        with patch(
            "lib.python.vps_init_framework.project_ops.urllib.request.build_opener",
            return_value=FakeOpener([ConnectionResetError("connection reset by peer"), FakeResponse()]),
        ):
            status = ensure_http_status(
                "http://127.0.0.1:18080/",
                timeout=3,
                accepted_statuses={200},
                label="root",
            )
        self.assertEqual(status, 200)

    def test_ensure_http_status_accepts_http_308_without_following_redirect(self) -> None:
        redirect_error = urllib.error.HTTPError(
            url="http://127.0.0.1:18080/",
            code=308,
            msg="Permanent Redirect",
            hdrs=None,
            fp=None,
        )
        with patch(
            "lib.python.vps_init_framework.project_ops.urllib.request.build_opener",
            return_value=FakeOpener([redirect_error]),
        ):
            status = ensure_http_status(
                "http://127.0.0.1:18080/",
                timeout=3,
                accepted_statuses={308},
                label="root",
            )
        self.assertEqual(status, 308)

    def test_ensure_postgres_ready_executes_pg_isready(self) -> None:
        env_values = {"POSTGRES_ADMIN_USER": "admin", "APP_DB_NAME": "appdb", "N8N_DB_NAME": "n8ndb"}
        with patch(
            "lib.python.vps_init_framework.project_ops.run_command",
            return_value=CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
        ) as mocked:
            ensure_postgres_ready(Path("/tmp/p"), Path("/tmp/p/env/.env.dev"), "dev", env_values)
        self.assertTrue(mocked.called)
        command = mocked.call_args.kwargs.get("command") or mocked.call_args.args[0]
        self.assertIn("pg_isready", command)
        self.assertIn("admin", command)

    def test_ensure_databases_exist_passes_when_both_present(self) -> None:
        env_values = {"POSTGRES_ADMIN_USER": "admin", "APP_DB_NAME": "appdb", "N8N_DB_NAME": "n8ndb"}
        with patch(
            "lib.python.vps_init_framework.project_ops.run_command",
            return_value=CompletedProcess(args=[], returncode=0, stdout="appdb\nn8ndb\n", stderr=""),
        ):
            ensure_databases_exist(Path("/tmp/p"), Path("/tmp/p/env/.env.dev"), "dev", env_values)

    def test_ensure_databases_exist_fails_when_one_missing(self) -> None:
        env_values = {"POSTGRES_ADMIN_USER": "admin", "APP_DB_NAME": "appdb", "N8N_DB_NAME": "n8ndb"}
        with patch(
            "lib.python.vps_init_framework.project_ops.run_command",
            return_value=CompletedProcess(args=[], returncode=0, stdout="appdb\n", stderr=""),
        ):
            with self.assertRaises(ProjectOpsError):
                ensure_databases_exist(Path("/tmp/p"), Path("/tmp/p/env/.env.dev"), "dev", env_values)


def reserve_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server_late(server: HTTPServer, delay_seconds: float) -> None:
    time.sleep(delay_seconds)
    server.serve_forever()


class FakeOpener:
    def __init__(self, side_effects: list[object]) -> None:
        self._side_effects = side_effects
        self._index = 0

    def open(self, request, timeout):  # noqa: ANN001
        if self._index >= len(self._side_effects):
            raise RuntimeError("no more side effects")
        value = self._side_effects[self._index]
        self._index += 1
        if isinstance(value, BaseException):
            raise value
        return value


if __name__ == "__main__":
    unittest.main()
