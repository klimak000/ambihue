from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml


class ConfigLoader:
    _instance: Optional["ConfigLoader"] = None
    _config_data: dict[str, Any]

    def __new__(cls, path: Union[str, Path] = "userconfig.yaml") -> "ConfigLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load(path)
        return cls._instance

    def _load(self, path: Union[str, Path]) -> None:
        with open(path, "r", encoding="utf-8") as f:
            self._config_data = yaml.safe_load(f)

        assert self.get_hue_entertainment()
        assert self.get_ambilight_tv()
        assert self.get_lights_setup()

    def get(self, key: str, default: Any = None) -> Dict[str, Any]:
        _ret = self._config_data.get(key, default)
        assert isinstance(_ret, dict)
        return _ret

    def get_ambilight_tv(self) -> Dict[str, Any]:
        _ret = self._config_data.get("ambilight_tv")
        assert isinstance(_ret, dict)
        return _ret

    def get_hue_entertainment(self) -> Dict[str, Any]:
        _ret = self._config_data.get("hue_entertainment_group")
        assert isinstance(_ret, dict)
        return _ret

    def get_lights_setup(self) -> Dict[str, Any]:
        _ret = self._config_data.get("lights_setup")
        assert isinstance(_ret, dict)
        return _ret

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """Access nested values, e.g. get_nested("db", "host")"""
        data: Any = self._config_data
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            else:
                return default
        return data if data is not None else default
