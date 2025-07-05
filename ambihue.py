#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
"""Main docker script."""

import argparse
import logging
import signal
import sys
from typing import Any

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


def main() -> None:
    """Main function to run the spawn AmbiHue. Enable logs and parse input."""
    args = _init_parser()

    init_logger(args.loglevel)

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
