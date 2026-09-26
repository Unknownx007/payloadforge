"""TCP listener — accepts a connection and hands you a shell.

Two input modes:

  line (default)   — you type a command, press Enter, the whole line is
                     sent with a trailing newline. Works with every
                     non-PTY reverse shell (bash, PowerShell, cmd, python).

  raw              — every keystroke is forwarded immediately. Required
                     for shells that allocate their own PTY (python3_pty,
                     socat) so that sudo, vim, ssh, and password prompts
                     work. Enable with `listen raw`.
"""

import select
import socket
import sys
import threading
import time

from payloadforge.ui.output import console
from payloadforge.ui.palette import PALETTE


class TCPListener:
    def __init__(self, host: str, port: int, timeout: float = 60.0, raw: bool = False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.raw = raw
        self._server: socket.socket | None = None
        self._client: socket.socket | None = None
        self._connected = threading.Event()

    def start(self) -> bool:
        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind((self.host, self.port))
            self._server.listen(1)
        except OSError as e:
            console.print(f"[{PALETTE['danger']}][-][/] Cannot bind {self.host}:{self.port}: {e}")
            return False

        console.print(
            f"[{PALETTE['secondary']}][+][/] Listening on {self.host}:{self.port}"
        )
        mode = "raw" if self.raw else "line"
        console.print(
            f"[dim]Waiting for connection ({mode} mode, Ctrl+C to stop)...[/dim]"
        )
        return True

    def accept(self) -> bool:
        try:
            assert self._server
            self._server.settimeout(self.timeout)
            client, addr = self._server.accept()
            self._client = client
            self._connected.set()
            console.print(
                f"\n[{PALETTE['secondary']}][+][/] Connection from {addr[0]}:{addr[1]}"
            )
            if self.raw:
                console.print("[dim]Raw mode. Ctrl+] to close.[/dim]\n")
                self._interactive_raw()
            else:
                console.print("[dim]Line mode. Type a command and press Enter. Ctrl+D or 'exit' to close.[/dim]\n")
                self._interactive_line()
            return True
        except socket.timeout:
            console.print(
                f"[{PALETTE['warning']}][!][/] Timeout — no connection in {self.timeout:.0f}s."
            )
            return False
        except KeyboardInterrupt:
            console.print("\n[dim]Listener stopped.[/dim]")
            return False
        finally:
            self.close()

    # ------------------------------------------------------------
    # Line-buffered input — default, works with non-PTY shells
    # ------------------------------------------------------------

    def _interactive_line(self) -> None:
        assert self._client
        stop = threading.Event()

        def reader():
            """Print whatever the shell sends back."""
            try:
                while not stop.is_set():
                    r, _, _ = select.select([self._client], [], [], 0.3)
                    if not r:
                        continue
                    data = self._client.recv(4096)
                    if not data:
                        break
                    sys.stdout.write(data.decode(errors="replace"))
                    sys.stdout.flush()
            except Exception:
                pass
            stop.set()

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        try:
            while not stop.is_set():
                # input() handles terminal line editing, arrows, backspace
                try:
                    line = input()
                except EOFError:
                    break
                if not line:
                    # still send a bare newline — many shells need it
                    try:
                        self._client.sendall(b"\n")
                    except Exception:
                        break
                    continue
                try:
                    self._client.sendall((line + "\n").encode())
                except Exception as e:
                    console.print(f"[dim]send failed: {e}[/dim]")
                    break
        except KeyboardInterrupt:
            pass
        finally:
            stop.set()
            console.print("\n[dim]Session closed.[/dim]")

    # ------------------------------------------------------------
    # Raw input — opt-in, for shells that allocate a PTY
    # ------------------------------------------------------------

    def _interactive_raw(self) -> None:
        assert self._client
        try:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            tty.setraw(fd)
        except Exception:
            old = None

        stop = threading.Event()

        def reader():
            try:
                while not stop.is_set():
                    r, _, _ = select.select([self._client], [], [], 0.2)
                    if not r:
                        continue
                    data = self._client.recv(4096)
                    if not data:
                        break
                    sys.stdout.write(data.decode(errors="replace"))
                    sys.stdout.flush()
            except Exception:
                pass
            stop.set()

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        try:
            while not stop.is_set():
                r, _, _ = select.select([sys.stdin], [], [], 0.2)
                if not r:
                    continue
                ch = sys.stdin.read(1)
                if not ch:
                    break
                if ch == "\x1d":  # Ctrl+]
                    break
                self._client.sendall(ch.encode())
        except KeyboardInterrupt:
            pass
        finally:
            stop.set()
            if old is not None:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                except Exception:
                    pass
            console.print("\n[dim]Session closed.[/dim]")

    def close(self) -> None:
        for s in (self._client, self._server):
            if s:
                try:
                    s.close()
                except Exception:
                    pass
        self._client = None
        self._server = None

    @property
    def connected(self) -> bool:
        return self._connected.is_set()
