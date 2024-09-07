from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import sys
import importlib.util
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
file_path = os.path.join(parent_dir, "global_data", "global_config.py")
spec = importlib.util.spec_from_file_location("global_config", file_path)
modu = importlib.util.module_from_spec(spec)
sys.modules["global_config"] = modu
spec.loader.exec_module(modu)
import global_config
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = global_config.API_ID
    API_HASH: str = global_config.API_HASH

    USE_TG_BOT: bool = global_config.USE_TG_BOT
    BOT_TOKEN: str = global_config.MEMEFI_BOT_TOKEN
    CHAT_ID: str = global_config.CHAT_ID

    ACC_DELAY: list[int] = global_config.ACC_DELAY
    BIG_SLEEP: list[int] = global_config.BIG_SLEEP

    MIN_AVAILABLE_ENERGY: int = 100
    SLEEP_BY_MIN_ENERGY: int = 200

    ADD_TAPS_ON_TURBO: int = 2500

    AUTO_UPGRADE_TAP: bool = True
    MAX_TAP_LEVEL: int = 5
    AUTO_UPGRADE_ENERGY: bool = True
    MAX_ENERGY_LEVEL: int = 5
    AUTO_UPGRADE_CHARGE: bool = True
    MAX_CHARGE_LEVEL: int = 3

    APPLY_DAILY_ENERGY: bool = True
    APPLY_DAILY_TURBO: bool = True

    RANDOM_TAPS_COUNT: list[int] = [15, 75]
    SLEEP_BETWEEN_TAP: list[int] = [15, 25]

    USE_PROXY_FROM_FILE: bool = global_config.USE_PROXY

    USE_TAP_BOT: bool = True
    EMERGENCY_STOP: bool = False


settings = Settings()
