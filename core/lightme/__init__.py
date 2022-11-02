"""The LightMe integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .api_lightme import LightMeAPI as API

async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up LightMe"""

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LightMe from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    api = API(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = api

    # TODO Validate the API connection (and authentication)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
