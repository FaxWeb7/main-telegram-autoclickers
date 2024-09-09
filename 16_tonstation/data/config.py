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
BOT_TOKEN = global_config.TONSTATION_BOT_TOKEN # API TOKEN get in @BotFather
CHAT_ID = global_config.CHAT_ID # Your telegram id

DELAYS = {
    "RELOGIN": [5, 50],  # delay after a login attempt
    'ACCOUNT': global_config.ACC_DELAY,  # delay between connections to accounts (the more accounts, the longer the delay)
    'CLAIM': [20, 60],   # delay between pour beers
    'TASK': [20, 60],  # delay after complete task
    'REPEAT': global_config.BIG_SLEEP  # delay after complete while
}

PROXY = {
    "USE_PROXY_FROM_FILE": global_config.USE_PROXY,  # True - if use proxy from file, False - if use proxy from accounts.json
    "PROXY_PATH": "proxy.txt",  # path to file proxy
    "TYPE": {
        "TG": global_config.PROXY_TYPE,  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": global_config.PROXY_TYPE  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
    }
}

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

SOFT_INFO = f"""{"TON Station".center(40)}
Soft for https://t.me/tonstationgames_bot
{"Functional:".center(40)}
Register accounts in web app; start and claim farming; 

The soft also collects statistics on accounts and uses proxies from {f"the {PROXY['PROXY_PATH']} file" if PROXY['USE_PROXY_FROM_FILE'] else "the accounts.json file"}
To buy this soft with the option to set your referral link write me: https://t.me/Axcent_ape
"""