"""Config flow for LightMe integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LightMe."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        # TODO Create some config_entry if any is needed.
        if user_input is not None:
            await self.async_set_unique_id()
            self._abort_if_unique_id_configured()
            return self.async_create_entry()
        
        return self.async_show_form(
            step_id="test",
            data_schema=vol.Schema(
                {
                    vol.Optional("TEST"): cv.string
                }
            )
        )

    async def async_step_import(self, user_input=None):
        """Handle configuration by yaml file."""
        await self.async_set_unique_id()
        for entry in self._async_current_entries():
            if entry.unique_id == self.unique_id:
                self.hass.config_entries.async_update_entry(entry, data=user_input)
                self._abort_if_unique_id_configured()
        return self.async_create_entry()

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
