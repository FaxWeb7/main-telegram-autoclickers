from utils.core import create_sessions
from utils.telegram import Accounts
from utils.cats import Cats
from data.config import USE_PROXY
import asyncio

async def main():
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
    
if __name__ == '__main__':
    asyncio.run(main())
