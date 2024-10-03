from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw import functions


from urllib.parse import unquote
from utils.core import logger
from fake_useragent import UserAgent
from pyrogram import Client
from data import config
from datetime import datetime,timezone,timedelta
import uuid, ssl, certifi
from aiohttp_socks import ProxyConnector

import aiohttp
import asyncio
import random
import os

class Cats:
    def __init__(self, thread: int, account: str, proxy : str):
        self.thread = thread
        self.name = account
        self.ref = config.REF_CODE
        self.error_cnt = 0
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
            'user-agent': UserAgent(os='android').random}
        sslcontext = ssl.create_default_context(cafile=certifi.where())
        connector = ProxyConnector.from_url(self.proxy, ssl=sslcontext) if self.proxy else aiohttp.TCPConnector(ssl=sslcontext, limit=1, force_close=True)
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def main(self):
        await asyncio.sleep(random.randint(*config.ACC_DELAY))
        while True:
            try:
                try:
                    login = await self.login()
                    logger.info(f"main | Thread {self.thread} | {self.name} | Start! | PROXY : {self.proxy}")
                except Exception as err:
                    logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
                    await self.session.close()
                    return 0
                if config.DO_PHOTOS:
                    reward = await self.send_cats()
                    if reward:
                        logger.info(f"main | Thread {self.thread} | {self.name} | Reward from Avatar quest: <y>{reward}</y>")
                    await asyncio.sleep(random.randint(5, 15))

                await self.do_tasks()
                await self.session.close()
                logger.info(f"main | Thread {self.thread} | {self.name} | All activities in cats completed")
                return 0
            except Exception as err:
                logger.error(f"main | Thread {self.thread} | {self.name} | {err}")
                await asyncio.sleep(52)
                self.error_cnt += 1
                if (self.error_cnt >= config.ERRORS_BEFORE_STOP):
                    await self.session.close()
                    return 0

    async def send_cats(self):
        avatar_info = await self.session.get("https://api.catshouse.club/user/avatar")
        avatar_info = await avatar_info.json()
        if avatar_info:
            attempt_time_str = avatar_info.get('attemptTime', None)
            if not attempt_time_str:
                time_difference = timedelta(hours=25)
            else:
                attempt_time = datetime.fromisoformat(attempt_time_str.replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                next_day_3am = (attempt_time + timedelta(days=1)).replace(hour=3, minute=0, second=0, microsecond=0)
                
                if current_time >= next_day_3am:
                    time_difference = timedelta(hours=25)
                else:
                    time_difference = next_day_3am - current_time

            if time_difference > timedelta(hours=24):
                response = await self.session.get(f"https://cataas.com/cat?timestamp={int(datetime.now().timestamp() * 1000)}", headers={
                    "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "accept-language": "en-US,en;q=0.9,ru;q=0.8",
                    "sec-ch-ua": "\"Not;A=Brand\";v=\"24\", \"Chromium\";v=\"128\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"macOS\"",
                    "sec-fetch-dest": "image",
                    "sec-fetch-mode": "no-cors",
                    "sec-fetch-site": "cross-site"
                })
                if not response and response.status not in [200, 201]:
                    logger.error(f"main | Thread {self.thread} | {self.name} | Failed to fetch image from cataas.com")
                    return None
                
                image_content = await response.read()
                    
                boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
                form_data = (
                    f'--{boundary}\r\n'
                    f'Content-Disposition: form-data; name="photo"; filename="{uuid.uuid4().hex}.jpg"\r\n'
                    f'Content-Type: image/jpeg\r\n\r\n'
                ).encode('utf-8')
                
                form_data += image_content
                form_data += f'\r\n--{boundary}--\r\n'.encode('utf-8')
                
                headers = self.session.headers.copy()
                headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
                response = await self.session.post("https://api.catshouse.club/user/avatar/upgrade", data=form_data, headers=headers)
                response = await response.json()
                if response:
                    return response.get('rewards', 0)
                else:
                    return None
            else:
                hours, remainder = divmod(time_difference.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                logger.info(f"main | Thread {self.thread} | {self.name} | Time until next avatar upload: <y>{hours}</y> hours, <y>{minutes}</y> minutes, and <y>{seconds}</y> seconds")
                return None

    async def login(self):
        try:
            tg_web_data = await self.get_tg_web_data()

            if tg_web_data == False:
                return False

            params = {
                'referral_code': self.ref,
            }
            resp = await self.session.post("https://api.catshouse.club/user/create", params=params)
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
            messages = await self.client.get_chat_history_count(chat_id='@catsgang_bot')
            if not messages:
                peer = await self.client.resolve_peer('catsgang_bot')
                await self.client.invoke(
                    functions.messages.StartBot(
                        bot=peer,
                        peer=peer,
                        start_param=config.REF_CODE,
                        random_id=random.randint(1, 9999999),
                    )
                )
            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('catsgang_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('catsgang_bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param=self.ref
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
        resp = await self.session.get('https://api.catshouse.club/tasks/user', params=params)
        resp_json = await resp.json()
        try:
            for task in resp_json['tasks']:
                if task['id'] in config.BLACKLIST:
                    continue
                try:
                    if not task['completed']:
                        if task['type'] == 'SUBSCRIBE_TO_CHANNEL':
                            continue
                        else:
                            try:
                                json_data = {}
                                response = await self.session.post(f'https://api.catshouse.club/tasks/{task["id"]}/complete', json=json_data)
                                resp = await response.json()
                                if resp['success']:
                                    logger.success(f"do_task | Thread {self.thread} | {self.name} | Claim task {task['title']}")
                                else:
                                    logger.error(f"do_task | Thread {self.thread} | {self.name} | task {task['id']} {resp}")
                            except Exception as err:
                                logger.error(f"tasks | Thread {self.thread} | {self.name} | {err} TASK_ID : {task['id']}")
                            await asyncio.sleep(random.uniform(*config.TASK_SLEEP))
                except Exception as err:
                    logger.error(f"tasks | Thread {self.thread} | {self.name} | {err} TASK_ID : {task['id']}")
                            
        except Exception as err:
            logger.error(f"tasks | Thread {self.thread} | {self.name} | {err} {task} TASK_ID : {task['id']}")
    
 
