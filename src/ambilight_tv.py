import json
import logging
import os
import time
from typing import Any, Dict

import requests
import urllib3

logger = logging.getLogger(__name__)

# Suppress "Unverified HTTPS request is being made" error message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AmbilightTV:

    def __init__(self, config: Dict[str, Any]) -> None:
        self._session = requests.Session()  # keep session to increase performance
        self._session.verify = False  # disable SSL
        self._session.mount(
            "https://", requests.adapters.HTTPAdapter(pool_connections=1)
        )  # limit to 1 connection!

        self._protocol = config.get("protocol", "https://")
        self._ip = config["ip"]
        self._port = config.get("port", "1926")
        self._api_version = config.get("api_version", "6")

        # https://jointspace.sourceforge.net/projectdata/documentation/jasonApi/1/doc/API-Method-ambilight-processed-GET.html
        # https://github.com/eslavnov/pylips/blob/master/docs/Home.md
        self._path = config.get("path", "ambilight/processed")

        self._full_path = (
            f"{self._protocol}{self._ip}:{self._port}/{self._api_version}/{self._path}"
        )

        self._wait_for_startup_s = config.get("wait_for_startup_s", 8)
        self.power_on_time_s = config.get("power_on_time_s", 8)

    def wait_for_startup(self) -> None:
        _was_enabled = True

        for cnt in range(int(self._wait_for_startup_s / 3)):
            response = os.system(f"ping -c 1 -W 1 {self._ip} > /dev/null 2>&1")
            if response == 0:
                if _was_enabled is False:
                    logger.error(f"TV is powering on... add {self.power_on_time_s}s more")
                    time.sleep(self.power_on_time_s)
                return

            _was_enabled = False
            logger.error(f"TV is not responding for {cnt*3}/{self._wait_for_startup_s}s")
            time.sleep(2)

        raise RuntimeError(f"TV IS NOT RESPONDING FOR {self._wait_for_startup_s}s")  #

    def get_ambilight_raw(self) -> Any:
        # logger.debug(f"Sending GET request to:\n{self._full_path}")
        try:
            response = self._session.get(
                self._full_path,
                verify=False,
                timeout=0.2,
            )
        except requests.exceptions.ConnectTimeout as err:
            raise RuntimeError(err) from err
        except requests.exceptions.ConnectionError as err:
            raise RuntimeError(err) from err
        except requests.exceptions.ReadTimeout as err:
            raise RuntimeError(err) from err

        return response.text

    def get_ambilight_json(self) -> Dict[str, Any]:
        response_text = self.get_ambilight_raw()

        try:
            data = json.loads(response_text)
            assert isinstance(data, dict), "Response is not a JSON object"
            # logger.debug(f"data:\n{data}\n")
        except json.JSONDecodeError as err:
            logger.error(f"Decoding JSON error:\n{response_text}")
            raise err
        return data
