"""JSON utility functions."""
from __future__ import annotations

import json
import logging

from lightme.exceptions import LightMeError

_LOGGER = logging.getLogger(__name__)

def load_json(fname: str, default: list | dict | None = None) -> list | dict:
    """Load JSON file."""

    try:
        with open(fname, encoding="utf-8") as json_file:
            return json.loads(json_file.read())
    except FileNotFoundError:
        _LOGGER.debug("JSON file not found: %s", fname)
    except ValueError as error:
        _LOGGER.exception("Failed to parse JSON content: %s", fname)
        raise LightMeError(error) from error
    except OSError as error:
        _LOGGER.exception("JSON file reading failed: %s", fname)
        raise LightMeError(error) from error
    return {} if default is None else default
