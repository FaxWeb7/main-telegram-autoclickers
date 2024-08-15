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

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = global_config.API_ID
    API_HASH: str = global_config.API_HASH

    USE_TG_BOT: bool = global_config.USE_TG_BOT
    BOT_TOKEN: str = global_config.POCKETFI_BOT_TOKEN
    CHAT_ID: str = global_config.CHAT_ID

    ACC_DELAY: list[int] = global_config.ACC_DELAY

    CLAIM_RETRY: list[int] = [2, 5]
    SLEEP_BETWEEN_CLAIM: list[int] = [180, 360]
    BIG_SLEEP: list[int] = global_config.BIG_SLEEP

    USE_PROXY_FROM_FILE: bool = global_config.USE_PROXY


settings = Settings()
