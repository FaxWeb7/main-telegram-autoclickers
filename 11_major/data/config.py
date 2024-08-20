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
BOT_TOKEN = global_config.MAJOR_BOT_TOKEN # API TOKEN get in @BotFather
CHAT_ID = global_config.CHAT_ID # Your telegram id

DELAYS = {
    'ACCOUNT': global_config.ACC_DELAY,  # delay between connections to accounts (the more accounts, the longer the delay)
    'MAJOR_SLEEP': [1800, 3600],
    'REPEAT': [300, 600],
}

# proxy type for tg client
PROXY = {
    "USE_PROXY_FROM_FILE": global_config.USE_PROXY,  # True - if use proxy from file, False - if use proxy from accounts.json
    "TYPE": {
        "TG": global_config.PROXY_TYPE,  # proxy type for tg client. "socks4", "socks5" and "http" are supported
        "REQUESTS": global_config.PROXY_TYPE  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
    }
}

BLACKLIST_TASK = ['ec5aff8e-82d4-4772-8640-36737222805f','bc944f60-87b4-4eb1-8674-61981eec4fa2', '31a44e44-ff64-4ee7-ab77-357d820f4e2c', '3ba85023-b6f1-4184-ab77-e876b1e4cc03', '8bc1e202-841b-413e-a189-dc0a38f30a34', '4848cc53-0f96-4e10-b79a-acaa3b5d14ff', 'ad80ae1b-6e0d-4917-9af4-7709615e100c']

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30