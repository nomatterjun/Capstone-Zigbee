"""Functions to fetch sensor datas."""

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Dict

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

@dataclass
class Medium:
    """DTO to get object datas from moment sensor."""
    name: str
    friendly_name: str
    is_online: bool
    counter_flag: int
    moment_weight: Dict()
    last_update: date

class LightMeAPI:
    """LightMe API"""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the LightMe."""
        self.hass = hass
