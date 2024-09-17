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

# auto complete tasks True/False
COMPLETE_TASKS = global_settings.BOTS_DATA['yescoin']['do_tasks']

REF_CODE = global_settings.BOTS_DATA['yescoin']['ref_code']

# autoupgrade fill rate; [True/False (use/no use), max upgrade lvl]
AUTOUPGRADE_FILL_RATE = [global_settings.BOTS_DATA['yescoin']['upgrade'], global_settings.BOTS_DATA['yescoin']['max_upgrade_lvl']]

# minimum allowable energy
MINIMUM_ENERGY = global_settings.BOTS_DATA['yescoin']['min_energy']

# daily boosters; True/False
BOOSTERS = {
    'USE_CHESTS': global_settings.BOTS_DATA['yescoin']['use_chests'],    # Chests
    'USE_RECOVERY': global_settings.BOTS_DATA['yescoin']['use_energy_recover']   # Full energy recover
}

DELAYS = {
    'ACCOUNT': global_settings.ACC_DELAY,  # delay between connections to accounts (the more accounts, the longer the delay)
    'CLICKS': global_settings.BOTS_DATA['yescoin']['clicks_sleep'],   # delay between clicks
    'TASKS': global_settings.BOTS_DATA['yescoin']['tasks_sleep'],      # delay between completed tasks
    'BIG_SLEEP' : global_settings.BIG_SLEEP
}

PROXY = {
    "USE_PROXY_FROM_FILE": global_settings.USE_PROXY,
    "PROXY_PATH": "./proxy.txt",
    "TYPE": {
        "TG": global_settings.PROXY_TYPE,
        "REQUESTS": global_settings.PROXY_TYPE
    }
}

# session folder (do not change)
WORKDIR = "sessions/"

SOFT_INFO = f"""{"Yescoin".center(40)}
Soft for https://t.me/theYescoin_bot; claim points;
claim daily boosters; complete tasks; upgrade 'FillRate';
register accounts in web app

The soft also collects statistics on accounts and uses proxies from {f"the {PROXY['PROXY_PATH']} file" if PROXY['USE_PROXY_FROM_FILE'] else "the accounts.json file"}
To buy this soft with the option to set your referral link write me: https://t.me/Axcent_ape
"""
