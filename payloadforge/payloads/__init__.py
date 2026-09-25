from payloadforge.payloads.registry import (
    PAYLOADS, Payload, register, render, by_category,
)

# Import every module so @register calls run
import payloadforge.payloads.linux      # noqa: F401
import payloadforge.payloads.windows    # noqa: F401
import payloadforge.payloads.aws        # noqa: F401
import payloadforge.payloads.kubernetes # noqa: F401
import payloadforge.payloads.tunnels    # noqa: F401
import payloadforge.payloads.java       # noqa: F401
import payloadforge.payloads.web        # noqa: F401
import payloadforge.payloads.chains     # noqa: F401

__all__ = ["PAYLOADS", "Payload", "register", "render", "by_category"]
