from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
from urllib.parse import urlparse,parse_qs
from utils.core import logger
from fake_useragent import UserAgent
from pyrogram import Client
from data import config

import string
import aiohttp
import asyncio
import random
import base64
import os

class OneWin:
    REQUIRED = config.REQUIRED
    PRICES = config.PRICES
    TOOLS = config.TOOLS
        
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
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,mk;q=0.5',
            'cache-control': 'no-cache',
            'origin': 'https://cryptocklicker-frontend-rnd-prod.100hp.app',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://cryptocklicker-frontend-rnd-prod.100hp.app/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent(os='android').random
            }
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=aiohttp.TCPConnector(verify_ssl=False))
        self.balance = 0
        
    async def main(self):
        try:
            login = await self.login()
            if login == False:
                await self.session.close()
                return 0
            logger.info(f"main | Thread {self.thread} | {self.name} | Start! | PROXY : {self.proxy}")
            while True:
                try:
                    await self.everydayreward()
                    #for _ in range(random.randint(1,100)):
                        #await self.tap()
                    info = await self.mining_info()
                    for tool in list(self.REQUIRED.keys())[::-1]:
                        if tool not in info:
                            if self.REQUIRED[tool] == None:
                                tool += '1'
                                price = self.PRICES[tool]
                                if self.balance >= price:
                                    await self.upgrade(name = tool)
                            else:
                                required = self.REQUIRED[tool]
                                for num in range(10):
                                    required = required.replace(str(num),'')
                                if required in info:
                                    level_now = info[required]
                                    if level_now >= int(self.REQUIRED[tool].replace(required,'')):
                                        tool += '1'
                                        price = self.PRICES[tool]
                                        if self.balance >= price:
                                            await self.upgrade(name = tool)
                        else:
                            for num in range(10):
                                tool = tool.replace(str(num),'')
                            if (info[tool]) < config.UPGRADE_LEVEL:
                                tool += str(info[tool]+1)
                                if tool in self.PRICES:
                                    price = self.PRICES[tool]
                                    if self.balance >= price:
                                        await self.upgrade(name = tool)
                except Exception as err:
                    logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
                    await asyncio.sleep(round(random.uniform(30,60),2))
                    
        except Exception as err:
            logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
            await self.session.close()
            await asyncio.sleep(round(random.uniform(30,60),2))
            
    def generate_boundary(self):
        return '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    async def upgrade(self, name):
        await self.get_balance()
        self.session.headers['content-type'] = 'application/json'
        json_data = {
            'id': name,
        }
        response = await self.session.post('https://crypto-clicker-backend-go-prod.100hp.app/minings', json=json_data, proxy = self.proxy)
        answer = (await response.json())
        tool = answer.get('NextLevel').get('id')
        for num in range(10):
            tool = tool.replace(str(num),'')
        logger.success(f"upgrade | Thread {self.thread} | {self.name} | upgrade {tool} to {answer.get('NextLevel').get('level')-1} LEVEL")
        
        del self.session.headers['content-type']
        
        authorization = self.session.headers['authorization']
        del self.session.headers['authorization']
        self.session.headers['access-control-request-headers'] = 'authorization,content-type'
        self.session.headers['access-control-request-method'] = 'POST'
        await self.session.options('https://crypto-clicker-backend-go-prod.100hp.app/minings',proxy = self.proxy)
        del self.session.headers['access-control-request-headers']
        del self.session.headers['access-control-request-method']
        self.session.headers['authorization'] = authorization
        
        await asyncio.sleep(round(random.uniform(10, 30), 2))
        
        await self.get_balance()
        
    async def mining_info(self):
        response = await self.session.get('https://crypto-clicker-backend-go-prod.100hp.app/minings', proxy = self.proxy)
        authorization = self.session.headers['authorization']
        del self.session.headers['authorization']
        self.session.headers['access-control-request-headers'] = 'authorization'
        self.session.headers['access-control-request-method'] = 'GET'
        await self.session.options('https://crypto-clicker-backend-go-prod.100hp.app/minings',proxy = self.proxy)
        del self.session.headers['access-control-request-headers']
        del self.session.headers['access-control-request-method']
        self.session.headers['authorization'] = authorization
        
        response = await response.json()
        answer = dict()
        for tool in response:
            name = tool['id']
            level = tool['level']
            for num in range(10):
                name = name.replace(str(num),'')
            answer[name] = level
        return answer
        
    async def everydayreward(self):
        response = await self.session.get("https://crypto-clicker-backend-go-prod.100hp.app/tasks/everydayreward", proxy = self.proxy)
        resp = await response.json()
        is_collected = resp.get('days')[0].get('isCollected')
        reward = resp.get('days')[0].get('money')
        day = resp.get('days')[0].get('id')
        if is_collected == False:
            post_response = await self.session.post('https://crypto-clicker-backend-go-prod.100hp.app/tasks/everydayreward',proxy = self.proxy)
            
            authorization = self.session.headers['authorization']
            del self.session.headers['authorization']
            self.session.headers['access-control-request-headers'] = 'authorization'
            self.session.headers['access-control-request-method'] = 'POST'
            
            await self.session.options('https://crypto-clicker-backend-go-prod.100hp.app/tasks/everydayreward',proxy = self.proxy)
            
            del self.session.headers['access-control-request-headers']
            del self.session.headers['access-control-request-method']
            self.session.headers['authorization'] = authorization
        
            logger.success(f"everyday | Thread {self.thread} | {self.name} | claim {day} reward : {reward}")

        await self.get_balance()
        
        
        
    async def tap(self):
        self.session.headers['content-type'] = 'application/json'
        json_data = {
            'tapsCount': random.randint(9,15),
        }
        await self.session.post('https://crypto-clicker-backend-go-prod.100hp.app/tap', json=json_data, proxy = self.proxy)
        del self.session.headers['content-type']
        
        authorization = self.session.headers['authorization']
        del self.session.headers['authorization']
        self.session.headers['access-control-request-headers'] = 'authorization,content-type'
        self.session.headers['access-control-request-method'] = 'POST'
        await self.session.options('https://crypto-clicker-backend-go-prod.100hp.app/tap',proxy = self.proxy)
        del self.session.headers['access-control-request-headers']
        del self.session.headers['access-control-request-method']
        self.session.headers['authorization'] = authorization
        await asyncio.sleep(2)
        
    async def get_balance(
        self 
    ):
        response = await self.session.get('https://crypto-clicker-backend-go-prod.100hp.app/user/balance',proxy = self.proxy)
        authorization = self.session.headers['authorization']
        del self.session.headers['authorization']
        self.session.headers['access-control-request-headers'] = 'authorization'
        self.session.headers['access-control-request-method'] = 'GET'
        await self.session.options('https://crypto-clicker-backend-go-prod.100hp.app/user/balance',proxy = self.proxy)
        del self.session.headers['access-control-request-headers']
        del self.session.headers['access-control-request-method']
        self.session.headers['authorization'] = authorization
        
        answer = await response.json()
        self.balance = answer.get('coinsBalance')
        await asyncio.sleep(round(random.uniform(3, 10), 2))

    async def login(self):
        try:
            boundary = self.generate_boundary()
            self.session.headers['content-type'] = f'multipart/form-data; boundary={boundary}'
            tg_web_data = await self.get_tg_web_data()
            files = {
                'referrer_tg_id': (None, '707649803'),
            }
            resp = await self.session.post('https://crypto-clicker-backend-go-prod.100hp.app/game/start', params=tg_web_data,data=files, proxy = self.proxy)
            del self.session.headers['content-type']
            self.session.headers['accept'] = '*/*'
            resp = await resp.json()
            self.session.headers['authorization'] = "Bearer " + (resp).get("token")
            await self.get_balance()
            await asyncio.sleep(round(random.uniform(3, 10), 2))
            return True
        except Exception as err:
            logger.error(f"login | Thread {self.thread} | {self.name} | {err}")
            if err == "Server disconnected":
                return True
            return False


    async def get_tg_web_data(self):
        await self.client.connect()
        try:
            bot = await self.client.resolve_peer('token1win_bot')
            app = InputBotAppShortName(bot_id=bot, short_name="start")
            
            web_view = await self.client.invoke(RequestAppWebView(
                    peer=bot,
                    app=app,
                    platform='android',
                    write_allowed=True,
                    start_param="refId707649803"
                ))
            auth_url = web_view.url
            parsed_url = urlparse(auth_url)
            fragment = parsed_url.fragment
            fragment_params = parse_qs(fragment)
            params = {key: value[0] for key, value in fragment_params.items()}
            tg_web_app_data = parse_qs(params['tgWebAppData'])
            tg_web_app_data = {key: value[0] for key, value in tg_web_app_data.items()}
            params.update(tg_web_app_data)
            del params['tgWebAppData']
            del params['tgWebAppVersion']
            del params['tgWebAppPlatform']
            del params['tgWebAppSideMenuUnavail']
        except Exception as err:
            logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
            if 'USER_DEACTIVATED_BAN' in str(err):
                logger.error(f"login | Thread {self.thread} | {self.name} | USER BANNED")
                await self.client.disconnect()
                return False
        await self.client.disconnect()
        return params

    def decode_param(self,encoded_param):
        decoded_bytes = base64.urlsafe_b64decode(encoded_param.encode('utf-8'))
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
