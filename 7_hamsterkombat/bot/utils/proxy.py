import aiohttp
from better_proxy import Proxy

from bot.utils.logger import logger
from bot.utils.json_db import JsonDB

import os
import sys
import importlib.util
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
file_path = os.path.join(parent_dir, "global_data", "global_config.py")
spec = importlib.util.spec_from_file_location("global_config", file_path)
modu = importlib.util.module_from_spec(spec)
sys.modules["global_config"] = modu
spec.loader.exec_module(modu)
import global_config

def get_proxy_dict(proxy: str):
    if (not global_config.USE_PROXY): return None
    try:
        proxy = Proxy.from_str(proxy=proxy.strip())

        proxy_dict = dict(
            scheme=proxy.protocol,
            hostname=proxy.host,
            port=proxy.port,
            username=proxy.login,
            password=proxy.password,
        )

        return proxy_dict
    except ValueError:
        return None


def get_proxy_string(name: str):
    proxy = ""
    with open('./proxy.txt','r',encoding='utf-8') as file:
        data = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
        for prox, proxName in data:
            if (name == proxName): proxy = prox

    proxy = f"{global_config.PROXY_TYPE}://{proxy.split(':')[2]}:{proxy.split(':')[3]}@{proxy.split(':')[0]}:{proxy.split(':')[1]}"

    return proxy


async def check_proxy(
    http_client: aiohttp.ClientSession, proxy: str, session_name: str
) -> None:
    try:
        response = await http_client.get(
            url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5)
        )
        ip = (await response.json()).get('origin')
        logger.info(f'{session_name} | Proxy IP: {ip}')
    except Exception as error:
        logger.error(f'{session_name} | Proxy: <le>{proxy}</le> | Error: <lr>{error}</lr>')
