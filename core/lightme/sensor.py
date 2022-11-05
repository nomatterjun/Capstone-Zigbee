"""LightMe moment sensor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import (
    TEMP_CELSIUS
)

from .const import DOMAIN

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([MomentSensor()])

class MomentSensor(SensorEntity):
    """Representation of a moment sensor."""
    
    _attr_name: str | None = "Example Moment Sensor"
    _attr_native_unit_of_measurement: str | None = TEMP_CELSIUS
    _attr_device_class: SensorDeviceClass | str | None = SensorDeviceClass.TEMPERATURE
    _attr_state_class: SensorStateClass | str | None = SensorStateClass.MEASUREMENT

    def update(self) -> None:
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._attr_native_value = self.hass.data[DOMAIN]['temperature']
