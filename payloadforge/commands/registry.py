from dataclasses import dataclass
from typing import Callable

from payloadforge.state import Session


@dataclass
class Command:
    name: str
    help: str
    handler: Callable[[Session, list[str]], None]
    category: str = "misc"
    hidden: bool = False


REGISTRY: dict[str, Command] = {}


def register(name: str, help: str, category: str = "misc", hidden: bool = False):
    def deco(fn):
        REGISTRY[name] = Command(name, help, fn, category, hidden)
        return fn
    return deco
