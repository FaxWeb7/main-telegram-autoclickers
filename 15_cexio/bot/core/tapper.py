import asyncio
from urllib.parse import unquote

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from fake_useragent import UserAgent
from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from datetime import datetime, timedelta, timezone
from random import shuffle, randint
import json


class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0

    async def get_tg_web_data(self, proxy: str | None) -> str:
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
            with_tg = True

            if not self.tg_client.is_connected:
                with_tg = False
                try:
                    await self.tg_client.connect()
                    start_command_found = False

                    async for message in self.tg_client.get_chat_history('cexio_tap_bot'):
                        if (message.text and message.text.startswith('/start')) or (message.caption and message.caption.startswith('/start')):
                            start_command_found = True
                            break

                    if not start_command_found:
                        await self.tg_client.send_message("cexio_tap_bot", f"/start 1724345287669959")
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('cexio_tap_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"{self.session_name} | FloodWait {fl}")
                    logger.info(f"{self.session_name} | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=peer,
                bot=peer,
                platform='android',
                from_bot_menu=False,
                url='https://cexp.cex.io/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

            self.user_id = (await self.tg_client.get_me()).id

            if with_tg is False:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def startTasks(self, http_client: aiohttp.ClientSession, task_list, tg_web_data: str):
        try:
            shuffle(task_list)
            results = []
            for task_id in task_list:
                response = await http_client.post(url='https://cexp.cex.io/api/startTask',
                                                  json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                        'data': {'taskId': task_id}})
                response_text = await response.text()
                response.raise_for_status()
                data = json.loads(response_text)
                if data["status"] == "ok":
                    results.append(True)
                else:
                    logger.info(f'{self.session_name} | Непредвиденная ошибка')
                    results.append(False)
            return results
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when starting tasks, {error}")
            await asyncio.sleep(delay=3)
            return [error] * len(task_list)

    async def checkTasks(self, http_client: aiohttp.ClientSession, task_list, tg_web_data: str):
        try:
            shuffle(task_list)
            results = []
            for task_id in task_list:
                response = await http_client.post(url='https://cexp.cex.io/api/checkTask',
                                                  json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                        'data': {'taskId': task_id}})
                response_text = await response.text()
                response.raise_for_status()
                data = json.loads(response_text)
                if data["status"] == "ok":
                    results.append(True)
                else:
                    logger.info(f'{self.session_name} | Непредвиденная ошибка')
                    results.append(False)
            return results
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming tasks, {error}")
            await asyncio.sleep(delay=3)
            return [error] * len(task_list)

    async def claimTasks(self, http_client: aiohttp.ClientSession, task_list, tg_web_data: str):
        try:
            shuffle(task_list)
            results = []
            for task_id in task_list:
                response = await http_client.post(url='https://cexp.cex.io/api/claimTask',
                                                  json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                        'data': {'taskId': task_id}})
                response_text = await response.text()
                response.raise_for_status()
                data = json.loads(response_text)
                if data["status"] == "ok":
                    results.append(True)
                else:
                    logger.info(f'{self.session_name} | Непредвиденная ошибка')
                    results.append(False)
            return results
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming tasks, {error}")
            await asyncio.sleep(delay=3)
            return [error] * len(task_list)

    async def getTasks(self, http_client: aiohttp.ClientSession, tg_web_data: str):
        try:
            none_tasks = []
            ready_to_check_tasks = []
            response = await http_client.post(url='https://cexp.cex.io/api/getUserInfo',
                                              json={'authData': tg_web_data, 'devAuthData': int(self.user_id),
                                                    'data': {}, 'platform': 'ios'})
            response_text = await response.text()
            response.raise_for_status()
            data = json.loads(response_text)
            if data["status"] == "ok":
                response_text = response_text.replace('\n', '')
                tasks = json.loads(response_text).get("data", {}).get("tasks", {})
                for task_id, task_info in tasks.items():
                    priority = task_info.get("priority", 0)
                    state = task_info.get("state", "")

                    if 13 <= priority <= 30:
                        if state == "NONE":
                            none_tasks.append(task_id)
                        elif state == "ReadyToCheck":
                            ready_to_check_tasks.append(task_id)
                return none_tasks, ready_to_check_tasks
            else:
                logger.info(f'{self.session_name} | Непредвиденная ошибка')
                return [], []
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting tasks, {error}")
            await asyncio.sleep(delay=3)
            return [], []

    async def claim_ref(self, http_client: aiohttp.ClientSession, part, tg_web_data: str):
        try:
            if part == 1:
                response = await http_client.post(url='	https://cexp.cex.io/api/getChildren',
                                              json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                    'data': {}})
                response_text = await response.text()
                response.raise_for_status()
                data = json.loads(response_text)
                return data
            elif part == 2:
                response = await http_client.post(url='	https://cexp.cex.io/api/claimFromChildren',
                                                  json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                        'data': {}})
                response_text = await response.text()
                response.raise_for_status()
                data = json.loads(response_text)
                status = data['status']
                return data
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming squad awards, {error}")
            await asyncio.sleep(delay=3)

            return error

    async def claim_taps(self, http_client: aiohttp.ClientSession, taps, tg_web_data: str) -> bool:
        try:
            response = await http_client.post(url='https://cexp.cex.io/api/claimTaps',
                                              json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                    'data': {'taps': taps}})
            response_text = await response.text()
            response.raise_for_status()
            data = json.loads(response_text)
            if data["status"] == "ok":
                return True
            else:
                logger.info(f'{self.session_name} | Непредвиденная ошибка')
                return False
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claim taps, {error}")
            await asyncio.sleep(delay=3)

            return False

    async def start_farm(self, http_client: aiohttp.ClientSession, tg_web_data: str) -> bool:
        try:
            response = await http_client.post(url='https://cexp.cex.io/api/startFarm',
                                              json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                    'data': {}})
            response_text = await response.text()
            response.raise_for_status()
            data = json.loads(response_text)
            if data["status"] == "ok":
                return True
            else:
                logger.info(f'{self.session_name} | Непредвиденная ошибка')
                return False
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when starting farm, {error}")
            await asyncio.sleep(delay=3)

            return False

    async def claim_farm(self, http_client: aiohttp.ClientSession, tg_web_data: str):
        try:
            response = await http_client.post(url='https://cexp.cex.io/api/claimFarm',
                                              json={'authData': tg_web_data, 'devAuthData': self.user_id,
                                                    'data': {}})
            response_text = await response.text()
            response.raise_for_status()
            data = json.loads(response_text)
            if data["status"] == "ok":
                return "ok"
            elif data["status"] == "error":
                return data["data"]["reason"]
            else:
                logger.info(f'{self.session_name} | Непредвиденная ошибка')
                return False
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming farm, {error}")
            await asyncio.sleep(delay=3)

            return error

    async def profile_data(self, http_client: aiohttp.ClientSession, tg_web_data: str):
        try:
            response = await http_client.post(url='https://cexp.cex.io/api/getUserInfo',
                                              json={'authData': tg_web_data, 'devAuthData': int(self.user_id),
                                                    'data': {}, 'platform': 'ios'})
            response_text = await response.text()
            response.raise_for_status()
            data = json.loads(response_text)
            if data:
                return data
            else:
                logger.error('Data error get')
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting data, {error}")
            await asyncio.sleep(delay=3)

            return error

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def run(self, proxy: str | None) -> None:
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers['User-Agent'] = UserAgent(os='android').random
        async with CloudflareScraper(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            tg_web_data = await self.get_tg_web_data(proxy=proxy)

            while True:
                try:
                    prof_data = await self.profile_data(http_client=http_client, tg_web_data=tg_web_data)
                    if prof_data:
                        pass

                    cooldown = int(prof_data['data']['currentTapWindowFinishAt'])
                    available_taps = int(prof_data['data']['availableTaps'])
                    farm_reward = int(float(prof_data['data']['farmReward']))
                    data = await self.claim_ref(http_client=http_client, tg_web_data=tg_web_data, part=1)
                    none_tasks, ready_to_check_tasks = await self.getTasks(http_client=http_client,
                                                                           tg_web_data=tg_web_data)

                    if settings.CLAIM_TASKS and (none_tasks or ready_to_check_tasks):
                        none_tasks, ready_to_check_tasks = await self.getTasks(http_client=http_client,
                                                                               tg_web_data=tg_web_data)

                        statuses = None

                        if none_tasks:
                            statuses = await self.startTasks(http_client=http_client, task_list=none_tasks,
                                                         tg_web_data=tg_web_data)

                        if ready_to_check_tasks:
                            only_check = True

                        if (statuses is not None and all(statuses)) or only_check:
                            logger.success(f'{self.session_name} | Waiting before claiming, 65 s')
                            await asyncio.sleep(delay=65)
                            none_tasks, ready_to_check_tasks = await self.getTasks(http_client=http_client,
                                                                                   tg_web_data=tg_web_data)
                            status = await self.checkTasks(http_client=http_client, task_list=ready_to_check_tasks,
                                                           tg_web_data=tg_web_data)
                            if all(status):
                                status = await self.claimTasks(http_client=http_client, task_list=ready_to_check_tasks,
                                                               tg_web_data=tg_web_data)
                                if all(status):
                                    logger.success(f'{self.session_name} | Claimed all tasks')

                    if settings.CLAIM_SQUAD_REWARD and int(float(data['data']['totalRewardsToClaim'])) != 0:
                        data = await self.claim_ref(http_client=http_client, tg_web_data=tg_web_data, part=2)
                        if data['status'] == "ok":
                            logger.success(f'{self.session_name} | Claimed referrals reward, amount: '
                                        f'{data["data"]["claimedBalance"]}')

                    if farm_reward == 0 and settings.FARM_MINING_ERA:
                        status = await self.start_farm(http_client=http_client, tg_web_data=tg_web_data)
                        if status is True:
                            prof_data = await self.profile_data(http_client=http_client, tg_web_data=tg_web_data)
                            farm_reward = int(float(prof_data['data']['farmReward']))
                            logger.success(f'{self.session_name} | Start mining era, early reward: {farm_reward}')

                    if farm_reward != 0 and settings.FARM_MINING_ERA:
                        try:
                            farm_reward = int(float(prof_data['data']['farmReward']))
                            current_time = datetime.now()
                            time_conv_rn = current_time.astimezone(timezone.utc)
                            time_conv_rn = time_conv_rn.strftime("%Y-%m-%d %H:%M:%S")
                            farm_start = prof_data['data']['farmStartedAt']
                            convert = datetime.strptime(farm_start, "%Y-%m-%dT%H:%M:%S.%fZ")
                            convert += timedelta(hours=4)
                            if time_conv_rn > str(convert):
                                status = await self.claim_farm(http_client=http_client, tg_web_data=tg_web_data)
                                if status == "ok":
                                    logger.success(f'{self.session_name} | Claimed mining era, got amount: '
                                                   f'{farm_reward}')
                                    status = await self.start_farm(http_client=http_client, tg_web_data=tg_web_data)
                                    if status is True:
                                        prof_data = await self.profile_data(http_client=http_client,
                                                                            tg_web_data=tg_web_data)
                                        farm_reward = int(float(prof_data['data']['farmReward']))
                                        logger.success(
                                            f'{self.session_name} | Start mining era, early reward: {farm_reward}')
                                else:
                                    logger.info(f'{self.session_name} | {status}')
                        except Exception as e:
                            logger.error(e)

                    if available_taps != 0 and settings.TAPS:
                        rand_taps = randint(a=settings.TAPS_AMOUNT[0], b=settings.TAPS_AMOUNT[1])
                        if available_taps < rand_taps:
                            status = await self.claim_taps(http_client=http_client, taps=available_taps,
                                                           tg_web_data=tg_web_data)
                            if status is True:
                                logger.success(f'{self.session_name} | Claimed taps, count: {available_taps}')
                                await asyncio.sleep(delay=2)
                        else:
                            status = await self.claim_taps(http_client=http_client, taps=rand_taps,
                                                       tg_web_data=tg_web_data)
                            if status is True:
                                logger.success(f'{self.session_name} | Claimed taps, count: {rand_taps}')
                                await asyncio.sleep(delay=2)
                    
                    Sleep = randint(*settings.BIG_SLEEP)
                    logger.info(f"Sleep {Sleep} seconds...")
                    await asyncio.sleep(Sleep)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)


async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        sleep_ = randint(*settings.ACC_DELAY)
        logger.info(f"{tg_client.name} | start after {sleep_}")
        await asyncio.sleep(sleep_)
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
