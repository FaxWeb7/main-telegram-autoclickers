from urllib.parse import unquote
from utils.core import logger
from fake_useragent import UserAgent
from pyrogram import Client
from data import config

from aiohttp_socks import ProxyConnector
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName

import aiohttp
import asyncio
import random

class Major:
    def __init__(self, thread: int, account: str, proxy : str):
        self.thread = thread
        self.name = account
        self.ref = config.REF_CODE
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
            
    async def create_session(self):
        connector = ProxyConnector.from_url(self.proxy, verify_ssl=False) if self.proxy else aiohttp.TCPConnector(verify_ssl=False)
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://major.bot/',
            'sec-ch-ua': '"Chromium";v="122", "Not;A=Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': UserAgent(os='android').random
        }

        return aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)
    
    async def main(self):
        while True:
            try:
                await asyncio.sleep(random.randint(*config.ACC_DELAY))
                self.session = await self.create_session()
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
                
                user = await self.user()
                await asyncio.sleep(random.uniform(*config.MINI_SLEEP))
                if random.randint(0,3) == 0 and config.JOIN_SQUAD:
                    if user['squad_id'] == None:
                        subscribe=True
                        tasks = await self.get_tasks(is_daily=False)
                        for task in tasks:
                            if task['id'] == 27:
                                subscribe = False
                        if not subscribe:
                            async with self.client:
                                ans = await self.client.join_chat('starsmajor')
                            await self.do_task(task_id=27)
                        await self.join_squad()
                    await asyncio.sleep(random.uniform(*config.MINI_SLEEP))

                await self.get_streak()
                await self.visit()
                
                await asyncio.sleep(random.uniform(*config.MINI_SLEEP))
                tasks = await self.get_tasks(is_daily=False)
                await asyncio.sleep(3*random.uniform(*config.MINI_SLEEP))
                for task in tasks:
                    if not task['is_completed'] and task['id'] not in config.BLACKLIST_TASKS:
                        if random.randint(0,3) == 0: 
                            task_info = (await self.do_task(task_id=task['id']))
                            if 'detail' in task_info:
                                logger.info(f"main | Thread {self.thread} | {self.name} | {task_info['detail']}")
                                await asyncio.sleep(10*random.uniform(*config.TASK_SLEEP))
                            elif task_info['is_completed']:
                                logger.success(f"main | Thread {self.thread} | {self.name} | CLAIM TASK {task['description']}")
                                await self.get_tasks(is_daily=False)
                                await self.get_tasks(is_daily=True)
                                await asyncio.sleep(random.uniform(*config.TASK_SLEEP))
                
                await asyncio.sleep(random.uniform(*config.MINI_SLEEP))
                
                tasks = await self.get_tasks(is_daily=True)
                for task in tasks:
                    if not task['is_completed'] and task['id'] == 5:
                        task_info = (await self.do_task(task_id=task['id']))
                        if 'detail' in task_info:
                            logger.info(f"main | Thread {self.thread} | {self.name} | {task_info['detail']}")
                        elif task_info['is_completed']:
                            logger.success(f"main | Thread {self.thread} | {self.name} | CLAIM TASK {task['description']}")
                
                mini_games = []
                if config.HOLD_COIN:
                    mini_games.append(self.play_hold_coin)
                if config.ROULETTE:
                    mini_games.append(self.play_roulette)
                if config.SWIPE_COIN:
                    mini_games.append(self.play_swipe_coin)
                random.shuffle(mini_games)
                for game in mini_games:
                    await game()
                    await asyncio.sleep(random.uniform(*config.GAME_SLEEP))
                
                await self.session.close()
                
                logger.info(f"main | Thread {self.thread} | {self.name} | КРУГ ОКОНЧЕН")
                await asyncio.sleep(random.uniform(*config.BIG_SLEEP))
            except Exception as err:
                logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
            
                
            

    async def play_swipe_coin(self):
        resp = await self.session.get("https://major.bot/api/swipe_coin/")
        resp = await self.session.get("https://major.bot/api/swipe_coin/")
        if 'detail' in await resp.json():
            return False

        await asyncio.sleep(60)
        
        json_data = {
            'coins': random.randint(500,1500),  
        }

        response = await self.session.post('https://major.bot/api/swipe_coin/', json=json_data)
        if 'detail' in await resp.json():
            logger.error(f"swipe_coin | Thread {self.thread} | {self.name} | {await response.json()}")
        elif (await resp.json())['success']:
            logger.success(f"swipe_coin | Thread {self.thread} | {self.name} | забрал {json_data['coins']} звезд")
        return await response.json()
    
    
    async def play_roulette(self):
        resp = await self.session.get("https://major.bot/api/roulette/")
        if 'detail' in await resp.json():
            return False

        response = await self.session.post('https://major.bot/api/roulette/')
        if 'detail' in await resp.json():
            logger.error(f"roulette | Thread {self.thread} | {self.name} | {await response.json()}")
        elif (await resp.json())['success']:
            logger.success(f"roulette | Thread {self.thread} | {self.name} | забрал {(await response.json())['rating_award']} звезд")
        return await response.json()
    
    async def play_hold_coin(self):
        resp = await self.session.get("https://major.bot/api/bonuses/coins/")
        resp = await self.session.get("https://major.bot/api/bonuses/coins/")
        if 'detail' in await resp.json():
            return False
        
        await asyncio.sleep(60)
        
        json_data = {
            'coins': random.randint(500,850),
        }
        response = await self.session.post('https://major.bot/api/bonuses/coins/', json=json_data)
        if 'detail' in await resp.json():
            logger.error(f"hold_coin | Thread {self.thread} | {self.name} | {await response.json()}")
        elif (await resp.json())['success']:
            logger.success(f"hold_coin | Thread {self.thread} | {self.name} | забрал {json_data['coins']} звезд")
        return await response.json()
    
    async def get_tasks(self, is_daily : bool = False):
        params = {
            'is_daily': str(is_daily).lower(),
        }

        resp = await self.session.get('https://major.bot/api/tasks/', params=params)
        return await resp.json()

    async def do_task(self, task_id : int):
        json_data = {
            'task_id': task_id,
        }

        resp = await self.session.post('https://major.bot/api/tasks/', json=json_data)
        return await resp.json()
    

    async def visit(self):
        resp = await self.session.post("https://major.bot/api/user-visits/visit/")
        return await resp.json()

    async def get_streak(self):
        resp = await self.session.get("https://major.bot/api/user-visits/streak/")
        return await resp.json()
        
    async def user(self):
        resp = await self.session.get(f"https://major.bot/api/users/{self.user_info.id}/")
        return await resp.json()

    async def join_squad(self):
        resp = await self.session.post('https://major.bot/api/squads/1916292383/join/')
        if 'detail' in await resp.json():
            return False
        if (await resp.json())['status'] == 'ok':
            logger.success(f"join_squad | Thread {self.thread} | {self.name} | Вступил в сквад")
            
    async def login(self):
        try:
            tg_web_data = await self.get_tg_web_data()
            if tg_web_data == False:
                return False
            json_data = {"init_data": tg_web_data}
            resp = await self.session.post("https://major.bot/api/auth/tg/", json=json_data)
            resp = await resp.json()
            self.session.headers['authorization'] = f"Bearer {resp['access_token']}"
            return True
        except Exception as err:
            logger.error(f"login | Thread {self.thread} | {self.name} | {err}")
            return False


    async def get_tg_web_data(self):
        async with self.client:
            try:
                web_view = await self.client.invoke(RequestAppWebView(
                    peer=await self.client.resolve_peer('major'),
                    app=InputBotAppShortName(bot_id=await self.client.resolve_peer('major'), short_name="start"),
                    platform='android',
                    write_allowed=True,
                    start_param=self.ref
                ))

                auth_url = web_view.url
                
                self.user_info = await self.client.get_me()
                return unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            except Exception as err:
                logger.error(f"get_tg_web_data | Thread {self.thread} | {self.name} | {err}")
                return False
  
