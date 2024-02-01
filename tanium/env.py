import json
from typing import Dict, Final

__all__ = (
    "TANIUM_HOST",
    "TANIUM_USER",
    "TANIUM_PASSWORD",
)

with open("setting.json", encoding="UTF-8") as f:
    SETTING = json.loads(f.read())

TANIUM_HOST: Final[str] = SETTING['CORE']['Tanium']['INPUT']['API']['URL']
TANIUM_USER: Final[str] = SETTING['CORE']['Tanium']['INPUT']['API']['username']
TANIUM_PASSWORD: Final[str] = SETTING['CORE']['Tanium']['INPUT']['API']['password']
