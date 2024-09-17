import asyncio
import os
import random

from data import config
from pyrogram import Client
from utils.core import logger, load_from_json, save_list_to_file, save_to_json, get_all_lines


class Accounts:
    def __init__(self):
        self.workdir = config.WORKDIR
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    @staticmethod
    def parse_proxy(proxy):
        return {
            "scheme": config.PROXY['TYPE']['TG'],
            "hostname": proxy.split(":")[1].split("@")[1],
            "port": int(proxy.split(":")[2]),
            "username": proxy.split(":")[0],
            "password": proxy.split(":")[1].split("@")[0]
        }

    @staticmethod
    def get_available_accounts(sessions: list):
        available_accounts = []

        if config.PROXY['USE_PROXY_FROM_FILE']:
            proxy_dict = {}
            with open(config.PROXY['PROXY_PATH'],'r',encoding='utf-8') as file:
                proxy = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                for prox,name in proxy:
                    proxy_dict[name] = prox

            for session in sessions:
                available_accounts.append({
                    'session_name': session,
                    'phone_number': '+0',
                    'proxy': proxy_dict[session]
                })

        else:
            for session in sessions:
                available_accounts.append({
                    'session_name': session,
                    'phone_number': '+0',
                    'proxy': None
                })
                
        return available_accounts

    def pars_sessions(self):
        sessions = [file.replace(".session", "") for file in os.listdir(self.workdir) if file.endswith(".session")]

        logger.info(f"Searched sessions: {len(sessions)}.")
        return sessions

    async def check_valid_account(self, account: dict):
        session_name, phone_number, proxy = account.values()

        try:
            proxy_dict = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(':')[0],
                "port": int(proxy.split(':')[1]),
                "username": proxy.split(':')[2],
                "password": proxy.split(':')[3],
            } if proxy else None

            client = Client(name=session_name, api_id=self.api_id, api_hash=self.api_hash, workdir=self.workdir, proxy=proxy_dict)

            connect = await asyncio.wait_for(client.connect(), timeout=30)
            if connect:
                await client.get_me()
                await client.disconnect()
                return account
            else:
                await client.disconnect()
        except:
            pass

    async def check_valid_accounts(self, accounts: list):
        logger.info(f"Checking accounts for valid...")

        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(self.check_valid_account(account)))

        v_accounts = await asyncio.gather(*tasks)

        valid_accounts = [account for account, is_valid in zip(accounts, v_accounts) if is_valid]
        invalid_accounts = [account for account, is_valid in zip(accounts, v_accounts) if not is_valid]
        logger.success(f"Valid accounts: {len(valid_accounts)}; Invalid: {len(invalid_accounts)}")

        return valid_accounts, invalid_accounts

    async def get_accounts(self):
        sessions = self.pars_sessions()
        available_accounts = self.get_available_accounts(sessions)

        if not available_accounts:
            raise ValueError("Have not available accounts!")
        else:
            logger.success(f"Search available accounts: {len(available_accounts)}.")

        valid_accounts, invalid_accounts = await self.check_valid_accounts(available_accounts)

        if invalid_accounts:
            save_list_to_file(f"{config.WORKDIR}invalid_accounts.txt", invalid_accounts)
            logger.info(f"Saved {len(invalid_accounts)} invalid account(s) in {config.WORKDIR}invalid_accounts.txt")

        if not valid_accounts:
            raise ValueError("Have not valid sessions")
        else:
            return valid_accounts

    async def create_sessions(self):
        while True:
            session_name = input('\nInput the name of the session (press Enter to exit): ')
            if not session_name: return

            if config.PROXY['USE_PROXY_FROM_FILE']:
                proxys = get_all_lines(config.PROXY['PROXY_PATH'])
                proxy = random.choice(proxys) if proxys else None
            else:
                proxy = input("Input the proxy in the format login:password@ip:port (press Enter to use without proxy): ")

            dict_proxy = self.parse_proxy(proxy) if proxy else None

            phone_number = (input("Input the phone number of the account: ")).replace(' ', '')
            phone_number = '+' + phone_number if not phone_number.startswith('+') else phone_number

            client = Client(
                api_id=self.api_id,
                api_hash=self.api_hash,
                name=session_name,
                workdir=self.workdir,
                phone_number=phone_number,
                proxy=dict_proxy,
                lang_code='ru'
            )

            async with client:
                me = await client.get_me()

            save_to_json(f'{config.WORKDIR}accounts.json', dict_={
                "session_name": session_name,
                "phone_number": phone_number,
                "proxy": proxy
            })
            logger.success(f'Added a account {me.username} ({me.first_name}) | {me.phone_number}')