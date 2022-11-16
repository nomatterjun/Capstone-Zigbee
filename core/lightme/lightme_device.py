"""Device class."""
from __future__ import annotations

import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .network import LightMeAPI as API

_LOGGER = logging.getLogger(__name__)

class LightMeBase:
    """Base class."""

    def __init__(self, device, api: API):
        """Init device class."""
        self.device = device
        self.api = api
        self.host = api.host
        self.port = api.port
        self.api.init_device(self.unique_id)
        self.register = self.api.get_device(self.unique_id, 'register')
        self.unregister = self.api.get_device(self.unique_id, 'unregister')

    @property
    def unique_id(self) -> str:
        """Get unique ID."""
        return self.host + ":" + self.device[0]

    @property
    def device_info(self):
        """Return device registry information for this entity."""
        return {
            "connections": {(self.host, self.unique_id)},
            "identifiers": {
                (
                    DOMAIN,
                    self.host,
                )
            },
            "manufacturer": f"{self.api.brand_name}",
            "model": f"{self.api.model} v{self.api.version}",
            "name": f"{self.api.brand_name} {self.host}",
            "sw_version": self.api.version,
            "via_device": (DOMAIN, self.host),
            "DeviceEntryType": "service",
        }

class LightMeDevice(LightMeBase, Entity):
    """Defines a device entity."""

    TYPE = ""

    def __init__(self, device, api):
        """Initialize the instance."""
        super().__init__(device, api)
        self.api.unique[self.unique_id] = {}
        self.api.hass.data[DOMAIN][self.unique_id] = True

    @property
    def entity_registry_enabled_default(self):
        """entity_registry_enabled_default."""
        return True

    async def async_added_to_hass(self):
        """Subscribe to device events."""
        self.register(self.unique_id, self.async_update_callback)
        if self.device[0] == "Light Me":
            await self.api.update()
        self.async_write_ha_state()

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect device object when removed."""
        if self.unique_id in self.api.hass.data[DOMAIN]:
            self.api.hass.data[DOMAIN].pop(self.unique_id)
        self.unregister(self.unique_id)

    @callback
    def async_update_callback(self):
        """Update the device's state."""
        self.async_write_ha_state()

    @property
    def available(self):
        """Return True if device is available."""
        return True

    @property
    def should_poll(self) -> bool:
        """No polling needed for this device."""
        return False

    @property
    def extra_state_attributes (self):
        """Return the state attributes of the sensor."""
        attr = {}
        return attr