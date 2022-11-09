"""LightMe moment sensor."""
from __future__ import annotations

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
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    TEMP_CELSIUS
)

from .const import DOMAIN
from .network import Coordinator

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.string
})

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]

    coordinator = Coordinator(host, port)
    coordinator.update()

    _sensors += [MomentSensor(coordinator)]
    add_entities(_sensors, True)

class MomentSensor(SensorEntity):
    """Representation of a moment sensor."""

    def __init__(self, api: Coordinator) -> None:
        """Initialize the moment sensor."""
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._api = api

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
        return self._api.result

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        if self._api is None:
            return

        self._api.update()

        # TODO get data from moment sensor and update entity's state.

        self._attr_native_value = self.hass.data[DOMAIN]['temperature']
