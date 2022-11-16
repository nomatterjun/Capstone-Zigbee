"""Constants for the LightMe integration."""

import homeassistant.helpers.config_validation as cv
from homeassistant.const import Platform

DOMAIN = "lightme"
MODEL = "Light Me Moment Sensor"
BRAND = "TeamZigbee"
VERSION = "0.1.0"
PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_API = "api"
CONF_HOST = "host"
DEFAULT_HOST = "127.0.0.1"
CONF_PORT = "port"
DEFAULT_PORT = 8080
CONF_ADDRESS = "address"
DEFAULT_ADDRESS = (DEFAULT_HOST, DEFAULT_PORT)

OPTIONS = [
    (CONF_HOST, DEFAULT_HOST, cv.string),
    (CONF_PORT, DEFAULT_PORT, cv.port)
]

# Informations
# [Key, Alias, Unit of Measurement, Icon, Device Class]
CURRENT_MOMENT = ["CurrentMoment", "현재 상황", "", "mdi:ray-vertex", ""]
UPCOMING_MOMENT = ["UpcomingMoment", "예약 상황", "", "mdi:ray-start-arrow", ""]

MOMENT_INFO = {
    CURRENT_MOMENT[0]: CURRENT_MOMENT,
    UPCOMING_MOMENT[0]: UPCOMING_MOMENT
}
