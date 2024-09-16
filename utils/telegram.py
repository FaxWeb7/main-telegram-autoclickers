import pyrogram
import asyncio
from random import randint

from global_settings import global_settings
from utils.logger import logger

async def create_session():
    try:
        session_name = input('Enter session name: ')
        while not session_name:
            print("Invalid session name, try again")
            session_name = input('Enter session name: ')
        
        proxy_dict = {}
        with open('proxies.txt', 'r', encoding='utf-8') as file:
            proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
            for prox,name in proxy_list: proxy_dict[name] = prox
        
        if session_name in proxy_dict:
            proxy = proxy_dict[session_name]
            proxy_client = {
                "scheme": global_settings.PROXY_TYPE,
                "hostname": proxy.split(':')[0],
                "port": int(proxy.split(':')[1]),
                "username": proxy.split(':')[2],
                "password": proxy.split(':')[3],
            }
            
            session = pyrogram.Client(
                api_id=global_settings.API_ID,
                api_hash=global_settings.API_HASH,
                name=session_name,
                workdir="sessions/",
                proxy=proxy_client
            )

            async with session:
                user_data = await session.get_me()
            print(f'Added session +{user_data.phone_number} @{user_data.username} PROXY {proxy.split(":")[0]}')
        else:
            session = pyrogram.Client(
                api_id=global_settings.API_ID,
                api_hash=global_settings.API_HASH,
                name=session_name,
                workdir="sessions/"
            )

            async with session:
                user_data = await session.get_me()
            print(f'Added session +{user_data.phone_number} @{user_data.username} PROXY : NONE')

    except Exception as e:
        print(f'Error (create_session): {e}')

async def leave_chats(session_name):
    sleep_ = randint(*global_settings.ACC_DELAY)
    logger.info(f'[SOFT] | leave_chats | {session_name} | Sleep {sleep_} seconds before start')
    await asyncio.sleep(sleep_)
    try:
        proxy_dict = {}
        with open('proxies.txt', 'r', encoding='utf-8') as file:
            proxy = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
            for prox,name in proxy: proxy_dict[name] = prox

        if session_name in proxy_dict:
            proxy = proxy_dict[session_name]
            proxy_client = {
                "scheme": global_settings.PROXY_TYPE,
                "hostname": proxy.split(':')[0],
                "port": int(proxy.split(':')[1]),
                "username": proxy.split(':')[2],
                "password": proxy.split(':')[3],
            }
            session = pyrogram.Client(
                api_id=global_settings.API_ID,
                api_hash=global_settings.API_HASH,
                name=session_name,
                workdir="sessions/",
                proxy=proxy_client
            )
            logger.info(f'[SOFT] | leave_chats | {session_name} | Sessions will be precessed with proxy {proxy}')
        else:
            session = pyrogram.Client(
                api_id=global_settings.API_ID,
                api_hash=global_settings.API_HASH,
                name=session_name,
                workdir="sessions/"
            )
            logger.info(f'[SOFT] | leave_chats | {session_name} | Session will be precessed without proxy')

        await session.connect()
        async for dialog in session.get_dialogs():
            if str(dialog.chat.type) not in ['ChatType.CHANNEL', 'ChatType.SUPERGROUP', 'ChatType.GROUP']: continue
            try:
                await session.leave_chat(dialog.chat.id)
                logger.success(f'[SOFT] | leave_chats | {session_name} | Leaved from chat {dialog.chat.title}')
                await asyncio.sleep(randint(8, 20))
            except Exception as e:
                logger.error(f'[SOFT] | leave_chats | {session_name} | Error leave from chat {dialog.chat.title}, error log: {e}')
        await session.disconnect()

    except Exception as e:
        logger.error(f'[SOFT] | leave_chats | {session_name} | Error log: {e}')