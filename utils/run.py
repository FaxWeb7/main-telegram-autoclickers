import asyncio
import os
from pathlib import Path
from shutil import copytree, rmtree

from global_settings import global_settings
from utils.logger import logger

async def update_data():
    try:
        logger.info('[SOFT] | update_data | Updating sessions...')
        for path in global_settings.FIRST_PATHS + global_settings.SECOND_PATHS:
            sessions_path = Path(f'bots/{path}/sessions')
            if sessions_path.exists():
                rmtree(sessions_path)
            copytree('sessions', sessions_path)
        logger.info('[SOFT] | update_data | Sessions successfully updated')

        logger.info('[SOFT] | update_data | Updating proxies...')
        all_proxies = ""
        with open('proxies.txt', 'r', encoding='utf-8') as file:
            all_proxies = file.read()

        for path in global_settings.FIRST_PATHS:
            with open(f'bots/{path}/proxy.txt', 'w', encoding='utf-8') as file:
                file.write(all_proxies)

        for path in global_settings.SECOND_PATHS:
            with open(f'bots/{path}/bot/config/proxies.txt', 'w', encoding='utf-8') as file:
                file.write('')
            with open(f'bots/{path}/bot/config/proxies.txt', 'a', encoding='utf-8') as file:
                for proxy in all_proxies.split('\n'):
                    if (proxy == '' or proxy == '\n' or len(proxy.strip().split(' ')) != 2): continue
                    proxy = proxy.strip().split(' ')[0].split(':')
                    file.write(f'{global_settings.PROXY_TYPE}://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n')
        logger.info('[SOFT] | update_data | Proxies successfully updated')

        logger.info('[SOFT] | update_data | Updating configs...')
        config_data = ""
        with open('.env', 'r') as file:
            config_data = file.read()
        for path in global_settings.FIRST_PATHS+global_settings.SECOND_PATHS:
            with open(f'bots/{path}/.env', 'w', encoding='utf-8') as file:
                file.write(config_data)
        logger.info('[SOFT] | update_data | Configs successfully updated')

        return True
    except Exception as e:
        logger.error(f"[SOFT] | update_data | Error in update_data: {e}")
        return False

async def run_soft():
    lapDelay = int(input(f"Enter the number of seconds during which every bot will work: "))
    workDelay = int(input(f"Enter a delay between the work of every pair of bots (in seconds): "))

    ok = await update_data()
    if (not ok): return
    folders = sorted([f'{path}' for path in global_settings.FIRST_PATHS+global_settings.SECOND_PATHS if global_settings.BOTS_DATA[path]['is_connected']])
    cur_idx = 0
    while True:
        try:
            folder = folders[cur_idx].upper()
            logger.info(f"[SOFT] | run_soft | Current working bot: {folder}")
            
            os.chdir(f'bots/{folders[cur_idx]}')
            process = await asyncio.create_subprocess_exec(
                'python' if os.name == 'nt' else 'python3.11',
                f'main.py',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            async def stream_output(process, folder):
                while True:
                    line = await process.stdout.readline()
                    if line:
                        logger.info(f'[{folder}] | {line.decode().rstrip()}')
                    else: break

            async def stream_errors(process, folder):
                while True:
                    line = await process.stderr.readline()
                    if line:
                        logger.error(f'[{folder}] | {line.decode().rstrip()}')
                    else: break

            asyncio.create_task(stream_output(process, folder))
            asyncio.create_task(stream_errors(process, folder))

            await asyncio.sleep(lapDelay)
            process.kill()
            await process.wait()

            logger.info(f"[SOFT] | run_soft | Wait {workDelay} seconds to next bot...")
            await asyncio.sleep(workDelay)
            cur_idx = (cur_idx + 1) % len(folders)

            os.chdir('../../')
        except Exception as e:
            logger.error(f"[SOFT] | run_soft | Error when running main.py in {folder.lower()}: {e}")
            return