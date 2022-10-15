"""Meta-Component to load default componenets."""

from lightme.core import LightMe
from lightme.helpers.typing import ConfigType

DOMAIN = "default_config"

async def async_setup(lightme: LightMe, config: ConfigType) -> bool:
    """Initialize default configuration."""
    print("Default Config")
