from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int = 0
    API_HASH: str = ''

    USE_PROXY: bool = False
    PROXY_TYPE: str = "socks5"

    SOFT_ITERATIONS_NUM: int = 1

    ACC_DELAY: list[int] = [0, 200]
    MINI_SLEEP: list[int] = [20, 80]
    USE_TAPS: bool = False

    USE_TG_BOT: bool = False
    CHAT_ID: str = ''
    BOT_TOKEN: str = ''

    BOTS_DATA: dict[str, dict[str, bool | list[int] | str | int | float]] = {
        "blum" : {
            "is_connected": True,
            "ref_code": "ref_qIFL0xYd8i",
            "errors_before_stop": 2,
            "spend_diamonds": True,
            "points": [120, 190],
            "sleep_game_time": [60, 180],
            "do_tasks": True
        },
        "major" : {
            "is_connected": True,
            "ref_code": "6046075760",
            "errors_before_stop": 2,
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
            "errors_before_stop": 2,
            "do_tasks": True,
            "upgrade": True,
            "max_upgrade_lvl": 7,
            "min_energy": 50,
            "use_chests": True,
            "use_energy_recover": True,
            "clicks_sleep": [60, 180],
            "tasks_sleep": [10, 40]
        },
        "dotcoin" : {
            "is_connected": True,
            "ref_code": "r_6046075760",
            "errors_before_stop": 2,
            "auto_upgrade_tap": True,
            "max_tap_level": 5,
            "auto_upgrade_attempts": True,
            "max_attempts_level": 5,
            "random_taps_count": [50, 200],
            "taps_sleep": [10, 25]
        },
        "cats" : {
            "is_connected": True,
            "ref_code": "18awB6nNqqe8928y1u4vp",
            "errors_before_stop": 2,
            "task_sleep": [40, 120]
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
    FIRST_PATHS: list[str] = ['blum', 'major', 'yescoin', 'cats']
    SECOND_PATHS: list[str] = ['dotcoin']

global_settings = Settings()