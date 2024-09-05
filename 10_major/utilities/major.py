from utilities.core import logger
from pyrogram import Client, raw 
from urllib.parse import unquote, quote
import asyncio
from fake_useragent import UserAgent
from random import uniform
from data import config
from random import randint
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import json
import os
import httpx
import time
from pyrogram.raw.functions.messages import RequestWebView

class MajorBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = proxy
        self.user_agent_file = "./sessions/user_agents.json"
        self.ref_link_file = "./sessions/ref_links.json"
        self.major_refs = './sessions/major_refs.json'

        if proxy:
            proxy_client = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split("://")[1].split("@")[1].split(':')[0],
                "port": int(proxy.split("://")[1].split("@")[1].split(':')[1]),
                "username": proxy.split("://")[1].split("@")[0].split(':')[0],
                "password": proxy.split("://")[1].split("@")[0].split(':')[1]
            }

            self.client = Client(
                name=session_name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                workdir=config.WORKDIR,
                proxy=proxy_client,
                lang_code='ru'
            )
        else:
            self.client = Client(
                name=session_name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                workdir=config.WORKDIR,
                lang_code='ru'
            )

    async def init_async(self, proxy):
        # self.refferal_link = await self.get_ref_link()
        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = httpx.AsyncClient(headers=headers)
        self.initialized = True


    @classmethod
    async def create(cls, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        instance = cls(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
        await instance.init_async(proxy)
        return instance
    

    async def make_cd_holder_task(self):
        await self.client.connect()
        web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('cityholder'),
                bot=await self.client.resolve_peer('cityholder'),
                platform='android',
                from_bot_menu=False,
                url='https://t.me/cityholder/app'
            ))
        await self.client.disconnect()

        auth_url = web_view.url
        query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        
        json_data = {
            'auth': f'{query}'
        }
        # print('holder query ', query)
        resp = await self.session.post('https://api-reserve.city-holder.com/auth', json=json_data)
        resp_json = resp.json()
        # print('resp_json ', resp_json)

    async def make_coin_game(self): #915 coins
        pass

    async def make_task(self, resp_json, headers):
        for task in resp_json:
            if task['id'] in config.BLACKLIST_TASK:
                continue
            if 'https://t.me/' in task['payload']['url'] and 'boost' not in task['payload']['url'] and 'addlist' not in task['payload']['url']:
              
                if 'startapp' in task['payload']['url']:
                    bot_username = task['payload']['url'].split('/')[3]
                    
                    start_param = task['payload']['url'].split('/')[4].split('=')[1]

                    await self.client.connect()
                    try:
                        result = await self.client.invoke(
                            raw.functions.messages.StartBot(
                                bot=await self.client.resolve_peer(bot_username),
                                peer=await self.client.resolve_peer(bot_username),
                                random_id=int(time.time() * 1000),
                                start_param=start_param
                            )
                        )
                    except Exception as e:
                        print("e = ", e)   
                    await self.client.disconnect() 

                    if 'cityholder' in task['payload']['url']:
                        await self.make_cd_holder_task()
                else:
                    await self.client.connect()
                    try:
                        if '+' in task['payload']['url']:
                            await self.client.join_chat(task['payload']['url'])
                        else:
                            await self.client.join_chat(task['payload']['url'].split('/')[3])
                    except Exception as e:
                        print("e = ", e)
                    await self.client.disconnect()
                    
                await asyncio.sleep(randint(10, 20))
            json_data = {
                'task_id': task['id']
            }
            resp = await self.session.post('https://major.glados.app/api/tasks/', json=json_data, headers=headers)
            if resp.status_code == 201:
                resp_json = resp.json()
                if 'task_id' in resp_json:
                    logger.info(f"Thread {self.thread} | {self.account} | Try task {resp_json['task_id']}")
                    await asyncio.sleep(randint(10, 30))
            else:
                logger.error(f"Thread {self.thread} | {self.account} | Error {resp.status_code}")
    
    async def hold_coin_task(self, headers):
        try:
            resp = await self.session.get('https://major.glados.app/api/bonuses/coins/', headers=headers)
            resp_json = resp.json()
            if resp_json['is_available'] == True:
                logger.info(f"Thread {self.thread} | {self.account} | Holding coin...")
                await asyncio.sleep(60)
                coinsNum = randint(700, 830)
                resp = await self.session.post('https://major.glados.app/api/bonuses/coins/', headers=headers, json={'coins': coinsNum})
                resp_json = resp.json()
                if resp_json['success'] == True:
                    logger.success(f"Thread {self.thread} | {self.account} | Hold coin success: +{coinsNum}")

        except Exception as e:
            logger.error(f"Thread {self.thread} | {self.account} | Holding coin error: {e}")
    async def claim_swipe_coins(self, headers):
        try:
            response = await self.session.get('https://major.glados.app/api/swipe_coin/', headers=headers)
            if response and response.get('success') is True:
                logger.info(f"Thread {self.thread} | {self.account} | Swiping coin...")
                coins = randint(500, 700)
                payload = {"coins": coins }
                await asyncio.sleep(55)
                response = await self.session.pos('https://major.glados.app/api/swipe_coin/', headers=headers, json=payload)
                if response and response.get('success') is True:
                    logger.success(f"Thread {self.thread} | {self.account} | Swipe coin success: +{coins}")
        
        except Exception as e:
            logger.error(f"Thread {self.thread} | {self.account} | Swipe coin error: {e}")
        
    async def login(self):
        query = await self.get_tg_web_data()
        headers = {
            'Host': 'major.glados.app',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'Sec-Ch-Ua-Mobile': '0',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Upgrade-Insecure-Requests': '0',
            'Sec-Fetch-User': '0',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://major.glados.app',
            'Referer': 'https://major.glados.app/',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Priority': 'u=1, i'
        }
        json_data = {
            'init_data': query
        }
        # print(f'query {self.account} :', query)
        await asyncio.sleep(randint(10, 20))
        resp = await self.session.post('https://major.glados.app/api/auth/tg/', json=json_data, headers=headers)
        resp_json = resp.json()
        user_id = ''
        if 'user' in resp_json and 'id' in resp_json['user']:
            user_id = resp_json['user']['id']
        logger.info(f"Thread {self.thread} | {self.account} | Auth in app, code {resp.status_code}")
        self.session.headers.pop('Authorization', None)
        self.session.headers['Authorization'] = "Bearer " + resp_json.get("access_token")

        resp = await self.session.post('https://major.glados.app/api/user-visits/visit/?', headers=headers)
        resp_json = resp.json()
        await asyncio.sleep(randint(10, 20))

        resp = await self.session.get("https://major.glados.app/api/tasks/?is_daily=true", headers=headers)
        resp_json_daily = resp.json()
        logger.info(f"Thread {self.thread} | {self.account} | Daily tasks, {[task['title'] for task in resp_json_daily]}")
        await asyncio.sleep(randint(10, 20))
        await self.make_task(resp_json_daily, headers)

        resp_json_daily = resp.json()
        logger.info(f"Thread {self.thread} | {self.account} | Repeat Daily tasks, {[task['title'] for task in resp_json_daily]}")
        await asyncio.sleep(randint(10, 20))
        await self.make_task(resp_json_daily, headers)

        resp = await self.session.get("https://major.glados.app/api/tasks/?is_daily=false", headers=headers)
        resp_json_not_daily = resp.json()
        logger.info(f"Thread {self.thread} | {self.account} | Not Daily tasks, {[task['title'] for task in resp_json_not_daily]}")
        await asyncio.sleep(randint(10, 20))
        await self.make_task(resp_json_not_daily, headers)

        resp = await self.session.post("https://major.glados.app/api/roulette?", headers=headers)
        resp_json_not_daily = resp.json()
        logger.success(f"Thread {self.thread} | {self.account} | Roulette done")
        await asyncio.sleep(randint(10, 20))

        await self.hold_coin_task(headers)

        await asyncio.sleep(randint(10, 20))

        await self.claim_swipe_coins(headers)

        await asyncio.sleep(randint(10, 20))
        try:
            resp = await self.session.get(f'https://major.glados.app/api/users/{user_id}/', headers=headers)
            resp_json = resp.json()
            rating = resp_json['rating']
            await asyncio.sleep(randint(10, 20))
            resp = await self.session.get(f'https://major.glados.app/api/users/top/position/{user_id}/?', headers=headers)
            resp_json = resp.json()
            position = resp_json['position']
            logger.success(f"Thread {self.thread} | {self.account} | Rating: {rating}, Pos: {position}")
        except Exception as e:
            logger.error(f"Thread {self.thread} | {self.account} | e = {e}")
        sleep_time = 60 * 60 * 8 + uniform(config.DELAYS['MAJOR_SLEEP'][0], config.DELAYS['MAJOR_SLEEP'][1])
        logger.info(f"Thread {self.thread} | {self.account} | Sleep {sleep_time}")
        await asyncio.sleep(sleep_time)


    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            bot_username = "major"
            bot = await self.client.get_users(bot_username)
            not_found = True
            # Пробуем получить чат по username бота
            try:
                messages = self.client.get_chat_history(bot.id, limit=1)
                async for message in messages:
                    logger.info(f"Thread {self.thread} | {self.account} | Button found")
                else:
                    not_found = False
            except Exception as e:
                clicked = False
                print("Error:", e)

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('major'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('major'), short_name="start"),
                platform='android',
                write_allowed=True,
                start_param='6046075760'
            ))
            await self.client.disconnect()

            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query
        except:
            return None
        

    async def logout(self):
        await self.session.close()