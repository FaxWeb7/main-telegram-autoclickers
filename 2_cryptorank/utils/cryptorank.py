from urllib.parse import unquote,urlparse,parse_qs
from utils.core import logger
from fake_useragent import UserAgent
from pyrogram import Client
from data import config
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName


import aiohttp
import asyncio
import random
import json
import base64
import time

class CryptoRank:
    def __init__(self, thread: int, account: str, proxy : str):
        self.thread = thread
        self.name = account
        if proxy:
            proxy_client = {
                "scheme": config.PROXY_TYPE,
                "hostname": proxy.split(':')[0],
                "port": int(proxy.split(':')[1]),
                "username": proxy.split(':')[2],
                "password": proxy.split(':')[3],
            }
            self.client = Client(name=account, api_id=config.API_ID, api_hash=config.API_HASH, workdir=config.WORKDIR, proxy=proxy_client)
        else:
            self.client = Client(name=account, api_id=config.API_ID, api_hash=config.API_HASH, workdir=config.WORKDIR)
                
        if proxy:
            self.proxy = f"{config.PROXY_TYPE}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
        else:
            self.proxy = None
    
        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=aiohttp.TCPConnector(verify_ssl=False))

    async def main(self):
        await asyncio.sleep(random.randint(*config.ACC_DELAY))
        try:
            login = await self.login()
            if login == False:
                await self.session.close()
                return 0
            logger.info(f"main | Thread {self.thread} | {self.name} | Start! | PROXY : {self.proxy}")
        except Exception as err:
            logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
            await self.session.close()
            return 0
        while True:
            try:
                account = await self.account()

                if account['farming'] == None:
                    await self.start_farming()
                else:
                    func = account['farming']['state']
                    if func == "START":
                        start_ts = account['farming']['timestamp']
                        if start_ts + 6*60*60*1000 < self.get_timestamp():
                            await self.end_farming()
                    elif func == "END":
                        await self.start_farming()
                reward = await self.buddies_reward()
                if reward != 0 :
                    await self.claim_reward()
                if random.randint(0,4) == 1:
                    await self.do_tasks()
                await self.claim_task(id="e7dae272-7d17-4543-9a30-92f071439210")
                sleep = random.randint(config.BIG_SLEEP[0], config.BIG_SLEEP[1])
                logger.info(f"main | Thread {self.thread} | {self.name} | Задержка {sleep} сек")
                await asyncio.sleep(sleep)
            except Exception as err:
                logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
                await asyncio.sleep(5*random.randint(*config.MINI_SLEEP))
    
    async def claim_task(self,id):
        try:
            resp = await self.session.post(f'https://api.cryptorank.io/v0/tma/account/claim/task/{id}',proxy = self.proxy)
            await asyncio.sleep(random.uniform(4,8))
            return (await resp.json())
        except Exception as err:
            logger.error(f"claim_tasks | Thread {self.thread} | {self.name} | {err}")
            
    def get_timestamp(self):
        return int(time.time()*1000)
    
    async def do_tasks(self):
        try:
            resp = await self.session.get('https://api.cryptorank.io/v0/tma/account/tasks',proxy=self.proxy)
            tasks = await resp.json()
            for task in tasks:
                if task['isRepeatable'] == False and task['lastClaim'] != None:
                    continue
                if task['id'] == 'e7dae272-7d17-4543-9a30-92f071439210':
                    continue
                ans = await self.claim_task(id=task['id'])
                if 'balance' in ans:
                    logger.info(f"do_tasks | Thread {self.thread} | {self.name} | Claim {task['name']} Balance : {ans['balance']}")
                
        except Exception as err:
            logger.error(f"do_tasks | Thread {self.thread} | {self.name} | {err}")
            

    async def start_farming(self):
        try:
            resp = await self.session.post("https://api.cryptorank.io/v0/tma/account/start-farming",proxy = self.proxy)
            logger.info(f"start_farming | Thread {self.thread} | {self.name} | Start farming")
        except Exception as err:
            logger.error(f"start_farming | Thread {self.thread} | {self.name} | {err}")

        
    async def end_farming(self):
        try:
            resp = await self.session.post("https://api.cryptorank.io/v0/tma/account/end-farming",proxy = self.proxy)
            answer = (await resp.json())
            balance = answer['balance']
            logger.success(f"end_farming | Thread {self.thread} | {self.name} | Claim farming. Balance : {balance}")
        except Exception as err:
            logger.error(f"end_farming | Thread {self.thread} | {self.name} | {err}")
        
    async def buddies_reward(self):
        try:
            resp = await self.session.get('https://api.cryptorank.io/v0/tma/account/buddies',proxy=self.proxy)
            resp = await resp.json()
            reward = resp['reward']
            return reward
        except Exception as err:
            logger.error(f"buddies_reward | Thread {self.thread} | {self.name} | {err}")
    
    async def claim_reward(self):
        try:
            resp = await self.session.get('https://api.cryptorank.io/v0/tma/account/buddies',proxy=self.proxy)
            resp = await resp.json()
            if resp['cooldown'] == 0:
                resp = await self.session.post('https://api.cryptorank.io/v0/tma/account/claim/buddies',proxy=self.proxy)
                resp = await resp.json()
                balance = resp['balance']
                logger.success(f"claim_reward | Thread {self.thread} | {self.name} | Claim referral reward. Balance : {balance}")
        except Exception as err:
            logger.error(f"claim_reward | Thread {self.thread} | {self.name} | {err}")
            
    async def balance(self):
        try:
            account = await self.account()
            return account['balance']
        except Exception as err:
            logger.error(f"balance | Thread {self.thread} | {self.name} | {err}")

    async def login(self):
        try:
            params = {
                'tgWebAppStartParam': 'ref_6046075760_'
            }
            await self.session.get('https://tma.cryptorank.io/',params = params,proxy=self.proxy)
            tg_web_data = await self.get_tg_web_data()
            if tg_web_data == False:
                return False
            authorization = self.get_jwt(data=tg_web_data)
            self.session.headers['authorization'] = authorization
            await asyncio.sleep(random.randint(1,5))
            json_data = {
                'inviterId' : '6046075760',
            }
            await self.session.post('https://api.cryptorank.io/v0/tma/account', json=json_data,proxy=self.proxy)
        except Exception as err:
            logger.error(f"login | Thread {self.thread} | {self.name} | {err}")
            if err == "Server disconnected":
                return True
            return False

    async def get_tg_web_data(self):
        await self.client.connect()
        try:
            bot = await self.client.resolve_peer('cryptorank_app_bot')
            app = InputBotAppShortName(bot_id=bot, short_name="points")

            web_view = await self.client.invoke(RequestAppWebView(
                    peer=bot,
                    app=app,
                    platform='android',
                    write_allowed=True,
                    start_param='ref_6046075760_'
                ))

            auth_url = web_view.url
        except Exception as err:
            logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
            if 'USER_DEACTIVATED_BAN' in str(err):
                logger.error(f"login | Thread {self.thread} | {self.name} | USER BANNED")
                await self.client.disconnect()
                return False
        await self.client.disconnect()
        return self.url_to_dict(auth_url)

    async def account(self):
        try:
            response = await self.session.get('https://api.cryptorank.io/v0/tma/account',proxy=self.proxy)
            return (await response.json())
        except Exception as err:
            logger.error(f"account | Thread {self.thread} | {self.name} | {await response.text()}")
            
    
    
    def url_to_dict(self,url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.fragment)
        tg_web_app_data = query_params.get('tgWebAppData', [None])[0]
        if tg_web_app_data:
            decoded_data = unquote(tg_web_app_data)
            data_dict = parse_qs(decoded_data)
            for key, value in data_dict.items():
                try:
                    data_dict[key] = json.loads(value[0])
                except json.JSONDecodeError:
                    data_dict[key] = value[0]
            if 'chat_instance' in data_dict:
                data_dict['chat_instance'] = str(data_dict['chat_instance'])
            if 'auth_date' in data_dict:
                data_dict['auth_date'] = str(data_dict['auth_date'])
            return data_dict
        else:
            return None
    
    def get_jwt(self, data):
        json_str = json.dumps(data, separators=(',', ':'))
        utf8_bytes = json_str.encode('utf-8')
        base64_str = base64.b64encode(utf8_bytes).decode('utf-8')
        return base64_str

    def decode_string(self,encoded_str):
        decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str