from __future__ import annotations

import socket
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

from lib.python.vps_init_framework.project_ops import ensure_http_status


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
            "lib.python.vps_init_framework.project_ops.urllib.request.urlopen",
            side_effect=[ConnectionResetError("connection reset by peer"), FakeResponse()],
        ):
            status = ensure_http_status(
                "http://127.0.0.1:18080/",
                timeout=3,
                accepted_statuses={200},
                label="root",
            )
        self.assertEqual(status, 200)


def reserve_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server_late(server: HTTPServer, delay_seconds: float) -> None:
    time.sleep(delay_seconds)
    server.serve_forever()


if __name__ == "__main__":
    unittest.main()
