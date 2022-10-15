"""Rest API for LightMe."""

from lightme.core import LightMe
from lightme.helpers.typing import ConfigType

async def async_setup(lightme: LightMe, config: ConfigType) -> bool:
    """Register API with HTTP interface."""

    lightme.http.register_view()
