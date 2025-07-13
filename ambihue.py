#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""Main docker script."""

import argparse
import json
import logging
import os
import signal
import sys
from typing import Any

import yaml

from src.ah_logger import init_logger
from src.main import AmbiHueMain, discover_hue, verify_hue, verify_tv

logger = logging.getLogger(__name__)


def _signal_handler(sig: Any, frame: Any) -> None:
    """Signal handler to handle Ctrl+C to gracefully exit app.

    Args:
        sig (Any): signal
        frame (Any): frame
    """
    assert sig
    assert frame
    logger.critical("Gracefully stopping all threads...")
    sys.exit(0)


# Register signal handler.
signal.signal(signal.SIGINT, _signal_handler)


def _init_parser() -> Any:
    parser = argparse.ArgumentParser(description="A script to handle test options.")
    parser.add_argument(
        "--verify",
        "-v",
        choices=["hue", "tv"],
        help="Specify which test option to handle.",
    )
    parser.add_argument(
        "--discover_hue",
        action="store_true",
        default=False,
        help="Detect Hue Entertainment configuration.",
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",  # Default log level
        help="Set the log level for the logger.",
    )

    try:
        import argcomplete  # pylint: disable=import-outside-toplevel

        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args()
    return args


_HOME_ASSISTANT_CONFIG = "/data/options.json"


def _create_user_config() -> None:
    if os.path.exists("userconfig.yaml"):
        return  # already exists

    # Try to load the user config from Home Assistant
    if os.path.exists(_HOME_ASSISTANT_CONFIG):
        with open(_HOME_ASSISTANT_CONFIG, encoding="utf-8") as ha_config_file:

            user_config_dict = json.load(ha_config_file)

            with open("userconfig.yaml", "w", encoding="utf-8") as out:
                yaml.dump(user_config_dict, out, default_flow_style=False)
            return

    raise FileNotFoundError(("userconfig.yaml NOT FOUND"))


def main() -> None:
    """Main function to run the spawn AmbiHue. Enable logs and parse input."""
    args = _init_parser()

    init_logger(args.loglevel)

    _create_user_config()

    if args.verify == "hue":
        verify_hue()
        return
    if args.verify == "tv":
        verify_tv()
        return
    if args.discover_hue:
        discover_hue()
        return

    AmbiHueMain().run()


if __name__ == "__main__":
    main()
