"""Built-in shell commands."""

from pathlib import Path

from rich.table import Table

from payloadforge.commands.registry import REGISTRY, register
from payloadforge.encoders import ENCODERS, encode
from payloadforge.obfuscators import OBFUSCATORS, obfuscate
from payloadforge.listener import TCPListener, TLSListener, HTTPServer
from payloadforge.payloads import PAYLOADS, by_category, render
from payloadforge.state import Session
from payloadforge.ui.output import console, ok, fail, warn, info, dedsec_table
from payloadforge.ui.palette import PALETTE


def _hr() -> None:
    console.print(f"[{PALETTE['border']}]" + "═" * 60 + "[/]")


@register("help", "Show commands. Usage: help [command]", category="shell")
def cmd_help(s: Session, args: list[str]) -> None:
    if args:
        c = REGISTRY.get(args[0])
        if not c:
            fail(f"No such command: {args[0]}")
            return
        console.print(f"[{PALETTE['primary']}]{c.name}[/]  —  {c.help}")
        return
    cats: dict[str, list] = {}
    for c in REGISTRY.values():
        if c.hidden:
            continue
        cats.setdefault(c.category, []).append(c)
    for cat in sorted(cats):
        t = Table(
            title=f"[bold {PALETTE['primary']}]◤ {cat} ◢[/]",
            show_header=False, box=None, pad_edge=False,
        )
        t.add_column(style=PALETTE["accent"], no_wrap=True, width=16)
        t.add_column(style=PALETTE["text"])
        for c in sorted(cats[cat], key=lambda x: x.name):
            t.add_row(c.name, c.help)
        console.print(t)


@register("set", "Set an option. Usage: set <key> <value>", category="config")
def cmd_set(s: Session, args: list[str]) -> None:
    if len(args) != 2:
        warn("Usage: set <key> <value>")
        info("Keys: lhost, lport, http_port, encoder, tls, obfuscators")
        return
    key, val = args[0].lower(), args[1]
    if key == "lhost":
        s.lhost = val
    elif key == "lport":
        if not val.isdigit():
            fail("lport must be a number.")
            return
        s.lport = int(val)
    elif key == "http_port":
        if not val.isdigit():
            fail("http_port must be a number.")
            return
        s.http_port = int(val)
    elif key == "encoder":
        if val.lower() in ("none", "off", ""):
            s.encoder = None
        elif val in ENCODERS:
            s.encoder = val
        else:
            fail(f"Unknown encoder: {val}")
            info(f"Available: {', '.join(ENCODERS)}")
            return
    elif key == "obfuscators":
        if val.lower() in ("none", "off", ""):
            s.obfuscators = []
        else:
            names = [x.strip() for x in val.split(",") if x.strip()]
            unknown = [n for n in names if n not in OBFUSCATORS]
            if unknown:
                fail(f"Unknown obfuscators: {', '.join(unknown)}")
                info(f"Available: {', '.join(OBFUSCATORS)}")
                return
            s.obfuscators = names
    elif key == "tls":
        s.use_tls = val.lower() in ("on", "true", "1", "yes")
    else:
        fail(f"Unknown key: {key}")
        return
    ok(f"{key} = {val}")


@register("show", "Show current options.", category="config")
def cmd_show(s: Session, args: list[str]) -> None:
    console.print(f"  [{PALETTE['primary']}]lhost[/]        = [{PALETTE['accent']}]{s.lhost}[/]")
    console.print(f"  [{PALETTE['primary']}]lport[/]        = [{PALETTE['accent']}]{s.lport}[/]")
    console.print(f"  [{PALETTE['primary']}]http_port[/]    = [{PALETTE['accent']}]{s.http_port}[/]")
    console.print(f"  [{PALETTE['primary']}]encoder[/]      = [{PALETTE['accent']}]{s.encoder or 'none'}[/]")
    obfs = ", ".join(s.obfuscators) if s.obfuscators else "none"
    console.print(f"  [{PALETTE['primary']}]obfuscators[/]  = [{PALETTE['accent']}]{obfs}[/]")
    console.print(f"  [{PALETTE['primary']}]tls[/]          = [{PALETTE['accent']}]{'on' if s.use_tls else 'off'}[/]")
    if s.last_payload_name:
        console.print(f"  [{PALETTE['dim']}]last         = {s.last_payload_name}[/]")


@register("list", "List payloads. Usage: list [category]", category="payloads")
def cmd_list(s: Session, args: list[str]) -> None:
    if args:
        cat = args[0].lower()
        items = by_category(cat)
        if not items:
            fail(f"No payloads in category '{cat}'.")
            cats = sorted(set(p.category for p in PAYLOADS.values()))
            info(f"Available categories: {', '.join(cats)}")
            return
    else:
        items = sorted(PAYLOADS.values(), key=lambda p: (p.category, p.name))

    t = dedsec_table("Payloads", [
        ("Name", {"style": PALETTE["accent"], "no_wrap": True}),
        ("Cat", {"style": PALETTE["dim"], "width": 8}),
        ("Lang", {"style": PALETTE["primary"], "width": 12}),
        ("Local", {"justify": "center", "width": 6}),
        ("Description", {"style": PALETTE["text"]}),
    ])
    for p in items:
        t.add_row(
            p.name, p.category, p.language,
            f"[{PALETTE['secondary']}]✓[/]" if p.testable else f"[{PALETTE['dim']}]✗[/]",
            p.description,
        )
    console.print(t)
    console.print(
        f"[{PALETTE['dim']}]Local ✓ = testable with 'testall' or 'verify' on this machine. "
        f"✗ = requires a real target (Windows, EC2, K8s, SSH server, web server).[/]"
    )


@register("categories", "List payload categories.", category="payloads")
def cmd_categories(s: Session, args: list[str]) -> None:
    cats: dict[str, int] = {}
    for p in PAYLOADS.values():
        cats[p.category] = cats.get(p.category, 0) + 1
    t = dedsec_table("Categories", [
        ("Category", {"style": PALETTE["accent"]}),
        ("Count", {"style": PALETTE["primary"], "justify": "right"}),
    ])
    for cat, n in sorted(cats.items()):
        t.add_row(cat, str(n))
    console.print(t)


@register("info", "Show payload details. Usage: info <payload>", category="payloads")
def cmd_info(s: Session, args: list[str]) -> None:
    if not args:
        warn("Usage: info <payload>")
        return
    p = PAYLOADS.get(args[0])
    if not p:
        fail(f"Unknown payload: {args[0]}")
        return
    console.print(f"[bold {PALETTE['primary']}]{p.name}[/]")
    console.print(f"  category:    [{PALETTE['accent']}]{p.category}[/]")
    console.print(f"  language:    [{PALETTE['accent']}]{p.language}[/]")
    testable = f"[{PALETTE['secondary']}]yes[/]" if p.testable else f"[{PALETTE['danger']}]no[/]"
    console.print(f"  testable:    {testable}")
    if p.testable:
        console.print(f"  verified:    [{PALETTE['secondary']}]yes (runs in 'testall'/'verify')[/]")
    else:
        console.print(f"  verified:    [{PALETTE['dim']}]no — not locally testable[/]")
    if p.test_note:
        console.print(f"  note:        [{PALETTE['dim']}]{p.test_note}[/]")
    if p.tags:
        console.print(f"  tags:        [{PALETTE['dim']}]{', '.join(p.tags)}[/]")
    console.print(f"  description: {p.description}")
    console.print()
    console.print(f"[{PALETTE['dim']}]Template:[/]")
    console.print(f"  {p.template}", markup=False)


@register("generate", "Generate a payload. Usage: generate <name> [-o file] [-c]", category="payloads")
def cmd_generate(s: Session, args: list[str]) -> None:
    if not args:
        warn("Usage: generate <payload> [-o file] [-c]")
        return
    name = args[0]
    if name not in PAYLOADS:
        fail(f"Unknown payload: {name}")
        info("Run 'list' to see available payloads.")
        return

    output_file: str | None = None
    to_clipboard = False
    rest = args[1:]
    i = 0
    while i < len(rest):
        if rest[i] in ("-o", "--output") and i + 1 < len(rest):
            output_file = rest[i + 1]
            i += 2
        elif rest[i] in ("-c", "--clip"):
            to_clipboard = True
            i += 1
        else:
            i += 1

    payload_str = render(name, s.lhost, s.lport, s.http_port)

    if s.obfuscators:
        for obf in s.obfuscators:
            try:
                payload_str = obfuscate(obf, payload_str)
                info(f"obfuscated with {obf}")
            except Exception as e:
                fail(f"obfuscator '{obf}' failed: {e}")

    if s.encoder:
        payload_str = encode(s.encoder, payload_str)
        info(f"encoded with {s.encoder}")

    s.last_generated = payload_str
    s.last_payload_name = name

    if output_file:
        try:
            Path(output_file).write_text(payload_str)
            ok(f"Written to {output_file}")
        except OSError as e:
            fail(f"Write failed: {e}")
            return

    if to_clipboard:
        try:
            import pyperclip
            pyperclip.copy(payload_str)
            ok("Copied to clipboard")
        except Exception as e:
            fail(f"Clipboard failed: {e}")

    _hr()
    console.print(payload_str, style=PALETTE["text"], markup=False)
    _hr()


@register("encoders", "List encoders.", category="config")
def cmd_encoders(s: Session, args: list[str]) -> None:
    t = dedsec_table("Encoders", [
        ("Name", {"style": PALETTE["accent"]}),
        ("Description", {"style": PALETTE["text"]}),
    ])
    for name, (desc, _) in sorted(ENCODERS.items()):
        t.add_row(name, desc)
    console.print(t)


@register("obfuscators", "List obfuscators.", category="config")
def cmd_obfuscators(s: Session, args: list[str]) -> None:
    t = dedsec_table("Obfuscators", [
        ("Name", {"style": PALETTE["accent"]}),
        ("Description", {"style": PALETTE["text"]}),
    ])
    for name, (desc, _) in sorted(OBFUSCATORS.items()):
        t.add_row(name, desc)
    console.print(t)
    console.print(
        f"\n[{PALETTE['dim']}]Chain them: set obfuscators split_strings_ps,ps_case_flip[/]"
    )


@register("serve", "Start the HTTP payload server. Usage: serve [docroot]", category="listener")
def cmd_serve(s: Session, args: list[str]) -> None:
    docroot = args[0] if args else "."
    server = HTTPServer(s.lhost, s.http_port, docroot=docroot)
    if not server.start():
        return
    console.print(f"[dim]Serving payloads on http://{s.lhost}:{s.http_port}/[/dim]")
    console.print("[dim]Press Ctrl+C to stop.[/dim]")
    try:
        while True:
            import time
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


@register("listen", "Start a listener. Usage: listen [tls|raw]", category="listener")
def cmd_listen(s: Session, args: list[str]) -> None:
    """Start a listener.

    Default: line-buffered input — works with every non-PTY shell
             (bash, PowerShell, cmd, python).

    'listen raw': raw keystroke forwarding — required for shells that
             allocate their own PTY (python3_pty, socat). Lets you use
             sudo, vim, ssh, password prompts.

    'listen tls': TLS listener (line mode).
    """
    flags = {a.lower() for a in args}
    use_tls = s.use_tls or "tls" in flags
    use_raw = "raw" in flags

    if use_tls:
        listener = TLSListener(s.lhost, s.lport)
        if listener.start():
            listener.accept()
    else:
        listener = TCPListener(s.lhost, s.lport, raw=use_raw)
        if listener.start():
            listener.accept()


@register("test", "Test a payload locally. Usage: test <payload>", category="listener")
def cmd_test(s: Session, args: list[str]) -> None:
    if not args:
        warn("Usage: test <payload>")
        return
    name = args[0]
    p = PAYLOADS.get(name)
    if not p:
        fail(f"Unknown payload: {name}")
        return
    if not p.testable:
        warn(f"'{name}' is not testable on this host.")
        if p.test_note:
            info(p.test_note)
        return

    import subprocess
    import threading
    import time
    import socket as _sock

    lhost_test = "127.0.0.1"
    lport_test = s.lport
    payload_str = render(name, lhost_test, lport_test, s.http_port)

    info(f"Testing {name} against 127.0.0.1:{lport_test}")

    listener = TCPListener(lhost_test, lport_test, timeout=10.0)
    if not listener.start():
        return

    def run_payload():
        time.sleep(0.5)
        try:
            subprocess.Popen(
                payload_str, shell=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            fail(f"payload spawn failed: {e}")

    threading.Thread(target=run_payload, daemon=True).start()
    info("Accepting (waiting up to 10s)...")

    try:
        assert listener._server
        listener._server.settimeout(10.0)
        client, addr = listener._server.accept()
        ok(f"Payload connected back from {addr[0]}:{addr[1]}")

        try:
            client.settimeout(3.0)
            client.sendall(b"echo PF_TEST_OK\n")
            time.sleep(0.4)
            data = client.recv(4096)
            if b"PF_TEST_OK" in data:
                ok("Shell is live — echoed PF_TEST_OK")
            else:
                warn("Connected but no echo — shell may be non-interactive.")
        except _sock.timeout:
            warn("Connected but no response in 3s.")
        except Exception as e:
            info(f"Read error: {e}")
        client.close()
    except _sock.timeout:
        fail("No connection in 10s. Payload may have failed or crashed.")
    except KeyboardInterrupt:
        pass
    finally:
        listener.close()
        info("Test complete.")


@register("clear", "Clear the screen.", category="shell")
def cmd_clear(s: Session, args: list[str]) -> None:
    console.clear()


@register("exit", "Exit PayloadForge.", category="shell")
@register("quit", "Exit PayloadForge.", category="shell", hidden=True)
def cmd_exit(s: Session, args: list[str]) -> None:
    s.running = False
