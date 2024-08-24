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
    BOT_TOKEN: str = global_config.HAMSTERKOMBAT_BOT_TOKEN
    CHAT_ID: str = global_config.CHAT_ID

    USE_PROXY: bool = global_config.USE_PROXY

    MIN_AVAILABLE_ENERGY: int = 126
    SLEEP_BY_MIN_ENERGY: list[int] = [1800, 3600]

    AUTO_UPGRADE: bool = True
    MAX_LEVEL: int = 8
    MAX_PRICE: int = 2000000

    BALANCE_TO_SAVE: int = 52
    UPGRADES_COUNT: int = 10

    MAX_COMBO_PRICE: int = 4000000

    APPLY_COMBO: bool = True
    APPLY_PROMO_CODES: bool = True
    APPLY_DAILY_CIPHER: bool = True
    APPLY_DAILY_REWARD: bool = True
    APPLY_DAILY_ENERGY: bool = True
    APPLY_DAILY_MINI_GAME: bool = True
    APPLY_DAILY_ENERGY: bool = True

    USE_RANDOM_MINI_GAME_KEY: bool = True
    AUTO_COMPLETE_TASKS: bool = True

    USE_TAPS: bool = True
    RANDOM_TAPS_COUNT: list[int] = [50, 200]
    SLEEP_BETWEEN_TAP: list[int] = [10, 25]

    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = global_config.ACC_DELAY

    BIG_SLEEP: list[int] = global_config.BIG_SLEEP

    USE_RANDOM_USERAGENT: bool = True


settings = Settings()
