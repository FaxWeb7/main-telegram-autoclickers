from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 0
    API_HASH: str = ''

    USE_PROXY: bool = False
    PROXY_TYPE: str = "socks5"

    ACC_DELAY: list[int] = [0, 200]
    BIG_SLEEP: list[int] = [10000, 20000]
    MINI_SLEEP: list[int] = [20, 80]
    USE_TAPS: bool = False

    USE_TG_BOT: bool = False
    CHAT_ID: str = ''
    BOT_TOKEN: str = ''

    BOTS_DATA: dict[str, dict[str, bool | list[int] | str | int]] = {
        "blum" : {
            "is_connected": True,
            "ref_code": "ref_qIFL0xYd8i",
            "spend_diamonds": True,
            "points": [120, 190],
            "sleep_game_time": [60, 180],
            "do_tasks": True,
            "big_sleep_add": [1800, 3600]
        },
        "major" : {
            "is_connected": True,
            "ref_code": "6046075760",
            "play_hold_coin": True,
            "play_roulette": True,
            "play_swipe_coin": True,
            "join_squad": True,
            "task_sleep": [30, 120],
            "game_sleep": [60, 180]
        },
        "yescoin" : {
            "is_connected": True,
            "ref_code": "KWWehI",
            "do_tasks": True,
            "upgrade": True,
            "max_upgrade_lvl": 7,
            "min_energy": 50,
            "use_chests": True,
            "use_energy_recover": True,
            "clicks_sleep": [60, 180],
            "tasks_sleep": [10, 40]
        }
    }

    MESSAGE: str = """
    ███████╗ █████╗ ██╗  ██╗██╗    ██╗███████╗██████╗
    ██╔════╝██╔══██╗╚██╗██╔╝██║    ██║██╔════╝██╔══██╗
    █████╗  ███████║ ╚███╔╝ ██║ █╗ ██║█████╗  ██████╔╝
    ██╔══╝  ██╔══██║ ██╔██╗ ██║███╗██║██╔══╝  ██╔══██╗
    ██║     ██║  ██║██╔╝ ██╗╚███╔███╔╝███████╗██████╔╝
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚═════╝
    GitHub Repository: https://github.com/FaxWeb7/main-telegram-autoclickers
    """
    FIRST_PATHS: list[str] = ['blum', 'major', 'yescoin']
    SECOND_PATHS: list[str] = []

global_settings = Settings()