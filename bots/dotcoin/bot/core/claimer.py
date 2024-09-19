import asyncio
from time import time
from datetime import datetime
from random import randint
from urllib.parse import unquote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView
from fake_useragent import UserAgent

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers


class Claimer:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.error_cnt = 0
        headers['User-Agent'] = UserAgent(os='android').random

    async def get_tg_web_data(self, proxy: str | None) -> dict[str]:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('dotcoin_bot'),
                bot=await self.tg_client.resolve_peer('dotcoin_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://dot.dapplab.xyz/',
                start_param=settings.REF_CODE
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            me = await self.tg_client.get_me()

            data_json = {
                'id': str(me.id),
                'tg_web_data': tg_web_data
            }
            
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            

            return data_json

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def get_token(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> dict[str]:
        try:
            http_client.headers["Authorization"] = f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impqdm5tb3luY21jZXdudXlreWlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg3MDE5ODIsImV4cCI6MjAyNDI3Nzk4Mn0.oZh_ECA6fA2NlwoUamf1TqF45lrMC0uIdJXvVitDbZ8"
            http_client.headers["Content-Type"] = "application/json"
            response = await http_client.post('https://api.dotcoin.bot/functions/v1/getToken', json={"initData": tg_web_data})
            response.raise_for_status()

            response_json = await response.json()

            return response_json['token']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting access token: {error}")
            await asyncio.sleep(delay=3)

    async def get_profile_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.post('https://api.dotcoin.bot/rest/v1/rpc/get_user_info', json={})
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
            await asyncio.sleep(delay=3)

    async def get_tasks_data(self, http_client: aiohttp.ClientSession, is_premium: bool) -> dict[str]:
        try:
            response = await http_client.post('https://api.dotcoin.bot/rest/v1/rpc/get_filtered_tasks', 
                json={"platform":"android","locale":"en","is_premium":is_premium})
            response.raise_for_status()

            response_json = await response.json()

            return response_json
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Tasks Data: {error}")
            await asyncio.sleep(delay=3)

    async def complate_task(self, http_client: aiohttp.ClientSession, task_id: int) -> bool:
        try:
            response = await http_client.post('https://api.dotcoin.bot/rest/v1/rpc/complete_task', 
                json={"oid":task_id})
            response.raise_for_status()

            response_json = await response.json()

            return response_json['success']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when complate task: {error}")
            await asyncio.sleep(delay=3)

            return False

    async def upgrade_boosts(self, http_client: aiohttp.ClientSession, boost_type: str, lvl: int) -> bool:
        try:
            response = await http_client.post(f'https://api.dotcoin.bot/rest/v1/rpc/{boost_type}', 
                json={"lvl":lvl})
            response.raise_for_status()

            response_json = await response.json()

            return response_json['success']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when complate task: {error}")
            await asyncio.sleep(delay=3)

            return False

    async def save_coins(self, http_client: aiohttp.ClientSession, taps: int) -> bool:
        try:
            response = await http_client.post('https://api.dotcoin.bot/rest/v1/rpc/save_coins', json={"coins":taps})
            response.raise_for_status()

            response_json = await response.json()

            return response_json['success']

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when saving coins: {error}")
            await asyncio.sleep(delay=3)

            return False

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        await asyncio.sleep(randint(*settings.ACC_DELAY))
        access_token_created_time = 0

        proxy_conn = ProxyConnector.from_url(proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            while True:
                try:
                    if time() - access_token_created_time >= 3600:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy)
                        access_token = await self.get_token(http_client=http_client, tg_web_data=tg_web_data['tg_web_data'])

                        http_client.headers["Authorization"] = f"Bearer {access_token}"
                        headers["Authorization"] = f"Bearer {access_token}"

                        http_client.headers["X-Telegram-User-Id"] = tg_web_data['id']
                        headers["X-Telegram-User-Id"] = tg_web_data['id']

                        access_token_created_time = time()

                        profile_data = await self.get_profile_data(http_client=http_client)

                        balance = profile_data['balance']
                        daily_attempts = profile_data['daily_attempts']
                        
                        logger.info(f"{self.session_name} | Balance: <c>{balance}</c>")
                        logger.info(f"{self.session_name} | Remaining attempts: <m>{daily_attempts}</m>")

                        tasks_data = await self.get_tasks_data(http_client=http_client, is_premium=profile_data['is_premium'])

                        for task in tasks_data:
                            task_id = task["id"]
                            task_title = task["title"]
                            task_reward = task["reward"]
                            task_status = task["is_completed"]

                            if task_status is True:
                                continue

                            if task["url"] is None and task["image"] is None:
                                continue

                            task_data_claim = await self.complate_task(http_client=http_client, task_id=task_id)
                            if task_data_claim:
                                logger.success(f"{self.session_name} | Successful claim task | "
                                            f"Task Title: <c>{task_title}</c> | "
                                            f"Task Reward: <g>+{task_reward}</g>")
                                continue

                        for i in range(daily_attempts, 0, -1):
                            if i == 0:
                                logger.info(f"{self.session_name} | Minimum attempts reached: {i}")
                                logger.info(f"{self.session_name} | Next try to tap coins in 1 hour")
                                break

                            taps = randint(a=settings.RANDOM_TAPS_COUNT[0], b=settings.RANDOM_TAPS_COUNT[1])
                            status = await self.save_coins(http_client=http_client, taps=taps)
                            if status:
                                new_balance = balance + taps
                                logger.success(f"{self.session_name} | Successful Tapped! | "
                                    f"Balance: <c>{new_balance}</c> (<g>+{taps}</g>) | Remaining attempts: <e>{i}</e>")

                            sleep = randint(a=settings.SLEEP_BETWEEN_TAP[0], b=settings.SLEEP_BETWEEN_TAP[1])
                            logger.info(f"{self.session_name} | Sleep {sleep}s for next tap")
                            await asyncio.sleep(delay=sleep)

                    profile_data = await self.get_profile_data(http_client=http_client)

                    balance = int(profile_data['balance'])
                    daily_attempts = int(profile_data['daily_attempts'])
                    multiple_lvl = profile_data['multiple_clicks']
                    attempts_lvl = profile_data['limit_attempts'] - 9
                    
                    next_multiple_lvl = multiple_lvl + 1
                    next_multiple_price = (2 ** multiple_lvl) * 1000
                    next_attempts_lvl = attempts_lvl + 1
                    next_attempts_price = (2 ** attempts_lvl) * 1000

                    logger.info(f"{self.session_name} | Balance: <c>{balance}</c>")
                    logger.info(f"{self.session_name} | Remaining attempts: <m>{daily_attempts}</m>")

                    if (settings.AUTO_UPGRADE_TAP is True
                            and balance > next_multiple_price
                            and next_multiple_lvl <= settings.MAX_TAP_LEVEL):
                        logger.info(f"{self.session_name} | Sleep 5s before upgrade tap to {next_multiple_lvl} lvl")
                        await asyncio.sleep(delay=5)

                        status = await self.upgrade_boosts(http_client=http_client, boost_type="add_multitap", lvl=multiple_lvl)
                        if status is True:
                            logger.success(f"{self.session_name} | Tap upgraded to {next_multiple_lvl} lvl")

                            await asyncio.sleep(delay=1)

                    if (settings.AUTO_UPGRADE_ATTEMPTS is True
                            and balance > next_attempts_price
                            and next_attempts_lvl <= settings.MAX_ATTEMPTS_LEVEL):
                        logger.info(
                            f"{self.session_name} | Sleep 5s before upgrade limit attempts to {next_attempts_lvl} lvl")
                        await asyncio.sleep(delay=5)

                        status = await self.upgrade_boosts(http_client=http_client, boost_type="add_attempts", lvl=attempts_lvl)
                        if status is True:
                            new_daily_attempts = next_attempts_lvl + 9
                            logger.success(f"{self.session_name} | Limit attempts upgraded to {next_attempts_lvl} lvl (<m>{new_daily_attempts}</m>)")

                            await asyncio.sleep(delay=1)

                    logger.info(f"{self.session_name} | All activities in dotcoin completed")
                    return 0
                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(52)
                    self.error_cnt += 1
                    if (self.error_cnt >= settings.ERRORS_BEFORE_STOP):
                        return 0


async def run_claimer(tg_client: Client, proxy: str | None):
    try:
        await Claimer(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
