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

    USE_TG_BOT: bool = global_config.USE_TG_BOT # True if you want use tg, else False
    BOT_TOKEN: str = global_config.LOSTDOGS_BOT_TOKEN # API TOKEN get in @BotFather
    CHAT_ID: str = global_config.CHAT_ID # Your telegram id

    ACC_DELAY: list[int] = global_config.ACC_DELAY
    SLEEP_TIME: list[int] = [14400, 21600]
    AUTO_TASK: bool = True
    RANDOM_CARD: bool = True
    CARD_NUMBER: int = 1
    USE_REF: bool = True

    USE_PROXY_FROM_FILE: bool = global_config.USE_PROXY


settings = Settings()
