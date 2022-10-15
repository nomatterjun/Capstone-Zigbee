"""Automation"""
from __future__ import annotations

from typing import (
    Any
)

from lightme.core import LightMe

DOMAIN = "automation"

async def async_setup(lightme: LightMe, config: dict[str, Any]) -> bool:
    """Setup all automations."""

    # lightme.data[DOMAIN] = component
