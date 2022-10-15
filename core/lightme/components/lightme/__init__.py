"""Application for LightMe to provide general data."""
import asyncio

import voluptuous as vol

from lightme.const import (
    ATTR_ENTITY_ID,
    BEHAV_TURN_ON,
    BEHAV_TURN_OFF,
    BEHAV_TOGGLE
)
import lightme.core as lme
from lightme.helpers import config_validation as cv
from lightme.helpers.typing import ConfigType

DOMAIN = lme.DOMAIN

async def async_setup(lightme: lme.LightMe, config: ConfigType) -> bool:
    """Set up general behaviors of LightMe."""

    async def async_handle_power_behavior(behavior: lme.BehaviorCall) -> None:
        """Handle calls to lightme.on/off."""

    behavior_schema = vol.Schema({ATTR_ENTITY_ID: cv.entity_ids}, extra=vol.ALLOW_EXTRA)

    lightme.behaviors.async_register(
        lme.DOMAIN, BEHAV_TURN_OFF, async_handle_power_behavior, schema=behavior_schema
    )
    lightme.behaviors.async_register(
        lme.DOMAIN, BEHAV_TURN_ON, async_handle_power_behavior, schema=behavior_schema
    )
    lightme.behaviors.async_register(
        lme.DOMAIN, BEHAV_TOGGLE, async_handle_power_behavior, schema=behavior_schema
    )

    return True
