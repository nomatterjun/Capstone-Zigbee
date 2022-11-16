"""Boot Config & Startup"""
from __future__ import annotations

import asyncio
import logging
import os
import sys

from . import core

_LOGGER = logging.getLogger(__name__)
    
async def async_setup_core() -> core.Core | None:
    """Set Up Core"""
    
    _core = core.Core()
    
    return _core

async def setup_and_run() -> int:
    """Set Up & Run"""
    core = await async_setup_core()

    if core is None:
        return 1

    return await core.async_run()

def run() -> int:
    """Run Core"""
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(setup_and_run())
    finally:
        asyncio.set_event_loop(None)
        loop.close()
