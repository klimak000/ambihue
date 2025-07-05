"""Hue Light Bridge by Entertainment.

https://github.com/hrdasdominik/hue-entertainment-pykit/blob/main/src/hue_entertainment_pykit.py
"""

import logging
import time
from typing import Any, Dict, Tuple

from hue_entertainment_pykit import Streaming  # type: ignore  # missing some types
from hue_entertainment_pykit import Discovery, Entertainment, create_bridge, setup_logs

logger = logging.getLogger(__name__)


class HueEntertainmentGroupKit:

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the Hue Entertainment Group Kit.

        Args:
            config (Dict[str, Any]): Configuration dictionary containing the necessary parameters.

        Based on official documentation:
        https://github.com/hrdasdominik/hue-entertainment-pykit?tab=readme-ov-file#streaming
        """
        assert isinstance(config, dict), "Configuration must be a dictionary."

        # Initialize default logging
        setup_logs()

        # DEBUG and higher levels are active. ah_logger manages the root logging level.
        setup_logs(level=logging.DEBUG)

        # Set up the Bridge instance with the all needed configuration
        self._bridge = create_bridge(
            identification=config["_identification"],
            rid=config["_rid"],
            ip_address=config["_ip_address"],
            swversion=config["_swversion"],
            username=config["_username"],
            hue_app_id=config["_hue_app_id"],
            clientkey=config["_client_key"],
            name=config["_name"],
        )

        # Set up the Entertainment API service
        entertainment_service = Entertainment(self._bridge)

        # Fetch all Entertainment Configurations on the Hue bridge
        entertainment_configs = entertainment_service.get_entertainment_configs()

        # Add choose Entertainment Area selection logic
        entertainment_config = list(entertainment_configs.values())[config["index"]]

        # Set up the Streaming service
        self._streaming = Streaming(
            self._bridge, entertainment_config, entertainment_service.get_ent_conf_repo()
        )

        # Start streaming messages to the bridge
        self._streaming.start_stream()

        # Set the color space to xyb or rgb
        self._streaming.set_color_space("rgb")

    def set_color(
        self,
        light_id: int,
        color: Tuple[int, int, int],
    ) -> None:
        """Set given light to given color.

        Args:
            light_id (int): light ID inside the Entertainment API
            color (Tuple[int, int, int]): tuple for the color RGB8(int)
        """
        self._streaming.set_input((*color, light_id))

    def __del__(self) -> None:
        logger.warning("Stop streaming in 10s ...")

        # For the purpose of example sleep is used for all inputs to process before stop_stream is
        # called
        # Inputs are set inside Event queue meaning they're on another thread so user can interact
        # with application continuously
        time.sleep(0.1)

        # Stop the streaming session
        self._streaming.stop_stream()


def detect_hue_entertainment() -> None:
    """Detect Hue Entertainment configuration."""
    print("Get ready to click Hue Bridge button. Sleeping for 5 seconds...")
    time.sleep(5)  # wait for user to click the button

    print("Click Hue Bridge button now!")
    bridges = Discovery().discover_bridges()

    obj_list = list(bridges.values())
    assert (
        len(obj_list) > 0
    ), "No Hue bridges found. Check your network connection. Did you click the button?"

    obj = obj_list[0]
    print("\nCopy & paste configuration to userconfig.yaml:\n")
    print(
        f'  _identification: "{obj._identification}"\n'  # pylint: disable=protected-access
        f'  _rid: "{obj._rid}"\n'  # pylint: disable=protected-access
        f'  _ip_address: "{obj._ip_address}"\n'  # pylint: disable=protected-access
        f"  _swversion: {obj._swversion}\n"  # pylint: disable=protected-access
        f'  _username: "{obj._username}"\n'  # pylint: disable=protected-access
        f'  _hue_app_id: "{obj._hue_app_id}"\n'  # pylint: disable=protected-access
        f'  _client_key: "{obj._client_key}"\n'  # pylint: disable=protected-access
        f'  _name: "{obj._name}"\n'  # pylint: disable=protected-access
    )
