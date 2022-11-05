"""Config flow for LightMe integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult, FlowHandler
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# class ConfigFlow(FlowHandler):
#     """Handle a config flow for LightMe."""
#     VERSION = 1

#     async def async_step_user(
#         self, user_input = None
#     ) -> FlowResult:
#         """Handle the initial step."""

#         errors = {}

#         return self.async_show_form(
#             step_id="user",
#             data_schema=vol.Schema(
#                 {
#                     vol.Optional("host"): cv.string
#                 }
#             ),
#             errors=errors
#         )
