"""lightme integration config entry."""

import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant import config_entries

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """lightme integration config_flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            host = user_input.get(CONF_HOST)
            port = user_input.get(CONF_PORT)

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=host, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_HOST, default="127.0.0.1"
                    ): cv.string,
                    vol.Optional(
                        CONF_PORT, default=8080
                    ): cv.port
                }
            )
        )
