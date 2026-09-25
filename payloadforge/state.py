from dataclasses import dataclass, field


@dataclass
class Session:
    lhost: str = "127.0.0.1"
    lport: int = 4444
    http_port: int = 8080
    use_tls: bool = False
    encoder: str | None = None
    obfuscators: list[str] = field(default_factory=list)
    last_generated: str | None = None
    last_payload_name: str | None = None
    running: bool = True
