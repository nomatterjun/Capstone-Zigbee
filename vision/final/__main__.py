"""Main File."""
from __future__ import annotations

import sys

from . import sensor

def main() -> int:
    """Start moment sensor."""
    exit_code = sensor.run()

    return exit_code

if __name__ == "__main__":
    sys.exit(main())