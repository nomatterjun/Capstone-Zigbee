"""LightMe moment sensor."""
from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (
    SensorEntity, SensorDeviceClass, SensorStateClass,
    PLATFORM_SCHEMA
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN, CONF_API, MOMENT_INFO
from .network import LightMeAPI as API

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor for LightMe."""

    api = hass.data[DOMAIN][CONF_API][config_entry.entry_id]

    def async_add_entity():
        """Add sensor from sensor."""
        entities = []
        for device in MOMENT_INFO.values():
            entities.append(MomentSensor(device, api))
        if entities:
            async_add_entities(entities)
    async_add_entity()

class MomentSensor(SensorEntity):
    """Representation of a moment sensor."""

    def __init__(self, device, api: API) -> None:
        """Initialize the moment sensor."""
        self.device = device
        self.api = api

    @property
    def name(self) -> str | None:
        return "Example Moment Sensor"

    @property
    def unique_id(self) -> str | None:
        return 'sensor.moment_sensor'

    @property
    def icon(self) -> str | None:
        return 'mdi:home-analytics'

    @property
    def state(self) -> Any:
        # value = self._api.result.get()
        return "sdf"
