"""LightMe moment sensor."""
from __future__ import annotations

import logging
from typing import Any
from time import sleep

from homeassistant.components.sensor import SensorEntity

from .lightme_device import LightMeDevice
from .const import DOMAIN, CONF_API, MOMENT_INFO

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
        self.api.update()
        value = self.api.result.get(self.device[0])
        _LOGGER.warn(f"Value of {self.device[0]}: {value}")
        return value

    @property
    def name(self) -> str | None:
        """Return name of moment sensor."""
        print(self.device)
        if not self.api.get_data(self.unique_id):
            self.api.set_data(self.unique_id, True)
            return DOMAIN + " " + self.device[0]
        else:
            return self.device[1]

    @property
    def icon(self) -> str | None:
        """Return the icon of the sensor."""
        icon = MOMENT_INFO.get(self.device[0])[3]
        return icon
