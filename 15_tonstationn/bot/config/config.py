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
    BOT_TOKEN: str = global_config.TONSTATION_BOT_TOKEN
    CHAT_ID: str = global_config.CHAT_ID

    USE_PROXY: bool = global_config.USE_PROXY

    REF_ID: str = ''

    AUTO_FARM: bool = True
    AUTO_QUESTS: bool = True
    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = global_config.ACC_DELAY

    FAKE_USERAGENT: bool = True
    ERRORS_BEFORE_STOP: int = 5
    USE_PROXY_FROM_FILE: bool = global_config.USE_PROXY
    BIG_SLEEP: list[int] = global_config.BIG_SLEEP

settings = Settings()
