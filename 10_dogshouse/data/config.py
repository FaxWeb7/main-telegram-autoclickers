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

API_ID = global_config.API_ID
API_HASH = global_config.API_HASH

USE_TG_BOT = global_config.USE_TG_BOT
BOT_TOKEN = global_config.DOGSHOUSE_BOT_TOKEN
CHAT_ID = global_config.CHAT_ID

REF_LINK = 'https://t.me/dogshouse_bot/join?startapp=ze_ke9DXRN-MaOuNvC3ZSw'

DELAYS = {
    'ACCOUNT': global_config.ACC_DELAY,
    'TASK': [20, 120],
    'CLAIMING': [28800, 50400]
}

WHITELIST_TASK = ['subscribe-dogs', 'subscribe-notcoin', 'follow-dogs-x', 'send-bone-okx', 'good-dog', 'subscribe-blum', 'send-bone-binance', 'send-bone-bybit', 'subscribe-durov']

PROXY = {
    "USE_PROXY_FROM_FILE": global_config.USE_PROXY,
    "PROXY_PATH": "./proxy.txt",
    "TYPE": {
        "TG": global_config.PROXY_TYPE,
        "REQUESTS": global_config.PROXY_TYPE
    }
}

WORKDIR = "sessions/"

TIMEOUT = 30