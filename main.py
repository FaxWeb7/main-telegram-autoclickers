import os
import asyncio
import argparse

from global_settings import global_settings
from utils.telegram import create_session, leave_chats
from utils.additional import additional_actions
from utils.run import run_soft

async def process():
    print(global_settings.MESSAGE)
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=str, help='Action')
    startAction = parser.parse_args().action
    if (startAction): startAction = int(startAction)

    if not os.path.exists('sessions'):
        os.mkdir('sessions')
    if not os.path.exists('proxies.txt'):
        with open('proxies.txt', 'w') as f: f.write('')
    if not os.path.exists('.env'):
        print("File .env not found, read README!")
        return
    if global_settings.API_ID == 0 or global_settings.API_HASH == '':
        print("API_ID or API_HASH not found in .env, read README!")
        return

    while True:
        if (startAction != None): 
            action = startAction
            startAction = None
        else: action = int(input("Select an action:\n1 -> Create new session\n2 -> Launch software\n3 -> Launch software from a specific bot\n4 -> Additional actions\n4 -> Exit\n"))

        if (action == 1):
            await create_session()

        elif (action == 2):
            await run_soft(0)

        elif (action == 3):
            folders = sorted([f'{path}' for path in global_settings.FIRST_PATHS+global_settings.SECOND_PATHS if global_settings.BOTS_DATA[path]['is_connected']])
            mess = "Enter the NUMBER with which bot to start the software?\n"
            for i in range(len(folders)):
                mess += str(i) + " - " + folders[i] + '\n'
            cur_idx = int(input(mess))
            await run_soft(cur_idx)

        elif (action == 4):
            await additional_actions()

        else: break

if __name__ == '__main__':
    asyncio.run(process())