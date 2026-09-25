from payloadforge.commands.registry import REGISTRY, Command
import payloadforge.commands.builtin  # noqa: F401 — register commands

__all__ = ["REGISTRY", "Command"]
