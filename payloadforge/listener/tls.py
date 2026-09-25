"""TLS listener — reverse shell over TLS. Uses a self-signed cert."""

import os
import socket
import ssl
import subprocess
import tempfile
import threading
import sys

from payloadforge.ui.output import console
from payloadforge.ui.palette import PALETTE


class TLSListener:
    def __init__(self, host: str, port: int, timeout: float = 60.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._server: socket.socket | None = None
        self._client: ssl.SSLSocket | None = None
        self._cert_file: str | None = None
        self._key_file: str | None = None

    def _gen_cert(self) -> bool:
        """Generate a self-signed cert with openssl."""
        tmpdir = tempfile.mkdtemp(prefix="pf_tls_")
        self._cert_file = os.path.join(tmpdir, "cert.pem")
        self._key_file = os.path.join(tmpdir, "key.pem")
        try:
            subprocess.run(
                [
                    "openssl", "req", "-x509", "-newkey", "rsa:2048",
                    "-keyout", self._key_file, "-out", self._cert_file,
                    "-days", "30", "-nodes", "-subj", "/CN=localhost",
                ],
                capture_output=True, timeout=20,
            )
            return os.path.exists(self._cert_file)
        except Exception as e:
            console.print(f"[{PALETTE['danger']}]✗ openssl failed:[/] {e}")
            return False

    def start(self) -> bool:
        if not self._gen_cert():
            return False
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(self._cert_file, self._key_file)
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind((self.host, self.port))
            self._server.listen(1)
            self._ctx = ctx
        except OSError as e:
            console.print(f"[{PALETTE['danger']}]✗ Cannot bind {self.host}:{self.port}:[/] {e}")
            return False

        console.print(
            f"[{PALETTE['secondary']}]✓ TLS listener on {self.host}:{self.port}[/]"
        )
        console.print(f"[dim]Self-signed cert generated.[/dim]")
        return True

    def accept(self) -> bool:
        try:
            assert self._server
            self._server.settimeout(self.timeout)
            raw, addr = self._server.accept()
            self._client = self._ctx.wrap_socket(raw, server_side=True)
            console.print(
                f"\n[{PALETTE['secondary']}]✓ TLS connection from {addr[0]}:{addr[1]}[/]"
            )
        except socket.timeout:
            console.print(f"[{PALETTE['accent']}]Timeout.[/]")
            return False
        except ssl.SSLError as e:
            console.print(f"[{PALETTE['danger']}]TLS handshake failed:[/] {e}")
            return False
        except KeyboardInterrupt:
            return False
        finally:
            self.close()
        return True

    def close(self) -> None:
        for s in (self._client, self._server):
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        self._client = None
        self._server = None
        for f in (self._cert_file, self._key_file):
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
