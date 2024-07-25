import os
import asyncio
from shutil import copytree, ignore_patterns, rmtree, copy2
from loguru import logger
import pyrogram
import global_config

petyaPaths = [
    '../1_blum',
    '../2_onewin',
    '../3_cryptorank',
    '../4_yescoin'
]

shamhiPaths = [
    '../5_tapswap',
    '../6_dotcoin',
    '../7_pocketfi'
]

async def create_session():
    session_name = input('Enter session name (press Enter to exit)\n')
    if not session_name:
        return
    
    proxy_dict = {}
    with open('proxies.txt','r') as file:
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
            workdir="./sessions/",
            proxy=proxy_client
        )

        async with session:
            user_data = await session.get_me()

        logger.success(f'Added session +{user_data.phone_number} @{user_data.username} PROXY {proxy.split(":")[0]}')
    else:
        
        session = pyrogram.Client(
            api_id=global_config.API_ID,
            api_hash=global_config.API_HASH,
            name=session_name,
            workdir="./sessions/"
        )

        async with session:
            user_data = await session.get_me()

        logger.success(f'Added session +{user_data.phone_number} @{user_data.username} PROXY : NONE')

async def process():
    while True:
        operation = int(input("Select an action:\n1 -> Actions with sessions\n2 -> Actions with proxies\n3 -> Exit\n"))

        if (operation == 1):
            sessionOperation = int(input("Select an action with sessions: \n1 -> Add one session from ./sessions\n2 -> Add all sessions from ./sessions\n3 -> Remove one session from all ./tapalka/sessions\n4 -> Remove all sessions from all ./tapalka/sessions\n5 -> Create new session\n6 -> Exit\n"))
            
            if (sessionOperation == 1):
                sessionNumber = int(input("Enter session number (1-INF): "))
                sessionFilePath = ""
                for root, dirs, files in os.walk('./sessions/'):
                    for file in files:
                        if file.startswith(str(sessionNumber)+'_'): 
                            sessionFilePath = os.path.join(root, file).split('s/')[1]

                for path in petyaPaths + shamhiPaths:
                    copy2(f'./sessions/{sessionFilePath}', f'{path}/sessions/')
                print(f'Session {sessionFilePath} added successfully!')
                
            elif (sessionOperation == 2):
                for path in petyaPaths + shamhiPaths:
                    rmtree(f'{path}/sessions')
                    copytree('./sessions', f'{path}/sessions/', ignore=ignore_patterns('*.txt'))
                print("All sessions added successfully!")

            elif (sessionOperation == 3):
                sessionNumber = int(input("Enter session number (1-INF): "))
                sessionFilePath = ""
                for root, dirs, files in os.walk('./sessions/'):
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
            proxyOperation = int(input("Select an action with proxies: \n1 -> Add one proxy from ./proxies.txt\n2 -> Add all proxies from ./proxies.txt\n3 -> Remove one proxy from all ./tapalka/proxy.txt\n4 -> Remove all proxies from all ./tapalka/proxy.txt\n5 -> Exit\n"))

            if (proxyOperation == 1):
                proxyNumber = int(input("Enter proxy number (1-INF): "))
                proxy = ""
                with open('./proxies.txt', 'r') as file:
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
                with open('./proxies.txt', 'r') as file:
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
                            proxy = proxy.split(' ')[0].split(':')
                            file.write(f'{global_config.PROXY_TYPE}://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n')
                        file.close()

                print(f'All proxies added successfully!')

            elif (proxyOperation == 3):
                proxyNumber = int(input("Enter proxy number (1-INF): "))
                proxy = ""
                with open('./proxies.txt', 'r') as file:
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

        else: break

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(process())