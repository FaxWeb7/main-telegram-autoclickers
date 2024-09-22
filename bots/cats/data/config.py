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

REF_CODE = global_settings.BOTS_DATA['cats']['ref_code']

# задержка в секундах между выполнеными тасками
TASK_SLEEP = global_settings.BOTS_DATA['cats']['task_sleep']

ERRORS_BEFORE_STOP = global_settings.BOTS_DATA['cats']['errors_before_stop']

# мини задержки
MINI_SLEEP = global_settings.MINI_SLEEP

# айди тасков которые будут пропускаться
BLACKLIST = [2, 3, 4, 5, 99, 104, 105]

hello ='''              _                               __  _        
 _ __    ___ | |_  _   _   __ _  ___   ___   / _|| |_  ___ 
| '_ \  / _ \| __|| | | | / _` |/ __| / _ \ | |_ | __|/ __|
| |_) ||  __/| |_ | |_| || (_| |\__ \| (_) ||  _|| |_ \__ \\
| .__/  \___| \__| \__, | \__,_||___/ \___/ |_|   \__||___/
|_|                |___/        

'''
