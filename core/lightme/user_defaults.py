"""Manage user defaults in LightMe."""
from __future__ import annotations

from .core import LightMe
from .typing import ConfigType

class UserDefault:
    """User default configuration."""

    def __init__(
        self
    ) -> None:
        pass

class UserDefaults:
    """Manage User Default configurations."""

    def __init__(self, lightme: LightMe, config: ConfigType) -> None:
        """Init User Defaults."""
        self.lightme = lightme
        self._config = config
        self._defaults: dict[str, UserDefault] = {}

    async def async_initialize(self) -> None:
        """Init user default config."""

        self._defaults = {}
