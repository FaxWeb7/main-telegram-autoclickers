from utilities.major import MajorBot
from asyncio import sleep
from random import uniform
from data import config
from random import randint
from utilities.core import logger
import asyncio
from aiohttp.client_exceptions import ContentTypeError
from utilities.telegram import Accounts
import datetime
import os

async def majorStart(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    major = await MajorBot.create(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name

    await sleep(uniform(config.DELAYS['ACCOUNT'][0], config.DELAYS['ACCOUNT'][1]))

    while True:
        try:
            await major.login()
            await sleep(30)

        except ContentTypeError as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"Thread {thread} | {account} | Error: {e}")