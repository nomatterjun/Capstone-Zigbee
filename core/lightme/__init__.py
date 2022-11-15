"""The LightMe integration."""

import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .network import LightMeAPI as API
from .const import DOMAIN, PLATFORMS, CONF_API

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    # Return boolean to indicate that initialization was successful.
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up lightme from a config entry."""
    hass.data.setdefault(DOMAIN, {CONF_API: {}})
    api = API(hass, entry)
    hass.data[DOMAIN][CONF_API][entry.entry_id] = api
    for component in PLATFORMS:
        hass .async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    try:
        unload_ok = all(
            await asyncio.gather(
                *[
                    hass.config_entries.async_forward_entry_unload(entry, component)
                    for component in PLATFORMS
                ]
            )
        )
        if unload_ok:
            hass.data[DOMAIN][CONF_API].pop(entry.entry_id)
        return unload_ok
    except Exception:
        return True
