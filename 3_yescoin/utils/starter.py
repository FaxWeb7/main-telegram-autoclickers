import os
import random
from utils.yescoin import YesCoin
from utils.core import logger
import datetime
from utils.core.telegram import Accounts
from aiohttp.client_exceptions import ContentTypeError
import asyncio
from data import config


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    yes = YesCoin(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await yes.login():
        logger.success(f"Thread {thread} | {account} | Login")

        update = False
        balance = await yes.get_balance()
        (single_coin_value, special_box_left_recovery_count, coin_pool_recovery_level,
         coin_pool_recovery_upgrade_cost, coin_pool_left_recovery_count) = await yes.get_account_build_info()
        while True:
            try:
                if update:
                    (single_coin_value, special_box_left_recovery_count, coin_pool_recovery_level,
                     coin_pool_recovery_upgrade_cost, coin_pool_left_recovery_count) = await yes.get_account_build_info()
                    update = False
                energy = await yes.get_energy()

                if energy > config.MINIMUM_ENERGY:
                    points = await yes.collect_points((energy-config.MINIMUM_ENERGY)//(single_coin_value*2))
                    logger.success(f"Thread {thread} | {account} | Collect {points} points!")
                    balance += points

                if energy < 100 and coin_pool_left_recovery_count and config.BOOSTERS['USE_RECOVERY']:
                    if await yes.recover_coin_pool():
                        logger.success(f"Thread {thread} | {account} | Made a full energy recovery!")
                        coin_pool_left_recovery_count -= 1

                if special_box_left_recovery_count and config.BOOSTERS['USE_CHESTS']:
                    if await yes.get_recover_special_box():
                        box_type, special_box_total_count = await yes.get_special_box_info()
                        special_box_left_recovery_count -= 1
                        await asyncio.sleep(9)

                        collect_points = await yes.collect_special_box_coin(box_type, special_box_total_count)
                        balance += collect_points
                        logger.success(f"Thread {thread} | {account} | Collect {collect_points} points from box!")

                if (coin_pool_recovery_level <= config.AUTOUPGRADE_FILL_RATE[1] and balance > coin_pool_recovery_upgrade_cost
                        and config.AUTOUPGRADE_FILL_RATE[0]):
                    if await yes.upgrade():
                        logger.success(f"Thread {thread} | {account} | Made fill rate upgrade")
                        balance = await yes.get_balance()
                        update = True

                if config.COMPLETE_TASKS:
                    for task in await yes.get_tasks():
                        if not task['taskStatus']:
                            status, bonus = await yes.finish_task(task['taskId'])

                            if status: logger.success(f"Thread {thread} | {account} | Complete task «{task['taskName']}» and got {bonus}")
                            else: logger.error(f"Thread {thread} | {account} | Can't complete task «{task['taskName']}»")
                            await asyncio.sleep(random.uniform(*config.DELAYS['TASKS']))

                await asyncio.sleep(random.uniform(*config.DELAYS['CLICKS']))

                big_sleep = random.randint(*config.DELAYS['BIG_SLEEP'])
                logger.success(f"Thread {thread} | {account} | Sleep {big_sleep}s")
                await asyncio.sleep(big_sleep)

            except ContentTypeError as e:
                logger.error(f"Thread {thread} | {account} | Error: {e}")
                await asyncio.sleep(120)

            except Exception as e:
                logger.error(f"Thread {thread} | {account} | Error: {e}")
                await asyncio.sleep(5)

    await yes.logout()


# async def stats():
#     accounts = await Accounts().get_accounts()

#     tasks = []
#     for thread, account in enumerate(accounts):
#         session_name, phone_number, proxy = account.values()
#         tasks.append(asyncio.create_task(YesCoin(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

#     data = await asyncio.gather(*tasks)

#     path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
#     columns = ['Phone number', 'Name', 'Balance', 'Referrals reward', 'Referrals', 'Referral link', 'Proxy (login:password@ip:port)']

#     if not os.path.exists('statistics'): os.mkdir('statistics')
#     df = pd.DataFrame(data, columns=columns)
#     df.to_csv(path, index=False, encoding='utf-8-sig')

#     logger.success(f"Saved statistics to {path}")
