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
BOT_TOKEN = global_config.YESCOIN_BOT_TOKEN
CHAT_ID = global_config.CHAT_ID

# auto complete tasks True/False
COMPLETE_TASKS = True

# autoupgrade fill rate; [True/False (use/no use), max upgrade lvl]
AUTOUPGRADE_FILL_RATE = [True, 5]

# minimum allowable energy
MINIMUM_ENERGY = 50

# daily boosters; True/False
BOOSTERS = {
    'USE_CHESTS': True,    # Chests
    'USE_RECOVERY': True   # Full energy recover
}

DELAYS = {
    'ACCOUNT': global_config.ACC_DELAY,  # delay between connections to accounts (the more accounts, the longer the delay)
    'CLICKS': [2, 10],   # delay between clicks
    'TASKS': [10, 40]      # delay between completed tasks
}

PROXY = {
    "USE_PROXY_FROM_FILE": global_config.USE_PROXY,
    "PROXY_PATH": "./proxy.txt",
    "TYPE": {
        "TG": global_config.PROXY_TYPE,
        "REQUESTS": global_config.PROXY_TYPE
    }
}

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

SOFT_INFO = f"""{"Yescoin".center(40)}
Soft for https://t.me/theYescoin_bot; claim points;
claim daily boosters; complete tasks; upgrade 'FillRate';
register accounts in web app

The soft also collects statistics on accounts and uses proxies from {f"the {PROXY['PROXY_PATH']} file" if PROXY['USE_PROXY_FROM_FILE'] else "the accounts.json file"}
To buy this soft with the option to set your referral link write me: https://t.me/Axcent_ape
"""
