import sys
import requests
import time
from threading import Thread
from queue import Queue
from loguru import logger
from data import config

TELEGRAM_API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"
message_queue = Queue()
def process_queue():
    while True:
        message = message_queue.get()
        if message is None:
            break
        try:
            time.sleep(3)
            response = requests.post(TELEGRAM_API_URL, data={'chat_id': config.CHAT_ID, 'text': message})
            if response.status_code != 200:
                logger.error(f"Failed to send log to Telegram: {response.text}")
        except Exception as e:
            logger.error(f"Failed to send log to Telegram: {e}")
        finally:
            message_queue.task_done()

thread = Thread(target=process_queue, daemon=True)
thread.start()

logger.remove()
logger.add(sink=sys.stdout, format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <blue>{level: <8}</blue> | <level>{message}</level>")

if config.USE_TG_BOT:
    logger.add(lambda msg: message_queue.put(msg), format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}", level="INFO")

logger = logger.opt(colors=True)
