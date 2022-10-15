"""Main File"""
from __future__ import annotations

import argparse
import sys
import os

from .const import (
    REQUIRED_PYTHON_VER,
    __version__
)

def validate_python() -> None:
    """Validate minimal required version of Python."""

    if sys.version_info[:3] < REQUIRED_PYTHON_VER:
        print(f"""Core needs Python with at least
                {REQUIRED_PYTHON_VER[0]}.{REQUIRED_PYTHON_VER[1]}.{REQUIRED_PYTHON_VER[2]}
        """)
        sys.exit(1)

def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""

    # pylint: disable=import-outside-toplevel
    from . import config
    parser = argparse.ArgumentParser(
        description='2022 캡스톤 디자인 지그비조 화이팅!'
    )
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument(
        '-c',
        '--config',
        metavar="path_to_config_dir",
        default=config.get_default_config_dir(),
        help="Directory of Configuration File"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Start LightMe in debug mode"
    )

    args = parser.parse_args()

    return args

def validate_config_path(config_dir: str) -> None:
    """Validate configuration directory."""

    # pylint: disable=import-outside-toplevel
    from . import config

    # check if configuration directory exists
    if not os.path.isdir(config_dir):
        if config_dir != config.get_default_config_dir():
            print(
                f"Error: Configuration directory {config_dir} "
                "doesn't exist"
            )
            sys.exit(1)

        try:
            os.mkdir(config_dir)
        except OSError:
            print(
                "Error: Failed to create default configuraiton "
                f"directory {config_dir}"
            )
            sys.exit(1)

def main() -> int:
    """Start LightMe.

    This is a main entry point for total project
    """

    validate_python()

    args = get_arguments()

    config_dir = os.path.abspath(os.path.join(os.getcwd(), args.config))
    validate_config_path(config_dir=config_dir)

    # pylint: disable=import-outside-toplevel
    from . import runner

    runtime_config = runner.RuntimeConfig(
        config_dir=config_dir,
        debug=args.debug
    )

    exit_code = runner.run(runtime_config)

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
