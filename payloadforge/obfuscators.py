"""Payload obfuscators — variable renaming, string splitting, PS chains.

These are best-effort transformations. They raise the cost of naive
signature detection; they don't defeat a determined analyst. That's
the honest ceiling.
"""

import random
import re
import string

OBFUSCATORS: dict[str, tuple[str, callable]] = {}


def register_obfuscator(name: str, description: str):
    def deco(fn):
        OBFUSCATORS[name] = (description, fn)
        return fn
    return deco


# ---------- Variable renaming ----------

_VAR_PREFIXES = ["_$", "__", "_0x", "_v", "x_", "_d"]


def _rand_var(prefix: str = "_") -> str:
    alphabet = string.ascii_lowercase + string.digits
    return f"{prefix}{''.join(random.choice(alphabet) for _ in range(8))}"


@register_obfuscator(
    "vars_bash",
    "Rename $VARIABLE references in bash to random names consistently.",
)
def obf_vars_bash(data: str) -> str:
    # Only rename user-defined vars — avoid $?, $$, $!, $0..$9
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
    "Rename simple single-letter Python variables in a payload string.",
)
def obf_vars_python(data: str) -> str:
    # Rename standalone single letters that look like variables
    mapping = {}
    for ch in string.ascii_lowercase:
        if re.search(rf"\b{ch}\b", data):
            mapping[ch] = _rand_var("_")

    def repl(m):
        tok = m.group(0)
        return mapping.get(tok, tok)

    return re.sub(r"\b[a-z]\b", repl, data)


# ---------- String splitting ----------

@register_obfuscator(
    "split_strings_bash",
    "Split string literals into concatenated substrings (bash-style).",
)
def obf_split_bash(data: str) -> str:
    # Break "word" into "wo""rd" (bash concatenates adjacent quoted strings)
    def repl(m):
        s = m.group(1)
        if len(s) < 4:
            return m.group(0)
        mid = len(s) // 2
        return f'"{s[:mid]}""{s[mid:]}"'

    return re.sub(r'"([^"\\]{4,})"', repl, data)


@register_obfuscator(
    "split_strings_python",
    "Split string literals into parenthesized concatenations (Python-style).",
)
def obf_split_python(data: str) -> str:
    def repl(m):
        s = m.group(1)
        if len(s) < 4:
            return m.group(0)
        mid = len(s) // 2
        return f'("{s[:mid]}" "{s[mid:]}")'

    return re.sub(r'"([^"\\]{4,})"', repl, data)


@register_obfuscator(
    "split_strings_ps",
    "Split strings into PowerShell concatenation ('ab' -> ('a'+'b')).",
)
def obf_split_ps(data: str) -> str:
    def repl(m):
        s = m.group(1)
        if len(s) < 4:
            return m.group(0)
        parts = [s[i:i + 2] for i in range(0, len(s), 2)]
        joined = "+".join(f"'{p}'" for p in parts)
        return f"({joined})"

    return re.sub(r"'([^'\\]{4,})'", repl, data)


# ---------- PowerShell-specific ----------

@register_obfuscator(
    "ps_case_flip",
    "Randomize case of PowerShell cmdlets/keywords (case-insensitive language).",
)
def obf_ps_case(data: str) -> str:
    # PowerShell is case-insensitive for cmdlets — flip case randomly
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
    # Insert backticks at cmdlet word boundaries
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
    "Concatenate + case-flip + split strings for PowerShell payloads.",
)
def obf_ps_concat_chain(data: str) -> str:
    data = obf_split_ps(data)
    data = obf_ps_case(data)
    return data


# ---------- Base64 chains ----------

@register_obfuscator(
    "double_b64",
    "Base64 twice — for endpoints that decode once.",
)
def obf_double_b64(data: str) -> str:
    import base64
    inner = base64.b64encode(data.encode()).decode()
    return base64.b64encode(inner.encode()).decode()


def obfuscate(name: str, data: str) -> str:
    if name not in OBFUSCATORS:
        raise KeyError(f"unknown obfuscator: {name}")
    return OBFUSCATORS[name][1](data)
