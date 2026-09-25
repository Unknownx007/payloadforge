"""PayloadForge CLI entry point."""

import atexit
import sys

from payloadforge._meta import __author__, __version__
from payloadforge.shell import run
from payloadforge.state import Session
from payloadforge.ui.banner import show_banner
from payloadforge.ui.output import console

HELP_TEXT = f"""
[bold]PayloadForge {__version__}[/bold] — reverse shell generator and listener
by {__author__}

[bold]Usage:[/bold]
  payloadforge [options]

[bold]Options:[/bold]
  -h, --help        Show this help
  -V, --version     Show version
      --no-banner   Skip the startup banner
      --no-anim     Skip banner animation
"""


def main(argv: list[str] | None = None) -> None:
    argv = list(argv if argv is not None else sys.argv[1:])

    if "--version" in argv or "-V" in argv:
        console.print(f"PayloadForge {__version__} — by {__author__}")
        return

    if "--help" in argv or "-h" in argv:
        console.print(HELP_TEXT)
        return

    no_banner = "--no-banner" in argv
    no_anim = "--no-anim" in argv

    if not no_banner:
        show_banner(console, animate=not no_anim)

    run(Session())


if __name__ == "__main__":
    main()
