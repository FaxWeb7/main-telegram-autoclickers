from pydantic_settings import BaseSettings, SettingsConfigDict
import os, sys, importlib.util
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
file_path = os.path.join(parent_dir, "global_settings.py")
spec = importlib.util.spec_from_file_location("global_settings", file_path)
modu = importlib.util.module_from_spec(spec)
sys.modules["global_settings"] = modu
spec.loader.exec_module(modu)
from global_settings import global_settings

# api id, hash

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env2", env_ignore_empty=True)

    API_ID: int = global_settings.API_ID
    API_HASH: str = global_settings.API_HASH
    PROXY_TYPE: str = global_settings.PROXY_TYPE

    ACC_DELAY: list[int] = global_settings.ACC_DELAY

    AUTO_UPGRADE_TAP: bool = global_settings.BOTS_DATA['dotcoin']['auto_upgrade_tap']
    MAX_TAP_LEVEL: int = global_settings.BOTS_DATA['dotcoin']['max_tap_level']
    AUTO_UPGRADE_ATTEMPTS: bool = global_settings.BOTS_DATA['dotcoin']['auto_upgrade_attempts']
    MAX_ATTEMPTS_LEVEL: int = global_settings.BOTS_DATA['dotcoin']['max_attempts_level']

    RANDOM_TAPS_COUNT: list[int] = global_settings.BOTS_DATA['dotcoin']['random_taps_count']
    SLEEP_BETWEEN_TAP: list[int] = global_settings.BOTS_DATA['dotcoin']['taps_sleep']
    REF_CODE: str = global_settings.BOTS_DATA['dotcoin']['ref_code']
    USE_PROXY_FROM_FILE: bool = global_settings.USE_PROXY
    ERRORS_BEFORE_STOP: int = global_settings.BOTS_DATA['dotcoin']['errors_before_stop']


settings = Settings()
