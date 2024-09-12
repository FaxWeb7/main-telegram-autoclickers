import asyncio
import functools
import urllib.parse
from random import randint
from time import time
from fake_useragent import UserAgent
from typing import Callable
from urllib.parse import unquote

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.exceptions import InvalidSession
from bot.utils import logger, utils
from .agents import generate_random_user_agent
from .headers import headers


def error_handler(func: Callable):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            await asyncio.sleep(1)

    return wrapper


class Tapper:
    def __init__(self, tg_client: Client, proxy: str | None):
        self.session_name = tg_client.name
        self.proxy = proxy
        self.tg_client = tg_client
        self.bot_name = 'tonstationgames_bot'  # Bot login
        self.app_url = 'https://tonstation.app/app/'  # webapp host
        self.api_endpoint = 'https://tonstation.app'
        self.start_param = None

        self.user = None
        self.token = None

        self.errors = 0

        self.farming_end = None

    async def get_tg_web_data(self):
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
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
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer(self.bot_name)
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | FloodWait {fl}")
                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            if settings.REF_ID == '':
                start_param = 'ref_ko3oyczvk57z6quvjj54p2'  # ref
                self.start_param = start_param  # ref
            else:
                start_param = settings.REF_ID
                self.start_param = start_param

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url=self.app_url,
                start_param='ref_jqocex2xmbd2ik27wspihm'
            ))

            auth_url = web_view.url

            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            self.user = await self.tg_client.get_me()

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(
                f"<light-yellow>{self.session_name}</light-yellow> | Error while Get TG web data: {error}")
            await asyncio.sleep(delay=3)

    @error_handler
    async def make_request(self, http_client, method, endpoint=None, url=None, **kwargs):
        try:
            full_url = url or f"{self.api_endpoint}{endpoint or ''}"
            response = await http_client.request(method, full_url, **kwargs)

            return await response.json()
        except aiohttp.ClientResponseError as error:
            self.errors += 1
            logger.error(f"{self.session_name} | HTTP error: {error}")
            await asyncio.sleep(delay=3)

    @error_handler
    async def check_proxy(self, http_client: aiohttp.ClientSession) -> None:
        response = await self.make_request(http_client, 'GET', url='https://httpbin.org/ip',
                                           timeout=aiohttp.ClientTimeout(5))
        ip = response.get('origin')
        logger.info(f"{self.session_name} | Proxy IP: {ip}")

    @error_handler
    async def auth(self, http_client):
        tg_web_data = await self.get_tg_web_data()
        parsed_query = urllib.parse.parse_qs(tg_web_data)
        encoded_query = urllib.parse.urlencode(parsed_query, doseq=True)

        response = await self.make_request(http_client, "POST", "/userprofile/api/v1/users/auth",
                                           json={'initData': f'{encoded_query}'})

        if response.get('code') != 403:
            self.token = response.get('accessToken')

            http_client.headers["Authorization"] = f"Bearer {self.token}"
            headers["Authorization"] = f"Bearer {self.token}"
            return response
        else:
            logger.info(f"{self.session_name} | Error while getting token: {response.get('message')}")

    @error_handler
    async def login(self, http_client):
        response = await self.make_request(http_client, "POST", "/farming/api/v1/user-rates/login",
                                           json={'userId': f'{self.user.id}'})
        return response

    @error_handler
    async def get_user_profile(self, http_client):
        response = await self.make_request(http_client, "GET",
                                           f"/userprofile/api/v1/users/{self.user.id}/by-telegram-id")
        return response

    @error_handler
    async def balance_by_address(self, http_client, address: str):
        response = await self.make_request(http_client, "GET",
                                           f"/balance/api/v1/balance/{address}/by-address")
        return response

    @error_handler
    async def get_farm_status(self, http_client):
        response = await self.make_request(http_client, "GET", f"/farming/api/v1/farming/{self.user.id}/running")
        return response

    @error_handler
    async def get_farm_boosts(self, http_client):
        response = await self.make_request(http_client, "GET", f"/farming/api/v1/boosts/{self.user.id}")
        return response

    @error_handler
    async def get_tasks(self, http_client):
        response = await self.make_request(http_client, "GET", f"/farming/api/v1/tasks")
        return response

    @error_handler
    async def start_farm(self, http_client):
        payload = {'userId': f'{self.user.id}', 'taskId': '1'}
        response = await self.make_request(http_client, "POST", '/farming/api/v1/farming/start', json=payload)
        return response

    @error_handler
    async def claim_farm(self, http_client, task_id: str):
        payload = {'userId': f'{self.user.id}', 'taskId': f'{task_id}'}
        response = await self.make_request(http_client, "POST", '/farming/api/v1/farming/claim', json=payload)
        return response

    @error_handler
    async def get_quests_categories(self, http_client):
        response = await self.make_request(http_client, "GET", f"/quests/api/v1/quests/categories")

        return response

    @error_handler
    async def get_quests(self, http_client):
        response = await self.make_request(http_client, "GET", f"/quests/api/v1/quests?userId={self.user.id}&size=50")

        return response

    @error_handler
    async def start_quest(self, http_client, project: str, quest_id: str):
        payload = {'project': f'{project}', 'userId': f'{self.user.id}', 'questId': f'{quest_id}'}
        response = await self.make_request(http_client, "POST", '/quests/api/v1/start', json=payload)
        return response

    @error_handler
    async def claim_quest(self, http_client, project: str, quest_id: str):
        payload = {'project': f'{project}', 'userId': f'{self.user.id}', 'questId': f'{quest_id}'}
        response = await self.make_request(http_client, "POST", '/quests/api/v1/claim', json=payload)
        return response

    async def run(self) -> None:
        if settings.USE_RANDOM_DELAY_IN_RUN:
            random_delay = randint(settings.RANDOM_DELAY_IN_RUN[0], settings.RANDOM_DELAY_IN_RUN[1])
            logger.info(f"{self.tg_client.name} | Run for <lw>{random_delay}s</lw>")

            await asyncio.sleep(delay=random_delay)

        proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if self.proxy:
            await self.check_proxy(http_client=http_client)

        http_client.headers['User-Agent'] = UserAgent(os='android').random

        while True:
            if self.errors >= settings.ERRORS_BEFORE_STOP:
                logger.error(f"{self.session_name} | Bot stopped (too many errors)")
                break
            try:
                if http_client.closed:
                    if proxy_conn:
                        if not proxy_conn.closed:
                            proxy_conn.close()

                    proxy_conn = ProxyConnector().from_url(self.proxy) if self.proxy else None
                    http_client = CloudflareScraper(headers=headers, connector=proxy_conn)
                    http_client.headers['User-Agent'] = UserAgent(os='android').random

                if not self.token:
                    access_token = await self.auth(http_client=http_client)
                    await asyncio.sleep(delay=0.5)

                    await self.login(http_client=http_client)

                    if access_token.get('code') == 403:
                        logger.info(f"{self.session_name} | Failed login")
                        logger.info(f"{self.session_name} | Sleep <light-red>300s</light-red>")
                        await asyncio.sleep(delay=300)
                        continue
                    else:
                        user_profile = await self.get_user_profile(http_client)
                        wallet = user_profile.get('address')
                        balance_data = await self.balance_by_address(http_client=http_client, address=wallet)
                        balance = round(balance_data.get('data').get('balance', [])[0].get('balance'))
                        logger.info(
                            f"{self.session_name} | <light-red>Login successful.</light-red> Balance: {balance} Wallet: {wallet}")

                        await self.get_farm_boosts(http_client)
                        await asyncio.sleep(delay=0.5)
                        await self.get_tasks(http_client)

                if settings.AUTO_FARM:
                    try:
                        farm_status = await self.get_farm_status(http_client=http_client)

                        if farm_status.get('code') == 200 and farm_status.get('data'):
                            self.farming_end = utils.convert_to_local_and_unix(
                                farm_status.get('data', [])[0].get('timeEnd')) + 120
                            task_id = farm_status.get('data', [])[0].get('_id')
                            is_claimed = farm_status.get('data', [])[0].get('isClaimed')

                            if time() > self.farming_end and is_claimed is False:
                                await self.claim_farm(http_client=http_client, task_id=task_id)
                                await asyncio.sleep(delay=3)

                                start = await self.start_farm(http_client=http_client)
                                if farm_status.get('code') == 200 and farm_status.get('data'):
                                    self.farming_end = utils.convert_to_local_and_unix(
                                        start.get('data').get('timeEnd')) + 120
                                    logger.info(
                                        f"{self.session_name} | Farm started, next claim in {round((self.farming_end - time()) / 60, 2)} min")
                                else:
                                    logger.warning(
                                        f"{self.session_name} | The server returned code: {farm_status.get('code')}")
                            else:
                                logger.info(
                                    f"{self.session_name} | Farming in progress, next claim in {round((self.farming_end - time()) / 60, 2)} min")
                        else:
                            start = await self.start_farm(http_client=http_client)
                            if farm_status.get('code') == 200 and farm_status.get('data'):
                                self.farming_end = utils.convert_to_local_and_unix(
                                    start.get('data').get('timeEnd')) + 120
                                logger.info(
                                    f"{self.session_name} | Farm started, next claim in {round((self.farming_end - time()) / 60, 2)} min")
                            else:
                                logger.warning(
                                    f"{self.session_name} | The server returned code: {farm_status.get('code')}")

                    except Exception as error:
                        logger.error(
                            f"<light-yellow>{self.session_name}</light-yellow> | Error while auto farming: {error}")
                        await asyncio.sleep(delay=3)

                if settings.AUTO_QUESTS:
                    try:
                        quests = await self.get_quests(http_client=http_client)
                        if quests.get('code') == 200 and quests.get('data'):
                            for quest in quests.get('data'):
                                # print(quest)
                                if quest.get('status') == 'new':
                                    start = await self.start_quest(http_client=http_client,
                                                                   project=quest.get('project'),
                                                                   quest_id=quest.get('id'))
                                    if start:
                                        logger.info(f"{self.session_name} | Quest {quest.get('description')} started!")
                                    else:
                                        logger.warning(
                                            f"{self.session_name} | Quest {quest.get('description')} not started!")
                                    await asyncio.sleep(delay=3)
                                elif quest.get('status') == 'progress':
                                    logger.warning(
                                        f"{self.session_name} | Quest {quest.get('description')} In progress, check in app!")
                                    await asyncio.sleep(delay=3)
                                elif quest.get('status') == 'claim':
                                    claim = await self.claim_quest(http_client=http_client,
                                                                   project=quest.get('project'),
                                                                   quest_id=quest.get('id'))
                                    if claim:
                                        logger.success(
                                            f"{self.session_name} | Quest {quest.get('description')} claimed!")
                                    else:
                                        logger.warning(
                                            f"{self.session_name} | Quest {quest.get('description')} not claimed!")

                                    await asyncio.sleep(delay=3)

                    except Exception as error:
                        logger.error(
                            f"<light-yellow>{self.session_name}</light-yellow> | Error while auto quests: {error}")
                        await asyncio.sleep(delay=3)

                # Close connection & reset token
                await http_client.close()
                self.token = None

                big_sleep = randint(a=settings.BIG_SLEEP[0], b=settings.BIG_SLEEP[1])
                logger.info(f"Big sleep <lw>{big_sleep}s</lw>")
                await asyncio.sleep(delay=big_sleep)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error: {error}")
                await asyncio.sleep(delay=3)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client, proxy=proxy).run()
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
