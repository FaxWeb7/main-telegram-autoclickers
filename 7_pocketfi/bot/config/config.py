from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 1111111
    API_HASH: str = "akjsfdshfjsdfsdjfsdf"

    USE_TG_BOT: bool = False
    BOT_TOKEN: str = '132432324:asdsdffgssfd'
    CHAT_ID: str = '234242323'

    ACC_DELAY: list[int] = [60, 180]

    CLAIM_RETRY: list[int] = [2, 5]
    SLEEP_BETWEEN_CLAIM: list[int] = [180, 360]

    USE_PROXY_FROM_FILE: bool = True


settings = Settings()
