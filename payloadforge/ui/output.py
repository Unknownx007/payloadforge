"""Shared output helpers with DEDSEC styling."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from payloadforge.ui.palette import PALETTE

console = Console()
err = Console(stderr=True)


def section(title: str) -> None:
    """Print a DEDSEC-style section header."""
    console.print()
    console.print(
        Panel(
            Text(title, style=f"bold {PALETTE['primary']}"),
            border_style=PALETTE["border"],
            expand=False,
            padding=(0, 2),
        )
    )


def dedsec_table(title: str, columns: list[tuple[str, dict]]) -> Table:
    """Build a DEDSEC-styled table."""
    t = Table(
        title=f"[bold {PALETTE['primary']}]{title}[/]",
        header_style=f"bold {PALETTE['accent']}",
        border_style=PALETTE["border"],
    )
    for name, kwargs in columns:
        t.add_column(name, **kwargs)
    return t


def ok(msg: str) -> None:
    console.print(f"[{PALETTE['secondary']}]✓[/] {msg}")


def fail(msg: str) -> None:
    console.print(f"[{PALETTE['danger']}]✗[/] {msg}")


def warn(msg: str) -> None:
    console.print(f"[{PALETTE['accent']}]![/] {msg}")


def info(msg: str) -> None:
    console.print(f"[{PALETTE['dim']}]{msg}[/]")
