"""lightme integration sensor platform."""
from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.typing import StateType

from . import get_coordinator
from .const import (
    CONF_HOST,
    CONF_PORT,
    BRAND,
    DOMAIN,
    MODEL,
    SW_VERSION
)

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="CurrentMoment",
        icon="mdi:ray-vertex",
        name="현재 상황"
    ),
    SensorEntityDescription(
        key="PreviousMoment",
        icon="mdi:ray-start",
        name="이전 상황"
    )
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the lightme integration sensor platform from a config_entry."""
    coordinator = await get_coordinator(hass, config_entry)

    sensors = [
        MomentSensor(coordinator, config_entry, description)
        for description in SENSOR_TYPES
    ]

    async_add_entities(sensors)

class MomentSensor(CoordinatorEntity, SensorEntity) :
    """Sensor representing moment sensor data."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription
    ):
        """Initializer."""
        super().__init__(coordinator) # coordinator defined here.
        self.description = description
        self.host = config_entry.data.get(CONF_HOST)
        self.port = config_entry.data.get(CONF_PORT)

        self._attr_icon = self.description.icon
        self._attr_unique_id = f"{self.host}-{self.description.key}"
        self._attr_name = self.description.name

    @property
    def device_info(self) -> DeviceInfo:
        """Return device_info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            manufacturer=BRAND,
            model=MODEL,
            name=self.description.name,
            sw_version=SW_VERSION,
            via_device=(DOMAIN, self.host)
        )

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.description.key) #[self.description.key]
