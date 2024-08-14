import asyncio
from datetime import datetime
from time import time
from typing import Any
from urllib.parse import unquote, quote

import aiohttp
from fake_useragent import UserAgent
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw import types
from pyrogram.raw.functions.messages import RequestAppWebView
from bot.core.agents import generate_random_user_agent
from bot.config import settings

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers

from random import randint


class Tapper:
    def __init__(self, tg_client: Client):
        self.tg_client = tg_client
        self.session_name = tg_client.name

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
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            peer = await self.tg_client.resolve_peer('lost_dogs_bot')

            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                platform='android',
                app=types.InputBotAppShortName(bot_id=peer, short_name="lodoapp"),
                write_allowed=True,
                start_param='ref-u_6046075760__s_573809'
            ))

            auth_url = web_view.url

            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            tg_web_data_parts = tg_web_data.split('&')

            user_data = tg_web_data_parts[0].split('=')[1]
            chat_instance = tg_web_data_parts[1].split('=')[1]
            chat_type = tg_web_data_parts[2].split('=')[1]
            start_param = tg_web_data_parts[3].split('=')[1]
            auth_date = tg_web_data_parts[4].split('=')[1]
            hash_value = tg_web_data_parts[5].split('=')[1]

            user_data_encoded = quote(user_data)

            init_data = (f"user={user_data_encoded}&chat_instance={chat_instance}&chat_type={chat_type}&"
                         f"start_param={start_param}&auth_date={auth_date}&hash={hash_value}")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return init_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def get_info_data(self, http_client: aiohttp.ClientSession):
        try:
            url = ('https://api.getgems.io/graphql?operationName=lostDogsWayUserInfo&variables=%7B%7D&extensions='
                   '%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash'
                   '%22%3A%22a17a9e148547c1c0ab250cca329a3ca237d46b615365dbd217e32aa7c068d10f%22%7D%7D')
            await http_client.options(url=url)

            response = await http_client.get(url=url)
            response.raise_for_status()

            response_json = await response.json()

            if not response_json["data"]:
                error = response_json["errors"][0]["message"]
                if error == "User not found":
                    register_response = await self.register_user(http_client=http_client)
                    if register_response:
                        logger.success(f"{self.session_name} | User <g>{register_response['nickname']}</g> "
                                       f"successfully registered! | User Id: <le>{register_response['id']}</le> ")
                        return await self.get_info_data(http_client=http_client)

                else:
                    logger.error(f"{self.session_name} | Error in response from server: {error}")
                    await asyncio.sleep(delay=randint(3, 7))

            json_data = {
                'launch': True,
                'timeMs': int(time() * 1000)
            }
            await self.save_game_event(http_client=http_client, data=json_data, event_name="Launch")

            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting user info data: {error}")
            await asyncio.sleep(delay=randint(3, 7))

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def register_user(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                "operationName": "lostDogsWayGenerateWallet",
                "variables": {},
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "d78ea322cda129ec3958fe21013f35ab630830479ea9510549963956127a44dd"
                    }
                }
            }

            response = await http_client.post(url='https://api.getgems.io/graphql', json=json_data)
            response.raise_for_status()
            response_json = await response.json()
            return response_json['data']['lostDogsWayGenerateWallet']['user']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when registering a user: {error}")
            await asyncio.sleep(delay=3)

    async def get_personal_tasks(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url=f'https://api.getgems.io/graphql?operationName=lostDogsWayWoofPersonalTasks&variables='
                                                 f'%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22'
                                                 f'sha256Hash%22%3A%22d94df8d9fce5bfdd4913b6b3b6ab71e2f9d6397e2a17de78872f604b9c53fe79%22%7D%7D')
            response.raise_for_status()
            response_json = await response.json()
            return response_json['data']['lostDogsWayWoofPersonalTasks']['items']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting personal tasks: {error}")
            await asyncio.sleep(delay=3)

    async def get_common_tasks(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url=f'https://api.getgems.io/graphql?operationName=lostDogsWayCommonTasks&variables='
                                                 f'%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash'
                                                 f'%22%3A%227c4ca1286c2720dda55661e40d6cb18a8f813bed50c2cf6158d709a116e1bdc1%22%7D%7D')
            response.raise_for_status()
            response_json = await response.json()
            return response_json['data']['lostDogsWayCommonTasks']['items']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting common tasks: {error}")
            await asyncio.sleep(delay=3)

    async def processing_tasks(self, http_client: aiohttp.ClientSession):
        try:
            personal_tasks = await self.get_personal_tasks(http_client=http_client)
            await asyncio.sleep(delay=2)
            event_data = {
                "commonPageView": "yourDog",
                "timeMs": int(time() * 1000)
            }
            await self.save_game_event(http_client=http_client, data=event_data, event_name="Common Page View")
            for task in personal_tasks:
                if not task['isCompleted'] and task['id'] != 'connectWallet' and task['id'] != 'joinSquad':
                    await asyncio.sleep(delay=randint(5, 10))
                    logger.info(f"{self.session_name} | Performing personal task <lc>{task['name']}</lc>...")
                    response_data = await self.perform_task(http_client=http_client, task_id=task['id'])
                    if response_data and response_data['success']:
                        logger.success(f"{self.session_name} | Task <lc>{response_data['task']['name']}</lc> completed! | "
                                       f"Reward: <e>+{int(response_data['woofReward']) / 1000000000}</e> $WOOF")
                    else:
                        logger.info(f"{self.session_name} | Failed to complete task <lc>{task['context']['name']}</lc>")

            await asyncio.sleep(delay=2)
            common_tasks = await self.get_common_tasks(http_client=http_client)
            done_tasks = await self.get_done_common_tasks(http_client=http_client)
            for task in common_tasks:
                if task['id'] not in done_tasks and task.get('customCheckStrategy') is None:
                    await asyncio.sleep(delay=randint(5, 10))
                    logger.info(f"{self.session_name} | Performing common task <lc>{task['name']}</lc>...")
                    response_data = await self.perform_common_task(http_client=http_client, task_id=task['id'])
                    if response_data and response_data['success']:
                        logger.success(f"{self.session_name} | Task <lc>{response_data['task']['name']}</lc> completed! | "
                                       f"Reward: <e>+{int(response_data['task']['woofReward']) / 1000000000}</e> $WOOF")
                    else:
                        logger.info(f"{self.session_name} | Failed to complete task <lc>{task['context']['name']}</lc>")

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when completing tasks: {error}")
            await asyncio.sleep(delay=3)

    async def perform_task(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            json_data = {
                "operationName": "lostDogsWayCompleteTask",
                "variables": {
                    "type": task_id
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "4c8a2a1192a55e9e84502cdd7a507efd5c98d3ebcb147e307dafa3ec40dca60a"
                    }
                }
            }

            response = await http_client.post(url=f'https://api.getgems.io/graphql', json=json_data)
            response.raise_for_status()
            response_json = await response.json()
            return response_json['data']['lostDogsWayCompleteTask']

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while check in personal task {task_id} | Error: {e}")

    async def perform_common_task(self, http_client: aiohttp.ClientSession, task_id: str):
        try:
            json_data = {
                "operationName": "lostDogsWayCompleteCommonTask",
                "variables": {
                    "id": task_id
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "313971cc7ece72b8e8edce3aa0bc72f6e40ef1c242250804d72b51da20a8626d"
                    }
                }
            }

            response = await http_client.post(url=f'https://api.getgems.io/graphql', json=json_data)
            response.raise_for_status()
            response_json = await response.json()

            event_data = {
                'timeMs': int(time() * 1000),
                'yourDogGetFreeDogs': True
            }
            await self.save_game_event(http_client, data=event_data, event_name="Complete Task")
            if response_json['data'] is None and response_json['errors']:
                error = response_json['errors'][0]['message']
                if error == "Task cannot be checked":
                    logger.info(f"{self.session_name} | Task <lc>{task_id}</lc> without reward")
                    return None

            return response_json['data']['lostDogsWayCompleteCommonTask']

        except Exception as e:
            logger.error(f"{self.session_name} | Unknown error while check in common task {task_id} | Error: {e}")

    async def get_done_common_tasks(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(url=f'https://api.getgems.io/graphql?operationName=lostDogsWayUserCommonTasksDone&variables='
                                                 f'%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22'
                                                 f'sha256Hash%22%3A%2299a387150779864b6b625e336bfd28bbc8064b66f9a1b6a55ee96b8777678239%22%7D%7D')
            response.raise_for_status()
            response_json = await response.json()
            return response_json['data']['lostDogsWayUserCommonTasksDone']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting done tasks: {error}")
            await asyncio.sleep(delay=3)

    async def get_game_status(self, http_client: aiohttp.ClientSession):
        try:
            response = await http_client.get(f'https://api.getgems.io/graphql?operationName=lostDogsWayGameStatus&variables='
                                             f'%7B%7D&extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash'
                                             f'%22%3A%22f706c4cd57a87632bd4360b5458e65f854b07e690cf7f8b9f96567fe072148c1%22%7D%7D')
            response_json = await response.json()
            return response_json['data']['lostDogsWayGameStatus']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting game status: {error}")
            await asyncio.sleep(delay=3)

    async def view_prev_round(self, http_client: aiohttp.ClientSession):
        try:
            json_data = {
                "operationName": "lostDogsWayViewPrevRound",
                "variables": {},
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "9d71c4ff04d1f8ec24f23decd0506e7b1b8a0c70ea6bb4c98fcaf6904eb96c35"
                    }
                }
            }
            response = await http_client.post(f'https://api.getgems.io/graphql', json=json_data)
            response_json = await response.json()
            return response_json['data']['lostDogsWayViewPrevRound']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting game status: {error}")
            await asyncio.sleep(delay=3)

    async def save_game_event(self, http_client: aiohttp.ClientSession, data: Any, event_name: str):
        try:
            json_data = {
                "operationName": "lostDogsWaySaveEvent",
                "variables": {
                    "data": {
                        "events": [data],
                        "utm": {
                            "campaign": None,
                            "content": None,
                            "medium": None,
                            "source": None,
                            "term": None
                        }
                    }
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "0b910804d22c9d614a092060c4f1809ee6e1fc0625ddb30ca08ac02bac32936a"
                     }
                 }
            }
            response = await http_client.post(f'https://api.getgems.io/graphql', json=json_data)
            response_json = await response.json()
            if response_json['data']['lostDogsWaySaveEvent']:
                logger.info(f"{self.session_name} | Game event <m>{event_name}</m> saved successfully")
            else:
                logger.warning(f"{self.session_name} | Failed to save game event: <m>{event_name}</m>")
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when saving game event: {error}")
            await asyncio.sleep(delay=3)

    async def way_vote(self, http_client: aiohttp.ClientSession):
        try:
            event_data = {
                "mainScreenVote": True,
                "timeMs": int(time() * 1000)
            }
            await self.save_game_event(http_client, event_data, event_name="MainScreen Vote")
            await asyncio.sleep(delay=randint(1, 3))

            if settings.RANDOM_CARD:
                number = randint(1, 3)
            else:
                number = settings.CARD_NUMBER

            json_data = {
                "operationName": "lostDogsWayVote",
                "variables": {
                    "value": str(number)
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "6fc1d24c3d91a69ebf7467ebbed43c8837f3d0057a624cdb371786477c12dc2f"
                    }
                }
            }

            response = await http_client.post(f'https://api.getgems.io/graphql', json=json_data)
            response_json = await response.json()
            response.raise_for_status()

            response_data = response_json['data']['lostDogsWayVote']
            card = response_data['selectedRoundCardValue']
            spend_bones = response_data['spentGameDogsCount']

            logger.success(f"{self.session_name} | Successful vote! | Selected card: <y>{card}</y> | "
                           f"Spend Bones: <e>{spend_bones}</e> ")

            return response_data

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when voting: {error}")
            await asyncio.sleep(delay=3)

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        random_delay = randint(settings.ACC_DELAY[0], settings.ACC_DELAY[1])
        logger.info(f"{self.tg_client.name} | Run for <lw>{random_delay}s</lw>")
        await asyncio.sleep(delay=random_delay)
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["User-Agent"] = UserAgent(os='android').random
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)

        if proxy:
            await self.check_proxy(http_client=http_client, proxy=proxy)

        token_live_time = randint(3500, 3600)
        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    http_client.headers["X-Auth-Token"] = tg_web_data
                    user_info = await self.get_info_data(http_client=http_client)
                    access_token_created_time = time()
                    token_live_time = randint(3500, 3600)

                    bones_balance = user_info['data']['lostDogsWayUserInfo']['gameDogsBalance']
                    woof_balance = int(user_info['data']['lostDogsWayUserInfo']['woofBalance']) / 1000000000
                    logger.info(
                        f"{self.session_name} | Balance: Bones = <e>{bones_balance}</e>; $WOOF = <e>{woof_balance}</e>")
                    prev_round_data = user_info['data']['lostDogsWayUserInfo']['prevRoundVote']
                    if prev_round_data:
                        logger.info(f"{self.session_name} | Previous round is over | Getting prediction rewards...")
                        prize = round(int(prev_round_data['woofPrize']) / 1000000000, 2)
                        if prev_round_data['userStatus'] == 'winner':
                            not_prize = round(int(prev_round_data['notPrize']) / 1000000000, 2)
                            logger.success(f"{self.session_name} | Successful card prediction! | "
                                           f"You got <e>{prize}</e> $WOOF and <y>{not_prize}</y> $NOT")
                        elif prev_round_data['userStatus'] == 'loser':
                            logger.info(f"{self.session_name} | Wrong card prediction | You got <e>{prize}</e> $WOOF")

                        await self.view_prev_round(http_client=http_client)
                        await asyncio.sleep(delay=2)

                    await self.processing_tasks(http_client=http_client)
                    await asyncio.sleep(delay=randint(5, 10))

                    current_round = user_info['data']['lostDogsWayUserInfo'].get('currentRoundVote')
                    if not current_round:
                        await self.way_vote(http_client=http_client)
                    else:
                        card = current_round['selectedRoundCardValue']
                        spend_bones = current_round['spentGameDogsCount']
                        logger.info(
                            f"{self.session_name} | Voted card: <y>{card}</y> | Spend Bones: <e>{spend_bones}</e>")

                    game_status = await self.get_game_status(http_client=http_client)
                    game_end_at = datetime.fromtimestamp(int(game_status['gameState']['gameEndsAt']))
                    round_end_at = max(game_status['gameState']['roundEndsAt'] - time(), 0)
                    logger.info(
                        f"{self.session_name} | Current round end at: <lc>{int(round_end_at / 60)}</lc> min |"
                        f" Game ends at : <lc>{game_end_at}</lc>")

                sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                logger.info(f"{self.session_name} | Sleep <y>{sleep_time}</y> seconds")
                await asyncio.sleep(delay=sleep_time)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
