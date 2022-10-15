"""Boot Config & Startup"""
from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING, Any
import logging
import voluptuous as vol
from termcolor import colored

from lightme.exceptions import LightMeError
from lightme.typing import ConfigType

from . import core, config as config_util, loader
from .setup import (
    DATA_SETUP_STARTED,
    DATA_SETUP,
    DATA_SETUP_TIME,
    async_setup_component
)

if TYPE_CHECKING:
    from lightme.runner import RuntimeConfig

CORE_INTEGRATIONS = {"lightme"}
NETWORK_INTEGRATIONS = {""}

_LOGGER = logging.getLogger(__name__)

async def async_setup_lightme(
    runtime_config: RuntimeConfig
) -> core.LightMe | None:
    """Setup LightMe."""

    lightme = core.LightMe()
    lightme.config.config_dir = runtime_config.config_dir

    # Validate if configuration.json file exists
    # if there's file missing which should be exist, create new one with default value.
    if not await config_util.async_validate_config(lightme):
        _LOGGER.error("Error: Configuration file validation error.")
        return None

    _LOGGER.info("You can find configuration.json file at: %s", runtime_config.config_dir)

    config_dict = None
    is_basic_setup_success = False

    # Update json configuration files before loading them to dict.
    await lightme.async_add_executor_job(config_util.upgrade_lightme_config, lightme)

    try:
        config_dict = await config_util.async_lightme_config_json_to_dict(lightme)
    except LightMeError:
        _LOGGER.error(
            "Failed to parse configuration file."
        )
    else:
        is_basic_setup_success = (
            await async_from_config_dict(config_dict, lightme) is not None
        )

    if config_dict is None:
        print(
            colored(
            "Failed to convert configuration file to dictionary "
            f"with: {runtime_config.config_dir}"
            " - [boot.py: async_setup_lightme]",
            'red'
            )
        )
        return None

    if not is_basic_setup_success:
        _LOGGER.warning("Failed to setup core integrations.")
        return None

    return lightme

async def async_from_config_dict(
    config: ConfigType, lightme: core.LightMe
) -> core.LightMe | None:
    """Try to configure LightMe from configuration dictionary."""

    # user_defaults disabled.
    # lightme.user_defaults = user_defaults.UserDefaults(lightme, config_util)
    # await lightme.user_defaults.async_initialize()

    # Set up Core.
    _LOGGER.debug("Setting up %s", CORE_INTEGRATIONS)
    print(colored(f"Setting up {CORE_INTEGRATIONS} - [boot.py: async_from_config_dict]", 'yellow'))

    if not all(
        await asyncio.gather(
            *(
                async_setup_component(lightme, domain, config)
                for domain in CORE_INTEGRATIONS
            )
        )
    ):
        print(colored("LightMe core failed to initialize.", 'red'))
        return None

    print(colored("LightMe core initialized.", 'green'))

    core_config = config.get(core.DOMAIN, {})

    try:
        await config_util.async_process_lightme_core_config(lightme,core_config)
    except vol.Invalid as config_error:
        _LOGGER.error(
            config_error
        )
        return None
    except LightMeError:
        _LOGGER.error(
            "LightMe core failed to initialize. "
            "Configuration error."
        )
        return None

    await _async_setup_applications(lightme, config=config)

    return lightme

@core.callback
def _get_domains(config: dict[str, Any]) -> set[str]:
    """Get domains of components to set up."""

    domains = {key.split(" ")[0] for key in config if key != core.DOMAIN}

    return domains

async def async_setup_multiple_components(
    lightme: core.LightMe,
    domains: set[str],
    config: ConfigType
) -> None:
    """Set up multiple domains."""

    futures = {
        domain: lightme.async_create_task(async_setup_component(lightme, domain, config))
        for domain in domains
    }
    await asyncio.wait(futures.values())

async def _async_setup_applications(
    lightme: core.LightMe, config: dict[str, Any]
) -> None:
    """Setup applications."""

    lightme.data[DATA_SETUP_STARTED] = {}
    setup_time: dict[str, timedelta] = lightme.data.setdefault(DATA_SETUP_TIME, {})

    domains_to_setup = _get_domains(config)
    print(colored(f"Domains to be set up: {domains_to_setup}", 'yellow'))

    while domains_to_setup:
        old_domains_to_setup: set[str] = domains_to_setup
        applications_to_process = [
            app_or_exc
            for app_or_exc in (
                await loader.async_get_application(lightme, old_domains_to_setup)
            ).values()
            if isinstance(app_or_exc, loader.Application)
        ]

    print(colored(f"Application setup times: {setup_time}", 'yellow'))
