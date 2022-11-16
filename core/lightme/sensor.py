"""LightMe moment sensor."""
from __future__ import annotations

import logging
import voluptuous as vol
from typing import Any

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from .lightme_device import LightMeDevice
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

class MomentSensor(LightMeDevice, SensorEntity):
    """Representation of a moment sensor."""

    @property
    def state(self) -> Any:
        """Return state of moment sensor."""

        # TODO Socket
        value = self.api.result.get("time")
        return f"{value}"

    @property
    def name(self) -> str | None:
        """Return name of moment sensor."""
        if not self.api.get_data(self.unique_id):
            self.api.set_data(self.unique_id, True)
            return DOMAIN + " " + self.device[0]
        else:
            return self.device[1]

    @property
    def unique_id(self) -> str | None:
        return 'sensor.moment_sensor'

    @property
    def icon(self) -> str | None:
        return 'mdi:home-analytics'
