from typing import Dict

from typing_extensions import Literal


class globalConfig:
    __conf: Dict[str, bool] = {}

    @staticmethod
    def get(name: str) -> bool:
        return globalConfig.__conf[name]

    @staticmethod
    def set(name: Literal["show-class-name"], value: bool) -> None:
        globalConfig.__conf[name] = value
