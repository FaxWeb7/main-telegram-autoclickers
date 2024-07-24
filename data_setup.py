import os
from shutil import copytree, ignore_patterns, rmtree, copy2

petyaPaths = [
    './1_blum',
    './2_onewin',
    './3_cryptorank',
    './4_yescoin'
]

shamhiPaths = [
    './5_tapswap',
    './6_dotcoin',
    './7_pocketfi'
]

while True:
    operation = int(input("Select an action:\n1 -> Actions with sessions\n2 -> Actions with proxies\n3 -> Exit\n"))

    if (operation == 1):
        sessionOperation = int(input("Select an action with sessions: \n1 -> Add one session from ./data/sessions\n2 -> Add all sessions from ./data/sessions\n3 -> Remove one session from all ./tapalka/sessions\n4 -> Remove all sessions from all ./tapalka/sessions\n5 -> Exit\n"))
        
        if (sessionOperation == 1):
            sessionNumber = int(input("Enter session number (1-INF): "))
            sessionFilePath = ""
            for root, dirs, files in os.walk('./data/sessions/'):
                for file in files:
                    if file.startswith(str(sessionNumber)+'_'): 
                        sessionFilePath = os.path.join(root, file).split('s/')[1]

            for path in petyaPaths + shamhiPaths:
                copy2(f'./data/sessions/{sessionFilePath}', f'{path}/sessions/')
            print(f'Session {sessionFilePath} added successfully!')
            
        elif (sessionOperation == 2):
            for path in petyaPaths + shamhiPaths:
                rmtree(f'{path}/sessions')
                copytree('./data/sessions', f'{path}/sessions/', ignore=ignore_patterns('*.txt'))
            print("All sessions added successfully!")

        elif (sessionOperation == 3):
            sessionNumber = int(input("Enter session number (1-INF): "))
            sessionFilePath = ""
            for root, dirs, files in os.walk('./data/sessions/'):
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
        
        else: continue


    elif (operation == 2):
        proxyOperation = int(input("Select an action with proxies: \n1 -> Add one proxy from ./data/proxies.txt\n2 -> Add all proxies from ./data/proxies.txt\n3 -> Remove one proxy from all ./tapalka/proxy.txt\n4 -> Remove all proxies from all ./tapalka/proxy.txt\n5 -> Exit\n"))

        if (proxyOperation == 1):
            proxyNumber = int(input("Enter proxy number (1-INF): "))
            proxy = ""
            with open('./data/proxies.txt', 'r') as file:
                for idx, line in enumerate(file):
                    if (idx == proxyNumber-1): proxy = line
                file.close()
            
            for path in petyaPaths:
                with open(f'{path}/proxy.txt', 'a') as file:
                    file.write(proxy)
                    file.close()
            
            proxy = proxy.split(' ')[0].split(':')
            proxy = f'socks5://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n'
            for path in shamhiPaths:
                with open(f'{path}/bot/config/proxies.txt', 'a') as file:
                    file.write(proxy)
                    file.close()

            print(f'Proxy {proxy[0:-1]} added successfully!')
        
        elif (proxyOperation == 2):
            proxies = ""
            with open('./data/proxies.txt', 'r') as file:
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
                        file.write(f'socks5://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n')
                    file.close()

            print(f'All proxies added successfully!')

        elif (proxyOperation == 3):
            proxyNumber = int(input("Enter proxy number (1-INF): "))
            proxy = ""
            with open('./data/proxies.txt', 'r') as file:
                for idx, line in enumerate(file):
                    if (idx == proxyNumber-1): proxy = line
                file.close()
            
            for path in petyaPaths:
                data = open(f'{path}/proxy.txt').read().replace(f'{proxy}','')
                with open(f'{path}/proxy.txt', 'w') as file:
                    file.write(data)
                    file.close()
            
            proxy = proxy.split(' ')[0].split(':')
            proxy = f'socks5://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}\n'
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
