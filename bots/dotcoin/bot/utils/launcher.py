import os
import glob
import asyncio

from pyrogram import Client
from better_proxy import Proxy

from bot.config import settings
from bot.utils import logger
from bot.core.claimer import run_claimer


start_text = """
Select an action:

    1. Create session
    2. Run Clicker
"""


def get_session_names() -> list[str]:
    session_names = glob.glob('sessions/*.session')
    session_names = [os.path.splitext(os.path.basename(file))[0] for file in session_names]

    return session_names


def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open('bot/config/proxies.txt', 'r', encoding='utf-8-sig') as file:
            proxies = file.read().split('\n')
            proxies = [i for i in proxies if i != '' and i != '\n' and len(i.split(' ')) == 2]
    else:
        proxies = []
    return proxies


async def get_tg_clients() -> list[Client]:
    session_names = get_session_names()

    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    tg_clients = [Client(
        name=session_name,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        workdir='sessions/',
        plugins=dict(root='bot/plugins'),
    ) for session_name in session_names]

    return tg_clients


async def process() -> None:
    logger.info(f"Detected {len(get_session_names())} sessions | {len(get_proxies())} proxies")
    tg_clients = await get_tg_clients()
    await run_tasks(tg_clients=tg_clients)


async def run_tasks(tg_clients: list[Client]):
    proxies = [prox.split() for prox in get_proxies()]
    proxy_dict = {}
    for proxy, name in proxies:
        proxy_dict[name] = f"{settings.PROXY_TYPE}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"

    tasks = []
    for tg_client in tg_clients:
        tasks.append(asyncio.create_task(
            run_claimer(
                tg_client=tg_client,
                proxy=proxies[tg_client.name] if tg_client.name in proxies else None
            )
        ))
    await asyncio.gather(*tasks)
