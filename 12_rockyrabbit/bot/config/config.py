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
    BOT_TOKEN: str = global_config.ROCKYRABBIT_BOT_TOKEN
    CHAT_ID: str = global_config.CHAT_ID

    ACC_DELAY: list[int] = global_config.ACC_DELAY

    MIN_AVAILABLE_ENERGY: int = 126
    SLEEP_BY_MIN_ENERGY: list[int] = [1800, 3600]
    REF_LINK: str = "https://t.me/rocky_rabbit_bot/play?startapp=frId6046075760"

    AUTO_TAP: bool = global_config.USE_TAPS
    TAP_COUNT: list[int] = [50, 125]
    DELAY_BETWEEN_TAPS: list[int] = [15, 20]

    AUTO_BOOST: bool = True
    AUTO_UPGRADE_BOOST: bool = True
    MAX_ENERGY_LVL: int = 5
    MULTI_TAP_LVL: int = 5
    PASSIVE_INCOME_LVL: int = 10

    AUTO_TASK: bool = True
    AUTO_ENIGMA: bool = True
    AUTO_SUPERSET: bool = True
    AUTO_EASTER: bool = True

    AUTO_UPGRADE_CARDS: bool = True
    AUTO_CLAIM_UPGRADE_CARDS: bool = True

    USE_PROXY_FROM_FILE: bool = global_config.USE_PROXY
    BIG_SLEEP: list[int] = global_config.BIG_SLEEP


settings = Settings()


