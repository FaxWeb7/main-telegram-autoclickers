
# Automatic autoclicker for popular telegram mini-apps
![](https://i.ibb.co/7QBLHsT/result.png)

## Bot Status

| Status | Bots                                            |
|:------:|-------------------------------------------------|
|   ✅   | **Blum, CryptoRank, YesCoin, DotCoin**       |
|   ✅   | **PocketFi, MuskEmpire, HamsterKombat**       |
|   ✅   | **OKX Racer, Lost Dogs, Major, Nomis**                       |
|   ✅   | **Cats, RockyRabbit, MemeFi, CexIo**                      |
|   ⌛   |                               |

## Requirements
- Python 3.11 (you can install it [here](https://www.python.org/downloads/release/python-3110/))
- Telegram API_ID and API_HASH (you can get them [here](https://my.telegram.org/auth?to=apps))

1. Install the required dependencies:
   ```bash
   python3.11 -m pip install -r requirements.txt
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
     
   - Set random delay between ```while True``` iterations in bots, in seconds
     ```python
     BIG_SLEEP = [minDelay, maxDelay]
     ```
     
   - Set `USE_TAPS = False` if you don't want your bots to use taps 
     ```python
     BIG_SLEEP = [minDelay, maxDelay]
     ```

   - If you want to use a proxy, set `USE_PROXY` to `True` and set your `PROXY_TYPE`, otherwise set it to `False`:
     ```python
     USE_PROXY = True  # or False
     PROXY_TYPE = "socks5" # or http
     ```
     
   - If you want to turn off some bots, you can do it by select False in the corresponding line in CONNECTED_BOTS, for example:
     ```python
      CONECTED_BOTS = {
          "./1_blum" : True,
          "./2_cryptorank" : False
          "./3_yescoin" : True,
          "./4_dotcoin" : False,
          "./5_pocketfi" : True,
          "./6_muskempire" : False,
          "./7_hamsterkombat" : True,
          "./8_okxracer" : True,
          "./9_lostdogs" : False,
          "./10_major" : False,
          "./11_nomis" : False,
          "./12_cats" : True,
      }

     ```

   - if you want to receive logs from each of the bots, set `USE_TG_BOT = True`, specify your `CHAT_ID`, and specify a token from `@BotFather` for each of the bots:
     ```python
      BLUM_BOT_TOKEN = '87265743:JKFDHad'
      CRYPTORANK_BOT_TOKEN = '87265743:JKFDHad'
      YESCOIN_BOT_TOKEN = '87265743:JKFDHad'
      DOTCOIN_BOT_TOKEN = '87265743:JKFDHad'
      POCKETFI_BOT_TOKEN = '87265743:JKFDHad'
      MUSKEMPIRE_BOT_TOKEN = '87265743:JKFDHad'
      HAMSTERKOMBAT_BOT_TOKEN = '87265743:JKFDHad'
      OKXRACER_BOT_TOKEN = '87265743:JKFDHad'
      LOSTDOGS_BOT_TOKEN = '87265743:JKFDHad'
      MAJOR_BOT_TOKEN = '87265743:JKFDHad'
      NOMIS_BOT_TOKEN = '87265743:JKFDHad'
      CATS_BOT_TOKEN = '87265743:JKFDHad'
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

Launch bots selected in ```global_data/global_config.py```
1. Run `python3.11 main.py -a 3`

## Important Notes

- DONT USE MAIN ACCOUNT BECAUSE THERE IS ALWAYS A CHANCE TO GET BANNED IN TELEGRAM
- **Python Version:** The software runs on Python 3.11. Using a different version may cause errors.
- The software will work with all accounts using the single `API_ID` and `API_HASH`. No need to change them for each account.

