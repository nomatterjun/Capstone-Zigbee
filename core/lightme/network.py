"""Helper class to network communication."""
from __future__ import annotations

import socket
import json
import logging

_LOGGER = logging.getLogger(__name__)

SIZE = 1024

class Coordinator:
    """Coordinator for receiving data from moment sensor."""

    def __init__(
        self, host: str, port: str
    ) -> None:
        """Initialize the coordinator."""
        self._host = host
        self._port = port
        self.result = {}

    def update(self):
        """Update function for updating data."""
        server_address = (self._host, int(self._port))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(10)
            msg: str | bytes
            try:
                client_socket.connect(server_address)  # 서버에 접속
                client_socket.send("Requesting state of sensor.".encode())  # 서버에 메시지 전송
                msg = client_socket.recv(SIZE)  # 서버로부터 응답받은 메시지 반환
                print("resp from server : {}".format(msg))  # 서버로부터 응답받은 메시지 출력
            except socket.timeout as error:
                _LOGGER.error("Timeout while requesting socket connection, %s", error)
            finally:
                client_socket.close()
            
            dict_msg = json.loads(msg)
            self.result = dict_msg['result']
