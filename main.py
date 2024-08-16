import os
import asyncio
import pyrogram
import subprocess
from contextlib import suppress
from shutil import copytree, ignore_patterns, rmtree, copy2
from global_data import global_config
from global_data.global_config import message, petyaPaths, shamhiPaths
from colorama import init, Fore
from colorama import Style
init(autoreset=True)

async def create_session():
    session_name = input('Enter session name (press Enter to exit)\n')
    if not session_name:
        return
    
    proxy_dict = {}
    with open('./global_data/proxies.txt','r') as file:
        proxy_list = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
        for prox,name in proxy_list:
            proxy_dict[name] = prox
    
    if session_name in proxy_dict:
        proxy = proxy_dict[session_name]
        proxy_client = {
            "scheme": global_config.PROXY_TYPE,
            "hostname": proxy.split(':')[0],
            "port": int(proxy.split(':')[1]),
            "username": proxy.split(':')[2],
            "password": proxy.split(':')[3],
        }
        
        session = pyrogram.Client(
            api_id=global_config.API_ID,
            api_hash=global_config.API_HASH,
            name=session_name,
            workdir="./global_data/sessions/",
            proxy=proxy_client
        )

        async with session:
            user_data = await session.get_me()

        print(f'Added session +{user_data.phone_number} @{user_data.username} PROXY {proxy.split(":")[0]}')
    else:
        
        session = pyrogram.Client(
            api_id=global_config.API_ID,
            api_hash=global_config.API_HASH,
            name=session_name,
            workdir="./global_data/sessions/"
        )

        async with session:
            user_data = await session.get_me()

        print(f'Added session +{user_data.phone_number} @{user_data.username} PROXY : NONE')

async def run_script(script_name):
    if ('./' + os.getcwd().split('\\' if os.name == 'nt' else '/')[-1] in petyaPaths+shamhiPaths):
        os.chdir('..')
    os.chdir(script_name)

    process = await asyncio.create_subprocess_exec(
        f'{"python" if os.name == "nt" else "python3.11"}', 'main.py',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    async def read_stream(stream, prefix):
        while True:
            line = await stream.readline()
            if not line:
                break
            pref = f'{Fore.GREEN}[{prefix}]'
            print(f'{pref:<{23}} | {Style.RESET_ALL}{line.decode().rstrip()}')
    
    await asyncio.gather(
        read_stream(process.stdout, script_name.upper()[2:]),
        read_stream(process.stderr, script_name.upper()[2:])
    )

    await process.wait()

async def process():
    print(message)
    while True:
        operation = int(input("Select an action:\n1 -> Actions with sessions\n2 -> Actions with proxies\n3 -> Run bots\n4 -> Exit\n"))

        if (operation == 1):
            sessionOperation = int(input("Select an action with sessions: \n1 -> Add one session from ./global_data/sessions/\n2 -> Add all sessions from ./global_data/sessions/\n3 -> Remove one session from all ./tapalka/sessions\n4 -> Remove all sessions from all ./tapalka/sessions\n5 -> Create new session\n6 -> Exit\n"))
            
            if (sessionOperation == 1):
                sessionNumber = int(input("Enter session number (1-INF): "))
                sessionFilePath = ""
                for root, dirs, files in os.walk('./global_data/sessions/'):
                    for file in files:
                        if file.startswith(str(sessionNumber)+'_'): 
                            sessionFilePath = os.path.join(root, file).split('s/')[1]

                for path in petyaPaths + shamhiPaths:
                    copy2(f'./global_data/sessions/{sessionFilePath}', f'{path}/sessions/')
                print(f'Session {sessionFilePath} added successfully!')
                
            elif (sessionOperation == 2):
                for path in petyaPaths + shamhiPaths:
                    rmtree(f'{path}/sessions')
                    copytree('./global_data/sessions', f'{path}/sessions/', ignore=ignore_patterns('*.txt'))
                print("All sessions added successfully!")

            elif (sessionOperation == 3):
                sessionNumber = int(input("Enter session number (1-INF): "))
                sessionFilePath = ""
                for root, dirs, files in os.walk('./global_data/sessions/'):
                    for file in files:
                        if file.startswith(str(sessionNumber)+'_'): 
                            sessionFilePath = os.path.join(root, file).split('s/')[1]

                for path in petyaPaths + shamhiPaths:
                    os.remove(f'{path}/sessions/{sessionFilePath}')
                print(f'Session {sessionFilePath} successfully removed!')

            elif (sessionOperation == 4):
                for path in petyaPaths + shamhiPaths:
                    rmtree(f'{path}/sessions')
                    os.mkdir(f'{path}/sessions')
                print("All sessions successfully removed!")

            elif (sessionOperation == 5):
                await create_session()

            else: continue

        elif (operation == 2):
            proxyOperation = int(input("Select an action with proxies: \n1 -> Add one proxy from ./global_data/proxies.txt/\n2 -> Add all proxies from ./global_data/proxies.txt/\n3 -> Remove one proxy from all ./tapalka/proxy.txt\n4 -> Remove all proxies from all ./tapalka/proxy.txt\n5 -> Exit\n"))

            if (proxyOperation == 1):
                proxyNumber = int(input("Enter proxy number (1-INF): "))
                proxy = ""
                with open('./global_data/proxies.txt', 'r') as file:
                    for idx, line in enumerate(file):
                        if (idx == proxyNumber-1): proxy = line
                    file.close()
                
                for path in petyaPaths:
                    with open(f'{path}/proxy.txt', 'a') as file:
                        file.write(proxy)
                        file.close()
                
                proxy = proxy.split(' ')[0].split(':')
                proxy = f'{global_config.PROXY_TYPE}://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n'
                for path in shamhiPaths:
                    with open(f'{path}/bot/config/proxies.txt', 'a') as file:
                        file.write(proxy)
                        file.close()

                print(f'Proxy {proxy[0:-1]} added successfully!')
            
            elif (proxyOperation == 2):
                proxies = ""
                with open('./global_data/proxies.txt', 'r') as file:
                    for line in file:
                        proxies += line
                    file.close()
                
                for path in petyaPaths:
                    with open(f'{path}/proxy.txt', 'w') as file:
                        file.write(proxies)
                        file.close()
                
                for path in shamhiPaths:
                    with open(f'{path}/bot/config/proxies.txt', 'w') as file:
                        file.write('')
                        file.close()
                    with open(f'{path}/bot/config/proxies.txt', 'a') as file:
                        for proxy in proxies.split('\n'):
                            if (proxy == '' or proxy == '\n'): continue
                            proxy = proxy.split(' ')[0].split(':')
                            file.write(f'{global_config.PROXY_TYPE}://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n')
                        file.close()

                print(f'All proxies added successfully!')

            elif (proxyOperation == 3):
                proxyNumber = int(input("Enter proxy number (1-INF): "))
                proxy = ""
                with open('./global_data/proxies.txt', 'r') as file:
                    for idx, line in enumerate(file):
                        if (idx == proxyNumber-1): proxy = line
                    file.close()
                
                for path in petyaPaths:
                    data = open(f'{path}/proxy.txt').read().replace(f'{proxy}','')
                    with open(f'{path}/proxy.txt', 'w') as file:
                        file.write(data)
                        file.close()
                
                proxy = proxy.split(' ')[0].split(':')
                proxy = f'{global_config.PROXY_TYPE}://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n'
                for path in shamhiPaths:
                    data = open(f'{path}/bot/config/proxies.txt').read().replace(f'{proxy}','')
                    with open(f'{path}/bot/config/proxies.txt', 'w') as file:
                        file.write(data)
                        file.close()

                print(f'Proxy {proxy[0:-1]} successfully removed!')
            
            elif (proxyOperation == 4):
                for path in petyaPaths:
                    with open(f'{path}/proxy.txt', 'w') as file:
                        file.write('')
                        file.close()
                for path in shamhiPaths:
                    with open(f'{path}/bot/config/proxies.txt', 'w') as file:
                        file.write('')
                        file.close()

                print(f'All proxies successfully removed!')

            else: continue

        elif (operation == 3):
            folders = [f'{path}' for path in petyaPaths+shamhiPaths if global_config.CONECTED_BOTS[path] == True]
            await asyncio.gather(*(run_script(folder) for folder in folders))

        else: break

if __name__ == '__main__':
    with suppress(KeyboardInterrupt, RuntimeError, RuntimeWarning):
        asyncio.run(process())