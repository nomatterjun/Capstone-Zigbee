"""Constants for lightme moment sensor."""

from homeassistant.const import Platform

DOMAIN = "lightme"
BRAND = "Team Zigbee"
MODEL = "Moment Sensor"
SW_VERSION = "0.0.1"

PLATFORMS: list[Platform] = [Platform.SENSOR]

ATTR_PREVIOUS_MOMENT = {
    'unique_id': "previous_moment",
    'name': "이전 상황",
    'icon': "mdi:ray-vertex"
}
ATTR_CURRENT_MOMENT = {
    'unique_id': "current_moment",
    'name': "현재 상황",
    'icon': "mdi:ray-vertex"
}

SENSOR_INFO = {
    ATTR_PREVIOUS_MOMENT["unique_id"]: ATTR_PREVIOUS_MOMENT,
    ATTR_CURRENT_MOMENT["unique_id"]: ATTR_CURRENT_MOMENT
}

CONF_HOST = "host"
CONF_PORT = "port"
