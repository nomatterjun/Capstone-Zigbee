"""Helper class to network communication."""
from __future__ import annotations

import socket
import json
import logging
import datetime

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_HOST, CONF_PORT,
    MODEL,
    BRAND,
    VERSION,
    MOMENT_INFO,
    CURRENT_MOMENT,
    UPCOMING_MOMENT
)

_LOGGER = logging.getLogger(__name__)

SIZE = 1024

class LightMeAPI:
    """LightMe API."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the LightMe API."""
        self.hass = hass
        self.entry = entry
        self.result = {}
        self.version = VERSION
        self.model = MODEL
        self.brand = BRAND.lower()
        self.brand_name = BRAND
        self.unique = {}
        _LOGGER.debug(f"""
        [{BRAND}] initialized on {self.host}:{self.port}.
        """)

    @property
    def host(self):
        """Return host."""
        data = self.entry.options.get(CONF_HOST, self.entry.data.get(CONF_HOST))
        return data

    @property
    def port(self):
        """Return port."""
        data = self.entry.options.get(CONF_PORT, self.entry.data.get(CONF_PORT))
        return data

    def set_data(self, name, value):
        """Set entry data."""
        self.hass.config_entries.async_update_entry(
            entry=self.entry, data={**self.entry.data, name: value}
        )

    def get_data(self, name, default=False):
        """Get entry data."""
        return self.entry.data.get(name, default)

    def init_device(self, unique_id):
        """Initialize device."""
        self.unique[unique_id] = {
            'update': None,
            'register': self.register_update_state,
            'unregister': self.unregister_update_state
        }

    def get_device(self, unique_id, key):
        """Get device info."""
        return self.unique.get(unique_id, {}).get(key)

    def device_update(self, device_id):
        """Update device state."""
        unique_id = self.host + ":" + device_id
        device_update = self.unique.get(unique_id, {}).get('update')
        if device_update is not None:
            device_update()

    def register_update_state(self, unique_id, cb):
        """Register device update function to update entity state."""
        if not self.unique[unique_id].get('update'):
            _LOGGER.info(f"[{BRAND}] Register device => {unique_id} [{self.host}]")
            self.unique[unique_id]['update'] = cb

    def unregister_update_state(self, unique_id):
        """Unregister device update function."""
        if self.unique[unique_id]['update'] is not None:
            _LOGGER.info(f"[{BRAND}] Unregister device => {unique_id} [{self.host}]")
            self.unique[unique_id]['update'] = None

    async def update(self):
        """Update function for updating api info."""
        # TODO 반복해서 업데이트 ㄱ
        self.websocket()
        _LOGGER.info(f"[{BRAND}] Update moment sensor information: {self.result}")
        for key in MOMENT_INFO.keys():
            _LOGGER.warn(key)
            try:
                self.device_update(key)
            except Exception as exc:
                _LOGGER.info(f"[{BRAND}] Updating failed: {exc}")

    def websocket(self):
        server_address = (self.host, self.port)
        _LOGGER.warn(f"{server_address}")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(10)
            msg: str | bytes | None
            try:
                client_socket.connect(server_address)  # 서버에 접속
                client_socket.send("Requesting state of sensor.".encode())  # 서버에 메시지 전송
                msg = client_socket.recv(SIZE)  # 서버로부터 응답받은 메시지 반환
                print("resp from server : {}".format(msg))  # 서버로부터 응답받은 메시지 출력
            except socket.timeout as error:
                _LOGGER.error("Timeout while requesting socket connection, %s", error)
            finally:
                client_socket.close()
            
            if msg is not None:
                dict_msg = json.loads(msg)
                self.result = dict_msg
