"""PayloadForge interactive shell — DEDSEC prompt."""

import shlex
from pathlib import Path

from payloadforge.commands.registry import REGISTRY
import payloadforge.commands.builtin  # noqa: F401
import payloadforge.commands.testing  # noqa: F401
import payloadforge.commands.verify   # noqa: F401
from payloadforge.state import Session

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from payloadforge.ui.output import console
from payloadforge.ui.palette import PALETTE


class ShellCompleter(Completer):
    def __init__(self, session: Session) -> None:
        self._s = session

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        if " " in document.text_before_cursor:
            parts = document.text_before_cursor.split()
            if parts and parts[0] in ("generate", "info", "test", "list"):
                from payloadforge.payloads import PAYLOADS
                for name in sorted(PAYLOADS.keys()):
                    if name.startswith(word):
                        yield Completion(name, start_position=-len(word))
            elif parts and parts[0] == "set":
                for key in ("lhost", "lport", "http_port", "encoder", "tls", "obfuscators"):
                    if key.startswith(word):
                        yield Completion(key, start_position=-len(word))
            return
        for name in sorted(REGISTRY.keys()):
            c = REGISTRY[name]
            if c.hidden:
                continue
            if name.startswith(word):
                yield Completion(name, start_position=-len(word))


_PROMPT_STYLE = Style.from_dict({
    "prompt.lbracket": "ansibrightblack",
    "prompt.user":     "ansibrightred bold",
    "prompt.at":       "ansibrightblack",
    "prompt.host":     "ansibrightmagenta bold",
    "prompt.rbracket": "ansibrightblack",
    "prompt.tilde":    "ansibrightblack",
    "prompt.target":   "ansicyan",
    "prompt.dollar":   "ansibrightred bold",
})


def _history_path() -> str:
    return str(Path.home() / ".payloadforge_history")


def _prompt_fragments(s: Session):
    label = f"{s.lhost}:{s.lport}"
    if s.encoder:
        label += f"|{s.encoder}"
    if s.obfuscators:
        label += f"|{len(s.obfuscators)}obf"
    return [
        ("class:prompt.lbracket", "["),
        ("class:prompt.user", "DEDSEC"),
        ("class:prompt.at", "@"),
        ("class:prompt.host", "pf"),
        ("class:prompt.rbracket", "]"),
        ("class:prompt.tilde", "~"),
        ("class:prompt.lbracket", "["),
        ("class:prompt.target", label),
        ("class:prompt.rbracket", "]"),
        ("class:prompt.dollar", " $ "),
    ]


def _dispatch(s: Session, line: str) -> None:
    try:
        parts = shlex.split(line)
    except ValueError as e:
        console.print(f"[{PALETTE['danger']}][-][/] Parse error: {e}")
        return
    if not parts:
        return
    name, args = parts[0].lower(), parts[1:]
    c = REGISTRY.get(name)
    if c is None:
        console.print(
            f"[{PALETTE['danger']}][-][/] Unknown command: {name}  "
            f"[{PALETTE['dim']}](type help)[/]"
        )
        return
    try:
        c.handler(s, args)
    except Exception as e:
        console.print(f"[{PALETTE['danger']}][-][/] Error: {e}")


def run(state: Session) -> None:
    session = PromptSession(
        history=FileHistory(_history_path()),
        completer=ShellCompleter(state),
        complete_while_typing=True,
        style=_PROMPT_STYLE,
    )

    console.print(
        f"[{PALETTE['dim']}]  set [{PALETTE['primary']}]lhost[/] "
        f"and [{PALETTE['primary']}]lport[/], then "
        f"[{PALETTE['accent']}]generate[/] or "
        f"[{PALETTE['accent']}]listen[/][/]"
    )
    console.print(
        f"[{PALETTE['dim']}]  type [{PALETTE['primary']}]help[/] for commands, "
        f"[{PALETTE['primary']}]exit[/] to quit[/]\n"
    )

    while state.running:
        try:
            line = session.prompt(_prompt_fragments(state))
        except (KeyboardInterrupt, EOFError):
            console.print()
            break
        _dispatch(state, line)

    console.print(f"[{PALETTE['dim']}]session ended.[/]")
