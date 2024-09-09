import os
import random
from utils.ton_station import TonStation
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
from aiohttp.client_exceptions import ContentTypeError
import asyncio
from data import config


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    tons = TonStation(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await tons.login()
    while True:
        try:
            farming = await tons.farming_running()
            if farming is False:
                if await tons.farming_start():
                    logger.success(f"Thread {thread} | {account} | Start farming")
                else:
                    logger.warning(f"Thread {thread} | {account} | Couldn't start farming")

            if farming is not False and tons.iso_to_unix_time(farming['timeEnd']) > tons.current_time():
                sleep = tons.iso_to_unix_time(farming['timeEnd']) - tons.current_time() + random.uniform(*config.DELAYS['CLAIM'])
                logger.info(f"Thread {thread} | {account} | Sleep {round(sleep, 1)} seconds")
                await asyncio.sleep(sleep)

            if farming is not False and tons.iso_to_unix_time(farming['timeEnd']) < tons.current_time():
                await tons.login()
                farming = await tons.farming_claim(farming["_id"])
                if farming:
                    logger.success(f"Thread {thread} | {account} | Claim farming! Balance: {farming.get('amount')}")
                else:
                    logger.warning(f"Thread {thread} | {account} | Couldn't claim farming")

            await asyncio.sleep(random.uniform(*config.DELAYS['REPEAT']))
            
        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(1)

    await tons.logout()

