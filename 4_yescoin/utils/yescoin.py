from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName

from urllib.parse import unquote
from utils.core import logger

from fake_useragent import UserAgent
from pyrogram import Client
from data import config

import random
import aiohttp
import asyncio


REF_CODE = "KWWehI"

class Yescoin:
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
        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=aiohttp.TCPConnector(verify_ssl=False))
        self.token = None
        if proxy:
            self.proxy = f"{config.PROXY_TYPE}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
        else:
            self.proxy = None

    async def main(self):
        while True:
            try:
                await asyncio.sleep(random.randint(*config.ACC_DELAY))
                logger.info(f"Thread {self.thread} | {self.name} | Start! | PROXY : {self.proxy}")
                tg_web_data = await self.get_tg_web_data()
                await self.login(tg_web_data=tg_web_data)
                info = await self.get_info()
                answer = await self.claim()
                if answer == True:
                    while answer:
                        answer = await self.claim()
                if config.AUTO_UPGRATE == True:
                    info = await self.get_info()
                    while True:
                        if info["Coin"] < config.MULIVALUE:
                            answer = await self.upgrate(name = 1)
                            if answer != 0 :
                                logger.success(f"Thread {self.thread} | {self.name} | улучшил Multivalue")
                                break
                        else:
                            break
                    while True:
                        if info["PoolRecovery"] < config.COINLIMIT:
                            answer = await self.upgrate(name = 3)
                            if answer != 0 :
                                logger.success(f"Thread {self.thread} | {self.name} | улучшил Coinlimit")
                                break
                        else:
                            break
                    while True:
                        if info ["PoolTotal"] < config.FILLRATE:
                            answer = await self.upgrate(name = 2)
                            if answer != 0:
                                logger.success(f"Thread {self.thread} | {self.name} | улучшил FillRate")
                                break
                        else:
                            break
                await self.get_account_info()
                sleep_time = random.randint(60*30,60*100)
                logger.info(f"Thread {self.thread} | {self.name} | уснул на {sleep_time} сек")
                await asyncio.sleep(sleep_time)
            except Exception as e:
                logger.error(f"Thread {self.thread} | {self.name} | Ошибка: {e}")

    async def get_tg_web_data(self):
        await self.client.connect()
        bot = await self.client.resolve_peer('theYescoin_bot')
        app = InputBotAppShortName(bot_id=bot, short_name="Yescoin")

        web_view = await self.client.invoke(RequestAppWebView(
                peer=bot,
                app=app,
                platform='android',
                write_allowed=True,
                start_param=REF_CODE
            ))

        auth_url = web_view.url
        await self.client.disconnect()
        return unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

    async def login(self, tg_web_data):
        json_data = {"code": tg_web_data}
        resp = await self.session.post("https://api-backend.yescoin.gold/user/login", json=json_data,proxy = self.proxy)
        resp_json = await resp.json()
        self.session.headers['token']=resp_json['data']["token"]
        await self.session.post(f'https://api-backend.yescoin.gold/invite/claimGiftBox?packId={REF_CODE}', proxy = self.proxy)
    
    async def claim(self):
        count = random.randint(20,85)
        response = await self.session.post('https://api-backend.yescoin.gold/game/collectCoin',json=count,proxy = self.proxy)
        text = await response.json()
        await asyncio.sleep(random.randint(3,6))
        if text['code'] == 0:
            logger.success(f"Thread {self.thread} | {self.name} | забрал {count*self.singleCoinLevel} yescoin")
            return True
        else:
            return False
    
    async def get_info(self):
        try:
            response = await self.session.get("https://api-backend.yescoin.gold/build/getAccountBuildInfo",proxy = self.proxy)
            data = (await response.json())['data']
            self.singleCoinLevel = data['singleCoinLevel']+1
            info = {
                "Coin" : data['singleCoinLevel']+1,
                "PoolRecovery" : data['coinPoolRecoveryLevel']+1,
                "PoolTotal" : data['coinPoolTotalLevel']+1,
            }
            
            return info
        except:
            return False
    
    async def get_account_info(self):
        try:
            response = await self.session.get("https://api-backend.yescoin.gold/account/getAccountInfo",proxy = self.proxy)
            data = (await response.json())['data']
            logger.info(f"Thread {self.thread} | {self.name} | Balance : {data['currentAmount']} | Rank : {data['rank']}")
            
        except:
            return False
    
    async def upgrate(self, name):
        response = await self.session.post('https://api-backend.yescoin.gold/build/levelUp', json=name,proxy = self.proxy)
        await asyncio.sleep(random.randint(2,6))
        return ((await response.json())['code'])
