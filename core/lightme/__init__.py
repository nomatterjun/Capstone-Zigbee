"""lightme intergration for moment sensor."""
from __future__ import annotations

import async_timeout
import logging
import json
import asyncio

from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry, ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    PLATFORMS
)

SIZE = 1024
UPDATE_INTERVAL = 3
TIMEOUT_INTERVAL = 10

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

    if hass.data[DOMAIN].get(host):
        return hass.data[DOMAIN][host]

    async def run_client(host: str, port: int):
        # 서버와의 연결을 생성합니다.
        reader: asyncio.StreamReader
        writer: asyncio.StreamWriter
        reader, writer = await asyncio.open_connection(host, port)

        # show connection info
        print("[C] connected")

        # 루프를 돌면서 입력받은 내용을 서버로 보내고,
        # 응답을 받으면 출력합니다.
        line = ("Capstone gogo")

        # 입력받은 내용을 서버로 전송
        payload = line.encode()
        writer.write(payload)
        await writer.drain()
        print(f"[C] sent: {len(payload)} bytes.\n")

        # 서버로부터 받은 응답을 표시
        data = await reader.read(1024)  # type: bytes
        print(f"[C] received: {len(data)} bytes")
        print(f"[C] message: {data.decode()}")
        if data is not None:
            result = json.loads(data)
            return result

    async def async_get_data():
        try:
            async with async_timeout.timeout(TIMEOUT_INTERVAL):
                return await run_client(host, port)
        except Exception as exc:
            raise UpdateFailed(f"LightMe error: {exc}") from exc

    # hass.data{
    #   "lightme": {
    #       "127.0.0.1": {
    #           coordinator
    # }
    # }
    # }
    # coordinator data: 전체
    hass.data[DOMAIN][host] = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_get_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL)
    )
    _coordinator: DataUpdateCoordinator = hass.data[DOMAIN][host]
    await _coordinator.async_refresh()

    return hass.data[DOMAIN][host]
