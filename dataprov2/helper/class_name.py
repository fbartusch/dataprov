from typing import Any

from ..config import globalConfig


def class_name(self: Any) -> str:
    return type(self).__name__ + ": " if globalConfig.get("show-class-name") else ""
