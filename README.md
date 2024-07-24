
# Main softwares for multiaccounting in telegram bots

## Bot Status

<div align="center">

| **Bot**  | **Status**  |
|:--------:|:-----------:|
| **Blum** | ✔️ Active   |
| **1Win Token** | ✔️ Active   |
| **CryptoRank** | ✔️ Active   |
| **YesCoin** | ✔️ Active   |
| **TapSwap** | ✔️ Active   |
| **Dotcoin** | ✔️ Active   |
| **PocketFi** | ✔️ Active   |
| **Musk Empire** | ❌ Inactive |
| **TapTether** | ❌ Inactive |
| **OKX Racer** | ❌ Inactive |

</div>

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

3. Configure the application:
   - Open `config.py` and add your `API_ID` and `API_HASH` (from 1_blum to 4_yescoin config is here: `n_name/data/config.py`, else `n_name/bot/config/config.py`):
     ```python
     API_ID = your_api_id
     API_HASH = 'your_api_hash'
     ```

   - If you want to use a proxy, set `USE_PROXY` to `True`, otherwise set it to `False`:
     ```python
     USE_PROXY = True  # or False
     ```

4. Creating sessions and proxies:
   - Put your telegram sessions in `data/sessions/`, it is important to name the sessions exactly like this (with numeration):
  ```txt
   1_name.session
   2_anothername.session
   ```
   - If `USE_PROXY` is `True`, open `data/proxies.txt` and fill it out using the example provided. Ensure there are no extra lines in the file.
   Proxy format : ip:port:login:password session_name, session name is which use this proxy (WITHOUT .session, only session name)
   ```txt
   192.168.1.1:1234:username:password 1_name
   192.168.1.2:2934:username:password 2_anothername
   ```
   - Now you need to move either all or some sessions and proxies from data/sessions/ and data/proxies.txt to all bots folders. This can be done by running ```python3 data_setup.py```


## Usage

Run the bot in each of the bots folders
1. cd n_bot
   ```bash
   cd n_bot
   ```
2. run bot
   ```bash
   python3 main.py
   ```


## Important Notes

- DONT USE MAIN ACCOUNT BECAUSE THERE IS ALWAYS A CHANCE TO GET BANNED IN TELEGRAM
- **Python Version:** The software runs on Python 3.11. Using a different version may cause errors.
- The software will work with all accounts using the single `API_ID` and `API_HASH`. No need to change them for each account.
