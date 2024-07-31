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

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers


class Claimer:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

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

            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('pocketfi_bot'),
                bot=await self.tg_client.resolve_peer('pocketfi_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://botui.pocketfi.org/mining/'
            ))

            auth_url = web_view.url
            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def get_mining_data(self, http_client: aiohttp.ClientSession) -> dict[str]:
        try:
            response = await http_client.get('https://gm.pocketfi.org/mining/getUserMining')
            response.raise_for_status()

            response_json = await response.json()
            mining_data = response_json['userMining']

            return mining_data
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
            await asyncio.sleep(delay=3)

    async def send_claim(self, http_client: aiohttp.ClientSession) -> bool:
        try:
            response = await http_client.post('https://gm.pocketfi.org/mining/claimMining', json={})
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when Claiming: {error}")
            await asyncio.sleep(delay=3)

            return False

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def check_daily(self, http_client: aiohttp.ClientSession) -> bool:
        try:
            response = await http_client.get('https://gm.pocketfi.org/mining/taskExecuting')
            response.raise_for_status()
            response_json = await response.json()
            claim = response_json['tasks']['daily'][0]['doneAmount']
            if claim == 0:
                return True
            else:
                return False
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when checking for daily reward: {error}")
            await asyncio.sleep(delay=3)

    async def claim_daily(self, http_client: aiohttp.ClientSession) -> int:
        try:
            response = await http_client.post(url='https://gm.pocketfi.org/boost/activateDailyBoost', json={})
            response.raise_for_status()
            response_json = await response.json()
            return response_json['updatedForDay']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming daily reward: {error}")
            await asyncio.sleep(delay=3)

    async def run(self, proxy: str | None) -> None:
        await asyncio.sleep(randint(*settings.ACC_DELAY))
        access_token_created_time = 0
        claim_time = 0

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, proxy=proxy)

            while True:
                try:
                    if time() - access_token_created_time >= 3600:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy)

                        http_client.headers["telegramRawData"] = tg_web_data
                        headers["telegramRawData"] = tg_web_data

                        access_token_created_time = time()

                        mining_data = await self.get_mining_data(http_client=http_client)

                        last_claim_time = datetime.fromtimestamp(
                            int(str(mining_data['dttmLastClaim'])[:-3])).strftime('%Y-%m-%d %H:%M:%S')
                        claim_deadline_time = datetime.fromtimestamp(
                            int(str(mining_data['dttmClaimDeadline'])[:-3])).strftime('%Y-%m-%d %H:%M:%S')

                        logger.info(f"{self.session_name} | Last claim time: {last_claim_time}")
                        logger.info(f"{self.session_name} | Claim deadline time: {claim_deadline_time}")

                    mining_data = await self.get_mining_data(http_client=http_client)

                    balance = mining_data['gotAmount']
                    available = mining_data['miningAmount']
                    speed = mining_data['speed']

                    logger.info(f"{self.session_name} | Balance: <c>{balance}</c> | "
                                f"Available: <e>{available}</e> | "
                                f"Speed: <m>{speed}</m>")

                    targetSleep = randint(settings.SLEEP_BETWEEN_CLAIM[0], settings.SLEEP_BETWEEN_CLAIM[1])
                    if time() - claim_time >= targetSleep * 60 and available > 0:
                        retry = 0
                        daily = await self.check_daily(http_client=http_client)
                        if daily:
                            claim = await self.claim_daily(http_client=http_client)
                            logger.info(f"{self.session_name} | Successful daily claim | "
                                        f"Current day: <g>{claim+1}</g>")
                        targetRetry = randint(settings.CLAIM_RETRY[0], settings.CLAIM_RETRY[1])
                        while retry <= targetRetry:
                            status = await self.send_claim(http_client=http_client)
                            if status:
                                mining_data = await self.get_mining_data(http_client=http_client)

                                balance = mining_data['gotAmount']

                                logger.success(f"{self.session_name} | Successful claim | "
                                               f"Balance: <c>{balance}</c> (<g>+{available}</g>)")
                                logger.info(f"Next claim in {targetSleep}min")

                                claim_time = time()
                                break

                            logger.info(f"{self.session_name} | Retry <y>{retry}</y> of <e>{targetRetry}</e>")
                            retry += 1

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)

                else:
                    logger.info(f"Sleep 10min")
                    await asyncio.sleep(delay=600)


async def run_claimer(tg_client: Client, proxy: str | None):
    try:
        await Claimer(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
