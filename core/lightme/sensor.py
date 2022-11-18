"""lightme integration sensor platform."""
from __future__ import annotations

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
    SW_VERSION,
    SENSOR_INFO
)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="PreviousMoment",
        icon="mdi:ray-vertex",
        name="이전 상황"
    ),
    SensorEntityDescription(
        key="CurrentMoment",
        icon="mdi:ray-vertex",
        name="현재 상황"
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
        MomentSensor(coordinator, config_entry, description) for description in SENSOR_TYPES
    ]

    async_add_entities(sensors)

class MomentSensor(CoordinatorEntity, SensorEntity) :
    """Sensor platform class."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: SensorEntityDescription
    ):
        """Initializer."""
        super().__init__(coordinator)
        self.description = description
        self.host = config_entry.data.get(CONF_HOST)
        self.port = config_entry.data.get(CONF_PORT)

        self._attr_unique_id = f"{self.host}-{self.description.key}"

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
    def icon(self) -> str | None:
        """Return icon of sensor."""
        return self.description.icon

    @property
    def name(self) -> str | None:
        """Return name of sensor."""
        return self.description.name

    @property
    def state(self) -> StateType:
        return "null"
