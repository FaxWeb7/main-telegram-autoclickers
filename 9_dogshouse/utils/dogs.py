import json
import random
import re
import time
from datetime import datetime, timezone, timedelta
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import asyncio
from urllib.parse import unquote, quote
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_proxy import ProxyConnector


class DogsHouse:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: str | None):
        self.account = session_name + '.session'
        self.thread = thread
        self.ref_code = config.REF_LINK.split('startapp=')[1]
        self.reference, self.telegram_id = None, None
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
        connector = aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(':')[0],
                "port": int(proxy.split(':')[1]),
                "username": proxy.split(':')[2],
                "password": proxy.split(':')[3],
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def verify_task(self, slug: str):
        resp = await self.session.post(f'https://api.onetime.dog/tasks/verify?task={slug}&user_id={self.telegram_id}&reference={self.reference}')
        return (await resp.json()).get('success')

    async def get_tasks(self):
        resp = await self.session.get(f'https://api.onetime.dog/tasks?user_id={self.telegram_id}&reference={self.reference}')
        return await resp.json()

    async def stats(self):
        balance, age, wallet, streak = await self.login(True)

        r = await (await self.session.get(f'https://api.onetime.dog/leaderboard?user_id={self.telegram_id}')).json()
        leaderboard = r.get('me').get('score')

        r = await (await self.session.get(f'https://api.onetime.dog/frens?user_id={self.telegram_id}&reference={self.reference}')).json()
        referrals = r.get('count')
        referral_link = f'https://t.me/dogshouse_bot/join?startapp={self.reference}'

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, str(balance), str(leaderboard), str(age), str(streak), str(referrals), referral_link, str(wallet), proxy]

    async def logout(self):
        await self.session.close()

    async def login(self, stats: bool = False):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None, None

        r = await (await self.session.post(f'https://api.onetime.dog/join?invite_hash={self.ref_code}', data=query)).json()
        self.reference = r.get('reference')
        self.telegram_id = r.get('telegram_id')

        if stats: return r.get('balance'), r.get('age'), r.get('wallet'), r.get('streak')
        else: return r.get('balance'), r.get('age')

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('dogshouse_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('dogshouse_bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param=self.ref_code
            ))
            await self.client.disconnect()
            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query

        except:
            return None
