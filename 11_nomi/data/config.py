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
BOT_TOKEN = global_config.NOMIS_BOT_TOKEN # API TOKEN get in @BotFather
CHAT_ID = global_config.CHAT_ID # Your telegram id

# задержка между подключениями к аккаунтам
ACC_DELAY = global_config.ACC_DELAY

# тип прокси
PROXY_TYPE = global_config.PROXY_TYPE # http/socks5

# рефка например ref_SpmeVi1tSP
REFERRAL_CODE = "ref_4s_BX7NZHN"

# какой часовой пояс на сервере или устройстве +3UTC = 180(минуты)
UTC = 120

# папка с сессиями (не менять)
WORKDIR = "sessions/"

# использование прокси
USE_PROXY = global_config.USE_PROXY # True/False

# задержка между клеймом и стартом фарминга
START_SLEEP = [60,180]

# задержка между тасками
TASKS_SLEEP = [60,180]

# задержка между кругами
END_SLEEP = global_config.BIG_SLEEP

# мини задержки
MINI_SLEEP = [10,20] #[min,max]
