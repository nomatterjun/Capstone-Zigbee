"""Unit System helper class and methods"""
from __future__ import annotations

from lightme.const import (
    UNIT_SYSTEM_METRIC,
    UNIT_SYSTEM_IMPERIAL,
    TEMPERATURE_CELSIUS,
    TEMPERATURE_FAHRENHEIT
)

from . import (
    temperature as temp_util
)

class UnitSystem:
    """Unit System"""

    def __init__(
        self,
        name: str,
        temperature: str
    ) -> None:
        """Init unit system object"""

        self.name = name
        self.temperature_unit = temperature

    def temperature(self, temperature:  float, from_unit: str) -> float:
        """Convert the given temperature to another unit system"""

        return temp_util.convert(
            temperature=temperature,
            from_unit=from_unit,
            to_unit=self.temperature_unit
        )

METRIC_SYSTEM = UnitSystem(
    name=UNIT_SYSTEM_METRIC,
    temperature=TEMPERATURE_CELSIUS
)

IMPERIAL_SYSTEM = UnitSystem(
    name=UNIT_SYSTEM_IMPERIAL,
    temperature=TEMPERATURE_FAHRENHEIT
)
