"""Payload registry."""

from dataclasses import dataclass, field


@dataclass
class Payload:
    name: str
    category: str       # linux | windows | web | macos
    language: str       # python, bash, powershell, ...
    template: str       # with {lhost} {lport}
    description: str
    testable: bool = True       # can be tested on this Linux host
    test_note: str = ""         # shown if testable is False
    tags: list[str] = field(default_factory=list)


PAYLOADS: dict[str, Payload] = {}


def register(
    name: str,
    category: str,
    language: str,
    template: str,
    description: str,
    testable: bool = True,
    test_note: str = "",
    tags: list[str] | None = None,
):
    PAYLOADS[name] = Payload(
        name=name,
        category=category,
        language=language,
        template=template,
        description=description,
        testable=testable,
        test_note=test_note,
        tags=tags or [],
    )


def render(name: str, lhost: str, lport: int, http_port: int = 8080) -> str:
    p = PAYLOADS.get(name)
    if p is None:
        raise KeyError(f"unknown payload: {name}")
    return p.template.format(lhost=lhost, lport=lport, http_port=http_port)

def by_category(cat: str) -> list[Payload]:
    return sorted(
        [p for p in PAYLOADS.values() if p.category == cat],
        key=lambda p: p.name,
    )
