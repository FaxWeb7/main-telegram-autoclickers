from utils.core import create_sessions
from utils.telegram import Accounts
from utils.cats import Cats
from data.config import USE_PROXY
import asyncio
import os
import csv

async def main():
    action = 1
    
    if not os.path.exists('sessions'):
        os.mkdir('sessions')
    
    if action == 2:
        await create_sessions()

    if action == 1:
        accounts = await Accounts().get_accounts()
                
        tasks = []
        if USE_PROXY:
            proxy_dict = {}
            with open('proxy.txt','r',encoding='utf-8') as file:
                proxy = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                for prox,name in proxy:
                    proxy_dict[name] = prox
            for thread, account in enumerate(accounts):
                if account in proxy_dict:
                    tasks.append(asyncio.create_task(Cats(account=account, thread=thread, proxy=proxy_dict[account]).main()))
                else:
                    tasks.append(asyncio.create_task(Cats(account=account, thread=thread,proxy = None).main()))
        else:
            for thread, account in enumerate(accounts):
                tasks.append(asyncio.create_task(Cats(account=account, thread=thread,proxy = None).main()))
        await asyncio.gather(*tasks)
    
    if action == 3:
        accounts = await Accounts().get_accounts()
                
        tasks = []
        if USE_PROXY:
            proxy_dict = {}
            with open('proxy.txt','r',encoding='utf-8') as file:
                proxy = [i.strip().split() for i in file.readlines() if len(i.strip().split()) == 2]
                for prox,name in proxy:
                    proxy_dict[name] = prox
            for thread, account in enumerate(accounts):
                if account in proxy_dict:
                    tasks.append(asyncio.create_task(Cats(account=account, thread=thread, proxy=proxy_dict[account]).stats()))
                else:
                    tasks.append(asyncio.create_task(Cats(account=account, thread=thread,proxy = None).stats()))
        else:
            for thread, account in enumerate(accounts):
                tasks.append(asyncio.create_task(Cats(account=account, thread=thread,proxy = None).stats()))
        results = await asyncio.gather(*tasks)
        
        with open('stats.csv', 'w', newline='') as csvfile:
            fieldnames = ['id','username', 'age', 'total']
        
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
            for row in results:
                writer.writerow(row)

if __name__ == '__main__':
    asyncio.run(main())
