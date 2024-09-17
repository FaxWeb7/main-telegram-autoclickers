import random
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import aiohttp_proxy
import asyncio
from urllib.parse import unquote
from data import config
import aiohttp
from fake_useragent import UserAgent


class YesCoin:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"
        connector = aiohttp_proxy.ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

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

    async def stats(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        await self.login()

        r = await (await self.session.get("https://api-backend.yescoin.gold/account/getAccountInfo")).json()
        balance = r.get('data').get('currentAmount')
        referrals_reward = r.get('data').get('inviteAmount')

        r = await (await self.session.get('https://api-backend.yescoin.gold/invite/getInvitedUserList?index=1&totalPage=1&pageSize=10&bindWalletType=0')).json()
        referrals = r.get('data').get("totalRecords")

        r = await (await self.session.get("https://api-backend.yescoin.gold/invite/getInviteGiftBoxInfo")).json()
        referral_code = r.get('data').get('inviteCode')
        referral_link = f"https://t.me/theYescoin_bot/Yescoin?startapp={config.REF_CODE}" if referral_code else '-'

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, str(balance), str(referrals_reward), str(referrals), str(referral_link), proxy]

    async def finish_task(self, task_id):
        resp = await self.session.post('https://api-backend.yescoin.gold/task/finishTask', json=task_id)
        resp_json = await resp.json()

        return resp_json.get('message') == 'Success', resp_json.get('data').get("bonusAmount")

    async def get_tasks(self):
        resp = await self.session.get('https://api-backend.yescoin.gold/task/getCommonTaskList')
        return (await resp.json()).get('data')

    async def tasks(self):
        tasks = await self.get_tasks()
        for task in tasks:
            if not task['taskStatus']:
                await self.finish_task(task['taskId'])

    async def recover_coin_pool(self):
        resp = await self.session.post('https://api-backend.yescoin.gold/game/recoverCoinPool')
        return (await resp.json()).get('data') is True

    async def get_account_build_info(self):
        resp = await self.session.get('https://api-backend.yescoin.gold/build/getAccountBuildInfo')
        resp_json = await resp.json()

        single_coin_value = resp_json.get('data').get('singleCoinValue')  # count point per click
        special_box_left_recovery_count = resp_json.get('data').get('specialBoxLeftRecoveryCount')  # count boost boxes
        coin_pool_recovery_level = resp_json.get('data').get('coinPoolRecoveryLevel')  #upgrade level
        coin_pool_recovery_upgrade_cost = resp_json.get('data').get('coinPoolRecoveryUpgradeCost')  # upgrade price
        coin_pool_left_recovery_count = resp_json.get('data').get('coinPoolLeftRecoveryCount')

        return single_coin_value, special_box_left_recovery_count, coin_pool_recovery_level, coin_pool_recovery_upgrade_cost, coin_pool_left_recovery_count

    async def collect_special_box_coin(self, box_type: int, coin_count: int):
        json_data = {'boxType': box_type, 'coinCount': coin_count}
        resp = await self.session.post('https://api-backend.yescoin.gold/game/collectSpecialBoxCoin', json=json_data)

        return (await resp.json()).get('data').get("collectAmount")

    async def get_recover_special_box(self):
        resp = await self.session.post('https://api-backend.yescoin.gold/game/recoverSpecialBox')
        return (await resp.json()).get('data') is True

    async def get_special_box_info(self):
        resp = await self.session.get('https://api-backend.yescoin.gold/game/getSpecialBoxInfo')
        resp_json = await resp.json()
        box_type = resp_json.get('data').get('recoveryBox').get('boxType')
        special_box_total_count = resp_json.get('data').get('recoveryBox').get('specialBoxTotalCount')

        return box_type, special_box_total_count

    async def upgrade(self):
        resp = await self.session.post('https://api-backend.yescoin.gold/build/levelUp', json="2")
        return (await resp.json()).get('data')

    async def get_balance(self):
        resp = await self.session.get('https://api-backend.yescoin.gold/account/getAccountInfo')
        return (await resp.json()).get('data').get('currentAmount')

    async def my_squad(self):
        resp = await self.session.get('https://api-backend.yescoin.gold/squad/mySquad')
        resp_json = await resp.json()

        is_join = resp_json.get('data').get('isJoinSquad')
        squad_link = resp_json.get('data').get('squadInfo').get('squadTgLink').split('t.me/')[1] if is_join else ""
        return squad_link.lower()

    async def join_squad(self, link: str = '@ApeCryptor'):
        resp = await self.session.post('https://api-backend.yescoin.gold/squad/joinSquad', json={'squadTgLink': link})
        return (await resp.json()).get('data').get('squadInfo').get("squadTitle")

    async def collect_points(self, count: int):
        resp = await self.session.post('https://api-backend.yescoin.gold/game/collectCoin', json=count)
        return (await resp.json()).get('data').get('collectAmount')

    async def get_energy(self):
        resp = await self.session.get('https://api-backend.yescoin.gold/game/getGameInfo')
        return (await resp.json()).get('data').get('coinPoolLeftCount')

    async def logout(self):
        await self.session.close()

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        json_data = {"code": query}

        resp = await self.session.post('https://api-backend.yescoin.gold/user/login', json=json_data)
        self.session.headers['token'] = (await resp.json()).get('data').get('token')

        return True

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('theYescoin_bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('theYescoin_bot'), short_name="Yescoin"),
                platform='android',
                write_allowed=True,
                start_param=config.REF_CODE
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            return query.replace('"', '\"')

        except:
            return None
