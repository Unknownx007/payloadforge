"""Comprehensive payload test command — runs the whole loop locally."""

import shutil
import socket as _sock
import subprocess
import threading
import time

from payloadforge.commands.registry import register
from payloadforge.listener import TCPListener
from payloadforge.payloads import PAYLOADS, render
from payloadforge.state import Session
from payloadforge.ui.output import (
    console, ok, fail, warn, info, dedsec_table,
)
from payloadforge.ui.palette import PALETTE


LANG_TO_CMD = {
    "bash": "bash",
    "nc": None,           # handled specially
    "python": "python3",
    "perl": "perl",
    "ruby": "ruby",
    "php": "php",
    "node": "node",
    "socat": "socat",
    "awk": "awk",
    "ssh": "ssh",
    "powershell": None,   # Windows-only in this test
    "cmd": None,
    "mshta": None,
    "jsp": None,
    "java": None,
    "aspx": None,
}


def _has_command(lang: str) -> tuple[bool, str]:
    if lang == "nc":
        for n in ("nc", "ncat", "netcat"):
            p = shutil.which(n)
            if p:
                return True, p
        return False, "nc"
    cmd = LANG_TO_CMD.get(lang)
    if cmd is None:
        return False, lang
    p = shutil.which(cmd)
    return (p is not None, p or cmd)


@register(
    "testall",
    "Test every testable payload locally. Usage: testall [category]",
    category="listener",
)
def cmd_testall(s: Session, args: list[str]) -> None:
    cat_filter = args[0].lower() if args else None

    candidates = [
        p for p in PAYLOADS.values()
        if p.testable and (cat_filter is None or p.category == cat_filter)
    ]
    if not candidates:
        warn("No testable payloads matched.")
        return

    candidates.sort(key=lambda p: p.name)

    console.print()
    console.print(
        f"[bold {PALETTE['primary']}]Testing {len(candidates)} payloads on 127.0.0.1[/]"
    )
    console.print()

    results: dict[str, tuple[str, str]] = {}

    for idx, p in enumerate(candidates):
        port = 4444 + idx
        console.print(
            f"[{PALETTE['primary']}]━━━ [{idx + 1}/{len(candidates)}] "
            f"{p.name} ({p.language}) ━━━[/]"
        )

        has_cmd, cmd_path = _has_command(p.language)
        if not has_cmd:
            warn(f"skipped — '{p.language}' not installed")
            results[p.name] = ("SKIP", f"{p.language} not installed")
            continue

        listener = TCPListener("127.0.0.1", port, timeout=8.0)
        if not listener.start():
            results[p.name] = ("FAIL", "listener bind failed")
            continue

        payload_str = render(p.name, "127.0.0.1", port)
        info(f"payload: {payload_str[:70]}{'...' if len(payload_str) > 70 else ''}")

        def run_payload(ps=payload_str):
            time.sleep(0.3)
            try:
                subprocess.Popen(
                    ps, shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception:
                pass

        threading.Thread(target=run_payload, daemon=True).start()

        try:
            assert listener._server
            listener._server.settimeout(8.0)
            client, addr = listener._server.accept()
            ok(f"connected from {addr[0]}:{addr[1]}")

            try:
                client.settimeout(3.0)
                client.sendall(b"echo PF_TEST_OK\n")
                time.sleep(0.4)
                data = client.recv(4096)
                if b"PF_TEST_OK" in data:
                    ok("shell live (echoed PF_TEST_OK)")
                    results[p.name] = ("PASS", "shell live")
                else:
                    warn("connected but no echo")
                    results[p.name] = ("PASS", "connected (no echo)")
            except Exception as e:
                warn(f"echo check failed: {e}")
                results[p.name] = ("PASS", "connected")

            client.close()
        except _sock.timeout:
            fail("no connection in 8s")
            results[p.name] = ("FAIL", "no connection")
        except Exception as e:
            fail(f"error: {e}")
            results[p.name] = ("FAIL", str(e))
        finally:
            listener.close()

        time.sleep(0.4)

    console.print()
    console.print(f"[bold {PALETTE['primary']}]═══════ TEST SUMMARY ═══════[/]")

    t = dedsec_table("Results", [
        ("Payload", {"style": PALETTE["accent"]}),
        ("Status", {"justify": "center", "width": 8}),
        ("Note", {"style": PALETTE["dim"]}),
    ])

    passed = failed = skipped = 0
    for name, (status, note) in sorted(results.items()):
        if status == "PASS":
            passed += 1
            t.add_row(name, f"[{PALETTE['secondary']}]PASS[/]", note)
        elif status == "FAIL":
            failed += 1
            t.add_row(name, f"[{PALETTE['danger']}]FAIL[/]", note)
        else:
            skipped += 1
            t.add_row(name, f"[{PALETTE['accent']}]SKIP[/]", note)

    console.print(t)
    console.print()
    console.print(
        f"[bold]Total: {len(results)} | "
        f"[{PALETTE['secondary']}]Passed: {passed}[/] | "
        f"[{PALETTE['danger']}]Failed: {failed}[/] | "
        f"[{PALETTE['accent']}]Skipped: {skipped}[/][/]"
    )
    console.print()


@register(
    "checkdeps",
    "Check which payload interpreters are installed.",
    category="listener",
)
def cmd_checkdeps(s: Session, args: list[str]) -> None:
    langs = sorted(set(p.language for p in PAYLOADS.values()))
    t = dedsec_table("Dependencies", [
        ("Language", {"style": PALETTE["accent"]}),
        ("Command", {"style": PALETTE["primary"]}),
        ("Status", {"justify": "center"}),
    ])
    for lang in langs:
        cmd = LANG_TO_CMD.get(lang) or (lang if lang == "nc" else "—")
        present, path = _has_command(lang)
        if present:
            t.add_row(lang, path, f"[{PALETTE['secondary']}]✓[/]")
        else:
            t.add_row(lang, cmd, f"[{PALETTE['danger']}]✗[/]")
    console.print(t)
