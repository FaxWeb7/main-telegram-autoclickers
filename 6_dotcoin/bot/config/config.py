from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 1111111
    API_HASH: str = "akjsfdshfjsdfsdjfsdf"

    USE_TG_BOT: bool = False
    BOT_TOKEN: str = '132432324:asdsdffgssfd'
    CHAT_ID: str = '234242323'

    ACC_DELAY: list[int] = [60, 180]

    AUTO_UPGRADE_TAP: bool = True
    MAX_TAP_LEVEL: int = 7
    AUTO_UPGRADE_ATTEMPTS: bool = True
    MAX_ATTEMPTS_LEVEL: int = 7

    RANDOM_TAPS_COUNT: list[int] = [50, 200]
    SLEEP_BETWEEN_TAP: list[int] = [10, 25]

    USE_PROXY_FROM_FILE: bool = True


settings = Settings()
