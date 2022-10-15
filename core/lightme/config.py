"""Generate Configuration File"""
from __future__ import annotations

import logging
import os
import json
from typing import Any

from awesomeversion import AwesomeVersion
import voluptuous as vol

from lightme.exceptions import LightMeError
from lightme.util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM
from .const import (
    CONFIG_DIR_NAME,
    CONFIG_FILE,
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_TEMPERATURE_UNIT,
    CONF_TIME_ZONE,
    CONF_UNIT_SYSTEM,
    UNIT_SYSTEM_IMPERIAL,
    __version__
)
from .helpers import config_validation as cv
from .helpers.typing import ConfigType
from .loader import Application, ApplicationNotFound
from .util.json import load_json
from .core import LightMe

_LOGGER = logging.getLogger(__name__)

VERSION_FILE = ".LIGHTME_VERSION"
AUTOMATION_CONFIG_PATH = "automations.json"
MOMENT_CONFIG_PATH = "moments.json"

DEFAULT_CONFIG = {
    # Loads default set of applications. Do not remove.
    "default_config": {

    }
}

DEFAULT_AUTOMATIONS = {
    "automations": {

    }
}

DEFAULT_MOMENTS = {
    "moments": {

    }
}

CORE_CONFIG_SCHEMA = vol.All(
    {
        CONF_NAME: vol.Coerce(str),
        CONF_LATITUDE: cv.latitude,
        CONF_LONGITUDE: cv.longitude,
        CONF_ELEVATION: vol.Coerce(int),
        vol.Optional(CONF_TEMPERATURE_UNIT): cv.temperature_unit,
        CONF_UNIT_SYSTEM: cv.unit_system,
        CONF_TIME_ZONE: cv.time_zone
    }
)

def get_default_config_dir() -> str:
    """Append OS directory + default configuraiton directory."""

    data_dir = os.path.expanduser("~")
    return os.path.join(data_dir, CONFIG_DIR_NAME)

async def async_validate_config(lightme: LightMe) -> bool:
    """Validate if configuration file exists in given directory."""

    config_path = lightme.config.path(CONFIG_FILE)

    if os.path.isfile(config_path):
        return True

    print(
        "Cannot find configuration file. "
        "Creating new one with default values "
        f"in {lightme.config.config_dir}"
    )

    return await async_create_default_config(lightme)

async def async_create_default_config(lightme: LightMe) -> bool:
    """Create default configuration file in given directory."""

    return await lightme.async_add_executor_job(
        _create_default_config, lightme.config.config_dir
    )

def _create_default_config(config_dir: str) -> bool:
    """Create default configuration file."""

    config_path = os.path.join(config_dir, CONFIG_FILE)
    version_path = os.path.join(config_dir, VERSION_FILE)
    automations_path = os.path.join(config_dir, AUTOMATION_CONFIG_PATH)
    moments_path = os.path.join(config_dir, MOMENT_CONFIG_PATH)

    # JSON
    try:
        # configuration.json
        with open(config_path, "wt", encoding="utf8") as config_file:
            json.dump(DEFAULT_CONFIG, config_file)
        # .LIGHTME_VERSION
        with open(version_path, "wt", encoding="utf8") as version_file:
            version_file.write(__version__)
        # automations.json
        if not os.path.isfile(automations_path):
            with open(automations_path, "wt", encoding="utf8") as automation_file:
                json.dump(DEFAULT_AUTOMATIONS, automation_file)
        # moments.json
        if not os.path.isfile(moments_path):
            with open(moments_path, "wt", encoding="utf8") as moment_file:
                json.dump(DEFAULT_MOMENTS, moment_file)
        return True
    except OSError:
        print(f"Failed to create default configuration file as {config_path}")
        return False

async def async_lightme_config_json_to_dict(lightme: LightMe) -> dict:
    """Convert configuration file from json to dictionary.
    Load JSON file to get configurations.
    """

    config_dict = await lightme.loop.run_in_executor(
        None,
        load_json_config_file,
        lightme.config.path(CONFIG_FILE)
    )

    return config_dict

def load_json_config_file(config_path: str) -> dict[Any, Any]:
    """Parse JSON configuration file."""

    config_dict = load_json(config_path)

    # Check if parsed configuration is dictionary type
    if not isinstance(config_dict, dict):
        msg = (
            "Configuration file %s has no dictionary",
            os.path.basename(config_path)
        )
        _LOGGER.error(msg)
        raise LightMeError(msg)

    # config_dict can be list, so convert to dictionary for sure.
    for key, value in config_dict.items():
        config_dict[key] = value or {}
    return config_dict

def upgrade_lightme_config(lightme: LightMe) -> None:
    """Upgrade configuration via version."""

    version_path = lightme.config.path(VERSION_FILE)

    try:
        with open(version_path, encoding="utf8") as cur:
            config_version = cur.readline().strip()
    except FileNotFoundError:
        config_version = "0.0.0"

    if config_version == __version__:
        return

    _LOGGER.info(
        "Upgrading configuration version from %s to %s", config_version, __version__
    )

    _version = AwesomeVersion(config_version)

    with open(version_path, "wt", encoding="utf8") as version_file:
        version_file.write(__version__)

async def async_process_lightme_core_config(lightme: LightMe, config: dict) -> None:
    """Process [lightme] section of configuration file."""

    config = CORE_CONFIG_SCHEMA(config)

    aur_config = lightme.config

    for key, attr in (
        (CONF_LATITUDE, "latitude"),
        (CONF_LONGITUDE, "longtitude"),
        (CONF_ELEVATION, "elevation"),
        (CONF_NAME, "location_name")
    ):
        if key in config:
            setattr(aur_config, attr, config[key])

    if CONF_TIME_ZONE in config:
        aur_config.set_time_zone(config[CONF_TIME_ZONE])

    if CONF_UNIT_SYSTEM in config:
        if config[CONF_UNIT_SYSTEM] == UNIT_SYSTEM_IMPERIAL:
            aur_config.units = IMPERIAL_SYSTEM
        else:
            aur_config.units = METRIC_SYSTEM

async def async_process_component_config(
    lightme: LightMe, config: ConfigType, application: Application
) -> ConfigType | None:
    """Validate component config and return processed one."""

    domain = application.domain
    try:
        component = application.get_component()
    except Exception: # pylint: disable=broad-except
        _LOGGER.error("Unable to import %s", domain)
        return None
