"""Payload encoders."""

import base64
import gzip
import urllib.parse

ENCODERS: dict[str, tuple[str, callable]] = {}


def register_encoder(name: str, description: str):
    def deco(fn):
        ENCODERS[name] = (description, fn)
        return fn
    return deco


@register_encoder("base64", "Standard base64 encoding.")
def enc_b64(data: str) -> str:
    return base64.b64encode(data.encode()).decode()


@register_encoder("base64_nl", "Base64, newline-stripped (for shells that break on newlines).")
def enc_b64_nl(data: str) -> str:
    return base64.b64encode(data.encode()).decode().replace("\n", "")


@register_encoder("utf16le_b64", "UTF-16LE + base64 — the format PowerShell -EncodedCommand expects.")
def enc_utf16le_b64(data: str) -> str:
    return base64.b64encode(data.encode("utf-16-le")).decode()


@register_encoder("hex", "Hex string (with \\x prefix).")
def enc_hex(data: str) -> str:
    return "".join(f"\\x{b:02x}" for b in data.encode())


@register_encoder("url", "URL percent encoding.")
def enc_url(data: str) -> str:
    return urllib.parse.quote(data, safe="")


@register_encoder("gzip_b64", "Gzip then base64 — for large payloads.")
def enc_gzip_b64(data: str) -> str:
    return base64.b64encode(gzip.compress(data.encode())).decode()


@register_encoder("rev", "Reversed string (for trivial filter bypass).")
def enc_rev(data: str) -> str:
    return data[::-1]


def encode(name: str, data: str) -> str:
    if name not in ENCODERS:
        raise KeyError(f"unknown encoder: {name}")
    return ENCODERS[name][1](data)
