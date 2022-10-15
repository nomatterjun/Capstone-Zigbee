"""LightMe aiohttp Site."""
from __future__ import annotations

import asyncio
from ssl import SSLContext

from aiohttp import web

class LightMeTCPSite(web.BaseSite):
    """LightMe specific aiohttp Site."""

    def __init__(
        self,
        runner: web.BaseRunner,
        host: None | str | list[str],
        port: int,
        *,
        shutdown_timeout: float = 10.0,
        ssl_context: SSLContext | None = None,
        backlog: int = 128
    ) -> None:
        """Initialize LightMeTCPSite."""
        super().__init__(
            runner,
            shutdown_timeout=shutdown_timeout,
            ssl_context=ssl_context,
            backlog=backlog
        )
        self._host = host
        self._port = port

    async def start(self) -> None:
        """Start server."""

        await super().start()
        loop = asyncio.get_running_loop()
        server = self._runner.server
        assert server is not None
        self._server = await loop.create_server(
            server,
            self._host,
            self._port,
            ssl=self._ssl_context,
            backlog=self._backlog
        )
