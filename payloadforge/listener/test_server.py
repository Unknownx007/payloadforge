"""Standalone listener used by CI to test payloads on Windows runners.

Usage:
    python -m payloadforge.listener.test_server --port 5555 --timeout 30
"""

import argparse
import socket
import sys
import time


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=5555)
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((args.host, args.port))
    s.listen(1)
    s.settimeout(args.timeout)

    print(f"LISTENING on {args.host}:{args.port}", flush=True)

    try:
        client, addr = s.accept()
        print(f"CONNECTED from {addr[0]}:{addr[1]}", flush=True)
        # Send a probe to the shell
        try:
            client.settimeout(3.0)
            client.sendall(b"echo PF_TEST_OK\n")
            time.sleep(0.5)
            data = client.recv(4096)
            if b"PF_TEST_OK" in data:
                print("SHELL_LIVE", flush=True)
        except Exception:
            pass
        client.close()
    except socket.timeout:
        print("TIMEOUT — no connection", flush=True)
        return 2
    finally:
        s.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
