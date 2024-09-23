import sys
import requests
import time
from threading import Thread
from queue import Queue
from loguru import logger

from global_settings import global_settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{global_settings.BOT_TOKEN}/sendMessage"
message_queue = Queue()
def process_queue():
    while True:
        message = message_queue.get()
        if message is None:
            break
        try:
            time.sleep(5)
            response = requests.post(TELEGRAM_API_URL, data={'chat_id': global_settings.CHAT_ID, 'text': message})
            if response.status_code != 200:
                if ('Too Many Requests' in response.text):
                    cooldown = int(response.text.split('retry after ')[1].split(',')[0][:-1]) + 600
                    logger.error(f"Too many requests to telegram bot, wait {cooldown} seconds")
                    time.sleep(cooldown)
                else:
                    logger.error(f"Failed to send log to Telegram: {response.text}")
        except Exception as e:
            logger.error(f"Failed to send log to Telegram: {e}")
        finally:
            message_queue.task_done()

thread = Thread(target=process_queue, daemon=True)
thread.start()

logger.remove()
logger.add(sys.stdout, format="<blue>{time:YYYY-MM-DD HH:mm:ss} | </blue> <level>{message}</level>", colorize=True)

if global_settings.USE_TG_BOT:
    logger.add(lambda msg: message_queue.put(msg), format="{time:YYYY-MM-DD HH:mm:ss} | {message}", level="INFO")

logger = logger.opt(colors=True)