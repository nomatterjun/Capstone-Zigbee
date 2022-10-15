"""Init File"""
from __future__ import annotations

from typing import Iterable, KeysView

def ensure_unique_string(
    preferred_string: str, current_strings: Iterable[str] | KeysView[str]
) -> str:
    """Return string which is not present in current_strings."""

    test_string = preferred_string
    current_strings_set = set(current_strings)

    tries = 1

    while test_string in current_strings_set:
        tries += 1
        test_string = f"{preferred_string}_{tries}"

    return test_string
