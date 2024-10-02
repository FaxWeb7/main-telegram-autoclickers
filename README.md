
# Automatic autoclicker for popular telegram mini-apps
[<img src="https://img.shields.io/badge/Telegram-%40My_Channel-orange">](https://t.me/faxweb_dev)
[<img src="https://img.shields.io/badge/Telegram-%40Me-orange">](https://t.me/faxweb_dev_admin)
[<img src="https://img.shields.io/badge/python-3.11-blue">](https://www.python.org/downloads/)

![](https://i.ibb.co/HBW9tSY/2024-09-22-19-49-28.png)

## Bot Status
#### Subscribe to the telegram channel to follow updates and/or purchase paid software version: [@faxweb_dev](https://t.me/faxweb_dev)
Free version of this software (current repository) has 5 bots: Blum, Major, Yescoin, Dotcoin and catsgang, but the paid version of the software has 18 bots. If you are interested in purchasing a paid bot, read the pinned message in my telegram channel: [@faxweb_dev](https://t.me/faxweb_dev). Paid version software bot status:
| Status | Bots                                            |
|:------:|-------------------------------------------------|
|   ✅   | **Blum, Cats, CexIo, Clayton**       |
|   ✅   | **DotCoin, LeapApp, Major, MemeFi**       |
|   ✅   | **MMProBump, Nomis, OKX Racer, PocketFi**                       |
|   ✅   | **TonStation, VanaDataHero, YesCoin**                      |
|   ✅   | **MoonBix, Not Pixel, FriendsFabric**                              |
|   ⌛   | **Tomarket, CoinSweeper, DuckChain**                              |

## Requirements
- Python 3.11 (you can install it [here](https://www.python.org/downloads/release/python-3110/))
- Telegram API_ID and API_HASH (you can get them [here](https://my.telegram.org/auth?to=apps))

## Run software
1. Installation:
   ```shell
   ~ >>> git clone https://github.com/FaxWeb7/main-telegram-autoclickers.git 
   ~ >>> cd main-telegram-autoclickers
   
   # Linux
   ~/main-telegram-autoclickers >>> pip3 install -r requirements.txt
   ~/main-telegram-autoclickers >>> cp .env-example .env
   
   # Windows
   ~ >>> chcp 1251
   ~/main-telegram-autoclickers >>> pip install -r requirements.txt
   ~/main-telegram-autoclickers >>> copy .env-example .env
   ```
2. Configure the application in `.env`:
   - open .env file (`nano .env` for linux, and `notepad .env` for windows)
   - Add your `API_ID` and `API_HASH`:
     ```python
     API_ID = your_api_id
     API_HASH = 'your_api_hash'
     ```
     
   - If you want to use a proxy, set `USE_PROXY` to `True` and set your `PROXY_TYPE`, otherwise set `USE_PROXY = False`:
     ```python
     USE_PROXY = True  # or False
     PROXY_TYPE = "socks5" # or http
     ```
     
   - Set `SOFT_BOTS_DELAY` (delay between transition from one bot to another), `SOFT_CIRCLES_NUM` (1 soft circle = execute all activities in all bots) and `SOFT_CIRCLES_DELAY` (delay between soft circles)
     ```python
     SOFT_BOTS_DELAY = [600, 900]
     SOFT_CIRCLES_NUM = 10
     SOFT_CIRCLES_DELAY = [21000, 25000]
     ```

   - Set ACC_DELAY and USE_TAPS variables
     ```python
     ACC_DELAY = [minDelay, maxDelay] # random delay between connections to accounts in seconds
     MINI_SLEEP = [minDelay, maxDelay] # random delay between requests in seconds
     USE_TAPS = True or False # USE_TAPS = False if you don't want your bots to use taps
     ```

   - if you want to receive logs from soft to your telegram, set `USE_TG_BOT = True`, specify your `CHAT_ID`, and specify a `BOT_TOKEN` from `@BotFather`, otherwise set `USE_TG_BOT = False`:
     ```python
     USE_TG_BOT = True
     CHAT_ID = '123456789'
     BOT_TOKEN = '1234567:asdfghjqwerty'
     ```
   - For each bot in BOTS_DATA, you can choose for you, use this bot or not (is_connected), and specify individual settings for this particular bot. Example BOTS_DATA:
     ```python
     BOTS_DATA= '{
        "blum" : {
            "is_connected": true,
            "spend_diamonds": true,
            "points": [120, 190],
            "sleep_game_time": [60, 180],
            "do_tasks": true,
            "big_sleep_add": [1800, 3600]
        }
     }'
     ```

3. Creating proxies
   - If `USE_PROXY = False` , then skip this step
   - Else, create empty file named `proxies.txt` in root and fill it out using the example provided. Ensure there are no extra lines in the file. Proxy format : ip:port:login:password session_name, session name is which use this proxy (WITHOUT .session, only session name)
   ```txt
   192.168.1.1:1234:username:password name
   192.168.1.2:2934:username:password anothername
   ```
     
4. Creating sessions:
   - Run `python3 main.py`
   - Choose `1` -> Create new session
   - Enter the session name, phone number and etc.

## Usage
1. Launching bots that have `is_connected = True` in the `BOTS_DATA` variable of the `.env` file:
   - Run `python3 main.py`
   - Choose `2` -> Run bots
   
2. Installing repository updates (if you see that I have committed a new change to a bot)
   - Run `git pull` in root of repository
      - If I added a new bot, you need to copy the variable with the settings for the new bot in BOTS_DATA in the .env-example file, and paste these settings into your .env file. (Adjust the settings for yourself if necessary)
      - if I didn’t add a new bot, but corrected the errors of the current bots, then just git pull is enough

  
## Important Notes
- DONT USE MAIN ACCOUNT BECAUSE THERE IS ALWAYS A CHANCE TO GET BANNED IN TELEGRAM
- **Python Version:** The software runs on Python 3.11. Using a different version may cause errors.
- The software will work with all accounts using the single `API_ID` and `API_HASH`. No need to change them for each account.

