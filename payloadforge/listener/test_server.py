"""Standalone listener used by CI to test payloads.

Binds BOTH IPv4 and IPv6 sockets. Windows treats these as separate
stacks, so a listener bound only to 127.0.0.1 will not receive
connections to [::ffff:127.0.0.1] from .NET's TCPClient.
"""

import argparse
import select
import socket
import sys
import time


def make_socket(family: int, host: str, port: int):
    try:
        s = socket.socket(family, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if family == socket.AF_INET6:
            try:
                s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
            except OSError:
                pass
        s.bind((host, port))
        s.listen(1)
        s.setblocking(False)
        return s
    except OSError as e:
        print(f"BIND_FAILED family={family} {host}:{port} - {e}", flush=True)
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5555)
    ap.add_argument("--timeout", type=float, default=40.0)
    args = ap.parse_args()

    s4 = make_socket(socket.AF_INET, "0.0.0.0", args.port)
    s6 = make_socket(socket.AF_INET6, "::", args.port)

    sockets = [s for s in (s4, s6) if s is not None]
    if not sockets:
        print("BIND_FAILED no sockets could be bound", flush=True)
        return 1

    print(f"LISTENING on ipv4:{bool(s4)} ipv6:{bool(s6)} port:{args.port}", flush=True)

    deadline = time.time() + args.timeout
    client = None
    addr = None

    while time.time() < deadline:
        ready, _, _ = select.select(sockets, [], [], 1.0)
        for s in ready:
            try:
                c, a = s.accept()
                client, addr = c, a
                break
            except OSError:
                continue
        if client:
            break

    if not client:
        print("TIMEOUT no connection", flush=True)
        for s in sockets:
            s.close()
        return 2

    print(f"CONNECTED from {addr[0]}:{addr[1]}", flush=True)

    try:
        client.settimeout(3.0)
        client.sendall(b"echo PF_TEST_OK\r\n")
        time.sleep(0.8)
        try:
            data = client.recv(4096)
            if b"PF_TEST_OK" in data:
                print("SHELL_LIVE", flush=True)
        except Exception as e:
            print(f"READ_ERROR {e}", flush=True)
    except Exception as e:
        print(f"SEND_ERROR {e}", flush=True)
    finally:
        try:
            client.close()
        except Exception:
            pass
        for s in sockets:
            try:
                s.close()
            except Exception:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
