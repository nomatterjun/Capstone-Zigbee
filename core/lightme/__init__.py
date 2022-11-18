"""lightme intergration for moment sensor."""
from __future__ import annotations

import async_timeout
import logging
import socket
import json

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    ATTR_CURRENT_MOMENT,
    ATTR_PREVIOUS_MOMENT,
    CONF_HOST,
    CONF_PORT,
    PLATFORMS
)

SIZE = 1024
UPDATE_INTERVAL = 3
TIMEOUT_INTERVAL = 30

_LOGGER = logging.getLogger(__name__)

async def async_setup(
    hass: HomeAssistant,
    config: ConfigType
) -> bool:
    """Set up lightme integration component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up lightme integration component from a config entry."""

    if not entry.unique_id:
        hass.config_entries.async_update_entry(entry, unique_id=entry.data.get(CONF_HOST))

    coordinator = await get_coordinator(hass, entry)

    if not coordinator.last_update_success:
        await coordinator.async_config_entry_first_refresh()

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def get_coordinator(
    hass: HomeAssistant,
    entry: ConfigEntry
) -> DataUpdateCoordinator:
    """Get the data update coordinator."""
    host = entry.data.get(CONF_HOST, "127.0.0.1")
    port = entry.data.get(CONF_PORT, 8080)

    if hass.data[DOMAIN]:
        return hass.data[DOMAIN]

    async def async_get_data():
        with async_timeout.timeout(TIMEOUT_INTERVAL):
            data: dict[str: Any] = []
            try:
                server_address = (host, port)
                _LOGGER.info(f"{server_address}")

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.settimeout(TIMEOUT_INTERVAL)
                    msg: str | bytes | None
                    try:
                        client_socket.connect(server_address)  # 서버에 접속
                        client_socket.send("Requesting state of sensor.".encode())  # 서버에 메시지 전송
                        msg = client_socket.recv(SIZE)  # 서버로부터 응답받은 메시지 반환
                        _LOGGER.info("response from server : %s", format(msg))  # 서버로부터 응답받은 메시지 출력
                    except socket.timeout as err:
                        _LOGGER.error("Timeout while requesting socket connection, %s", err)
                    finally:
                        client_socket.close()
                    if msg is not None:
                        data = json.loads(msg)
            except Exception as exc:
                _LOGGER.error("Failed to receive data from socket Error: %s", exc)
                raise
            return data

    hass.data[DOMAIN] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_get_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL)
    )
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN]
    await coordinator.async_refresh()

    return hass.data[DOMAIN]
