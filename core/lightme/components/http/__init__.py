"""LightMe API helper."""
from __future__ import annotations

from typing import Final
from termcolor import colored
import logging

import fastapi

DOMAIN: Final = "http"

_LOGGER: Final = logging.getLogger(__name__)

async def async_setup(lightme: LightMe, config: ConfigType) -> bool:
    """Set up HTTP server."""

    print(colored("Hi!", 'green'))

    return True
