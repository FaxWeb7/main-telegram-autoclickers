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

# api id, hash
API_ID = global_config.API_ID
API_HASH = global_config.API_HASH

USE_TG_BOT = global_config.USE_TG_BOT # True if you want use tg, else False
BOT_TOKEN = global_config.BLUM_BOT_TOKEN # API TOKEN get in @BotFather
CHAT_ID = global_config.CHAT_ID # Your telegram id

# задержка между подключениями к аккаунтам
ACC_DELAY = global_config.ACC_DELAY

# тип прокси
PROXY_TYPE = global_config.PROXY_TYPE # http/socks5

# папка с сессиями (не менять)
WORKDIR = "sessions/"

# использование прокси
USE_PROXY = global_config.USE_PROXY # True/False

# скок поинтов с игры
POINTS = [120, 190] #[min, max]

# тратить алмазы
SPEND_DIAMONDS = True # True/False

# сон между играми
SLEEP_GAME_TIME = [60,180] #[min,max]

# мини задержки
MINI_SLEEP = [20,80] #[min,max]

BIG_SLEEP_ADD = [1800, 3600]
