"""Run LightMe"""
from __future__ import annotations

import asyncio
import dataclasses
import logging

from . import boot

_LOGGER = logging.getLogger(__name__)

@dataclasses.dataclass
class RuntimeConfig:
    """Class to hold information for running LightMe"""

    config_dir: str

    debug: bool = False

class LightMeEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
    """Event loop policy for LightMe"""

    def __init__(self, debug: bool) -> None:
        """Init event loop policy"""
        super().__init__()
        self.debug = debug

    @property
    def loop_name(self) -> str:
        """Retrieve name of loop"""
        return self._loop_factory.__name__

async def setup_and_run_lightme(runtime_config: RuntimeConfig) -> int:
    """Setup LightMe and run"""

    lightme = await boot.async_setup_lightme(runtime_config)

    if lightme is None:
        return 1

    return await lightme.async_run()

def run(runtime_config: RuntimeConfig) -> int:
    """Run LightMe."""

    asyncio.set_event_loop_policy(LightMeEventLoopPolicy(runtime_config.debug))
    # Create loop.
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(setup_and_run_lightme(runtime_config))
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.run_until_complete(loop.shutdown_default_executor())
        finally:
            asyncio.set_event_loop(None)
            loop.close()
