import os, sys, importlib.util
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
file_path = os.path.join(parent_dir, "global_settings.py")
spec = importlib.util.spec_from_file_location("global_settings", file_path)
modu = importlib.util.module_from_spec(spec)
sys.modules["global_settings"] = modu
spec.loader.exec_module(modu)
from global_settings import global_settings

# api id, hash
API_ID = global_settings.API_ID
API_HASH = global_settings.API_HASH

USE_TG_BOT = False # True if you want use tg, else False
BOT_TOKEN = global_settings.BOT_TOKEN # API TOKEN get in @BotFather
CHAT_ID = global_settings.CHAT_ID # Your telegram id

# задержка между подключениями к аккаунтам
ACC_DELAY = global_settings.ACC_DELAY

# тип прокси
PROXY_TYPE = global_settings.PROXY_TYPE # http/socks5

# папка с сессиями (не менять)
WORKDIR = "sessions/"

# использование прокси
USE_PROXY = global_settings.USE_PROXY # True/False

# скок поинтов с игры
POINTS = global_settings.BOTS_DATA['blum']['points'] #[min, max]
MAX_GAMES_COUNT = global_settings.BOTS_DATA['blum']['max_games_count'] #[min, max]

# тратить алмазы
SPEND_DIAMONDS = global_settings.BOTS_DATA['blum']['spend_diamonds'] # True/False

# сон между играми
SLEEP_GAME_TIME = global_settings.BOTS_DATA['blum']['sleep_game_time'] #[min,max]

# мини задержки
MINI_SLEEP = global_settings.MINI_SLEEP #[min,max]
DO_TASKS = global_settings.BOTS_DATA['blum']['do_tasks']

REF_CODE = global_settings.BOTS_DATA['blum']['ref_code']
ERRORS_BEFORE_STOP = global_settings.BOTS_DATA['blum']['errors_before_stop']