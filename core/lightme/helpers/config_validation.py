"""Helper for config validation."""
from __future__ import annotations

import os
from typing import Any, TypeVar, overload, cast

import voluptuous as vol

from lightme.const import (
    TEMPERATURE_CELSIUS,
    TEMPERATURE_FAHRENHEIT,
    UNIT_SYSTEM_IMPERIAL,
    UNIT_SYSTEM_METRIC
)
from lightme.core import valid_entity_id
from lightme.util import dt as dt_util

_T = TypeVar("_T")

latitude = vol.All(
    vol.Coerce(float), vol.Range(min=-90, max=90), msg="invalid latitude"
)
longitude = vol.All(
    vol.Coerce(float), vol.Range(min=-180, max=180), msg="invalid longitude"
)
port = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))

def file(value: Any) -> str:
    """Validate if value is an existing file."""

    if value is None:
        raise vol.Invalid("There's no file.")
    file_in = os.path.expanduser(str(value))

    if not os.path.isfile(file_in):
        raise vol.Invalid(f"{file_in} is not a file.")
    if not os.access(file_in, os.R_OK):
        raise vol.Invalid(f"{file_in} is not readable.")

    return file_in

@overload
def ensure_list(value: None) -> list[Any]:
    ...

@overload
def ensure_list(value: list[_T]) -> list[_T]:
    ...

@overload
def ensure_list(value: list[_T] | _T) -> list[_T]:
    ...

@overload
def ensure_list(value: _T | None) -> list[_T] | list[Any]:
    """Wrap value in list."""

    if value is None:
        return []
    return cast("list[_T]", value) if isinstance(value, list) else [value]

def entity_id(value: Any) -> str:
    """Validate entity_id."""

    str_value = string(value).lower()
    if valid_entity_id(str_value):
        return str_value

    raise vol.Invalid(f"Entity ID {value} is an invalid entity ID.")

def entity_ids(value: str | list) -> list[str]:
    """Validate entity_ids."""

    if value is None:
        raise vol.Invalid("Entity IDs can not be None.")
    if isinstance(value, str):
        value = [entity_id.strip() for entity_id in value.split(",")]

def string(value: Any) -> str:
    """Coerce value to string."""

    if value is None:
        raise vol.Invalid("String value is None.")

    if isinstance(value, (list, dict)):
        raise vol.Invalid("Value should be a string.")

    return str(value)

def temperature_unit(value: Any) -> str:
    """Validate and transform temperature unit."""
    value = str(value).upper()
    if value == "C":
        return TEMPERATURE_CELSIUS
    if value == "F":
        return TEMPERATURE_FAHRENHEIT
    raise vol.Invalid("invalid temperature unit (expected C or F)")

unit_system = vol.All(
    vol.Lower, vol.Any(UNIT_SYSTEM_METRIC, UNIT_SYSTEM_IMPERIAL)
)

def time_zone(value: str) -> str:
    """Validate timezone."""
    if dt_util.get_time_zone(value) is not None:
        return value
    raise vol.Invalid(
        "Invalid timezone passed in."
    )
