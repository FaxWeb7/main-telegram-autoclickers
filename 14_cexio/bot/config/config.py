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
    BOT_TOKEN: str = global_config.CEXIO_BOT_TOKEN
    CHAT_ID: str = global_config.CHAT_ID

    ACC_DELAY: list[int] = global_config.ACC_DELAY
    BIG_SLEEP: list[int] = global_config.BIG_SLEEP

    AUTO_TAP: bool = global_config.USE_TAPS
    RANDOM_TAPS_COUNT: list = [25, 75]
    SLEEP_BETWEEN_TAPS: list = [25, 35]
    AUTO_CONVERT: bool = True
    MINIMUM_TO_CONVERT: float = 0.1
    AUTO_BUY_UPGRADE: bool = True
    AUTO_TASK: bool = True
    AUTO_CLAIM_SQUAD_BONUS: bool = False
    REF_ID: str = '1724345287669959'

    USE_PROXY_FROM_FILE: bool = global_config.USE_PROXY


settings = Settings()


