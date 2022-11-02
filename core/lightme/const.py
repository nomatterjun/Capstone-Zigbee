"""Constants for the LightMe integration."""

from homeassistant.const import Platform

DOMAIN = "lightme"
PLATFORMS: list[Platform] = [Platform.SCENE, Platform.SENSOR]
