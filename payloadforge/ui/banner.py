"""PayloadForge banner — detailed ASCII skull, DEDSEC palette."""

import random
import shutil
import time

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from payloadforge._meta import __author__, __tool__, __version__
from payloadforge.ui.palette import PALETTE

TAGLINE = "Craft. Obfuscate. Deliver."

QUOTES = [
    "A shell is a promise kept.",
    "Every target is a language waiting to be spoken.",
    "We are the ghosts in the machine.",
    "Fire shapes the tool. The tool shapes the outcome.",
    "Silence, then access.",
    "The door you don't knock on is the door they forget to lock.",
    "Precision over power.",
    "Exploit the gap between intent and implementation.",
    "One connection is enough.",
    "Trust nothing. Verify everything.",
    "The payload that works is the one that runs.",
    "Locked doors are just doors.",
]

WORDMARK = "P A Y L O A D F O R G E"
SUBTITLE = "═══  b y   D E D S E C  ═══"


# ─── ASCII skull — drawn in the classic text-art style ────────────────

LOGO_FULL = r'''

            ___           _,.---,---.,_
            |         ,;~'             '~;,
            |       ,;                     ;,
   Frontal  |      ;                         ; ,--- Supraorbital Foramen
    Bone    |     ,'                         /'
            |    ,;                        /' ;,
            |    ; ;      .           . <-'  ; |
            |__  | ;   ______       ______   ;<----- Coronal Suture
           ___   |  '/~"     ~" . "~     "~\'  |
           |     |  ~  ,-~~~^~, | ,~^~~~-,  ~  |
 Maxilla,  |      |   |        }:{        | <------ Orbit
Nasal and  |      |   l       / | \       !   |
Zygomatic  |      .~  (__,.--" .^. "--.,__)  ~.
  Bones    |      |    ----;' / | \ `;-<--------- Infraorbital Foramen
           |__     \__.       \/^\/       .__/
              ___   V| \                 / |V <--- Mastoid Process
              |      | |T~\___!___!___/~T| |
              |      | |`IIII_I_I_I_IIII'| |
     Mandible |      |  \,III I I I III,/  |
              |       \   `~~~~~~~~~~'    /
              |         \   .       . <-x---- Mental Foramen
              |__         \.    ^    ./
                            ^~~~^~~~^       -dcau (4/15/95)

'''

LOGO_COMPACT = r'''

                    ______
                 .-"      "-.
                /            \
               |              |
               |,  .-.  .-.  ,|
               | )(__/  \__)( |
               |/     /\     \|
               (_     ^^     _)
                \__|IIIIII|__/
                 | \IIIIII/ |
                 \          /
                  `--------`

'''

LOGO_TINY = r'''
    .---.
   / o o \
  |   ^   |
  |  \_/  |
   \     /
    '---'
'''

def _pick_logo() -> str:
    w = shutil.get_terminal_size((80, 24)).columns
    if w >= 70:
        return LOGO_FULL
    if w >= 45:
        return LOGO_COMPACT
    return LOGO_TINY


def _hex_lerp(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def _padded_lines(logo: str) -> list[str]:
    lines = logo.strip("\n").splitlines()
    max_w = max(len(line) for line in lines)
    return [line.ljust(max_w) for line in lines]


def _glitch_wordmark() -> Text:
    wm = Text()
    for i, ch in enumerate(WORDMARK):
        if ch == " ":
            wm.append(" ")
        elif i % 3 == 0:
            wm.append(ch, style=f"bold {PALETTE['primary']}")
        elif i % 3 == 1:
            wm.append(ch, style=f"bold {PALETTE['accent']}")
        else:
            wm.append(ch, style=f"bold {PALETTE['secondary']}")
    return wm


def show_banner(console: Console | None = None, animate: bool = True) -> None:
    console = console or Console()
    logo = _pick_logo()
    lines = _padded_lines(logo)

    n = max(1, len(lines) - 1)
    colored = [
        (line, _hex_lerp(PALETTE["primary"], PALETTE["accent"], i / n))
        for i, line in enumerate(lines)
    ]

    console.print()

    if animate:
        for line, color in colored:
            console.print(Align.center(Text(line, style=color)))
            time.sleep(0.05)
    else:
        block = Text()
        for i, (line, color) in enumerate(colored):
            block.append(line, style=color)
            if i < len(colored) - 1:
                block.append("\n")
        console.print(Align.center(block))

    console.print()
    console.print(Align.center(_glitch_wordmark()))
    console.print(Align.center(Text(SUBTITLE, style=PALETTE["dim"])))
    console.print()
    console.print(Align.center(Text(TAGLINE, style=PALETTE["text"])))
    console.print()
    console.print(
        Align.center(
            Text(
                f"version v{__version__}   ·   built by {__author__}",
                style=PALETTE["dim"],
            )
        )
    )
    console.print(
        Align.center(
            Text(
                f"\u201c{random.choice(QUOTES)}\u201d",
                style=f"italic {PALETTE['dim']}",
            )
        )
    )
    console.print()

    panel_body = Text.from_markup(
        f"[bold {PALETTE['danger']}]▓▒░  AUTHORIZED USE ONLY  ░▒▓[/]\n\n"
        f"[{PALETTE['text']}]PayloadForge is intended for authorized security testing[/]\n"
        f"[{PALETTE['text']}]and educational purposes only. Use it exclusively against[/]\n"
        f"[{PALETTE['text']}]systems you own or have explicit written permission to test.[/]\n\n"
        f"[{PALETTE['dim']}]Unauthorized access to systems is illegal.[/]"
    )
    console.print(
        Align.center(
            Panel(
                panel_body,
                title=f"[bold {PALETTE['primary']}]◤ {__tool__} ◢[/]",
                subtitle=f"[{PALETTE['dim']}]v{__version__} · {__author__}[/]",
                border_style=PALETTE["primary"],
                padding=(1, 3),
                expand=False,
            )
        )
    )
    console.print()
