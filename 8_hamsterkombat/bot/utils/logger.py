import sys
import requests
from loguru import logger
from bot.config import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
def send_log_to_telegram(message):
    try:
        response = requests.post(TELEGRAM_API_URL, data={'chat_id': settings.CHAT_ID, 'text': message})
        if response.status_code != 200:
            logger.error(f"Failed to send log to Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Failed to send log to Telegram: {e}")

logger.remove()
logger.add(sink=sys.stdout, format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
                                   " | <level>{level: <8}</level>"
                                   " | <cyan><b>{line}</b></cyan>"
                                   " - <white><b>{message}</b></white>")

if settings.USE_TG_BOT:
    logger.add(lambda msg: send_log_to_telegram(msg), format="<white>{time:YYYY-MM-DD HH:mm:ss}</white>"
                                   " | <level>{level: <8}</level>"
                                   " | <cyan><b>{line}</b></cyan>"
                                   " - <white><b>{message}</b></white>", level="INFO")
    
logger = logger.opt(colors=True)