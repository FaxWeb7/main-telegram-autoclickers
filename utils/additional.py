import os
import asyncio

from utils.telegram import leave_chats
from utils.logger import logger

async def additional_actions():
    action = int(input("Select an additional action: \n1 -> Log out of all channels and groups in sessions/*.sessions\n2 -> Exit\n"))
    if (action == 1):
        session_names = []
        for session_name in os.listdir("sessions/"):
            if os.path.isfile(os.path.join("sessions/", session_name)):
                if (session_name.split('.')[1] != 'session'): continue
                session_names.append(session_name.split('.')[0])

        logger.info(f"[SOFT] | additional_actions | Found {len(session_names)} sessions...")
        await asyncio.gather(*(leave_chats(session_name) for session_name in session_names))

    else: return 