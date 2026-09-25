"""HTTP server for hosting payloads — used by chain/dropper payloads
and the powershell_iex_web / certutil_download templates.
"""

import http.server
import os
import socket
import socketserver
import threading
from pathlib import Path
from typing import Optional

from payloadforge.ui.output import console
from payloadforge.ui.palette import PALETTE


class _Handler(http.server.SimpleHTTPRequestHandler):
    """Quiet handler — logs minimally to the console."""

    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def log_message(self, fmt, *args):
        # Example: "GET /stager.sh HTTP/1.1" 200 -
        msg = fmt % args
        console.print(f"[{PALETTE['dim']}][http] {msg}[/]")

    def log_error(self, fmt, *args):
        pass


class HTTPServer:
    def __init__(self, host: str, port: int, docroot: Optional[str] = None):
        self.host = host
        self.port = port
        self.docroot = docroot or str(Path.cwd())
        self._server: Optional[socketserver.TCPServer] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> bool:
        if not os.path.isdir(self.docroot):
            console.print(f"[red]Docroot does not exist:[/red] {self.docroot}")
            return False

        handler = lambda *a, **kw: _Handler(
            *a, directory=self.docroot, **kw
        )

        try:
            self._server = socketserver.TCPServer(
                (self.host, self.port), handler
            )
            self._server.allow_reuse_address = True
        except OSError as e:
            console.print(
                f"[{PALETTE['danger']}]✗ Cannot bind {self.host}:{self.port}:[/] {e}"
            )
            return False

        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True
        )
        self._thread.start()

        console.print(
            f"[{PALETTE['secondary']}]✓ HTTP server on http://{self.host}:{self.port}/[/]"
        )
        console.print(f"[dim]Docroot: {self.docroot}[/dim]")
        console.print(f"[dim]Files in docroot:[/dim]")
        for f in sorted(os.listdir(self.docroot)):
            full = os.path.join(self.docroot, f)
            tag = "dir " if os.path.isdir(full) else "file"
            console.print(f"  [dim]\\[{tag}][/dim] {f}")
        console.print(f"[dim]Ctrl+C to stop.[/dim]")
        return True

    def serve_until_interrupt(self) -> None:
        try:
            while True:
                if self._thread and not self._thread.is_alive():
                    break
                self._thread.join(timeout=0.5) if self._thread else None
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        if self._server:
            try:
                self._server.shutdown()
                self._server.server_close()
            except Exception:
                pass
        self._server = None
        self._thread = None
        console.print("[dim]HTTP server stopped.[/dim]")
