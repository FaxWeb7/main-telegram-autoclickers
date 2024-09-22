import asyncio
import os, sys
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
                file.write(all_proxies)
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
    session_path = Path('sessions')
    session_files = session_path.glob('*.session')
    session_names = [file.stem for file in session_files]
    if (len(session_names) == 0):
        print("Create sessions!")
        return
    
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
            
            def colored_message(message):
                if "ERROR" in message: return f"<red>{message}</red>"
                elif "INFO" in message: return f"<white>{message}</white>"
                else: return f"<green>{message}</green>"

            async def stream_output(process, folder):
                while True:
                    line = await process.stdout.readline()
                    if line:
                        s = line.decode(sys.stdout.encoding).rstrip().replace("<", "\\<").replace(">", "\\>")
                        logger.info(f'<blue>[{folder}] | </blue> {colored_message(s)}')
                    else: break

            async def stream_errors(process, folder):
                while True:
                    line = await process.stderr.readline()
                    if line:
                        s = line.decode(sys.stdout.encoding).rstrip().replace("<", "\\<").replace(">", "\\>")
                        logger.error(f'<blue>[{folder}] | </blue> {s}')
                    else: break

            asyncio.create_task(stream_output(process, folder))
            asyncio.create_task(stream_errors(process, folder))
            await process.wait()

            logger.info(f"[SOFT] | run_soft | Wait {workDelay} seconds to next bot...")
            await asyncio.sleep(workDelay)
            cur_idx = (cur_idx + 1) % len(folders)

            os.chdir('../../')
        except Exception as e:
            logger.error(f"[SOFT] | run_soft | Error when running main.py in {folder.lower()}: {e}")
            return