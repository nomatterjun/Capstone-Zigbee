"""Main File"""
from __future__ import annotations

from .const import REQUIRED_PYTHON_VER

import sys
import os

def validate_python() -> None:
    """Validate Minimal Required Version of Python"""
    if sys.version_info[:3] < REQUIRED_PYTHON_VER:
        print(f"""Core needs Python with at least 
                {REQUIRED_PYTHON_VER[0]}.{REQUIRED_PYTHON_VER[1]}.{REQUIRED_PYTHON_VER[2]}
        """)
        sys.exit(1)

def main() -> int:
    """Start Core

    This is a main entry point for total project
    """
    validate_python()

    local_dir = os.path.abspath(os.path.join(os.getcwd()))
    print(local_dir)

    # pylint: disable=import-outside-toplevel
    from . import boot
    exit_code = boot.run()
    print(f"Exit Code: {exit_code}")

    return exit_code

if __name__ == "__main__":
    main()
