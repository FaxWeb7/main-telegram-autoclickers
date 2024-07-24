from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 1111111
    API_HASH: str = "akjsfdshfjsdfsdjfsdf"

    USE_TG_BOT: bool = False
    BOT_TOKEN: str = '132432324:asdsdffgssfd'
    CHAT_ID: str = '234242323'

    ACC_DELAY: list[int] = [60, 180]

    MIN_AVAILABLE_ENERGY: int = 140
    SLEEP_BY_MIN_ENERGY: list[int] = [1800, 2400]

    ADD_TAPS_ON_TURBO: int = 2500

    AUTO_UPGRADE_TAP: bool = True
    MAX_TAP_LEVEL: int = 10
    AUTO_UPGRADE_ENERGY: bool = True
    MAX_ENERGY_LEVEL: int = 10
    AUTO_UPGRADE_CHARGE: bool = True
    MAX_CHARGE_LEVEL: int = 3

    APPLY_DAILY_ENERGY: bool = True
    APPLY_DAILY_TURBO: bool = True

    RANDOM_TAPS_COUNT: list[int] = [50, 250]
    SLEEP_BETWEEN_TAP: list[int] = [10, 35]

    USE_PROXY_FROM_FILE: bool = True


settings = Settings()
