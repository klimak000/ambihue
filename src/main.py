import logging
import sys
from json import JSONDecodeError
from pathlib import Path
from time import sleep
from typing import Any, Dict, Optional, Union

from src.ambilight_tv import AmbilightTV  # TODO install
from src.color_mixer import ColorMixer
from src.config_loader import ConfigLoader
from src.hue_entertainment import HueEntertainmentGroupKit, detect_hue_entertainment

logger = logging.getLogger(__name__)


class AmbiHueMain:
    """Main class to run the AmbiHue application."""

    def __init__(self, config_path: Union[str, Path] = "userconfig.yaml") -> None:
        """Initialize the AmbiHue main class."""
        self._config_loader = ConfigLoader(config_path)

        self._tv = AmbilightTV(self._config_loader.get_ambilight_tv())
        self._hue = HueEntertainmentGroupKit(self._config_loader.get_hue_entertainment())
        self._mixer = ColorMixer()

        self._light_setup = self._config_loader.get_lights_setup()

        self._tv_error_cnt = 0

    def _read_tv(self) -> Optional[Dict[str, Any]]:
        """Read the Ambilight TV data.

        If the TV is not reachable, return None.

        Returns:
            Optional[Dict[str, Any]]: The JSON data from the TV or None if an error occurs.
        """
        try:
            tv_data = self._tv.get_ambilight_json()
            self._tv_error_cnt = 0  # reset error count on success
            return tv_data

        except JSONDecodeError as err:
            self._tv_error_cnt += 1
            logger.error(f"Decoding JSON error: {err}")

        except RuntimeError as err:
            self._tv_error_cnt += 1
            logger.error(f"Request error: {err}")

        # Error handling for TV data
        if self._tv_error_cnt > 10:
            self._exit(10)  # exit if TV is not reachable for too long

        return None  # return None if an error occurs

    def run(self) -> None:
        """Run the main loop of the AmbiHue application."""
        self._tv.wait_for_startup()
        logger.info("Starting AmbiHue application...")

        while True:  # while true
            sleep(0.01)

            tv_data = self._read_tv()
            if tv_data is None:
                continue  # skip this loop if TV data is not available this time

            self._mixer.apply_tv_data(tv_data)
            self._mixer.print_colors()

            for light_name, light_data in self._light_setup.items():
                color = self._mixer.get_average_color(light_data["positions"])
                self._hue.set_color(light_data["id"], color.get_tuple())

                print_color = color.get_css_color_name_colored()
                logger.info(f"Light: {light_name} - {print_color} - {light_data} ")

            logger.info("\n\n")

    def _exit(self, exit_code: int = 0) -> None:
        """Exit the AmbiHue application."""
        logger.warning(f"Exiting AmbiHue application {exit_code}.")
        del self._hue
        del self._tv
        sys.exit(exit_code)


def verify_tv() -> None:
    """Verify the Ambilight TV connection."""
    config = ConfigLoader().get_ambilight_tv()
    data = AmbilightTV(config).get_ambilight_json()
    mixer = ColorMixer()
    mixer.apply_tv_data(data)
    mixer.print_colors()


def verify_hue() -> None:
    """Verify the Hue Entertainment connection."""
    config = ConfigLoader().get_hue_entertainment()
    HueEntertainmentGroupKit(config).set_color(0, (255, 0, 0))  # check zero index light


def discover_hue() -> None:
    """Discover Hue Entertainment configuration."""
    detect_hue_entertainment()
