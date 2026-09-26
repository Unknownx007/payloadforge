"""Payload obfuscators — variable renaming, string splitting, PS chains.

These are best-effort transformations. They raise the cost of naive
signature detection; they do not defeat a determined analyst.
"""

import base64
import random
import re
import string

OBFUSCATORS: dict[str, tuple[str, callable]] = {}


def register_obfuscator(name: str, description: str):
    def deco(fn):
        OBFUSCATORS[name] = (description, fn)
        return fn
    return deco


# ============================================================
# Variable renaming
# ============================================================

def _rand_var(prefix: str = "_") -> str:
    alphabet = string.ascii_lowercase + string.digits
    return f"{prefix}{''.join(random.choice(alphabet) for _ in range(8))}"


_STRING_LITERAL_RE = re.compile(
    r'"(?:[^"\\]|\\.)*"'
    r"|"
    r"'(?:[^'\\]|\\.)*'"
)


def _protect_strings(data: str) -> tuple[str, list[str]]:
    originals: list[str] = []

    def keep(m):
        originals.append(m.group(0))
        return f"\x00S{len(originals) - 1}\x00"

    return _STRING_LITERAL_RE.sub(keep, data), originals


def _restore_strings(data: str, originals: list[str]) -> str:
    def restore(m):
        return originals[int(m.group(1))]
    return re.sub(r"\x00S(\d+)\x00", restore, data)


@register_obfuscator(
    "vars_bash",
    "Rename $VARIABLE references in bash to random names consistently.",
)
def obf_vars_bash(data: str) -> str:
    special = {"?", "$", "!", "#", "@", "*", "-", "_"}
    seen: dict[str, str] = {}

    def repl(m):
        name = m.group(1)
        if name in special or name.isdigit():
            return m.group(0)
        if name not in seen:
            seen[name] = _rand_var("_")
        return "${" + seen[name] + "}"

    return re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*|\d|\?)", repl, data)


@register_obfuscator(
    "vars_python",
    "Rename single-letter Python variables. Skips string literals and "
    "skips single letters preceded by a hyphen (CLI flags like -c, -i).",
)
def obf_vars_python(data: str) -> str:
    protected, originals = _protect_strings(data)
    pattern = re.compile(r"(?<!-)\b([a-z])\b")
    letters = set(m.group(1) for m in pattern.finditer(protected))
    mapping = {ch: _rand_var("_") for ch in letters}

    def repl(m):
        return mapping[m.group(1)]

    protected = pattern.sub(repl, protected)
    return _restore_strings(protected, originals)


# ============================================================
# String splitting
# ============================================================

@register_obfuscator(
    "split_strings_bash",
    "Split double-quoted string literals into adjacent-quoted substrings "
    "(bash concatenates adjacent strings).",
)
def obf_split_bash(data: str) -> str:
    def repl(m):
        s = m.group(1)
        if len(s) < 4:
            return m.group(0)
        mid = len(s) // 2
        return '"' + s[:mid] + '""' + s[mid:] + '"'

    return re.sub(r'"([^"\\]{4,})"', repl, data)


@register_obfuscator(
    "split_strings_python",
    "Split double-quoted string literals into parenthesized concatenations.",
)
def obf_split_python(data: str) -> str:
    def repl(m):
        s = m.group(1)
        if len(s) < 4:
            return m.group(0)
        mid = len(s) // 2
        return '("' + s[:mid] + '" "' + s[mid:] + '")'

    return re.sub(r'"([^"\\]{4,})"', repl, data)


@register_obfuscator(
    "split_strings_ps",
    "Replace '.' in PowerShell single-quoted literals with a marker char "
    "and reconstruct at runtime using .Replace(). "
    "Example: '127.0.0.1' -> \"127x0x0x1\".Replace(\"x\",\".\")",
)
def obf_split_ps(data: str) -> str:
    def pick_marker(s: str) -> str | None:
        for cand in ("x", "X", "~", "|", "^", "@", "#", "z", "Q"):
            if cand not in s:
                return cand
        return None

    def repl(m):
        s = m.group(1)
        if len(s) < 4 or "." not in s:
            return m.group(0)
        marker = pick_marker(s)
        if marker is None:
            return m.group(0)
        mangled = s.replace(".", marker)
        # Skip if mangled would contain characters that break PowerShell strings
        if any(c in mangled for c in ('"', "$", "`")):
            return m.group(0)
        return '"' + mangled + '".Replace("' + marker + '",".")'

    return re.sub(r"'([^'\\]{4,})'", repl, data)


# ============================================================
# PowerShell-specific
# ============================================================

@register_obfuscator(
    "ps_case_flip",
    "Randomize case of PowerShell cmdlets/keywords.",
)
def obf_ps_case(data: str) -> str:
    words = [
        "New-Object", "Net.WebClient", "DownloadString", "IEX",
        "Invoke-Expression", "Get-Stream", "Read", "Write",
        "ASCIIEncoding", "GetString", "GetBytes", "TcpClient",
        "Write", "Flush", "Close",
    ]
    for w in words:
        flipped = "".join(
            c.upper() if random.random() < 0.5 else c.lower() for c in w
        )
        data = data.replace(w, flipped)
    return data


@register_obfuscator(
    "ps_backticks",
    "Insert backtick line-continuations inside PowerShell cmdlet names.",
)
def obf_ps_backticks(data: str) -> str:
    words = [
        "New-Object", "Net.WebClient", "DownloadString",
        "Invoke-Expression", "ASCIIEncoding", "GetString", "TcpClient",
    ]
    for w in words:
        if w in data:
            parts = w.split("-")
            if len(parts) == 2:
                data = data.replace(w, f"{parts[0]}`-{parts[1]}")
    return data


@register_obfuscator(
    "ps_concat_chain",
    "Combine split_strings_ps + ps_case_flip for PowerShell payloads.",
)
def obf_ps_concat_chain(data: str) -> str:
    data = obf_split_ps(data)
    data = obf_ps_case(data)
    return data


# ============================================================
# Base64 chains
# ============================================================

@register_obfuscator(
    "double_b64",
    "Base64 twice — for endpoints that decode once.",
)
def obf_double_b64(data: str) -> str:
    inner = base64.b64encode(data.encode()).decode()
    return base64.b64encode(inner.encode()).decode()


def obfuscate(name: str, data: str) -> str:
    if name not in OBFUSCATORS:
        raise KeyError(f"unknown obfuscator: {name}")
    return OBFUSCATORS[name][1](data)
