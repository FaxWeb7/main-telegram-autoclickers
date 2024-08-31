from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName


from urllib.parse import unquote
from utils.core import logger
from fake_useragent import UserAgent
from pyrogram import Client
from data import config

import aiohttp
import asyncio
import random

class Cats:
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
            'accept': '*/*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,mk;q=0.5',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="122", "Chromium";v="122"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': UserAgent(os='android').random
        }
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=aiohttp.TCPConnector(verify_ssl=False))

    async def main(self):
        try:
            await asyncio.sleep(random.randint(*config.ACC_DELAY))
            while True:
                try:
                    try:
                        login = await self.login()
                        logger.info(f"main | Thread {self.thread} | {self.name} | Start! | PROXY : {self.proxy}")
                    except Exception as err:
                        logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
                        self.session.close()
                        return 0
                    await self.do_tasks()
                    await asyncio.sleep(random.uniform(24*60*60,26*60*60))
                except Exception as err:
                    logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
                    await asyncio.sleep(5*random.uniform(*config.MINI_SLEEP))
        except:
            await self.session.close()
    
    async def stats(self):
        await self.login()
        resp = await self.session.get('https://cats-backend-cxblew-prod.up.railway.app/user',proxy=self.proxy)
        resp = await resp.json()
        await self.session.close()
        return {'id':resp['id'],'username':resp['username'],'age':resp['telegramAge'],'total':resp['totalRewards']}

    async def login(self):
        try:
            tg_web_data = await self.get_tg_web_data()

            if tg_web_data == False:
                return False

            params = {
                'referral_code': '18awB6nNqqe8928y1u4vp',
            }
            resp = await self.session.post("https://cats-backend-cxblew-prod.up.railway.app/user/create", params=params,proxy=self.proxy)
            resp = await resp.text()
            if 'message' in resp:
                return False
            return True
        except Exception as err:
            logger.error(f"login | Thread {self.thread} | {self.name} | {err} {tg_web_data}")
            if err == "Server disconnected":
                return True
            return False
    
    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('catsgang_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('catsgang_bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param='18awB6nNqqe8928y1u4vp'
            ))
            await self.client.disconnect()
            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            self.session.headers['Authorization'] = f"tma {query}"
            return query

        except Exception as err:
            logger.error(f"get_tg_webdata | Thread {self.thread} | {self.name} | {err}")
            if 'USER_DEACTIVATED_BAN' in str(err):
                logger.error(f"login | Thread {self.thread} | {self.name} | USER BANNED")
                await self.client.disconnect()
                return False
            await self.client.disconnect()

    async def do_tasks(self):

        params = {
            'group':'cats'
        }
        resp = await self.session.get('https://cats-backend-cxblew-prod.up.railway.app/tasks/user', params=params,proxy=self.proxy)
        resp_json = await resp.json()
        try:
            for task in resp_json['tasks']:
                if task['id'] in [36,45,5,4,3,2,49]:
                    continue
                if not task['completed']:
                    if task['type'] == 'SUBSCRIBE_TO_CHANNEL':
                        link = task['params']['channelUrl']
                        async with self.client:
                            try:
                                await self.client.join_chat(link)
                            except:
                                await self.client.join_chat(link.replace('https://t.me/',''))
                            await asyncio.sleep(random.uniform(*config.MINI_SLEEP))
                            
                            response = await self.session.post(f'https://cats-backend-cxblew-prod.up.railway.app/tasks/{task["id"]}/check', proxy=self.proxy)
                            response = await self.session.post(f'https://cats-backend-cxblew-prod.up.railway.app/tasks/{task["id"]}/complete', proxy=self.proxy)
                            logger.success(f"do_task | Thread {self.thread} | {self.name} | Claim task {task['title']}")
                            await asyncio.sleep(random.uniform(*config.TASK_SLEEP))
                    else:
                        response = await self.session.post(f'https://cats-backend-cxblew-prod.up.railway.app/tasks/{task["id"]}/complete', proxy=self.proxy)
                        resp = await response.json()
                        if resp['success']:
                            logger.success(f"do_task | Thread {self.thread} | {self.name} | Claim task {task['title']}")
                        await asyncio.sleep(random.uniform(*config.TASK_SLEEP))
                tasks = await self.session.get('https://cats-backend-cxblew-prod.up.railway.app/tasks/user?group=bitget',proxy=self.proxy)
                tasks = (await tasks.json())['tasks']
                for task in tasks:
                    if not task['completed']:
                        response = await self.session.post(f'https://cats-backend-cxblew-prod.up.railway.app/tasks/{task["id"]}/complete', proxy=self.proxy)
                        response = (await response.json())
                        if response['success']:
                            logger.success(f"do_task | Thread {self.thread} | {self.name} | Claim task {task['title']}")
                        await asyncio.sleep(random.uniform(*config.TASK_SLEEP))
                        
        except Exception as err:
            logger.error(f"tasks | Thread {self.thread} | {self.name} | {err}")
    
 