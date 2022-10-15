"""Custom Types for LightMe."""
from typing import Any
from datetime import datetime

ConfigType = dict[str, Any]

class Object:
    obj_name: str
    moment_weight: dict[str, float]
    is_presence: bool
    counter_flag: int
    last_update: datetime
