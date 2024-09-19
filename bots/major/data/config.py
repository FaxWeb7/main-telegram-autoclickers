import os, sys, importlib.util
parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../.."))
file_path = os.path.join(parent_dir, "global_settings.py")
spec = importlib.util.spec_from_file_location("global_settings", file_path)
modu = importlib.util.module_from_spec(spec)
sys.modules["global_settings"] = modu
spec.loader.exec_module(modu)
from global_settings import global_settings

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

# реф код, идет после startapp=
REF_CODE = global_settings.BOTS_DATA['major']['ref_code']

# задержка между тасками
TASK_SLEEP = global_settings.BOTS_DATA['major']['task_sleep']

# задержка между минииграми
GAME_SLEEP = global_settings.BOTS_DATA['major']['game_sleep']

# айди тасков которые проверяются
BLACKLIST_TASKS = {33,21,27,20,36,80,77}

# играть в данную мини игру True/False
HOLD_COIN = global_settings.BOTS_DATA['major']['play_hold_coin']
ROULETTE = global_settings.BOTS_DATA['major']['play_roulette']
SWIPE_COIN = global_settings.BOTS_DATA['major']['play_swipe_coin']

# мини задержки
MINI_SLEEP = global_settings.MINI_SLEEP

#задержка между циклами

# вступать в сквад
JOIN_SQUAD = global_settings.BOTS_DATA['major']['join_squad']
ERRORS_BEFORE_STOP = global_settings.BOTS_DATA['major']['errors_before_stop']