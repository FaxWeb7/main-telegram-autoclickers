
# Automatic autoclicker for popular telegram mini-apps
![](https://i.ibb.co/5GFZXyB/res.png)

## Bot Status

| Status | Bots                                            |
|:------:|-------------------------------------------------|
|   ✅   | **Blum, 1Win Token, CryptoRank, YesCoin, TapSwap, DotCoin**       |
|   ✅   | **PocketFi, MuskEmpire, HamsterKombat**       |
|   ⌛   | **DOGS, OKX Racer, TapTether**                        |


## Requirements
- Python 3.11 (you can install it [here](https://www.python.org/downloads/release/python-3110/))
- Telegram API_ID and API_HASH (you can get them [here](https://my.telegram.org/auth?to=apps))

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get your API_ID and API_HASH:
   - Go to [my.telegram.org](https://my.telegram.org/auth?to=apps)
   - Sign in with your Telegram account
   - Create a new application to get your API_ID and API_HASH

3. Configure the application in `global_data/global_config.py`:
   - Add your `API_ID` and `API_HASH`:
     ```python
     API_ID = your_api_id
     API_HASH = 'your_api_hash'
     ```

   - Set random delay between connections to accounts in seconds
     ```python
     ACC_DELAY = [minDelay, maxDelay]
     ```

   - If you want to use a proxy, set `USE_PROXY` to `True` and set your `PROXY_TYPE`, otherwise set it to `False`:
     ```python
     USE_PROXY = True  # or False
     PROXY_TYPE = "socks5" # or http
     ```

   - if you want to receive logs from each of the bots, set `USE_TG_BOT = True`, specify your `CHAT_ID`, and specify a token from `@BotFather` for each of the bots:
     ```python
     USE_TG_BOT = False
     CHAT_ID = '237856'
     # api tokens for tg bots, if USE_TH_BOT=True (get in @BotFather)
     BLUM_BOT_TOKEN = '87265743:JKFDHad'
     ONEWIN_BOT_TOKEN = '87265743:JKFDHad'
     CRYPTORANK_BOT_TOKEN = '87265743:JKFDHad'
     YESCOIN_BOT_TOKEN = '87265743:JKFDHad'
     TAPSWAP_BOT_TOKEN = '87265743:JKFDHad'
     DOTCOIN_BOT_TOKEN = '87265743:JKFDHad'
     POCKETFI_BOT_TOKEN = '87265743:JKFDHad'
     ```

4. Creating proxies:
   - If `USE_PROXY` is `True`, open `global_data/proxies.txt` and fill it out using the example provided. Ensure there are no extra lines in the file.
   Proxy format : ip:port:login:password session_name, session name is which use this proxy (WITHOUT .session, only session name)
      ```txt
      192.168.1.1:1234:username:password 1_name
      192.168.1.2:2934:username:password 2_anothername
      ```
   - Now you need to move all these proxies to all folders with bots, run `python3.11 main.py`
   - Choose `2` -> Actions with proxies
   - Choose `2` -> Add all proxies from ./global_data/proxies.txt/
     
5. Creating sessions:
   - Run `python3.11 main.py`
   - Choose `1` -> Actions with sessions
   - Choose `5` -> Create new session. it is important to name sessions exactly like this (with numeration):
      ```txt
      1_name.session
      2_anothername.session
      ```
   - Now you need to move all these sessions to all folders with bots, run `python3.11 main.py`
   - Choose `1` -> Actions with sessions
   - Choose `2` -> Add all sessions from ./global_data/sessions/

## Usage

Launch all or one bot
1. Run `python3.11 main.py`
2. Choose `3` -> Actions with bots
3. Choose `0` if you need to launch all bots, or the number of one bot you need to launch


## Important Notes

- DONT USE MAIN ACCOUNT BECAUSE THERE IS ALWAYS A CHANCE TO GET BANNED IN TELEGRAM
- **Python Version:** The software runs on Python 3.11. Using a different version may cause errors.
- The software will work with all accounts using the single `API_ID` and `API_HASH`. No need to change them for each account.

